import os

class Config:
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', './uploaded-resumes')
    OUTPUT_FOLDER = os.getenv('OUTPUT_FOLDER', './output')
    ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc'}
    DEFAULT_FORMAT = 'json'
    LOG_FILE = os.getenv('LOG_FILE', './logs/parser.log')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
