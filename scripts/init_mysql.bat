@echo off
echo Initializing MySQL root access...

REM Создаем временный файл с командами SQL
(
echo SET PASSWORD FOR 'root'@'localhost' = PASSWORD('12345678');
echo FLUSH PRIVILEGES;
) > temp.sql

REM Пытаемся выполнить команды без пароля
mysql -u root < temp.sql

REM Удаляем временный файл
del temp.sql

echo MySQL root access initialized.
echo Please restart the application: python start.py
pause
