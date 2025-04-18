@echo off
echo Installing dependencies...

REM Устанавливаем Python зависимости
pip install -r requirements.txt

REM Устанавливаем и собираем frontend
cd frontend
npm install
npm run build
cd ..

echo Setup completed!
echo To start the system, run: npm start
pause
