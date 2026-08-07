class RecommendationService:

    @staticmethod
    def generate_recommendations(
        crop_type: str,
        weather_data: dict,
        disease_result=None,
        crop_stage=None,
        market_data=None,
        farm_memory=None
    ):
        recommendations = []
        # Weather recommendations
        recommendations.extend(
            RecommendationService._weather_recommendations(weather_data)
        )
        # Disease recommendations
        if disease_result:
            recommendations.extend(
                RecommendationService._disease_recommendations(disease_result)
            )
        # Crop stage recommendations
        if crop_stage:
            recommendations.extend(
                RecommendationService._stage_recommendations(crop_stage)
            )
        # Market recommendations
        if market_data:
            recommendations.extend(
                RecommendationService._market_recommendations(market_data)
            )
        recommendations.sort(key=lambda x: x["priority"])
        return recommendations

    @staticmethod
    def _weather_recommendations(weather):
        recommendations = []
        irrigation = weather["irrigation"]
        recommendations.append({
            "priority": 2,
            "category": "Irrigation",
            "title": irrigation["level"],
            "reason": irrigation["reason"]
        })
        for disease in weather["prevention"]:
            recommendations.append({
                "priority": 1,
                "category": "Disease Prevention",
                "title": f"Monitor for {disease['disease']}",
                "reason": disease["reason"]
            })
        return recommendations

    @staticmethod
    def _disease_recommendations(result):

        if result["severity"] == "High":
            return [
                {
                    "priority": 0,
                    "category": "Treatment",
                    "title": f"Treat {result['disease']} immediately",
                    "reason": "High severity detected from uploaded image."
                }
            ]
        return []