# Chatbot Streamlit App

This is a simple Streamlit application that allows users to send messages to a chatbot via a REST API.

## Setup

1. Start milvus server
   ```
   ./standalone_embed.bat start
   ```

2. Install dependencies:
   ```
   python -m pip install -r requirements.txt
   ```

3. Run the chatbot server:
   ```
   python server.py
   ```

4. In a new terminal, run the Streamlit app:
   ```
   python -m streamlit run app.py
   ```

5. Open the Streamlit app in your browser (usually at http://localhost:8501).

## Usage

- Enter a message in the text input.
- Click "Send" to send the message to the chatbot.
- The chatbot's response will be displayed below.
