import re
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DataValidator:
    @staticmethod
    def validate_email(email: str) -> bool:
        """Проверка корректности email"""
        if not email:
            return False
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Проверка корректности телефона"""
        if not phone:
            return False
        # Удаляем все нецифровые символы
        digits = re.sub(r'\D', '', phone)
        return len(digits) >= 10

    @staticmethod
    def validate_date(date_str: str) -> bool:
        """Проверка корректности даты"""
        if not date_str:
            return False
        try:
            # Проверка формата YYYY-MM
            if re.match(r'^\d{4}-\d{2}$', date_str):
                year, month = map(int, date_str.split('-'))
                if 1 <= month <= 12 and year >= 1900:
                    return True
            return False
        except Exception:
            return False

    @staticmethod
    def validate_education(education: List[Dict[str, str]]) -> bool:
        """Проверка корректности данных об образовании"""
        if not education:
            return False
            
        required_fields = {'degree', 'university', 'year'}
        valid_degrees = {'Bachelor', 'Master', 'PhD', 'BSc', 'MSc', 'MBA', 'Diploma'}
        
        for edu in education:
            # Проверка наличия обязательных полей
            if not all(field in edu for field in required_fields):
                return False
                
            # Проверка корректности степени
            if edu.get('degree') not in valid_degrees:
                return False
                
            # Проверка корректности даты
            if not DataValidator.validate_date(edu.get('year', '')):
                return False
                
        return True

    @staticmethod
    def validate_experience(experience: List[Dict[str, Any]]) -> bool:
        """Проверка корректности опыта работы"""
        if not experience:
            return False
            
        required_fields = {'company', 'position', 'start_date'}
        
        for exp in experience:
            # Проверка наличия обязательных полей
            if not all(field in exp for field in required_fields):
                return False
                
            # Проверка корректности дат
            if not DataValidator.validate_date(exp.get('start_date', '')):
                return False
                
            end_date = exp.get('end_date')
            if end_date and not DataValidator.validate_date(end_date):
                return False
                
            # Проверка логики дат
            if end_date and exp['start_date'] > end_date:
                return False
                
        return True

    @staticmethod
    def validate_skills(skills: List[str]) -> bool:
        """Проверка корректности навыков"""
        if not skills:
            return False
            
        # Проверка, что все навыки не пустые и не слишком длинные
        return all(skill and len(skill) <= 100 for skill in skills)

    @staticmethod
    def validate_personal_details(details: Dict[str, str]) -> bool:
        """Проверка корректности личных данных"""
        if not details:
            return False
            
        # Проверка имени
        if 'name' in details:
            name = details['name']
            if not name or len(name.split()) < 2:
                return False
                
        # Проверка email
        if 'email' in details and not DataValidator.validate_email(details['email']):
            return False
            
        # Проверка телефона
        if 'phone' in details and not DataValidator.validate_phone(details['phone']):
            return False
            
        return True

    @staticmethod
    def validate_resume_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Полная валидация данных резюме
        Возвращает словарь с результатами валидации
        """
        validation_results = {
            'is_valid': True,
            'errors': []
        }
        
        try:
            # Валидация личных данных
            if not DataValidator.validate_personal_details(data.get('personal_details', {})):
                validation_results['is_valid'] = False
                validation_results['errors'].append('Invalid personal details')
                
            # Валидация образования
            if not DataValidator.validate_education(data.get('education', [])):
                validation_results['is_valid'] = False
                validation_results['errors'].append('Invalid education data')
                
            # Валидация опыта
            if not DataValidator.validate_experience(data.get('experience', [])):
                validation_results['is_valid'] = False
                validation_results['errors'].append('Invalid experience data')
                
            # Валидация навыков
            if not DataValidator.validate_skills(data.get('skills', [])):
                validation_results['is_valid'] = False
                validation_results['errors'].append('Invalid skills data')
                
            return validation_results
        except Exception as e:
            logger.error(f"Error validating resume data: {str(e)}")
            return {
                'is_valid': False,
                'errors': [f'Validation error: {str(e)}']
            } 