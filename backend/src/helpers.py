import os
from datetime import datetime
from werkzeug.utils import secure_filename
from config import Config

def is_allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def generate_new_filename(filename):
    base, ext = os.path.splitext(filename)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{base}_{timestamp}{ext}"

def save_file(file, upload_folder, prefix="temp_"):
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    filename = secure_filename(file.filename)
    temp_path = os.path.join(upload_folder, prefix + filename)
    file.save(temp_path)
    return temp_path

def file_already_exists(file_path):
    return os.path.exists(file_path)

def parse_resume(file_path, format, output_folder):
    from resume_parser import ResumeParser  # Import here to avoid circular import issues
    parser = ResumeParser(Config.OPENAI_API_KEY)
    response = parser.query_resume(file_path, format)
    return response
