# Chatbot Streamlit App

This is a simple Streamlit application that allows users to send messages to a chatbot via a REST API.

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the chatbot server:
   ```
   python server.py
   ```

3. In a new terminal, run the Streamlit app:
   ```
   streamlit run app.py
   ```

4. Open the Streamlit app in your browser (usually at http://localhost:8501).

## Usage

- Enter a message in the text input.
- Click "Send" to send the message to the chatbot.
- The chatbot's response will be displayed below.

## Notes

- The chatbot server runs on http://localhost:5000.
- The current chatbot implementation simply echoes the message. Replace the logic in `server.py` with your actual chatbot API.