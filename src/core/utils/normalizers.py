import re
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DataNormalizer:
    @staticmethod
    def normalize_text(text: str) -> str:
        """
        Нормализация текста:
        - Удаление лишних пробелов
        - Приведение к нижнему регистру
        - Удаление специальных символов
        """
        if not text:
            return ""
            
        # Удаление лишних пробелов
        text = re.sub(r'\s+', ' ', text)
        
        # Удаление специальных символов, кроме букв, цифр и основных знаков препинания
        text = re.sub(r'[^\w\s.,;:!?-]', '', text)
        
        return text.strip()

    @staticmethod
    def normalize_date(date_str: str) -> Optional[str]:
        """
        Нормализация даты в формат YYYY-MM
        Поддерживаемые форматы:
        - YYYY
        - MM/YYYY
        - MM-YYYY
        - Month YYYY
        """
        if not date_str:
            return None
            
        try:
            # Обработка года
            if re.match(r'^\d{4}$', date_str):
                return f"{date_str}-01"
                
            # Обработка MM/YYYY или MM-YYYY
            if re.match(r'^\d{1,2}[/-]\d{4}$', date_str):
                parts = re.split(r'[/-]', date_str)
                month = parts[0].zfill(2)
                year = parts[1]
                return f"{year}-{month}"
                
            # Обработка Month YYYY
            month_map = {
                'january': '01', 'february': '02', 'march': '03', 'april': '04',
                'may': '05', 'june': '06', 'july': '07', 'august': '08',
                'september': '09', 'october': '10', 'november': '11', 'december': '12'
            }
            
            for month_name, month_num in month_map.items():
                if month_name in date_str.lower():
                    year_match = re.search(r'\d{4}', date_str)
                    if year_match:
                        return f"{year_match.group()}-{month_num}"
                        
            return None
        except Exception as e:
            logger.error(f"Error normalizing date {date_str}: {str(e)}")
            return None

    @staticmethod
    def normalize_education(education: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Нормализация данных об образовании:
        - Стандартизация степеней
        - Нормализация дат
        - Очистка названий университетов
        """
        normalized = []
        degree_map = {
            'bachelor': 'Bachelor',
            'master': 'Master',
            'phd': 'PhD',
            'doctor': 'PhD',
            'bsc': 'BSc',
            'msc': 'MSc',
            'mba': 'MBA',
            'diploma': 'Diploma'
        }
        
        for edu in education:
            try:
                normalized_edu = {}
                
                # Нормализация степени
                degree = edu.get('degree', '').lower()
                for key, value in degree_map.items():
                    if key in degree:
                        normalized_edu['degree'] = value
                        break
                else:
                    normalized_edu['degree'] = edu.get('degree', '')
                
                # Нормализация года
                year = edu.get('year', '')
                normalized_edu['year'] = DataNormalizer.normalize_date(year)
                
                # Нормализация университета
                university = edu.get('university', '')
                normalized_edu['university'] = DataNormalizer.normalize_text(university)
                
                # Нормализация специальности
                speciality = edu.get('speciality', '')
                normalized_edu['speciality'] = DataNormalizer.normalize_text(speciality)
                
                normalized.append(normalized_edu)
            except Exception as e:
                logger.error(f"Error normalizing education entry: {str(e)}")
                continue
                
        return normalized

    @staticmethod
    def normalize_skills(skills: List[str]) -> List[str]:
        """
        Нормализация навыков:
        - Удаление дубликатов
        - Стандартизация названий
        - Сортировка
        """
        if not skills:
            return []
            
        try:
            # Нормализация каждого навыка
            normalized = [DataNormalizer.normalize_text(skill) for skill in skills]
            
            # Удаление пустых строк и дубликатов
            normalized = list(set(filter(None, normalized)))
            
            # Сортировка
            normalized.sort()
            
            return normalized
        except Exception as e:
            logger.error(f"Error normalizing skills: {str(e)}")
            return []

    @staticmethod
    def normalize_experience(experience: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Нормализация опыта работы:
        - Нормализация дат
        - Стандартизация должностей
        - Очистка описаний
        """
        normalized = []
        
        for exp in experience:
            try:
                normalized_exp = {}
                
                # Нормализация дат
                start_date = exp.get('start_date', '')
                end_date = exp.get('end_date', '')
                
                normalized_exp['start_date'] = DataNormalizer.normalize_date(start_date)
                normalized_exp['end_date'] = DataNormalizer.normalize_date(end_date)
                
                # Нормализация компании
                company = exp.get('company', '')
                normalized_exp['company'] = DataNormalizer.normalize_text(company)
                
                # Нормализация должности
                position = exp.get('position', '')
                normalized_exp['position'] = DataNormalizer.normalize_text(position)
                
                # Нормализация описания
                description = exp.get('description', '')
                normalized_exp['description'] = DataNormalizer.normalize_text(description)
                
                normalized.append(normalized_exp)
            except Exception as e:
                logger.error(f"Error normalizing experience entry: {str(e)}")
                continue
                
        return normalized

    @staticmethod
    def normalize_personal_details(details: Dict[str, str]) -> Dict[str, str]:
        """
        Нормализация личных данных:
        - Стандартизация формата телефона
        - Проверка email
        - Нормализация имени
        """
        normalized = {}
        
        try:
            # Нормализация имени
            if 'name' in details:
                name = details['name']
                # Удаление лишних пробелов и приведение к правильному регистру
                parts = [part.capitalize() for part in name.split()]
                normalized['name'] = ' '.join(parts)
            
            # Нормализация email
            if 'email' in details:
                email = details['email'].lower().strip()
                if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                    normalized['email'] = email
            
            # Нормализация телефона
            if 'phone' in details:
                phone = details['phone']
                # Удаление всех нецифровых символов
                digits = re.sub(r'\D', '', phone)
                if len(digits) >= 10:
                    normalized['phone'] = f"+{digits}"
            
            return normalized
        except Exception as e:
            logger.error(f"Error normalizing personal details: {str(e)}")
            return {} 