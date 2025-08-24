from flask import Flask, render_template, Response, stream_with_context, request, jsonify, session, redirect
import os
import google.generativeai as genai
from firebase_admin import db
import time
import json
import firebase_admin
from firebase_admin import credentials
import cloudinary
import cloudinary.uploader

# ==============================================================================
# CONFIGURATION - LOAD SECRETS FROM ENVIRONMENT VARIABLES
# ==============================================================================

# --- Firebase Configuration ---
# Load Firebase credentials from a JSON string in an environment variable
firebase_credentials_json = os.environ.get('FIREBASE_CREDENTIALS')
if not firebase_credentials_json:
    raise ValueError("FIREBASE_CREDENTIALS environment variable not set.")
service_account_info = json.loads(firebase_credentials_json)
cred = credentials.Certificate(service_account_info)

# Initialize Firebase
firebase_database_url = os.environ.get('FIREBASE_DATABASE_URL')
if not firebase_database_url:
    raise ValueError("FIREBASE_DATABASE_URL environment variable not set.")
firebase_admin.initialize_app(cred, {'databaseURL': firebase_database_url})

# --- Gemini AI Configuration ---
gemini_api_key = os.environ.get('GEMINI_API_KEY')
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY environment variable not set.")
genai.configure(api_key=gemini_api_key)
model = genai.GenerativeModel(
    model_name='gemini-1.5-flash-latest',
    system_instruction=["You are a super intelligent AI assistant."]
)

# --- Cloudinary Configuration ---
cloudinary.config(
    cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME"),
    api_key=os.environ.get("CLOUDINARY_API_KEY"),
    api_secret=os.environ.get("CLOUDINARY_API_SECRET"),
    secure=True
)

# ==============================================================================
# FLASK APPLICATION SETUP
# ==============================================================================

app = Flask(__name__)
# Load Flask secret key from environment variable
flask_secret_key = os.environ.get('FLASK_SECRET_KEY')
if not flask_secret_key:
    raise ValueError("FLASK_SECRET_KEY environment variable not set.")
app.secret_key = flask_secret_key

# Ensure a writable temporary directory exists (for Vercel)
TMP_FOLDER = '/tmp/uploads'
if not os.path.exists(TMP_FOLDER):
    os.makedirs(TMP_FOLDER)

# ==============================================================================
# FILE HANDLING (Cloudinary + Gemini)
# ==============================================================================

def uploadFile(file_content, filename):
    """
    Uploads a file to both Cloudinary (for storage) and Gemini (for analysis).
    Returns a dictionary containing the Gemini file object and the Cloudinary URL.
    """
    # 1. Upload to Cloudinary for permanent storage
    try:
        cloudinary_upload_result = cloudinary.uploader.upload(file_content)
        cloudinary_url = cloudinary_upload_result.get('secure_url')
    except Exception as e:
        print(f"Error uploading to Cloudinary: {e}")
        cloudinary_url = None

    # 2. Write to a temporary file for Gemini upload (Vercel uses /tmp)
    temp_file_path = os.path.join(TMP_FOLDER, filename)
    with open(temp_file_path, "wb") as file:
        file.write(file_content)

    # 3. Upload the temporary file to Gemini for analysis
    gemini_file_response = None
    try:
        gemini_file_response = genai.upload_file(path=temp_file_path)
    except Exception as e:
        print(f"Error uploading to Gemini: {e}")
    finally:
        # 4. Clean up the temporary file
        os.remove(temp_file_path)

    return {
        "gemini_file": gemini_file_response,
        "cloudinary_url": cloudinary_url
    }

# ==============================================================================
# CORE CHAT AND PROMPT LOGIC
# ==============================================================================

def prompt(inp, chatId, files=[]):
    """
    Handles a user's prompt, processes optional files, and streams the AI response.
    """
    try:
        history = get_chat(chatId)
        chats = model.start_chat(history=history)

        gemini_files_to_send = []
        file_metadata_for_history = []

        if files:
            for file in files:
                file_content = file.read()
                upload_results = uploadFile(file_content, file.filename)

                if upload_results["gemini_file"]:
                    gemini_files_to_send.append(upload_results["gemini_file"])
                
                # Store original filename and its permanent Cloudinary URL for history
                file_metadata_for_history.append({
                    "filename": file.filename,
                    "url": upload_results["cloudinary_url"]
                })

            # Create the message parts for the user's prompt in Firebase
            user_parts_for_history = [inp, f"Uploaded Files: {json.dumps(file_metadata_for_history)}"]
            append_chat_without_retrieve(chatId, {"role": "user", 'parts': user_parts_for_history})

            # Send the text prompt and the actual file data to Gemini
            gemini_prompt_content = [inp] + gemini_files_to_send
            response = chats.send_message(gemini_prompt_content, stream=True)

        else:
            append_chat_without_retrieve(chatId, {"role": "user", 'parts': [inp]})
            response = chats.send_message(inp, stream=True)

        # Stream the response and build the full response for history
        fullResponse = ""
        for chunk in response:
            fullResponse += chunk.text
            yield chunk.text.encode('utf-8')
        
        # Save the complete model response to history
        append_chat_without_retrieve(chatId, {"role": "model", 'parts': [fullResponse]})

    except Exception as e:
        print(f"Error in prompt function: {e}")
        yield str(e).encode('utf-8')

