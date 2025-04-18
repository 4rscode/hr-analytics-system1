import yaml
import json
import os
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, JSON, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)

Base = declarative_base()

class Resume(Base):
    __tablename__ = 'resumes'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    extracted_info = Column(JSON)
    analysis_results = Column(JSON)
    university = Column(String(255))
    speciality = Column(String(255))
    graduation_year = Column(String(50))
    education_score = Column(Integer)
    skills = Column(JSON)
    experience_years = Column(Integer)
    total_score = Column(Integer)
    upload_date = Column(DateTime, default=datetime.utcnow)
    last_modified = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Database:
    def __init__(self, config_path: str = 'config.yaml'):
        try:
            with open(config_path) as f:
                config = yaml.safe_load(f)['database']
                
            # Создаем путь к файлу базы данных
            db_path = os.path.abspath(config['path'])
            db_dir = os.path.dirname(db_path)
            
            # Создаем директорию для базы данных, если она не существует
            if not os.path.exists(db_dir):
                os.makedirs(db_dir)
                logger.info(f"Created database directory: {db_dir}")
            
            self.engine = create_engine(f"sqlite:///{db_path}")
            
            # Удаляем существующую таблицу и создаем новую с обновленной схемой
            Base.metadata.drop_all(self.engine)
            Base.metadata.create_all(self.engine)
            
            Session = sessionmaker(bind=self.engine)
            self.session = Session()
            logger.info("Database connection established successfully")
            
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            raise

    def save_analysis(self, extracted_info: Dict, analysis_result: Dict) -> Optional[int]:
        """
        Сохраняет результаты анализа резюме в базу данных.
        
        Args:
            extracted_info (Dict): Извлеченная информация из резюме
            analysis_result (Dict): Результаты анализа компетенций
            
        Returns:
            Optional[int]: ID сохраненной записи или None в случае ошибки
        """
        try:
            # Логируем входные данные для отладки
            logger.debug(f"Extracted info: {json.dumps(extracted_info, indent=2)}")
            logger.debug(f"Analysis result: {json.dumps(analysis_result, indent=2)}")
            
            # Получаем данные об образовании
            education = extracted_info.get('education', [{}])[0] if extracted_info.get('education') else {}
            
            # Подсчитываем годы опыта с обработкой русских текстовых значений
            experience = extracted_info.get('experience', [])
            total_experience = 0
            for exp in experience:
                if isinstance(exp, dict):
                    duration = exp.get('years', '0')
                    if isinstance(duration, str):
                        # Обработка русских текстовых значений
                        if 'месяц' in duration.lower():
                            try:
                                months = float(duration.split()[0]) / 12
                                total_experience += months
                            except (ValueError, IndexError):
                                total_experience += 0
                        else:
                            try:
                                total_experience += float(duration)
                            except ValueError:
                                total_experience += 0
                    else:
                        total_experience += float(duration)
            
            # Получаем оценки из результатов анализа
            overall_score = analysis_result.get('overall_score', {}).get('value', 0)
            education_score = analysis_result.get('details', {}).get('education', {}).get('score', 0)
            
            # Преобразуем оценки в целые числа
            try:
                if isinstance(overall_score, dict):
                    total_score = int(float(overall_score.get('value', 0)))
                else:
                    total_score = int(float(overall_score))
                
                if isinstance(education_score, dict):
                    education_score = int(float(education_score.get('value', 0)))
                else:
                    education_score = int(float(education_score))
            except (ValueError, TypeError):
                total_score = 0
                education_score = 0
            
            # Создаем запись в БД
            resume = Resume(
                filename=extracted_info.get('original_filename', 'unknown.pdf'),
                content=extracted_info.get('text', ''),
                extracted_info=json.dumps(extracted_info),
                analysis_results=json.dumps(analysis_result),
                university=education.get('institution', ''),
                speciality=education.get('speciality', ''),
                graduation_year=education.get('end_date', ''),
                education_score=education_score,
                skills=json.dumps(extracted_info.get('skills', {})),
                experience_years=int(total_experience),
                total_score=total_score
            )
            
            # Логируем данные перед сохранением
            logger.info(f"Saving resume: filename={resume.filename}, "
                       f"university={resume.university}, "
                       f"total_score={resume.total_score}")
            
            self.session.add(resume)
            self.session.commit()
            logger.info(f"Successfully saved analysis results with ID: {resume.id}")
            return resume.id
            
        except SQLAlchemyError as e:
            logger.error(f"Database error while saving analysis: {str(e)}")
            self.session.rollback()
            return None
        except Exception as e:
            logger.error(f"Error saving analysis: {str(e)}")
            logger.error(f"Extracted info type: {type(extracted_info)}")
            logger.error(f"Analysis result type: {type(analysis_result)}")
            self.session.rollback()
            return None

    def save_resume(self, filename: str, content: str, extracted_info: Dict, 
                   analysis_results: Dict) -> Optional[int]:
        try:
            resume = Resume(
                filename=filename,
                content=content,
                extracted_info=json.dumps(extracted_info),
                analysis_results=json.dumps(analysis_results),
                university=extracted_info.get('education', [{}])[0].get('university'),
                speciality=extracted_info.get('education', [{}])[0].get('speciality'),
                graduation_year=extracted_info.get('education', [{}])[0].get('year'),
                education_score=analysis_results.get('education_score'),
                skills=json.dumps(extracted_info.get('skills', [])),
                experience_years=analysis_results.get('experience_years'),
                total_score=analysis_results.get('total_score')
            )
            self.session.add(resume)
            self.session.commit()
            logger.info(f"Successfully saved resume with ID: {resume.id}")
            return resume.id
        except SQLAlchemyError as e:
            logger.error(f"Database error while saving resume: {str(e)}")
            self.session.rollback()
            return None
        except Exception as e:
            logger.error(f"Error saving resume: {str(e)}")
            self.session.rollback()
            return None

    def get_resume(self, resume_id: int) -> Optional[Dict]:
        try:
            resume = self.session.query(Resume).filter(Resume.id == resume_id).first()
            if resume:
                return {
                    'id': resume.id,
                    'filename': resume.filename,
                    'content': resume.content,
                    'extracted_info': json.loads(resume.extracted_info),
                    'analysis_results': json.loads(resume.analysis_results),
                    'university': resume.university,
                    'speciality': resume.speciality,
                    'graduation_year': resume.graduation_year,
                    'education_score': resume.education_score,
                    'skills': json.loads(resume.skills),
                    'experience_years': resume.experience_years,
                    'total_score': resume.total_score,
                    'upload_date': resume.upload_date.isoformat(),
                    'last_modified': resume.last_modified.isoformat()
                }
            return None
        except Exception as e:
            logger.error(f"Error retrieving resume {resume_id}: {str(e)}")
            return None

    def get_all_resumes(self) -> List[Dict]:
        try:
            resumes = self.session.query(Resume).all()
            return [{
                'id': r.id,
                'filename': r.filename,
                'university': r.university,
                'speciality': r.speciality,
                'graduation_year': r.graduation_year,
                'education_score': r.education_score,
                'experience_years': r.experience_years,
                'total_score': r.total_score,
                'upload_date': r.upload_date.isoformat(),
                'last_modified': r.last_modified.isoformat()
            } for r in resumes]
        except Exception as e:
            logger.error(f"Error retrieving all resumes: {str(e)}")
            return []

    def update_resume(self, resume_id: int, updates: Dict[str, Any]) -> bool:
        try:
            resume = self.session.query(Resume).filter(Resume.id == resume_id).first()
            if resume:
                for key, value in updates.items():
                    if hasattr(resume, key):
                        setattr(resume, key, value)
                self.session.commit()
                logger.info(f"Successfully updated resume {resume_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error updating resume {resume_id}: {str(e)}")
            self.session.rollback()
            return False

    def delete_resume(self, resume_id: int) -> bool:
        try:
            resume = self.session.query(Resume).filter(Resume.id == resume_id).first()
            if resume:
                self.session.delete(resume)
                self.session.commit()
                logger.info(f"Successfully deleted resume {resume_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting resume {resume_id}: {str(e)}")
            self.session.rollback()
            return False

    def search_resumes(self, criteria: Dict[str, Any]) -> List[Dict]:
        try:
            query = self.session.query(Resume)
            
            if 'university' in criteria:
                query = query.filter(Resume.university.ilike(f"%{criteria['university']}%"))
            if 'speciality' in criteria:
                query = query.filter(Resume.speciality.ilike(f"%{criteria['speciality']}%"))
            if 'min_education_score' in criteria:
                query = query.filter(Resume.education_score >= criteria['min_education_score'])
            if 'min_experience_years' in criteria:
                query = query.filter(Resume.experience_years >= criteria['min_experience_years'])
            if 'min_total_score' in criteria:
                query = query.filter(Resume.total_score >= criteria['min_total_score'])
            
            resumes = query.all()
            return [{
                'id': r.id,
                'filename': r.filename,
                'university': r.university,
                'speciality': r.speciality,
                'graduation_year': r.graduation_year,
                'education_score': r.education_score,
                'experience_years': r.experience_years,
                'total_score': r.total_score,
                'upload_date': r.upload_date.isoformat(),
                'last_modified': r.last_modified.isoformat()
            } for r in resumes]
        except Exception as e:
            logger.error(f"Error searching resumes: {str(e)}")
            return []

    def __del__(self):
        try:
            self.session.close()
            logger.info("Database connection closed")
        except:
            pass
