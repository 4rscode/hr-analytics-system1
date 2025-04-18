class Requirement:
    def __init__(self, role, competencies):
        self.role = role
        self.competencies = competencies

    def add_competency(self, competency):
        self.competencies.append(competency)

    def remove_competency(self, competency):
        self.competencies.remove(competency)

    def get_requirements(self):
        return {
            "role": self.role,
            "competencies": self.competencies
        }