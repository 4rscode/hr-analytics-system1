from typing import Dict, List, Any, Tuple
import yaml
import numpy as np
import logging
import pandas as pd
from sklearn.preprocessing import StandardScaler
from datetime import datetime
from .input_validator import InputValidator
from .data_validator import DataValidator
import re

logger = logging.getLogger(__name__)

class CompetencyAnalyzer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.competency_matrix = self._load_competency_matrix()
        self.industry_matrix = self._load_industry_matrix()
        self.universities = self._load_universities()
        self.course_recommendations = self._load_course_recommendations()
        self.experience_matrix = self._load_experience_matrix()
        self.roles = [
            'data_scientist', 
            'data_engineer', 
            'technical_analyst', 
            'ai_manager',
            'ml_engineer',
            'data_architect',
            'business_intelligence_analyst',
            'research_scientist'
        ]
        self.validator = DataValidator()
        
        # Уровни позиций
        self.seniority_levels = {
            'junior': {
                'min_experience': 0,
                'max_experience': 2,
                'education_weight': 0.5,
                'experience_weight': 0.2,
                'skills_weight': 0.2,
                'languages_weight': 0.1
            },
            'middle': {
                'min_experience': 2,
                'max_experience': 5,
                'education_weight': 0.3,
                'experience_weight': 0.4,
                'skills_weight': 0.2,
                'languages_weight': 0.1
            },
            'senior': {
                'min_experience': 5,
                'max_experience': float('inf'),
                'education_weight': 0.2,
                'experience_weight': 0.5,
                'skills_weight': 0.2,
                'languages_weight': 0.1
            }
        }
        
        # Веса для разных ролей
        self.role_weights = {
            'data_scientist': {
                'education': 0.35,
                'experience': 0.25,
                'skills': 0.3,
                'languages': 0.1
            },
            'data_engineer': {
                'education': 0.3,
                'experience': 0.35,
                'skills': 0.25,
                'languages': 0.1
            },
            'technical_analyst': {
                'education': 0.25,
                'experience': 0.3,
                'skills': 0.35,
                'languages': 0.1
            },
            'ai_manager': {
                'education': 0.3,
                'experience': 0.4,
                'skills': 0.2,
                'languages': 0.1
            },
            'ml_engineer': {
                'education': 0.3,
                'experience': 0.3,
                'skills': 0.35,
                'languages': 0.05
            },
            'data_architect': {
                'education': 0.3,
                'experience': 0.4,
                'skills': 0.2,
                'languages': 0.1
            },
            'business_intelligence_analyst': {
                'education': 0.25,
                'experience': 0.3,
                'skills': 0.35,
                'languages': 0.1
            },
            'research_scientist': {
                'education': 0.4,
                'experience': 0.3,
                'skills': 0.2,
                'languages': 0.1
            }
        }
        
        # Веса для образования
        self.education_weights = {
            'degree': {
                'phd': 1.0,
                'master': 0.9,
                'bachelor': 0.8,
                'specialist': 0.7,
                'incomplete_higher': 0.5
            },
            'university_rank': {
                'top': 1.0,
                'good': 0.8,
                'average': 0.6,
                'unknown': 0.4
            }
        }
        
        # Веса для опыта
        self.experience_weights = {
            'years_multiplier': 0.15,
            'relevant_experience_multiplier': 1.8,
            'management_multiplier': 1.2
        }
        
        # Веса для навыков
        self.skills_weights = {
            'required_skills_weight': 1.5,
            'additional_skills_weight': 1.0,
            'certifications_weight': 0.8
        }
        
        # Веса для языков
        self.languages_weights = {
            'native': 1.2,
            'fluent': 1.0,
            'advanced': 0.8,
            'intermediate': 0.6,
            'basic': 0.4
        }
        
        # Граничные значения для проверки выбросов
        self.boundaries = {
            'education': {
                'min_score': 0.0,
                'max_score': 1.0,
                'warning_threshold': 0.2
            },
            'experience': {
                'min_years': 0,
                'max_years': 50,
                'warning_threshold': 0.3
            },
            'skills': {
                'min_skills': 0,
                'max_skills': 100,
                'warning_threshold': 0.4
            },
            'languages': {
                'min_languages': 0,
                'max_languages': 10,
                'warning_threshold': 0.3
            }
        }

    def analyze_candidate(self, candidate_data: Dict[str, Any]) -> Dict[str, Any]:
        """Анализ кандидата"""
        try:
            self.logger.info(f"Starting candidate analysis at {datetime.now()}")
            
            # Сохраняем данные об опыте для использования в расчетах
            self.experience_data = candidate_data.get('experience', [])
            
            # Стандартизируем данные
            standardized_data = {
                'education': self._standardize_education(candidate_data.get('education', [])),
                'experience': self._standardize_experience(self.experience_data),
                'skills': self._standardize_skills(candidate_data.get('skills', {})),
                'languages': self._standardize_languages(candidate_data.get('languages', []))
            }
            
            # Рассчитываем оценки по категориям
            scores = {
                'education': self._calculate_education_score(standardized_data['education']),
                'experience': self._calculate_experience_score(standardized_data['experience']),
                'skills': self._calculate_skills_score(standardized_data['skills']),
                'languages': self._calculate_languages_score(standardized_data['languages'])
            }
            
            # Веса для общей оценки
            weights = {
                'education': 0.25,
                'experience': 0.35,
                'skills': 0.25,
                'languages': 0.15
            }
            
            # Рассчитываем общую оценку (максимум 100)
            overall_score = sum(score * weights[category] for category, score in scores.items())
            overall_score = min(overall_score, 100.0)  # Ограничиваем сверху
            
            # Рассчитываем соответствие ролям
            role_scores = self._calculate_role_scores(scores)
            best_fit_role = max(role_scores.items(), key=lambda x: x[1])
            
            return {
                'status': 'success',
                'overall_score': {
                    'value': round(overall_score, 1),
                    'details': {
                        category: round(score, 1)
                        for category, score in scores.items()
                    }
                },
                'role_fit': {
                    'best_fit': {
                        'role': best_fit_role[0],
                        'score': round(best_fit_role[1], 1)
                    },
                    'all_roles': {
                        role: round(score, 1)
                        for role, score in role_scores.items()
                    }
                },
                'details': {
                    'education': self._get_education_details(standardized_data['education']),
                    'experience': self._get_experience_details(standardized_data['experience']),
                    'skills': self._get_skills_details(standardized_data['skills']),
                    'languages': self._get_languages_details(standardized_data['languages'])
                },
                'recommendations': self._generate_recommendations(scores, best_fit_role[0])
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing candidate: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }

    def _standardize_education(self, education_data: List[Dict]) -> List[Dict]:
        """Стандартизация данных об образовании"""
        standardized = []
        for edu in education_data:
            if isinstance(edu, dict):
                degree = edu.get('degree', '').lower()
                if degree in ['phd', 'master', 'bachelor', 'specialist', 'incomplete_higher']:
                    # Получаем даты
                    start_date = edu.get('start_date', '')
                    end_date = edu.get('end_date', '')
                    
                    # Корректируем даты для бакалавриата
                    if degree == 'bachelor':
                        try:
                            # Пытаемся определить год начала обучения
                            if start_date:
                                start_year = int(start_date.split('-')[0])
                            elif end_date:
                                # Если есть только год окончания, отнимаем 4 года
                                end_year = int(end_date.split('-')[0])
                                start_year = end_year - 4
                            else:
                                # Если нет дат вообще, пропускаем
                                continue
                            
                            # Устанавливаем стандартные даты для бакалавриата
                            # Начало: 1 сентября года поступления
                            # Окончание: 30 июня года выпуска (через 4 года)
                            start_date = f"{start_year}-09-01"
                            end_date = f"{start_year + 4}-06-30"
                        except (ValueError, IndexError):
                            # Если не удалось распарсить дату, пропускаем
                            continue
                    
                    standardized.append({
                        'degree': degree,
                        'institution': edu.get('institution', ''),
                        'speciality': edu.get('speciality', ''),
                        'start_date': start_date,
                        'end_date': end_date
                    })
        return standardized

    def _standardize_experience(self, experience_data: List[Dict]) -> List[Dict]:
        """Стандартизация данных об опыте работы."""
        if not isinstance(experience_data, list):
            return []

        standardized = []
        for exp in experience_data:
            if not isinstance(exp, dict):
                continue

            # Загрузка матрицы опыта
            experience_matrix = self._load_experience_matrix()
            if not experience_matrix:
                experience_matrix = {
                    'positions': [],
                    'companies': [],
                    'tasks': [],
                    'industries': []
                }

            # Нормализация дат
            start_date = exp.get('start_date', '')
            end_date = exp.get('end_date', '')
            
            try:
                if start_date:
                    start_date = datetime.strptime(start_date, '%Y-%m-%d')
                if end_date:
                    end_date = datetime.strptime(end_date, '%Y-%m-%d')
                else:
                    # Если дата окончания не указана, считаем текущей
                    end_date = datetime.now()
            except ValueError:
                continue

            # Расчет продолжительности в годах с учетом месяцев
            duration_years = 0
            if start_date and end_date:
                duration = end_date - start_date
                duration_years = duration.days / 365.25

            # Определение релевантности опыта
            position = exp.get('position', '').lower()
            company = exp.get('company', '').lower()
            description = exp.get('description', '').lower()
            
            # Проверка релевантности должности
            position_relevance = 0
            for pos in experience_matrix['positions']:
                if any(alias.lower() in position for alias in pos['aliases']):
                    position_relevance = pos['weight']
                    break

            # Проверка релевантности компании
            company_relevance = 0
            for comp in experience_matrix['companies']:
                if any(alias.lower() in company for alias in comp['aliases']):
                    company_relevance = comp['weight']
                    break

            # Проверка релевантности задач
            tasks_relevance = 0
            for task in experience_matrix['tasks']:
                if any(alias.lower() in description for alias in task['aliases']):
                    tasks_relevance = max(tasks_relevance, task['weight'])

            # Определение общего веса релевантности
            relevance_weight = max(position_relevance, company_relevance, tasks_relevance)

            standardized.append({
                'company': exp.get('company', ''),
                'position': exp.get('position', ''),
                'start_date': start_date.strftime('%Y-%m-%d') if start_date else '',
                'end_date': end_date.strftime('%Y-%m-%d') if end_date else '',
                'duration_years': round(duration_years, 2),
                'is_relevant': relevance_weight >= 0.7,
                'relevance_weight': relevance_weight,
                'description': exp.get('description', '')
            })

        return standardized

    def _standardize_skills(self, skills_data: Dict) -> Dict:
        """Стандартизация данных о навыках"""
        if not isinstance(skills_data, dict):
            return {
                'required': [],
                'additional': [],
                'certifications': []
            }
            
        return {
            'required': [skill.lower().strip() for skill in skills_data.get('required', []) if isinstance(skill, str)],
            'additional': [skill.lower().strip() for skill in skills_data.get('additional', []) if isinstance(skill, str)],
            'certifications': [cert.lower().strip() for cert in skills_data.get('certifications', []) if isinstance(cert, str)]
        }

    def _standardize_languages(self, languages_data: List[Dict]) -> List[Dict]:
        """Стандартизация данных о языках"""
        if not isinstance(languages_data, list):
            return []
            
        standardized = []
        valid_levels = {'native', 'fluent', 'advanced', 'intermediate', 'basic'}
        
        for lang in languages_data:
            if not isinstance(lang, dict):
                continue
                
            language = lang.get('language', '').lower().strip()
            level = lang.get('level', '').lower().strip()
            
            if not language or level not in valid_levels:
                continue
                
            standardized.append({
                'language': language,
                'level': level
            })
            
        return standardized

    def _calculate_education_score(self, education_data: List[Dict]) -> float:
        """Расчет оценки за образование"""
        if not education_data:
            return 0.0

        max_score = 0.0
        for edu in education_data:
            # Базовый балл за степень
            degree = edu.get('degree', '').lower()
            base_score = self.education_weights['degree'].get(degree, 0.0)
            
            # Бонус за рейтинг университета
            institution = edu.get('institution', '').strip()
            university_score = 0.0
            
            # Ищем университет в списке
            for univ in self.universities:
                if univ['name'].lower() in institution.lower():
                    rank = univ['rank']
                    university_score = self.education_weights['university_rank'].get(rank, 0.0)
                    break
            
            # Итоговый балл (70% за степень, 30% за университет)
            final_score = (base_score * 0.7 + university_score * 0.3)
            max_score = max(max_score, final_score)
            
        return min(max_score * 100, 100.0)  # Нормализуем к 100 баллам

    def _calculate_experience_score(self, experience_data: List[Dict]) -> float:
        """Расчет оценки опыта работы с учетом матрицы."""
        if not experience_data:
            return 0.0

        # 1. Расчет общего стажа
        total_years = sum(float(exp.get('duration_years', 0)) for exp in experience_data if float(exp.get('duration_years', 0)) > 0)
        
        if total_years <= 0:
            return 0.0

        # 2. Базовый балл за стаж
        base_score = min(total_years * self.experience_weights['years_multiplier'], 1.0)

        # 3. Модификаторы за качество опыта
        weighted_scores = []

        for exp in experience_data:
            position = exp.get('position', '').lower()
            company = exp.get('company', '').lower()
            description = exp.get('description', '').lower()
            duration = float(exp.get('duration_years', 0))
            
            if duration <= 0:
                continue
            
            # 3.1. Оценка позиции
            position_score = 0.5
            for pos in self.experience_matrix['positions']:
                if any(alias.lower() in position for alias in pos['aliases']):
                    position_score = min(pos['weight'], 1.0)
                    break
            
            # 3.2. Оценка компании
            company_score = 0.5
            for comp in self.experience_matrix['companies']:
                if any(alias.lower() in company for alias in comp['aliases']):
                    company_score = min(comp['weight'], 1.0)
                    break
            
            # 3.3. Оценка задач
            tasks_score = 0.5
            for task in self.experience_matrix['tasks']:
                if any(alias.lower() in description for alias in task['aliases']):
                    tasks_score = min(max(tasks_score, task['weight']), 1.0)
            
            # 3.4. Общий вес опыта
            experience_weight = (
                position_score * 0.4 +
                company_score * 0.3 +
                tasks_score * 0.3
            )
            
            # 3.5. Учитываем продолжительность
            duration_weight = duration / total_years
            
            # 3.6. Добавляем взвешенную оценку
            weighted_scores.append(experience_weight * duration_weight)

        # 4. Рассчитываем итоговый модификатор
        quality_modifier = sum(weighted_scores) if weighted_scores else 0.5
        quality_modifier = min(quality_modifier, 1.0)

        # 5. Финальная оценка
        final_score = base_score * quality_modifier * self.experience_weights['relevant_experience_multiplier']
        return min(final_score * 100, 100.0)  # Нормализуем к 100 баллам

    def _calculate_skills_score(self, skills_data: Dict) -> float:
        """Рассчитывает оценку навыков"""
        # Веса для разных категорий навыков
        weights = {
            'required': 1.5,
            'additional': 1.0,
            'certifications': 0.8
        }
        
        # Максимальное количество навыков для каждой категории
        max_counts = {
            'required': 10,
            'additional': 15,
            'certifications': 5
        }
        
        # Считаем количество навыков в каждой категории
        counts = {
            'required': len(skills_data.get('required', [])),
            'additional': len(skills_data.get('additional', [])),
            'certifications': len(skills_data.get('certifications', []))
        }
        
        # Рассчитываем взвешенную сумму
        total_score = sum(
            min(counts[category] / max_counts[category], 1.0) * weight
            for category, weight in weights.items()
        )
        
        # Нормализуем к 100 баллам
        return min(total_score * 20, 100.0)

    def _calculate_languages_score(self, languages_data: List[Dict]) -> float:
        """Рассчитывает оценку языковых навыков"""
        if not languages_data:
            return 0.0

        # Веса для разных уровней владения языком
        level_weights = {
            'native': 1.2,
            'fluent': 1.0,
            'advanced': 0.8,
            'intermediate': 0.6,
            'basic': 0.4
        }
        
        # Рассчитываем взвешенную сумму
        total_score = sum(
            level_weights.get(lang.get('level', '').lower(), 0.0)
            for lang in languages_data
        )
        
        # Нормализуем к 100 баллам
        return min(total_score * 25, 100.0)

    def _calculate_role_scores(self, scores: Dict[str, float]) -> Dict[str, float]:
        """Рассчитывает оценки для каждой роли на основе весов"""
        role_scores = {}
        
        for role, weights in self.role_weights.items():
            # Рассчитываем взвешенную сумму для каждой роли
            total_score = (
                scores['education'] * weights['education'] +
                scores['experience'] * weights['experience'] +
                scores['skills'] * weights['skills'] +
                scores['languages'] * weights['languages']
            )
            
            # Нормализуем к 100 баллам
            role_scores[role] = min(total_score, 100.0)
            
        return role_scores

    def _generate_recommendations(self, scores: Dict[str, float], best_fit_role: str) -> Dict[str, Any]:
        """Генерирует рекомендации по улучшению для каждой категории"""
        recommendations = {
            'education': [],
            'experience': [],
            'skills': [],
            'languages': [],
            'course_recommendations': []
        }
        
        # Рекомендации по образованию
        if scores['education'] < 80:
            recommendations['education'].append(
                "Рассмотрите возможность получения дополнительного образования или сертификации"
            )
            
        # Рекомендации по опыту
        if scores['experience'] < 80:
            recommendations['experience'].append(
                "Попробуйте получить больше практического опыта в соответствующей области"
            )
            
        # Рекомендации по навыкам
        if scores['skills'] < 80:
            recommendations['skills'].append(
                "Изучите дополнительные технологии и инструменты, востребованные в вашей роли"
            )
            
        # Рекомендации по языкам
        if scores['languages'] < 80:
            recommendations['languages'].append(
                "Улучшите уровень владения английским языком и рассмотрите изучение дополнительных языков"
            )

        # Добавляем рекомендации по курсам на основе роли и текущих навыков
        role_courses = {
            'data_scientist': ["Методы машинного обучения", "Глубокое обучение", "SQL базы данных"],
            'data_engineer': ["SQL базы данных", "Hadoop и большие данные"],
            'technical_analyst': ["SQL базы данных", "Методы машинного обучения"],
            'ai_manager': ["Методы машинного обучения", "Глубокое обучение"],
            'ml_engineer': ["Глубокое обучение", "Анализ естественного языка", "Анализ изображений и видео"],
            'data_architect': ["SQL базы данных", "Hadoop и большие данные"],
            'business_intelligence_analyst': ["SQL базы данных", "Методы машинного обучения"],
            'research_scientist': ["Глубокое обучение", "Анализ естественного языка", "Анализ изображений и видео"]
        }

        # Получаем рекомендуемые курсы для роли
        recommended_course_types = role_courses.get(best_fit_role, [])
        
        # Загружаем доступные курсы
        available_courses = self.course_recommendations
        
        # Добавляем конкретные курсы в рекомендации
        for course_type in recommended_course_types:
            if course_type in available_courses:
                for course in available_courses[course_type]:
                    recommendations['course_recommendations'].append({
                        'name': course['name'],
                        'platform': course['platform'],
                        'url': course['url'],
                        'duration': course['duration'],
                        'level': course['level']
                    })
            
        return recommendations

    def _get_education_details(self, education_data: List[Dict]) -> Dict[str, Any]:
        """Возвращает детали образования"""
        if not education_data:
            return {
                'degrees': [],
                'institutions': [],
                'years': [],
                'score': 0.0
            }
            
        return {
            'degrees': [edu.get('degree', '') for edu in education_data],
            'institutions': [edu.get('institution', '') for edu in education_data],
            'years': [f"{edu.get('start_date', '')} - {edu.get('end_date', '')}" for edu in education_data],
            'score': round(self._calculate_education_score(education_data), 1)
        }

    def _get_experience_details(self, experience_data: List[Dict]) -> Dict[str, Any]:
        """Возвращает детали опыта работы"""
        if not experience_data:
            return {
                'positions': [],
                'companies': [],
                'years': [],
                'responsibilities': [],
                'score': 0.0
            }
            
        return {
            'positions': [exp.get('position', '') for exp in experience_data],
            'companies': [exp.get('company', '') for exp in experience_data],
            'years': [str(exp.get('duration_years', 0)) for exp in experience_data],
            'responsibilities': [exp.get('description', '') for exp in experience_data],
            'score': round(self._calculate_experience_score(experience_data), 1)
        }

    def _get_skills_details(self, skills_data: Dict) -> Dict[str, Any]:
        """Возвращает детали навыков"""
        if not skills_data:
            return {
                'required_skills': [],
                'additional_skills': [],
                'certifications': [],
                'score': 0.0
            }
            
        return {
            'required_skills': skills_data.get('required', []),
            'additional_skills': skills_data.get('additional', []),
            'certifications': skills_data.get('certifications', []),
            'score': round(self._calculate_skills_score(skills_data), 1)
        }

    def _get_languages_details(self, languages_data: List[Dict]) -> Dict[str, Any]:
        """Возвращает детали знания языков"""
        if not languages_data:
            return {
                'languages': [],
                'score': 0.0
            }
            
        return {
            'languages': [
                {
                    'language': lang.get('language', ''),
                    'level': lang.get('level', ''),
                    'score': self._calculate_languages_score([lang])
                }
                for lang in languages_data
            ],
            'score': round(self._calculate_languages_score(languages_data), 1)
        }

    def _load_competency_matrix(self) -> Dict:
        """Загружает матрицу компетенций"""
        try:
            with open('data/competency_matrix.yaml', 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                
            matrix = {
                'roles': data['roles'],
                'competencies': {}
            }
            
            # Собираем все компетенции в один словарь
            for category in ['general', 'algorithms', 'data_management']:
                for comp in data['competencies'][category]:
                    matrix['competencies'][comp['name']] = {
                        'levels': comp['levels'],
                        'skills': comp.get('skills', [])
                    }
            
            return matrix
        except Exception as e:
            self.logger.error(f"Error loading competency matrix: {str(e)}")
            return {}

    def _load_industry_matrix(self) -> Dict:
        """Загружает матрицу отраслей"""
        try:
            with open('data/industry_matrix.yaml', 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)['industry_matrix']
        except Exception as e:
            self.logger.error(f"Error loading industry matrix: {str(e)}")
            return {}

    def _load_universities(self) -> List[Dict]:
        """Загружает данные об университетах"""
        try:
            with open('data/universities.yaml', 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                return data.get('universities', [])
        except Exception as e:
            self.logger.error(f"Error loading universities data: {str(e)}")
            return []

    def _load_course_recommendations(self) -> Dict:
        """Загружает рекомендации по курсам"""
        try:
            with open('data/course_recommendations.yaml', 'r', encoding='utf-8') as f:
                return yaml.safe_load(f).get('courses', {})
        except Exception as e:
            self.logger.error(f"Error loading course recommendations: {str(e)}")
            return {}

    def _load_experience_matrix(self) -> Dict:
        """Загружает матрицу опыта"""
        try:
            with open('data/experience_matrix.yaml', 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                return data.get('experience_matrix', {
                    'positions': [],
                    'companies': [],
                    'tasks': [],
                    'industries': []
                })
        except Exception as e:
            self.logger.error(f"Error loading experience matrix: {str(e)}")
            return {
                'positions': [],
                'companies': [],
                'tasks': [],
                'industries': []
            }