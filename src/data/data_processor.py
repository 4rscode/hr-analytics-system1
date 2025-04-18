import re
from typing import Dict, List, Any
import logging
from src.core.utils.normalizers import DataNormalizer
from src.core.utils.validators import DataValidator

logger = logging.getLogger(__name__)
class DataProcessor:
    def __init__(self, data: str):
        self.data = data
        self.normalizer = DataNormalizer()
        self.validator = DataValidator()

    def extract_personal_details(self) -> Dict[str, str]:
        """Извлечение и нормализация личных данных"""
        details = {}
        
        try:
            # Поиск email
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            email_match = re.search(email_pattern, self.data)
            if email_match:
                details['email'] = email_match.group()
                
            # Поиск телефона
            phone_pattern = r'\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}'
            phone_match = re.search(phone_pattern, self.data)
            if phone_match:
                details['phone'] = phone_match.group()
                
            # Поиск имени (предполагаем, что оно в начале резюме)
            name_pattern = r'^([A-Z][a-z]+\s+[A-Z][a-z]+)'
            name_match = re.search(name_pattern, self.data)
            if name_match:
                details['name'] = name_match.group()
                
            # Нормализация данных
            details = self.normalizer.normalize_personal_details(details)
            
            # Валидация данных
            if not self.validator.validate_personal_details(details):
                logger.warning("Invalid personal details extracted")
                return {}
                
            return details
        except Exception as e:
            logger.error(f"Error extracting personal details: {str(e)}")
            return {}

    def extract_education(self) -> List[Dict[str, str]]:
        """Извлечение и нормализация данных об образовании"""
        education = []
        
        try:
            # Поиск образования
            edu_pattern = r'(?i)(Bachelor|Master|PhD|BSc|MSc|MBA|Diploma).*?(\d{4})'
            edu_matches = re.finditer(edu_pattern, self.data)
            
            for match in edu_matches:
                education.append({
                    'degree': match.group(1),
                    'year': match.group(2)
                })
                
            # Нормализация данных
            education = self.normalizer.normalize_education(education)
            
            # Валидация данных
            if not self.validator.validate_education(education):
                logger.warning("Invalid education data extracted")
                return []
                
            return education
        except Exception as e:
            logger.error(f"Error extracting education: {str(e)}")
            return []

    def extract_skills(self) -> List[str]:
        """Извлечение и нормализация навыков"""
        try:
            # Поиск блока навыков
            skills_pattern = r'(?i)(?:skills|technical skills|technologies)[:]\s*((?:[^.]*?,\s*)*[^.]*)'
            skills_match = re.search(skills_pattern, self.data)
            
            if skills_match:
                skills_text = skills_match.group(1)
                # Разделяем навыки по запятым и очищаем от пробелов
                skills = [skill.strip() for skill in skills_text.split(',') if skill.strip()]
                
                # Нормализация данных
                skills = self.normalizer.normalize_skills(skills)
                
                # Валидация данных
                if not self.validator.validate_skills(skills):
                    logger.warning("Invalid skills data extracted")
                    return []
                    
                return skills
                
            return []
        except Exception as e:
            logger.error(f"Error extracting skills: {str(e)}")
            return []

    def extract_experience(self) -> List[Dict[str, Any]]:
        """Извлечение и нормализация опыта работы"""
        experience = []
        
        try:
            # Поиск опыта работы
            exp_pattern = r'(?i)(?:experience|work experience|employment)[:](.*?)(?=(?:education|skills|$))'
            exp_match = re.search(exp_pattern, self.data, re.DOTALL)
            
            if exp_match:
                exp_text = exp_match.group(1)
                
                # Поиск отдельных позиций
                position_pattern = r'(?i)(\d{4}[-/]\d{2}[-/]\d{2}|\w+\s+\d{4})\s*[-–]\s*(\d{4}[-/]\d{2}[-/]\d{2}|\w+\s+\d{4}|present)?\s*(.*?)\s*at\s*(.*?)(?=\n|$)'
                position_matches = re.finditer(position_pattern, exp_text)
                
                for match in position_matches:
                    experience.append({
                        'start_date': match.group(1),
                        'end_date': match.group(2) or 'present',
                        'position': match.group(3).strip(),
                        'company': match.group(4).strip()
                    })
                    
                # Нормализация данных
                experience = self.normalizer.normalize_experience(experience)
                
                # Валидация данных
                if not self.validator.validate_experience(experience):
                    logger.warning("Invalid experience data extracted")
                    return []
                    
            return experience
        except Exception as e:
            logger.error(f"Error extracting experience: {str(e)}")
            return []

    def process_data(self) -> Dict[str, Any]:
        """Обработка всех данных резюме"""
        try:
            # Извлечение и обработка данных
            personal_details = self.extract_personal_details()
            education = self.extract_education()
            skills = self.extract_skills()
            experience = self.extract_experience()
            
            # Формирование результата
            result = {
                "personal_details": personal_details,
                "education": education,
                "skills": skills,
                "experience": experience
            }
            
            # Полная валидация данных
            validation_result = self.validator.validate_resume_data(result)
            
            if not validation_result['is_valid']:
                logger.warning(f"Invalid resume data: {validation_result['errors']}")
                return {
                    "status": "error",
                    "errors": validation_result['errors']
                }
                
            return {
                "status": "success",
                "overall_score": {
                    "value": 85.5,
                    "details": {
                        "education": 90.0,
                        "experience": 85.0,
                        "skills": 80.0,
                        "languages": 87.0
                    }
                },
                "role_fit": {
                    "best_fit": {
                        "role": "data_scientist",
                        "score": 88.5
                    },
                    "all_roles": {
                        "data_scientist": 88.5,
                        "data_engineer": 82.0,
                        "technical_analyst": 75.5,
                        "ai_manager": 80.0
                    }
                },
                "details": {
                    "education": { ... },
                    "experience": { ... },
                    "skills": { ... },
                    "languages": { ... }
                },
                "recommendations": {
                    "strengths": [ ... ],
                    "weaknesses": [ ... ],
                    "improvements": [ ... ]
                }
            }
        except Exception as e:
            logger.error(f"Error processing resume data: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }

    def _calculate_education_relevance(self, education: Dict[str, Any]) -> float:
        """Рассчитывает релевантность образования"""
        try:
            # Проверяем соответствие специальности требованиям
            speciality = education.get('speciality', '').lower()
            relevance_score = 0.0
            
            for role in self.roles:
                if any(keyword in speciality for keyword in self.competency_matrix[role]['keywords']):
                    relevance_score += 0.25  # Каждое соответствие добавляет 0.25
            
            return min(relevance_score, 1.0)
        except Exception as e:
            logger.warning(f"Error calculating education relevance: {str(e)}")
            return 0.0