import os
import subprocess
import sys
import webbrowser
from time import sleep

def run_system():
    # Проверяем наличие Node.js и Python
    if not all([check_requirements()]):
        sys.exit(1)

    # Инициализируем базу данных
    print("Инициализация базы данных...")
    init_database()

    # Запускаем backend
    print("Запуск backend сервера...")
    backend_process = subprocess.Popen([sys.executable, "src/main.py"])

    # Запускаем frontend
    print("Запуск frontend сервера...")
    os.chdir("frontend")
    frontend_process = subprocess.Popen(["npm", "start"])

    # Даем время на запуск серверов
    print("Подождите, система запускается...")
    sleep(5)

    # Открываем браузер
    webbrowser.open("http://localhost:3000")

    try:
        # Ожидаем прерывания от пользователя
        backend_process.wait()
    except KeyboardInterrupt:
        print("\nЗавершение работы системы...")
        backend_process.terminate()
        frontend_process.terminate()

def check_requirements():
    try:
        # Проверка Node.js
        subprocess.run(["node", "--version"], capture_output=True)
        # Проверка MySQL
        subprocess.run(["mysql", "--version"], capture_output=True)
        return True
    except FileNotFoundError:
        print("Ошибка: Убедитесь, что установлены Node.js и MySQL")
        return False

def init_database():
    try:
        # Запуск SQL скрипта
        subprocess.run([
            "mysql",
            "-u", "root",
            "-p",
            "<", "scripts/init_db.sql"
        ], shell=True)
    except Exception as e:
        print(f"Ошибка при инициализации базы данных: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_system()
