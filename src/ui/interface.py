# filepath: hr-analytics-system/src/ui/interface.py

class UserInterface:
    def __init__(self):
        self.resume_file = None

    def upload_resume(self, file_path):
        self.resume_file = file_path
        print(f"Резюме загружено: {file_path}")

    def display_analysis_results(self, results):
        print("Результаты анализа:")
        for key, value in results.items():
            print(f"{key}: {value}")