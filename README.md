# Chatbot Streamlit App

This is a simple Streamlit application that allows users to send messages to a chatbot via a REST API.

## Prerequisites

1. **Python 3.8+** installed
2. **OpenAI API key** with access to embeddings and chat models

## Setup

1. Start milvus server
   on windows:
   ```
   ./standalone_embed.bat start
   ```
   OR
   on other shells:
   ```
   ./standalone_embed.sh start
   ```
2. Install dependencies:
   ```
   python -m pip install -r requirements.txt
   ```

3. Environment variables
   
   Duplicate .env.sample into .env and add your OpenAI API Key.

5. Run the chatbot server:
   ```
   python server.py
   ```

6. In a new terminal, run the Streamlit app:
   ```
   python -m streamlit run app.py
   ```

7. Open the Streamlit app in your browser (usually at http://localhost:8501).

## Usage

- Enter a message in the text input.
- Click "Send" to send the message to the chatbot.
- The chatbot's response will be displayed below.
