# Chatbot Streamlit App

This is a simple Streamlit application that allows users to send messages to a chatbot via a REST API.

## Setup

1. Get last milvus docker image
   ```
   docker pull milvusdb/milvus:latest
   ```
2. Start milvus server
   ```
   docker run -d --name milvus-standalone -p 19530:19530 -p 19121:19121 milvusdb/milvus:latest
   ```
3. Install dependencies:
   ```
   python -m pip install -r requirements.txt
   ```

4. Run the chatbot server:
   ```
   python server.py
   ```

5. In a new terminal, run the Streamlit app:
   ```
   python -m streamlit run app.py
   ```

6. Open the Streamlit app in your browser (usually at http://localhost:8501).

## Usage

- Enter a message in the text input.
- Click "Send" to send the message to the chatbot.
- The chatbot's response will be displayed below.

## Notes

- The chatbot server runs on http://localhost:5000.
- The current chatbot implementation simply echoes the message. Replace the logic in `server.py` with your actual chatbot API.