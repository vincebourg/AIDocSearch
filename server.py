from flask import Flask, request, jsonify
from bot_service import ask_bot, initialize_services, bot_health_check

app = Flask(__name__)


@app.route('/chat', methods=['POST'])
def chat():
    """
    Chat endpoint with RAG (Retrieval Augmented Generation).

    Expects JSON: {"message": "user question"}
    Returns JSON: {"response": "assistant answer"}
    """
    try:
        data = request.get_json()
        message = data.get('message', '')

        if not message:
            return jsonify({"error": "No message provided"}), 400

        response = ask_bot(message)

        return jsonify({"response": response})

    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify(bot_health_check())


if __name__ == '__main__':
    try:
        initialize_services()
        print("Server initialization complete. Starting Flask app...")
        app.run(debug=True)
    except Exception as e:
        print(f"Failed to initialize server: {e}")
        raise