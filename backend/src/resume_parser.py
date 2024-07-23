import os
import json
import csv
import logging
from pdfminer.high_level import extract_text
from openai import OpenAI
import docx2txt
from tika import parser
from tokenizer import num_tokens_from_string
from config import Config

class ResumeParser:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)
        self.prompt_questions = (
            "Please convert the text below into a complete JSON object with the following structure: "
            "{Name, Email, Phone, Location, Recent Role/Title, Summary, Skills: [], "
            "Education: [{university, degree, field_of_study, start_date, end_date}], "
            "Experience: [{job_title, company, location, start_date, end_date, job_summary}], "
            "Certifications: [{name, issuing_organization, issue_date, expiration_date, credential_id, credential_url}], "
            "Projects: [{name, description, start_date, end_date, role}], "
            "Publications: [{title, publisher, publication_date, url}], "
            "Languages: [{language, proficiency}], "
            "Volunteer: [{role, organization, cause, start_date, end_date, description}], "
            "Courses: [{name, institution}], "
            "Honors and Awards: [{title, issuer, date, description}], "
            "Work Authorization, Linkedin URL, GitHub URL, Personal Website URL}. "
            "Ensure that the 'Summary' field contains a visible and comprehensive summary."
        )
        self.setup_logging()

    def setup_logging(self):
        """Set up logging for the parser."""
        log_dir = os.path.dirname(Config.LOG_FILE)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        logging.basicConfig(filename=Config.LOG_FILE, level=logging.DEBUG)
        self.logger = logging.getLogger()

    def query_completion(self, prompt: str, engine: str='gpt-3.5-turbo', max_tokens: int=100) -> object:
        """
        Query GPT-3 for a completion.
        :param prompt: GPT-3 completion prompt.
        :param engine: GPT-3 engine to use.
        :param max_tokens: Maximum number of tokens to return.
        """
        self.logger.info(f'Querying GPT-3 with engine {engine}')

        estimated_prompt_tokens = num_tokens_from_string(prompt, engine)
        estimated_answer_tokens = max_tokens - estimated_prompt_tokens
        self.logger.info(f'Tokens: {estimated_prompt_tokens} + {estimated_answer_tokens} = {max_tokens}')

        response = self.client.chat.completions.create(
            messages=[{'role': 'user', 'content': prompt}],
            model=engine
        )
        return response

    def extract_text_from_file(self, file_path: str) -> str:
        """
        Extract text from a file based on its extension.
        :param file_path: Path to the file.
        :return: Extracted text.
        """
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext == '.doc':
            return self.extract_text_from_doc(file_path)
        elif file_ext == '.docx':
            return docx2txt.process(file_path)
        elif file_ext == '.pdf':
            return extract_text(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")

    def extract_text_from_doc(self, file_path: str) -> str:
        """Extract text from a .doc file using Tika."""
        parsed = parser.from_file(file_path)
        return parsed.get('content', '')

    def query_resume(self, file_path: str, format: str='json') -> str:
        """
        Process a resume file and save the parsed data.
        :param file_path: Path to the resume file.
        :param format: Output format ('json' or 'csv').
        :return: Status message.
        """
        file_name = os.path.basename(file_path)
        if self.check_file_exists(file_name):
            return 'That file has already been parsed.'

        extracted_text = self.extract_text_from_file(file_path)
        prompt = self.prompt_questions + '\n' + extracted_text
        response = self.query_completion(prompt)
        response_text = response.choices[0].message.content
        parsed_json = json.loads(response_text)
        parsed_json['File Name'] = file_name

        output_file_path = self.save_parsed_data(parsed_json, format)
        return f"Resume parse result has been successfully saved at {output_file_path}"

    def save_parsed_data(self, parsed_json: dict, format: str) -> str:
        """Save the parsed JSON data in the specified format."""
        if not os.path.exists(Config.OUTPUT_FOLDER):
            os.makedirs(Config.OUTPUT_FOLDER)
        
        if format == 'json':
            file_path = os.path.join(Config.OUTPUT_FOLDER, 'data.json')
            with open(file_path, 'w') as file:
                json.dump(parsed_json, file, indent=4)
        elif format == 'spreadsheet':
            file_path = os.path.join(Config.OUTPUT_FOLDER, 'data.csv')
            self.append_row_to_csv(parsed_json, file_path)
        else:
            raise ValueError(f"Unsupported format: {format}")

        return file_path

    def append_row_to_csv(self, new_data: dict, file_path: str):
        """Append new data to a CSV file."""
        file_exists = os.path.exists(file_path)

        with open(file_path, 'a' if file_exists else 'w', newline='') as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(new_data.keys())
            writer.writerow(new_data.values())

    def check_file_exists(self, file_name: str) -> bool:
        """Check if the file has been previously parsed."""
        file_path = os.path.join(Config.OUTPUT_FOLDER, 'data.csv')
        if not os.path.exists(file_path):
            return False

        try:
            with open(file_path, 'r') as csv_file:
                reader = csv.DictReader(csv_file)
                for row in reader:
                    if row.get('File Name') == file_name:
                        return True
        except Exception as e:
            self.logger.error(f"Error checking file existence: {e}")

        return False
