class Competency:
    def __init__(self, name: str, required_level: int):
        self.name = name
        self.required_level = required_level

    def __repr__(self):
        return f"Competency(name={self.name}, required_level={self.required_level})"