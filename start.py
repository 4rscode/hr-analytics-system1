import os
import sys
import subprocess
import webbrowser
import time
import logging
from pathlib import Path
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_dependencies():
    """Проверяем наличие всех необходимых зависимостей"""
    try:
        import flask
        import openai
        return True
    except ImportError as e:
        logger.error(f"Отсутствует зависимость: {e}")
        return False

def setup_environment():
    """Настраиваем окружение"""
    try:
        # Устанавливаем переменные окружения
        os.environ['FLASK_APP'] = 'src/main.py'
        os.environ['FLASK_ENV'] = 'development'
        
        # Проверяем наличие static директории и файлов
        static_dir = os.path.join(os.path.dirname(__file__), 'static')
        os.makedirs(static_dir, exist_ok=True)
        
        # Проверяем наличие всех необходимых статических файлов
        required_files = ['index.html', 'style.css', 'script.js']
        for file in required_files:
            file_path = os.path.join(static_dir, file)
            if not os.path.exists(file_path):
                logger.error(f"Missing required file: {file}")
                return False
                
        return True

    except Exception as e:
        logger.error(f"Error setting up environment: {e}")
        return False

def start_server():
    """Запускаем сервер"""
    try:
        if not check_dependencies():
            logger.error("Установите зависимости: pip install -r requirements.txt")
            return

        if not setup_environment():
            return

        logger.info("Запуск сервера...")
        
        # Запускаем Flask на порту 5000
        server = subprocess.Popen([
            sys.executable,
            "-m", "flask",
            "run",
            "--host=0.0.0.0",
            "--port=5000"
        ])

        # Даем серверу время на запуск
        time.sleep(2)

        # Открываем браузер
        webbrowser.open('http://localhost:5000')
        
        logger.info("Сервер запущен на http://localhost:5000")
        logger.info("Нажмите Ctrl+C для завершения")

        # Ждем завершения процесса
        server.wait()

    except KeyboardInterrupt:
        logger.info("Завершение работы сервера...")
    except Exception as e:
        logger.error(f"Ошибка при запуске сервера: {e}")
        sys.exit(1)

if __name__ == "__main__":
    start_server()
