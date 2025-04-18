USE hr_analytics;

-- Создаем основную таблицу
CREATE TABLE IF NOT EXISTS resumes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    filename VARCHAR(255),
    content TEXT,
    extracted_info JSON,
    analysis_results JSON,
    university VARCHAR(255),
    speciality VARCHAR(255),
    graduation_year VARCHAR(50),
    education_score INT,
    upload_date DATETIME DEFAULT CURRENT_TIMESTAMP
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
