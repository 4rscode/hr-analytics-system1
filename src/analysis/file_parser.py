import logging
import os
from typing import Dict, Any
import PyPDF2
import docx
from .resume_parser import ResumeParser

logger = logging.getLogger(__name__)

class FileParser:
    def __init__(self, api_key: str = None):
        """
        Initialize FileParser with OpenAI API key
        
        Args:
            api_key (str): OpenAI API key for ResumeParser
        """
        if not api_key:
            api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OpenAI API key is required. Set it in environment variables or pass directly.")
            
        self.parser = ResumeParser(api_key=api_key)

    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """Парсит файл резюме и возвращает структурированные данные"""
        try:
            filename = os.path.basename(file_path)
            extension = os.path.splitext(filename)[1].lower()
            
            logger.info(f"Processing file: {file_path} with extension: {extension}")
            
            if extension == '.pdf':
                text = self._extract_text_from_pdf(file_path)
            elif extension == '.docx':
                text = self._extract_text_from_docx(file_path)
            elif extension == '.doc':
                text = self._extract_text_from_doc(file_path)
            else:
                raise ValueError(f"Unsupported file format: {extension}")
                
            return self.parser.parse_resume(text, filename)
            
        except Exception as e:
            logger.error(f"Error parsing file: {str(e)}")
            return {
                'education': [],
                'experience': [],
                'skills': {
                    'required': [],
                    'additional': [],
                    'certifications': []
                },
                'languages': []
            }

    def _extract_text_from_pdf(self, file_path: str) -> str:
        """Извлекает текст из PDF файла"""
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            logger.info(f"PDF file has {len(pdf_reader.pages)} pages")
            
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
                
        return text.strip()

    def _extract_text_from_docx(self, file_path: str) -> str:
        """Извлекает текст из DOCX файла"""
        doc = docx.Document(file_path)
        text = ""
        
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
            
        return text.strip()

    def _extract_text_from_doc(self, file_path: str) -> str:
        """Извлекает текст из DOC файла"""
        # TODO: Реализовать извлечение текста из DOC файлов
        raise NotImplementedError("Parsing DOC files is not implemented yet") 