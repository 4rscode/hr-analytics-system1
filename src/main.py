from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from analysis.resume_parser import ResumeParser
from analysis.competency_analyzer import CompetencyAnalyzer
from analysis.file_parser import FileParser
from analysis.input_validator import InputValidator
from data.database import Database
import os
import logging
from dotenv import load_dotenv
import tempfile
from werkzeug.utils import secure_filename
from datetime import datetime
import json
import time
from tempfile import gettempprefix

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Загрузка переменных окружения
load_dotenv()

# Обновляем путь к статическим файлам
app = Flask(__name__, 
    static_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static')),
    static_url_path='/static')

CORS(app)

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

# Инициализация компонентов
try:
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY не найден в переменных окружения")
    
    parser = ResumeParser(api_key=api_key)
    analyzer = CompetencyAnalyzer()
    file_parser = FileParser(api_key=api_key)
    input_validator = InputValidator()
    db = Database('config.yaml')
    logger.info("Все компоненты успешно инициализированы")
except Exception as e:
    logger.error(f"Ошибка при инициализации компонентов: {e}")
    raise

ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc'}

def allowed_file(filename):
    """Проверяет допустимость расширения файла"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def read_file_content(file) -> str:
    """Читает содержимое файла с автоопределением кодировки"""
    encodings = ['utf-8', 'windows-1251', 'cp866', 'koi8-r']
    content = file.read()
    
    # Пробуем разные кодировки
    for encoding in encodings:
        try:
            return content.decode(encoding)
        except UnicodeDecodeError:
            continue
            
    # Если не удалось определить кодировку, используем latin1
    return content.decode('latin1')

def save_temp_file(file) -> str:
    """Сохраняет файл во временную директорию"""
    # Получаем оригинальное имя файла
    filename = secure_filename(file.filename)
    logger.info(f"Original filename: {filename}")
    
    # Если расширение отсутствует, добавляем .pdf
    if '.' not in filename:
        filename += '.pdf'
        logger.info(f"Added default extension, new filename: {filename}")
    
    # Получаем расширение файла
    file_ext = os.path.splitext(filename)[1]
    logger.info(f"File extension: {file_ext}")
    
    # Создаем временное имя файла
    temp_filename = f"resume_{datetime.now().strftime('%Y%m%d_%H%M%S')}{file_ext}"
    temp_path = os.path.join(os.environ.get('TEMP', '/tmp'), temp_filename)
    
    # Сохраняем файл
    file.save(temp_path)
    logger.info(f"File saved to {temp_path}")
    
    return temp_path

@app.route('/api/upload', methods=['POST'])
def upload_resume():
    """Обрабатывает загрузку резюме"""
    try:
        # Проверяем наличие файла в запросе
        if 'resume' not in request.files:
            return jsonify({'error': 'No file part'}), 400
            
        file = request.files['resume']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
            
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type'}), 400
            
        # Сохраняем файл
        temp_path = save_temp_file(file)
        
        try:
            # Извлекаем информацию из файла
            parsed_data = file_parser.parse_file(temp_path)
            if not parsed_data:
                return jsonify({'error': 'Failed to parse resume'}), 400
                
            # Анализируем данные
            analysis_result = analyzer.analyze_candidate(parsed_data)
            
            # Сохраняем результаты в базу данных
            logger.info(f"Saving analysis for file: {os.path.basename(temp_path)}")
            db.save_analysis(
                extracted_info=parsed_data,
                analysis_result=analysis_result
            )
            
            # Возвращаем результат
            logger.info(f"Analysis result: {analysis_result}")
            return jsonify(analysis_result)
            
        finally:
            # Удаляем временный файл
            try:
                os.remove(temp_path)
                logger.info(f"Successfully deleted temporary file: {temp_path}")
            except Exception as e:
                logger.error(f"Error deleting temporary file: {str(e)}")
                
    except Exception as e:
        logger.error(f"Error processing upload: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    """Возвращает историю анализов"""
    try:
        history = db.get_history()
        return jsonify(history)
    except Exception as e:
        logger.error(f"Error getting history: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/')
def serve_frontend():
    """Отдаем главную страницу"""
    try:
        return send_from_directory(app.static_folder, 'index.html')
    except Exception as e:
        logger.error(f"Error serving frontend: {e}")
        return f"Error loading page: {str(e)}", 500

# Обновляем обработчик статических файлов
@app.route('/static/<path:path>')
def serve_static(path):
    """Отдаем статические файлы"""
    return send_from_directory(app.static_folder, path)

if __name__ == '__main__':
    try:
        logger.info("Запуск сервера...")
        app.run(host='0.0.0.0', port=5000, debug=True)
    except Exception as e:
        logger.error(f"Ошибка при запуске сервера: {e}")