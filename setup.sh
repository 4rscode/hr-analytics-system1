#!/bin/bash

echo "Installing HR Analytics System..."

# Проверка Python
if ! command -v python3 &> /dev/null; then
    echo "Python не установлен!"
    exit 1
fi

# Проверка Node.js и npm
if ! command -v node &> /dev/null; then
    echo "Node.js не установлен!"
    exit 1
fi

# Проверка MySQL
if ! command -v mysql &> /dev/null; then
    echo "MySQL не установлен!"
    exit 1
fi

echo "Установка Python зависимостей..."
pip3 install --upgrade pip setuptools wheel
pip3 install -r requirements.txt

echo "Установка Node.js зависимостей..."
cd frontend
npm install
cd ..

echo "Настройка базы данных..."
mysql -u root -p < scripts/init_db.sql

echo "Установка завершена!"
echo "Для запуска системы выполните: python3 run.py"
