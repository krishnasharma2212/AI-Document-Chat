# AI Document Chat 📄🤖

AI Document Chat is an intelligent web application that allows users to have interactive conversations with Google's Gemini AI. It supports user authentication, file uploads to provide context for conversations, and saves chat history for a personalized experience.

![AI Chat Interface](https://i.imgur.com/vH9YgEN.png)

## ✨ Features

- **User Authentication**: Secure sign-up and login system for personalized user sessions.
- **AI-Powered Chat**: Engage in dynamic and intelligent conversations with Google's Gemini Pro model.
- **File Uploads**: Upload documents and files to provide context to the AI for more accurate and relevant responses.
- **Persistent Chat History**: All conversations are saved and can be revisited at any time.
- **Clean User Interface**: A modern and intuitive interface for a seamless user experience.
- **Real-time Streaming**: AI responses are streamed back to the user in real-time for a more interactive feel.

## 🛠️ Technologies Used

- **Backend**: Python, Flask
- **AI Model**: Google Gemini API
- **Database**: Firebase Realtime Database
- **Frontend**: HTML, CSS, JavaScript

## 🚀 Getting Started

Follow these instructions to get a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

- Python 3.7+
- A Google Gemini API Key
- A Firebase project with Realtime Database enabled

### Installation

1.  **Clone the repository:**
    ```sh
    git clone https://github.com/your-username/ai-document-chat.git
    cd ai-document-chat
    ```

2.  **Create and activate a virtual environment:**
    ```sh
    # For Windows
    python -m venv venv
    venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the required dependencies:**
    ```sh
    pip install Flask firebase-admin google-generativeai
    ```

4.  **Configure your credentials:**

    *   **Firebase:**
        *   Go to your Firebase project settings and generate a new private key for your service account.
        *   Replace the `service_account_info` dictionary in `flask_app.py` with the contents of your downloaded JSON file.
        *   Update the `databaseURL` in `firebase_admin.initialize_app` with your Firebase Realtime Database URL.

    *   **Google Gemini:**
        *   Obtain an API key from [Google AI Studio](https://aistudio.google.com/app/apikey).
        *   Replace the placeholder `gemini_api_key` in `flask_app.py` with your actual key.

        ```python
        gemini_api_key = 'YOUR_GEMINI_API_KEY'
        ```

5.  **Set a secret key for the Flask application:**
    *   Change the `app.secret_key` in `flask_app.py` to a new random string for session management.
    ```python
    app.secret_key = "your-very-secret-key"
    ```

### Usage

Once the setup is complete, you can run the application with the following command:

```sh
python flask_app.py
