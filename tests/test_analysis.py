import unittest
from src.analysis.competency_analyzer import CompetencyAnalyzer
from src.analysis.market_analyzer import MarketAnalyzer

class TestCompetencyAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = CompetencyAnalyzer()

    def test_analyze_competencies(self):
        # Пример теста для анализа компетенций
        result = self.analyzer.analyze_competencies(candidate_data)
        self.assertEqual(result, expected_result)

class TestMarketAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = MarketAnalyzer()

    def test_analyze_market_demand(self):
        # Пример теста для анализа рыночного спроса
        result = self.analyzer.analyze_market_demand(candidate_skills)
        self.assertEqual(result, expected_market_insights)

if __name__ == '__main__':
    unittest.main()