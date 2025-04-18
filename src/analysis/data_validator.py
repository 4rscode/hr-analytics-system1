from typing import Dict, List, Any, Optional
import re
from datetime import datetime

class DataValidator:
    def __init__(self):
        self.degree_aliases = {
            'phd': ['phd', 'ph.d', 'доктор наук', 'кандидат наук'],
            'master': ['master', 'master\'s', 'магистр', 'магистратура'],
            'bachelor': ['bachelor', 'бакалавр', 'бакалавриат'],
            'specialist': ['specialist', 'специалист', 'специалитет'],
            'incomplete_higher': ['incomplete', 'неоконченное высшее', 'неполное высшее']
        }
        
        self.language_level_aliases = {
            'native': ['native', 'родной', 'родной язык', 'native speaker'],
            'fluent': ['fluent', 'свободно', 'advanced', 'c1', 'c2'],
            'upper intermediate': ['upper intermediate', 'выше среднего', 'b2'],
            'intermediate': ['intermediate', 'средний', 'b1'],
            'basic': ['basic', 'базовый', 'начальный', 'elementary', 'a1', 'a2']
        }

    def standardize_education(self, education: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Стандартизирует данные об образовании"""
        standardized = []
        for edu in education:
            if not isinstance(edu, dict):
                continue
                
            degree = self._standardize_degree(edu.get('degree', ''))
            if not degree:
                continue
                
            standardized.append({
                'degree': degree,
                'institution': self._clean_institution_name(edu.get('institution', '')),
                'speciality': self._clean_text(edu.get('speciality', '')),
                'years': self._extract_years(edu.get('years', ''))
            })
        return standardized

    def standardize_experience(self, experience: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Стандартизирует данные об опыте работы"""
        standardized = []
        for exp in experience:
            if not isinstance(exp, dict):
                continue
                
            years = self._extract_experience_years(exp.get('years', ''))
            if years <= 0:
                continue
                
            standardized.append({
                'position': self._clean_text(exp.get('position', '')),
                'company': self._clean_text(exp.get('company', '')),
                'years': years,
                'responsibilities': self._clean_responsibilities(exp.get('responsibilities', [])),
                'is_relevant': self._check_relevance(exp),
                'is_management': self._check_management(exp)
            })
        return standardized

    def standardize_skills(self, skills: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """Стандартизирует данные о навыках"""
        if not isinstance(skills, dict):
            return {'required': [], 'additional': [], 'certifications': []}
            
        return {
            'required': self._clean_skill_list(skills.get('required', [])),
            'additional': self._clean_skill_list(skills.get('additional', [])),
            'certifications': self._clean_skill_list(skills.get('certifications', []))
        }

    def standardize_languages(self, languages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Стандартизирует данные о языках"""
        standardized = []
        for lang in languages:
            if not isinstance(lang, dict):
                continue
                
            level = self._standardize_language_level(lang.get('level', ''))
            if not level:
                continue
                
            standardized.append({
                'language': self._clean_text(lang.get('language', '')),
                'level': level
            })
        return standardized

    def _standardize_degree(self, degree: str) -> str:
        """Стандартизирует степень образования"""
        degree = degree.lower().strip()
        for std_degree, aliases in self.degree_aliases.items():
            if degree in aliases or any(alias in degree for alias in aliases):
                return std_degree
        return ''

    def _standardize_language_level(self, level: str) -> str:
        """Стандартизирует уровень владения языком"""
        level = level.lower().strip()
        for std_level, aliases in self.language_level_aliases.items():
            if level in aliases or any(alias in level for alias in aliases):
                return std_level
        return ''

    def _clean_institution_name(self, name: str) -> str:
        """Очищает название учебного заведения"""
        return self._clean_text(name)

    def _clean_text(self, text: str) -> str:
        """Очищает текст от лишних пробелов и специальных символов"""
        if not isinstance(text, str):
            return ''
        return ' '.join(text.strip().split())

    def _extract_years(self, years: str) -> str:
        """Извлекает годы обучения"""
        if isinstance(years, str):
            # Ищем годы в формате "2019-2023" или "2019 - 2023"
            match = re.search(r'(\d{4})\s*-\s*(\d{4})', years)
            if match:
                return f"{match.group(1)}-{match.group(2)}"
        return ''

    def _extract_experience_years(self, duration: Any) -> float:
        """Извлекает количество лет опыта работы"""
        if isinstance(duration, (int, float)):
            return float(duration)
            
        if isinstance(duration, str):
            # Ищем числа в строке
            numbers = re.findall(r'\d+(?:\.\d+)?', duration)
            if numbers:
                # Берем первое найденное число
                return float(numbers[0])
                
            # Проверяем на "less than" и подобные фразы
            if 'less than' in duration.lower():
                return 0.5
                
        return 0.0

    def _clean_responsibilities(self, responsibilities: List[str]) -> List[str]:
        """Очищает список обязанностей"""
        if not isinstance(responsibilities, list):
            return []
            
        return [self._clean_text(resp) for resp in responsibilities if isinstance(resp, str) and resp.strip()]

    def _clean_skill_list(self, skills: List[str]) -> List[str]:
        """Очищает список навыков"""
        if not isinstance(skills, list):
            return []
            
        return [self._clean_text(skill) for skill in skills if isinstance(skill, str) and skill.strip()]

    def _check_relevance(self, experience: Dict[str, Any]) -> bool:
        """Проверяет релевантность опыта работы"""
        relevant_keywords = {
            'python', 'java', 'javascript', 'developer', 'программист', 'разработчик',
            'analyst', 'аналитик', 'data', 'данные', 'ml', 'ai', 'machine learning',
            'deep learning', 'neural', 'нейронные сети'
        }
        
        text = ' '.join([
            str(experience.get('position', '')),
            str(experience.get('company', '')),
            ' '.join(str(r) for r in experience.get('responsibilities', []))
        ]).lower()
        
        return any(keyword in text for keyword in relevant_keywords)

    def _check_management(self, experience: Dict[str, Any]) -> bool:
        """Проверяет наличие управленческого опыта"""
        management_keywords = {
            'lead', 'лид', 'manager', 'менеджер', 'head', 'руководитель',
            'director', 'директор', 'chief', 'team lead', 'тимлид'
        }
        
        text = ' '.join([
            str(experience.get('position', '')),
            ' '.join(str(r) for r in experience.get('responsibilities', []))
        ]).lower()
        
        return any(keyword in text for keyword in management_keywords) 