# ==============================================================================
# FIREBASE DATABASE FUNCTIONS (User and Chat Management)
# ==============================================================================

def get_chat(id):
    try:
        ref = db.reference(f'chats/{id}')
        data = ref.get()
        return [data[key] for key in data] if data else []
    except Exception as e:
        print(f"Error getting chat: {e}")
        return []

def append_chat_without_retrieve(id, new_chat):
    try:
        ref = db.reference(f'chats/{id}')
        ref.push(new_chat)
        return True
    except Exception as e:
        return False

def register_user(name, email, password):
    email_key = email.replace('.', ',')
    try:
        ref = db.reference(f'users/{email_key}')
        if ref.get() is not None:
            return f"User with email {email} already exists."
        ref.set({'name': name, 'email': email, 'password': password})
        return "success"
    except Exception as e:
        return f"Error registering user: {e}"

def login_user(email, password):
    email_key = email.replace('.', ',')
    try:
        ref = db.reference(f'users/{email_key}')
        user_data = ref.get()
        return user_data and user_data.get('password') == password
    except Exception:
        return False

def get_user(email, password):
    email_key = email.replace('.', ',')
    try:
        ref = db.reference(f'users/{email_key}')
        user_data = ref.get()
        return user_data if user_data and user_data.get('password') == password else None
    except Exception:
        return None

def allChatUser(email):
    email_key = email.replace('.', ',')
    try:
        ref = db.reference(f'users/{email_key}/chats')
        data = ref.get()
        return [data[key] for key in data] if data else []
    except:
        return []

def addToUser(email, id):
    email_key = email.replace('.', ',')
    try:
        ref = db.reference(f'users/{email_key}/chats')
        ref.push(id)
    except Exception:
        return False

# ==============================================================================
# FLASK ROUTES
# ==============================================================================

@app.route('/logout')
def logout():
    session.clear()
    return redirect("/login")

@app.route('/')
def home():
    if "email" in session and login_user(session['email'], session['password']):
        userData = get_user(session['email'], session['password'])
        if not userData: return redirect('/login')
        
        icon = "".join(i[0] for i in userData['name'].split())
        chat_id = request.args.get('chat')
        chat_history = get_chat(chat_id) if chat_id else []
        
        all_chats_list = allChatUser(session['email'])
        if all_chats_list:
            all_chats_list.reverse()
            
        return render_template(
            'index.html',
            icon=icon,
            name=userData['name'],
            email=userData['email'],
            chat=json.dumps(chat_history),
            allChat=json.dumps(all_chats_list)
        )
    return redirect('/login')


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if "email" in session and login_user(session['email'], session['password']):
        return redirect('/')
    if request.method == "POST":
        data = request.get_json()
        result = register_user(data['name'], data['email'], data['password'])
        return jsonify({"data": result})
    return render_template('register.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if "email" in session and login_user(session['email'], session['password']):
        return redirect('/')
    if request.method == "POST":
        data = request.get_json()
        email, password = data['email'], data['password']
        if login_user(email, password):
            session['email'] = email
            session['password'] = password
            return jsonify({"data": True})
        return jsonify({"data": False})
    return render_template('login.html')


@app.route('/generate', methods=['POST'])
def generate():
    if "email" not in session:
        return "Login Error", 401

    files = request.files.getlist('files')
    promptText = request.form.get('prompt', ' ')
    chatId = request.form.get('chatId')

    if chatId == "null" or not chatId:
        chatId = str(int(time.time() * 1000))
        title_response = model.generate_content(
            f"On the basis of this prompt, create a short title for a new chat. Prompt: '{promptText}'. Only return the title."
        )
        chat_title = title_response.text.strip().replace('"', '')
        addToUser(session['email'], [chatId, chat_title])

    response = Response(stream_with_context(prompt(promptText, chatId, files)), content_type='text/plain')
    response.headers['Chat-Id'] = chatId
    return response


if __name__ == '__main__':
    app.run(debug=True)
