from app.analysis.technical_analyzer import TechnicalAnalyzer


class TechnicalSignalTool:

    requirement = "technical_signal"

    def execute(self, params):

        technical = params["technical"]

        analyzer = TechnicalAnalyzer()

        result = analyzer.analyze(technical)

        return {
            "status": "success",
            "data": result.model_dump()
        }