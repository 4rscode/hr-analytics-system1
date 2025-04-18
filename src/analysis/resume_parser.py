import openai
from typing import Dict, List, Any
import logging
import json
import re
from datetime import datetime
import hashlib
import os
from pathlib import Path

logger = logging.getLogger(__name__)

class ResumeParser:
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("API key is required")
        self.client = openai.OpenAI(
            api_key=api_key,
            base_url='https://api.rockapi.ru/openai/v1'
        )
        self.section_patterns = {
            'education': r'(?i)(образование|education|учёба|университет|вуз|институт)',
            'experience': r'(?i)(опыт работы|experience|трудовой стаж|места работы)',
            'skills': r'(?i)(навыки|skills|компетенции|умения)',
            'languages': r'(?i)(языки|languages|знание языков)',
            'certifications': r'(?i)(сертификаты|certifications|курсы|обучение)'
        }
        self.cache_dir = Path("cache")
        self.cache_dir.mkdir(exist_ok=True)

    def _split_text(self, text: str, max_length: int = 1500) -> List[str]:
        """Разбивает текст на части подходящей длины"""
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 > max_length:
                chunks.append(' '.join(current_chunk))
                current_chunk = [word]
                current_length = len(word)
            else:
                current_chunk.append(word)
                current_length += len(word) + 1
                
        if current_chunk:
            chunks.append(' '.join(current_chunk))
            
        return chunks

    def _extract_years_from_text(self, text: str) -> int:
        """Извлекает количество лет опыта из текста"""
        if not text:
            return 0
            
        # Пытаемся найти числа в тексте
        numbers = re.findall(r'\d+', str(text))
        if numbers:
            return int(numbers[0])
        return 0

    def _normalize_experience(self, experience_data: Any) -> Dict[str, int]:
        """Нормализует данные об опыте работы"""
        try:
            if isinstance(experience_data, dict) and 'years' in experience_data:
                years = experience_data['years']
                if isinstance(years, (int, float)):
                    return {"years": int(years)}
                return {"years": self._extract_years_from_text(years)}
            elif isinstance(experience_data, (int, float)):
                return {"years": int(experience_data)}
            else:
                return {"years": self._extract_years_from_text(str(experience_data))}
        except:
            return {"years": 0}

    def parse_resume(self, text: str, filename: str) -> Dict[str, Any]:
        """Парсит текст резюме и возвращает структурированные данные"""
        try:
            # Создаем хэш из текста резюме
            text_hash = hashlib.md5(text.encode()).hexdigest()
            cache_file = self.cache_dir / f"{text_hash}.json"
            
            # Проверяем наличие кэшированного результата
            if cache_file.exists():
                logger.info(f"Using cached parsing result for {filename}")
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            
            logger.info("Starting information extraction")
            
            # Используем GPT для извлечения структурированной информации
            prompt = self._get_prompt(text)

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that extracts structured information from resumes. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            try:
                extracted_data = json.loads(response.choices[0].message.content)
                logger.debug("Extracted data:")
                logger.debug(json.dumps(extracted_data, ensure_ascii=False, indent=2))
                
                # Сохраняем результат в кэш
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump(extracted_data, f, ensure_ascii=False, indent=2)
                
                return extracted_data
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse GPT response as JSON: {str(e)}")
                return {}
                
        except Exception as e:
            logger.error(f"Error parsing resume: {str(e)}", exc_info=True)
            return {}

    def _split_into_sections(self, text: str) -> Dict[str, str]:
        """Разделяет текст на секции по заголовкам"""
        sections = {}
        current_section = None
        current_text = []
        
        # Расширяем паттерны для определения секций
        self.section_patterns = {
            'education': [
                r'(?i)(образование|education|учёба|университет|вуз|институт|высшее образование)',
                r'(?i)(образование|education|учёба|университет|вуз|институт|высшее образование)\s*[:：]'
            ],
            'experience': [
                r'(?i)(опыт работы|experience|трудовой стаж|места работы|профессиональный опыт)',
                r'(?i)(опыт работы|experience|трудовой стаж|места работы|профессиональный опыт)\s*[:：]'
            ],
            'skills': [
                r'(?i)(навыки|skills|компетенции|умения|профессиональные навыки)',
                r'(?i)(навыки|skills|компетенции|умения|профессиональные навыки)\s*[:：]'
            ],
            'languages': [
                r'(?i)(языки|languages|знание языков|иностранные языки)',
                r'(?i)(языки|languages|знание языков|иностранные языки)\s*[:：]'
            ],
            'certifications': [
                r'(?i)(сертификаты|certifications|курсы|обучение|дополнительное образование)',
                r'(?i)(сертификаты|certifications|курсы|обучение|дополнительное образование)\s*[:：]'
            ]
        }
        
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Проверяем, является ли строка заголовком секции
            section_found = False
            for section_name, patterns in self.section_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, line):
                        if current_section:
                            sections[current_section] = '\n'.join(current_text)
                        current_section = section_name
                        current_text = []
                        section_found = True
                        break
                if section_found:
                    break
                    
            if not section_found and current_section:
                current_text.append(line)
                
        if current_section:
            sections[current_section] = '\n'.join(current_text)
            
        # Если не найдено ни одной секции, пробуем определить их по контексту
        if not sections:
            logger.warning("No sections found by headers, trying to determine by context")
            # Разделяем текст на абзацы
            paragraphs = re.split(r'\n\s*\n', text)
            for paragraph in paragraphs:
                paragraph = paragraph.strip()
                if not paragraph:
                    continue
                    
                # Определяем секцию по ключевым словам в тексте
                for section_name, patterns in self.section_patterns.items():
                    for pattern in patterns:
                        if re.search(pattern, paragraph):
                            if section_name not in sections:
                                sections[section_name] = ''
                            sections[section_name] += '\n' + paragraph
                            break
                            
        logger.debug(f"Found sections: {list(sections.keys())}")
        for section_name, content in sections.items():
            logger.debug(f"Section '{section_name}' content length: {len(content)}")
            
        return sections

    def _parse_education(self, text: str) -> List[Dict[str, Any]]:
        """Парсит секцию образования"""
        education = []
        if not text:
            return education
            
        # Паттерны для извлечения информации об образовании
        patterns = {
            'degree': r'(?i)(phd|master|bachelor|specialist|incomplete_higher|доктор|магистр|бакалавр|специалист|неоконченное высшее)',
            'institution': r'(?i)(университет|институт|академия|college|university|institute)',
            'speciality': r'(?i)(специальность|направление|major|specialization)',
            'years': r'(?i)(год|years|срок обучения)'
        }
        
        # Разделяем текст на записи об образовании
        entries = re.split(r'\n\s*\n', text)
        for entry in entries:
            if not entry.strip():
                continue
                
            edu_entry = {
                'degree': '',
                'institution': '',
                'speciality': '',
                'start_date': '',
                'end_date': ''
            }
            
            # Извлекаем информацию с помощью паттернов
            for field, pattern in patterns.items():
                match = re.search(pattern, entry)
                if match:
                    edu_entry[field] = match.group(1)
                    
            # Если не найдена степень, пробуем определить по контексту
            if not edu_entry['degree']:
                if re.search(r'(?i)(phd|доктор)', entry):
                    edu_entry['degree'] = 'phd'
                elif re.search(r'(?i)(master|магистр)', entry):
                    edu_entry['degree'] = 'master'
                elif re.search(r'(?i)(bachelor|бакалавр)', entry):
                    edu_entry['degree'] = 'bachelor'
                elif re.search(r'(?i)(specialist|специалист)', entry):
                    edu_entry['degree'] = 'specialist'
                else:
                    edu_entry['degree'] = 'incomplete_higher'
                    
            # Если не найдено учебное заведение, используем "Unknown"
            if not edu_entry['institution']:
                edu_entry['institution'] = 'Unknown'
                
            education.append(edu_entry)
            
        return education

    def _parse_experience(self, text: str) -> List[Dict[str, Any]]:
        """Парсит секцию опыта работы"""
        experience = []
        if not text:
            return experience
            
        # Паттерны для извлечения информации об опыте
        patterns = {
            'position': r'(?i)(должность|position|роль|role)',
            'company': r'(?i)(компания|организация|company|organization)',
            'years': r'(?i)(стаж|опыт|experience|years)',
            'responsibilities': r'(?i)(обязанности|responsibilities|функции|functions)'
        }
        
        # Разделяем текст на записи об опыте
        entries = re.split(r'\n\s*\n', text)
        for entry in entries:
            if not entry.strip():
                continue
                
            exp_entry = {
                'position': '',
                'company': '',
                'years': 0,
                'is_relevant': False,
                'is_management': False,
                'start_date': '',
                'end_date': '',
                'responsibilities': []
            }
            
            # Извлекаем информацию с помощью паттернов
            for field, pattern in patterns.items():
                match = re.search(pattern, entry)
                if match:
                    exp_entry[field] = match.group(1)
                    
            # Если не найдена должность, используем "Unknown"
            if not exp_entry['position']:
                exp_entry['position'] = 'Unknown'
                
            # Если не найдена компания, используем "Unknown"
            if not exp_entry['company']:
                exp_entry['company'] = 'Unknown'
                
            # Определяем релевантность опыта
            exp_entry['is_relevant'] = self._is_relevant_experience(entry)
            
            # Определяем управленческий опыт
            exp_entry['is_management'] = self._is_management_position(entry)
            
            experience.append(exp_entry)
            
        return experience

    def _parse_skills(self, text: str) -> Dict[str, List[str]]:
        """Парсит секцию навыков"""
        skills = {
            'required': [],
            'additional': [],
            'certifications': []
        }
        
        if not text:
            return skills
            
        # Разделяем навыки на категории
        lines = text.split('\n')
        current_category = 'additional'
        
        for line in lines:
            line = line.strip().lower()
            if not line:
                continue
                
            # Определяем категорию навыков
            if re.search(r'(?i)(обязательные|required|основные)', line):
                current_category = 'required'
                continue
            elif re.search(r'(?i)(дополнительные|additional|другие)', line):
                current_category = 'additional'
                continue
            elif re.search(r'(?i)(сертификаты|certifications|курсы)', line):
                current_category = 'certifications'
                continue
                
            # Добавляем навык в соответствующую категорию
            if current_category == 'certifications':
                skills['certifications'].append(line)
            else:
                skills[current_category].append(line)
                
        return skills

    def _parse_languages(self, text: str) -> List[Dict[str, str]]:
        """Парсит секцию языков"""
        languages = []
        if not text:
            return languages
            
        # Паттерны для извлечения информации о языках
        patterns = {
            'language': r'(?i)(английский|русский|немецкий|французский|испанский|english|russian|german|french|spanish)',
            'level': r'(?i)(родной|свободный|продвинутый|средний|начальный|native|fluent|advanced|intermediate|basic)'
        }
        
        # Разделяем текст на записи о языках
        entries = re.split(r'\n', text)
        for entry in entries:
            if not entry.strip():
                continue
                
            lang_entry = {
                'language': '',
                'level': ''
            }
            
            # Извлекаем информацию с помощью паттернов
            for field, pattern in patterns.items():
                match = re.search(pattern, entry)
                if match:
                    lang_entry[field] = match.group(1)
                    
            # Если не найден язык, пропускаем запись
            if not lang_entry['language']:
                continue
                
            # Если не найден уровень, используем "basic"
            if not lang_entry['level']:
                lang_entry['level'] = 'basic'
                
            languages.append(lang_entry)
            
        return languages

    def _parse_certifications(self, text: str) -> List[Dict[str, str]]:
        """Парсит секцию сертификатов"""
        certifications = []
        if not text:
            return certifications
            
        entries = text.split('\n')
        for entry in entries:
            if not entry.strip():
                continue
                
            # Извлекаем информацию о сертификате
            date_match = re.search(r'(\d{4})', entry)
            certifications.append({
                'name': entry.strip(),
                'year': date_match.group(1) if date_match else ''
            })
            
        return certifications

    def _is_relevant_experience(self, text: str) -> bool:
        """Определяет, является ли опыт релевантным"""
        relevant_keywords = [
            'data', 'analytics', 'analysis', 'python', 'sql',
            'machine learning', 'ai', 'artificial intelligence',
            'big data', 'data science', 'analyst'
        ]
        
        text = text.lower()
        return any(keyword in text for keyword in relevant_keywords)

    def _is_management_position(self, text: str) -> bool:
        """Определяет, является ли позиция управленческой"""
        management_keywords = [
            'lead', 'head', 'manager', 'director', 'chief',
            'руководитель', 'начальник', 'директор', 'глава'
        ]
        
        text = text.lower()
        return any(keyword in text for keyword in management_keywords)

    def _enhance_with_gpt(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Улучшает структурированные данные с помощью GPT"""
        try:
            prompt = f"""
            Проанализируй следующую структурированную информацию из резюме и улучши её:
            {json.dumps(data, ensure_ascii=False, indent=2)}
            
            Улучши структуру данных, добавив:
            1. Более точные категории для навыков
            2. Дополнительные метаданные для опыта работы
            3. Уточнённые уровни владения языками
            4. Дополнительные детали об образовании
            
            Верни ответ в формате JSON.
            """

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that enhances resume data structure. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            try:
                enhanced_data = json.loads(response.choices[0].message.content)
                return enhanced_data
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse GPT response as JSON: {str(e)}")
                return data
                
        except Exception as e:
            logger.error(f"Error enhancing data with GPT: {str(e)}")
            return data

    def _get_prompt(self, text: str) -> str:
        return f"""Проанализируй текст резюме и извлеки структурированную информацию. 
Используй только факты из резюме, оставляй поля пустыми, если информация отсутствует.

Правила для дат:
1. Все даты должны быть в формате YYYY-MM-DD
2. Если указан только год, используй:
   - Начало: YYYY-01-01
   - Конец: YYYY-12-31
3. Если указан месяц и год, используй:
   - Начало: YYYY-MM-01
   - Конец: YYYY-MM-31
4. Если указан только период (например, "2023-2024"), используй:
   - Начало: 2023-01-01
   - Конец: 2024-12-31
5. Если дата окончания не указана, используй текущую дату
6. Если дата начала не указана, но есть дата окончания, отними 1 год от даты окончания

Правила для опыта работы:
1. Для каждой позиции указывай:
   - Точное название должности
   - Полное название компании
   - Даты начала и окончания
   - Основные обязанности и достижения
2. Если обязанности не указаны, попробуй вывести их из контекста
3. Рассчитывай продолжительность работы в годах с точностью до двух знаков после запятой
4. Если опыт менее месяца, указывай 0.08 (1/12 года)
5. Не суммируй опыт из разных позиций

Правила для образования:
1. Указывай:
   - Степень (phd, master, bachelor, specialist, incomplete_higher)
   - Полное название учебного заведения
   - Даты начала и окончания
2. Если даты не указаны, используй стандартные сроки:
   - Бакалавриат: 4 года
   - Магистратура: 2 года
   - PhD: 4 года

Правила для навыков:
1. Разделяй навыки на категории:
   - required_skills: технические навыки, необходимые для работы
   - additional_skills: дополнительные знания и умения
   - certifications: сертификаты и курсы
2. Стандартизируй названия навыков
3. Не дублируй навыки между категориями

Правила для языков:
1. Указывай уровень владения:
   - native: родной язык
   - fluent: свободное владение
   - advanced: продвинутый уровень
   - intermediate: средний уровень
   - basic: базовый уровень
2. Используй стандартные названия языков

Формат ответа:
{{
    "education": [
        {{
            "degree": "master",
            "institution": "Название университета",
            "speciality": "Специальность",
            "start_date": "YYYY-MM-DD",
            "end_date": "YYYY-MM-DD"
        }}
    ],
    "experience": [
        {{
            "company": "Название компании",
            "position": "Должность",
            "start_date": "YYYY-MM-DD",
            "end_date": "YYYY-MM-DD",
            "duration_years": "X.XX",
            "description": "Описание обязанностей и достижений",
            "is_relevant": true,
            "is_management": false
        }}
    ],
    "skills": {{
        "required": ["навык1", "навык2"],
        "additional": ["навык3", "навык4"],
        "certifications": ["сертификат1", "сертификат2"]
    }},
    "languages": [
        {{
            "language": "название языка",
            "level": "уровень владения"
        }}
    ]
}}

Текст резюме:
{text}"""
