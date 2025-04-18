from typing import Dict, List, Any, Optional
import logging
from datetime import datetime
import re

class InputValidator:
    """Класс для валидации входных данных"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Регулярные выражения для валидации
        self.patterns = {
            'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            'phone': r'^\+?[1-9]\d{10,14}$',
            'date': r'^\d{4}-\d{2}-\d{2}$',
            'years': r'^\d+(\.\d{1,2})?$'
        }
        
        # Допустимые значения для различных полей
        self.allowed_values = {
            'degree': ['phd', 'master', 'bachelor', 'specialist', 'incomplete_higher'],
            'language_level': ['native', 'fluent', 'advanced', 'intermediate', 'basic'],
            'skill_level': ['expert', 'advanced', 'intermediate', 'basic'],
            'position_level': ['manager', 'lead', 'senior', 'middle', 'junior']
        }

    def validate_candidate_data(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        """Валидация данных кандидата"""
        errors = {
            'education': [],
            'experience': [],
            'skills': [],
            'languages': [],
            'general': []
        }
        
        try:
            # Валидация образования
            if 'education' in data:
                for edu in data['education']:
                    if not edu.get('institution'):
                        self.logger.warning(f"Missing institution in education entry: {edu}")
                    if not edu.get('degree'):
                        self.logger.warning(f"Missing degree in education entry: {edu}")
                        
            # Валидация опыта
            if 'experience' in data:
                for exp in data['experience']:
                    if not exp.get('position'):
                        self.logger.warning(f"Missing position in experience entry: {exp}")
                    if not exp.get('company'):
                        self.logger.warning(f"Missing company in experience entry: {exp}")
                        
            # Валидация навыков
            if 'skills' in data:
                if not data['skills'].get('required'):
                    self.logger.warning("No required skills found")
                    
            # Валидация языков
            if 'languages' in data:
                for lang in data['languages']:
                    if not lang.get('language'):
                        self.logger.warning(f"Missing language name in entry: {lang}")
                    if not lang.get('level'):
                        self.logger.warning(f"Missing language level in entry: {lang}")
                        
            # Если есть только предупреждения, возвращаем пустой словарь ошибок
            return {}
            
        except Exception as e:
            self.logger.error(f"Error during validation: {str(e)}")
            return {}

    def _validate_education(self, education_data: List[Dict[str, Any]]) -> List[str]:
        """Валидация данных об образовании"""
        errors = []
        
        for edu in education_data:
            try:
                # Проверка обязательных полей
                if not edu.get('degree'):
                    errors.append('Missing degree')
                if not edu.get('institution'):
                    errors.append('Missing institution')
                    
                # Валидация степени
                if edu.get('degree') and edu['degree'].lower() not in self.allowed_values['degree']:
                    errors.append(f"Invalid degree: {edu['degree']}")
                    
                # Валидация дат
                if edu.get('start_date'):
                    if not self._validate_date(edu['start_date']):
                        errors.append(f"Invalid start date: {edu['start_date']}")
                if edu.get('end_date'):
                    if not self._validate_date(edu['end_date']):
                        errors.append(f"Invalid end date: {edu['end_date']}")
                        
                # Проверка логики дат
                if edu.get('start_date') and edu.get('end_date'):
                    if not self._validate_date_range(edu['start_date'], edu['end_date']):
                        errors.append('End date is before start date')
                        
            except Exception as e:
                errors.append(f"Error validating education entry: {str(e)}")
                
        return errors

    def _validate_experience(self, experience_data: List[Dict[str, Any]]) -> List[str]:
        """Валидация данных об опыте работы"""
        errors = []
        
        for exp in experience_data:
            try:
                # Проверка обязательных полей
                if not exp.get('position'):
                    errors.append('Missing position')
                if not exp.get('company'):
                    errors.append('Missing company')
                    
                # Валидация лет опыта
                if exp.get('years'):
                    if not self._validate_years(exp['years']):
                        errors.append(f"Invalid years of experience: {exp['years']}")
                        
                # Валидация уровня позиции
                if exp.get('position_level'):
                    if exp['position_level'].lower() not in self.allowed_values['position_level']:
                        errors.append(f"Invalid position level: {exp['position_level']}")
                        
                # Валидация дат
                if exp.get('start_date'):
                    if not self._validate_date(exp['start_date']):
                        errors.append(f"Invalid start date: {exp['start_date']}")
                if exp.get('end_date'):
                    if not self._validate_date(exp['end_date']):
                        errors.append(f"Invalid end date: {exp['end_date']}")
                        
                # Проверка логики дат
                if exp.get('start_date') and exp.get('end_date'):
                    if not self._validate_date_range(exp['start_date'], exp['end_date']):
                        errors.append('End date is before start date')
                        
            except Exception as e:
                errors.append(f"Error validating experience entry: {str(e)}")
                
        return errors

    def _validate_skills(self, skills_data: Dict[str, List[Dict[str, Any]]]) -> List[str]:
        """Валидация данных о навыках"""
        errors = []
        
        try:
            # Валидация обязательных навыков
            if 'required' in skills_data:
                for skill in skills_data['required']:
                    if not skill.get('name'):
                        errors.append('Missing skill name in required skills')
                    if skill.get('level') and skill['level'].lower() not in self.allowed_values['skill_level']:
                        errors.append(f"Invalid skill level: {skill['level']}")
                        
            # Валидация дополнительных навыков
            if 'additional' in skills_data:
                for skill in skills_data['additional']:
                    if not skill.get('name'):
                        errors.append('Missing skill name in additional skills')
                    if skill.get('level') and skill['level'].lower() not in self.allowed_values['skill_level']:
                        errors.append(f"Invalid skill level: {skill['level']}")
                        
            # Валидация сертификатов
            if 'certifications' in skills_data:
                for cert in skills_data['certifications']:
                    if not cert.get('name'):
                        errors.append('Missing certification name')
                    if cert.get('date') and not self._validate_date(cert['date']):
                        errors.append(f"Invalid certification date: {cert['date']}")
                        
        except Exception as e:
            errors.append(f"Error validating skills: {str(e)}")
            
        return errors

    def _validate_languages(self, languages_data: List[Dict[str, Any]]) -> List[str]:
        """Валидация данных о языках"""
        errors = []
        
        for lang in languages_data:
            try:
                if not lang.get('language'):
                    errors.append('Missing language name')
                if not lang.get('level'):
                    errors.append('Missing language level')
                elif lang['level'].lower() not in self.allowed_values['language_level']:
                    errors.append(f"Invalid language level: {lang['level']}")
                    
            except Exception as e:
                errors.append(f"Error validating language entry: {str(e)}")
                
        return errors

    def _validate_date(self, date_str: str) -> bool:
        """Валидация даты"""
        try:
            if not re.match(self.patterns['date'], date_str):
                return False
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False

    def _validate_date_range(self, start_date: str, end_date: str) -> bool:
        """Проверка логики дат (конечная дата должна быть после начальной)"""
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            return end >= start
        except ValueError:
            return False

    def _validate_years(self, years: str) -> bool:
        """Валидация количества лет"""
        try:
            if not re.match(self.patterns['years'], str(years)):
                return False
            years_float = float(years)
            return 0 <= years_float <= 50
        except ValueError:
            return False

    def _log_validation_results(self, errors: Dict[str, List[str]]) -> None:
        """Логирование результатов валидации"""
        total_errors = sum(len(err_list) for err_list in errors.values())
        
        if total_errors == 0:
            self.logger.info("Input validation passed successfully")
        else:
            self.logger.warning(f"Input validation found {total_errors} errors:")
            for category, err_list in errors.items():
                if err_list:
                    self.logger.warning(f"{category}: {', '.join(err_list)}") 