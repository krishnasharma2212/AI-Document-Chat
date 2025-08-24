from flask import Flask, render_template, Response, stream_with_context, request,jsonify,session,redirect
import os
import google.generativeai as genai
from firebase_admin import db
import time

import json
# Get the current time in milliseconds since the epoch

import firebase_admin
from firebase_admin import credentials
import os
# Replace the JSON content here with the actual credentials from your service account
service_account_info = os.environ.get('FIREBASE_CREDENTIALS')

cred = credentials.Certificate(service_account_info)



firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://fauzanai-default-rtdb.firebaseio.com'
})


gemini_api_key = os.environ.get('GEMINI_API_KEY')
genai.configure(api_key = gemini_api_key)
model = genai.GenerativeModel(model_name='gemini-1.5-flash-latest',system_instruction=[
        "You are super intelegent AI Product Search."
    ],)
app = Flask(__name__)
app.secret_key = "fazuansecreatcodedontsharewith anyone"
# Directory where the uploaded files will be saved
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def put_data(path, data):
    """
    Store data in Firebase Realtime Database at the specified path.

    Args:
    path (str): The path in the database where data should be stored.
    data (dict): The data to be stored in the database.

    Example:
    put_data('users/user1', {'name': 'John', 'age': 30})
    """
    ref = db.reference(path)
    ref.set(data)
    print(f"Data successfully written to {path}")

# Function to retrieve data from Firebase Realtime Database
def get_data(path):
    """
    Retrieve data from Firebase Realtime Database at the specified path.

    Args:
    path (str): The path in the database from which data should be retrieved.

    Returns:
    dict: The retrieved data.
    """
    ref = db.reference(path)
    data = ref.get()
    if data:
        print(f"Data retrieved from {path}: {data}")
    else:
        print(f"No data found at {path}")
    return data
def uploadFile(file_content,filename):
    filename = f"uploads/{filename}"
    # Create a temporary file to save the content
    # with tempfile.NamedTemporaryFile(delete=False) as temp_file:
    #     temp_file.write(file_content)
    #     temp_file.flush()  # Make sure all content is written
    #     temp_file_path = temp_file.name

    with open(filename,"wb") as file:
        file.write(file_content)
        file.flush()




    try:

        # Upload the temporary file to Gemini using the file path

        response = genai.upload_file(path=filename)

    finally:
        # Clean up the temporary file
        os.remove(filename)

    return response
# Function to handle the prompt and file input
def prompt(inp,chatId, files=[]):
    try:
        history = get_chat(chatId)
        chats = model.start_chat(history=history)


        sendFiles = []
        saved_file_metadata = []  # List to store file metadata for saving in Firebase

        if files:
            for file in files:
                file_content = file.read()  # Read file content into bytes
                sendFiles.append(uploadFile(file_content, file.filename))
                saved_file_metadata.append(file.filename)


            sendFiles.append(inp)  # Append input with the files
            append_chat_without_retrieve(chatId, {"role": "user", 'parts': [inp,f"Uploaded Files - {saved_file_metadata}"]})

            response = chats.send_message(sendFiles, stream=True)
            fullResponse = ""
            for chunk in response:
                fullResponse += chunk.text
                yield chunk.text.encode('utf-8')

        else:
            response = chats.send_message(inp, stream=True)
            fullResponse = ""
            for chunk in response:
                fullResponse += chunk.text
                yield chunk.text.encode('utf-8')

        append_chat_without_retrieve(chatId,{"role":"model",'parts':[fullResponse]})
    except Exception as e:

        print(e)
        return str(e).encode('utf-8')
def register_user(name, email, password):
    """
    Registers a new user in Firebase Realtime Database.

    Args:
    name (str): The name of the user.
    email (str): The email of the user.
    password (str): The password of the user.

    Returns:
    str: A message indicating whether registration was successful or an error occurred.
    """
    # Replace "." with "," in email to use as a valid Firebase key
    email_key = email.replace('.', ',')

    try:
        # Reference to the user's node in the database
        ref = db.reference(f'users/{email_key}')

        # Check if user already exists
        if ref.get() is not None:
            return f"User with email {email} already exists."

        # Hash the password before storing
        hashed_password = password

        # Save the new user's data
        ref.set({
            'name': name,
            'email': email,
            'password': hashed_password  # Store hashed password
        })

        return f"success"

    except Exception as e:
        return f"Error registering user: {e}"
