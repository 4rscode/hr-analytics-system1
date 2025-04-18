import os
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class DataLoader:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            logger.info(f"Created data directory: {data_dir}")

    def save_resume_data(self, resume_id: str, data: Dict[str, Any]) -> bool:
        try:
            file_path = os.path.join(self.data_dir, f"{resume_id}.json")
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"Successfully saved resume data for ID: {resume_id}")
            return True
        except Exception as e:
            logger.error(f"Error saving resume data for ID {resume_id}: {str(e)}")
            return False

    def load_resume_data(self, resume_id: str) -> Optional[Dict[str, Any]]:
        try:
            file_path = os.path.join(self.data_dir, f"{resume_id}.json")
            if not os.path.exists(file_path):
                logger.warning(f"Resume data not found for ID: {resume_id}")
                return None
                
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"Successfully loaded resume data for ID: {resume_id}")
            return data
        except Exception as e:
            logger.error(f"Error loading resume data for ID {resume_id}: {str(e)}")
            return None

    def list_resumes(self) -> list:
        try:
            files = [f for f in os.listdir(self.data_dir) if f.endswith('.json')]
            resume_ids = [os.path.splitext(f)[0] for f in files]
            return resume_ids
        except Exception as e:
            logger.error(f"Error listing resumes: {str(e)}")
            return []

    def delete_resume(self, resume_id: str) -> bool:
        try:
            file_path = os.path.join(self.data_dir, f"{resume_id}.json")
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Successfully deleted resume data for ID: {resume_id}")
                return True
            else:
                logger.warning(f"Resume data not found for deletion: {resume_id}")
                return False
        except Exception as e:
            logger.error(f"Error deleting resume data for ID {resume_id}: {str(e)}")
            return False

    def load_data(self):
        # Здесь будет логика загрузки данных из файловой системы
        pass

    def parse_resume(self, resume_content):
        # Здесь будет логика парсинга резюме
        pass