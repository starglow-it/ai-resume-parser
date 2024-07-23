import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from helpers import is_allowed_file, save_file, file_already_exists, parse_resume, generate_new_filename
from config import Config

app = Flask(__name__)
CORS(app)

app.config.from_object(Config)

@app.route('/parse-resume', methods=['POST'])
def parse_resume_endpoint():
    if 'file' not in request.files:
        return jsonify(error="No file part"), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify(error="No selected file"), 400
    
    if not is_allowed_file(file.filename):
        return jsonify(error="File type not allowed"), 400
    
    try:
        temp_file_path = save_file(file, app.config['UPLOAD_FOLDER'], "temp_")

        # Check if file already exists and rename if needed
        final_file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
        if file_already_exists(final_file_path):
            new_filename = generate_new_filename(file.filename)
            final_file_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
            os.rename(temp_file_path, final_file_path)
        else:
            os.rename(temp_file_path, final_file_path)

        format = request.form.get('format', app.config['DEFAULT_FORMAT'])
        output_folder = request.form.get('output_folder', app.config['OUTPUT_FOLDER'])
        response = parse_resume(final_file_path, format, output_folder)
        
        return jsonify(message=response), 200
    except Exception as e:
        return jsonify(error=str(e)), 500

if __name__ == '__main__':
    app.run(debug=True)