def login_user(email, password):
    """
    Logs in a user by checking credentials against Firebase Realtime Database.

    Args:
    email (str): The email of the user.
    password (str): The password of the user.

    Returns:
    str: A success message with user info or an error message.
    """
    # Replace "." with "," in email to use as a valid Firebase key
    email_key = email.replace('.', ',')

    try:
        # Reference to the user's node in the database
        ref = db.reference(f'users/{email_key}')
        user_data = ref.get()

        if user_data is None:
            return "User not found."

        # Verify the password
        hashed_password = password
        if user_data['password'] == hashed_password:
            return True
        else:
            return False

    except Exception as e:
        return False

def get_user(email, password):

    # Replace "." with "," in email to use as a valid Firebase key
    email_key = email.replace('.', ',')

    try:
        # Reference to the user's node in the database
        ref = db.reference(f'users/{email_key}')
        user_data = ref.get()

        if user_data is None:
            return "User not found."

        # Verify the password
        hashed_password = password
        if user_data['password'] == hashed_password:
            return user_data
        else:
            return False

    except Exception as e:
        return False

def get_chat(id):

    try:
        # Reference to the user's node in the database
        ref = db.reference(f'chats/{id}')
        user_data = ref.get()

        user_data = list(map(lambda x: user_data[x],user_data))

        return user_data

    except Exception as e:
        return None

def append_chat_without_retrieve(id, new_chat):
    """
    Appends a new chat item to the list in Firebase Realtime Database without retrieving the entire list.

    Args:
    id (str): The ID of the chat.
    new_chat (dict): The new chat dictionary to append.

    Returns:
    str: A success message or error message.
    """
    try:
        # Reference to the chats node in the database with a unique key for each chat
        ref = db.reference(f'chats/{id}')

        # Push the new chat item to the database
        ref.push(new_chat)

        return True

    except Exception as e:
        return False


def allChatUser(email):
    email_key = email.replace('.', ',')

    try:
        # Reference to the user's node in the database
        ref = db.reference(f'users/{email_key}/chats')
        user_data = ref.get()

        user_data = list(map(lambda x: user_data[x],user_data))

        return user_data

    except:
        pass

def addToUser(email,id):
    # Replace "." with "," in email to use as a valid Firebase key
    email_key = email.replace('.', ',')

    try:
        # Reference to the user's node in the database
        ref = db.reference(f'users/{email_key}/chats')
        ref.push(id)



    except Exception as e:
        return False




@app.route('/logout')
def logout():
    session.clear()
    return redirect("/login")
@app.route('/')
def home():
    if "email" in session and login_user(session['email'],session['password']):
        userData = get_user(session['email'],session['password'])
        icon = ""
        for i in userData['name'].split(" "):
            icon+=i[0]
        chat = request.args.get('chat')
        if chat == None:
            chat = []
        else:
            chat = get_chat(chat)


        allChatsList = allChatUser(session['email'])
        allChatsList.reverse()
        return render_template('index.html',icon=icon,name=userData['name'],email=userData['email'],chat=json.dumps(chat),allChat=json.dumps(allChatsList))
    else:
        return redirect('/login')


@app.route('/signup',methods=['POST',"GET"])
def signup():
    if "email" in session and login_user(session['email'],session['password']):
        return redirect('/')

    if request.method == "POST":
        data = request.get_json()

        return jsonify({"data":register_user(data['name'],data['email'],data['password'])})
    return render_template('register.html')
@app.route('/login',methods=['POST',"GET"])
def login():
    if "email" in session and login_user(session['email'],session['password']):
        return redirect('/')
    if request.method == "POST":
        data = request.get_json()
        email = data['email']
        password = data['password']

        m = login_user(email,password)
        if m:
            session['email'] = email
            session['password'] = password

        return jsonify({"data":m})
    return render_template('login.html')

@app.route('/generate', methods=['POST'])
def generate():
    if "email" not in session:
        return "Login Error"
    isFile = True
    # Check if files are present in the request
    if 'files' not in request.files:
        isFile = False


    files = request.files.getlist('files') if isFile else []  # Get the list of files

    # Get additional text data from the request
    promptText = request.form.get('prompt')
    chatId = request.form.get('chatId')


    if chatId == "null":
        chatId = str(int(time.time() * 1000))

        addToUser(session['email'],[chatId,model.generate_content(f"On the basis of the first prompt of user - '{promptText}'. Title the chat only return title.").text])





    if not promptText:
        promptText = " "



    # Stream the response back in chunks
    # Stream the response back in chunks
    response = Response(stream_with_context(prompt(promptText, chatId, files)), content_type='text/plain')
    response.headers['Chat-Id'] = chatId  # Set the Chat-Id in the response headers
    return response


if __name__ == '__main__':
    app.run(debug=True)