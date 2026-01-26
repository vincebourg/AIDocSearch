import os
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from bot_service import ask_bot, initialize_services, bot_health_check, upload_document

app = Flask(__name__)

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'html', 'csv'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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


@app.route('/upload', methods=['POST'])
def upload():
    """
    Upload and index a document.

    Expects multipart/form-data with 'file' field.
    Returns JSON: {"success": bool, "message": str, "chunks_indexed": int}
    """
    try:
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({"success": False, "message": "No file provided"}), 400

        file = request.files['file']

        # Check if filename is empty
        if file.filename == '':
            return jsonify({"success": False, "message": "No file selected"}), 400

        # Check if file type is allowed
        if not allowed_file(file.filename):
            return jsonify({
                "success": False,
                "message": f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
            }), 400

        # Save file
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Get file extension
        file_type = filename.rsplit('.', 1)[1].lower()

        # Index document
        result = upload_document(file_path, file_type)

        # Clean up uploaded file after indexing
        if os.path.exists(file_path):
            os.remove(file_path)

        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 500

    except Exception as e:
        print(f"Error in upload endpoint: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


if __name__ == '__main__':
    try:
        initialize_services()
        print("Server initialization complete. Starting Flask app...")
        app.run(debug=True)
    except Exception as e:
        print(f"Failed to initialize server: {e}")
        raise