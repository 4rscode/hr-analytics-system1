CREATE DATABASE IF NOT EXISTS hr_analytics CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Создаем пользователя для приложения (синтаксис для MySQL 5.5)
GRANT ALL PRIVILEGES ON hr_analytics.* TO 'hr_admin'@'localhost' IDENTIFIED BY '12345678';
FLUSH PRIVILEGES;

USE hr_analytics;

-- Создаем основную таблицу
CREATE TABLE IF NOT EXISTS resumes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    filename VARCHAR(255),
    content TEXT,
    extracted_info TEXT,
    analysis_results TEXT,
    university VARCHAR(255),
    speciality VARCHAR(255),
    graduation_year VARCHAR(50),
    education_score INT,
    upload_date DATETIME DEFAULT CURRENT_TIMESTAMP
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
