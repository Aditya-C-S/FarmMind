from app.knowledge.disease_prevention import DISEASE_PREVENTION

class WeatherIntelligenceService:

    @staticmethod
    def irrigation_advice(crop_type: str, forecast):

        today = forecast[0]

        rainfall = today["rainfall"]
        humidity = today["humidity"]
        temp = today["temperature_max"]

        crop = crop_type.lower()

        if crop == "rice":

            if rainfall >= 10:
                return {
                    "level": "Skip Irrigation",
                    "status": "Good",
                    "reason": "Heavy rainfall expected."
                }

            if rainfall >= 3:
                return {
                    "level": "Reduce Irrigation",
                    "status": "Moderate",
                    "reason": "Rainfall will provide partial water."
                }

            return {
                "level": "Normal Irrigation",
                "status": "Required",
                "reason": "Low rainfall expected."
            }

        elif crop == "tomato":

            if rainfall >= 10:
                return {
                    "level": "Skip Irrigation",
                    "status": "Good",
                    "reason": "Soil moisture will remain high."
                }

            if temp > 32 and humidity < 60:
                return {
                    "level": "Increase Irrigation",
                    "status": "Attention",
                    "reason": "Hot and dry weather expected."
                }

            return {
                "level": "Normal Irrigation",
                "status": "Required",
                "reason": "Weather conditions are suitable."
            }

        return {
            "level": "Unavailable",
            "status": "Unknown",
            "reason": "Unsupported crop."
        }
    
    @staticmethod
    def disease_prevention(crop_type: str, forecast):

        crop = crop_type.lower()

        if crop not in DISEASE_PREVENTION:
            return []

        today = forecast[0]

        humidity = today["humidity"]
        rainfall = today["rainfall"]
        temperature = today["temperature_max"]

        alerts = []
        for disease in DISEASE_PREVENTION[crop]:
            condition = disease["condition"]
            triggered = False
            if "humidity" in condition:
                triggered = humidity >= condition["humidity"]

            elif "rainfall" in condition:
                triggered = rainfall >= condition["rainfall"]

            elif "temperature" in condition:
                triggered = temperature >= condition["temperature"]

            if triggered:
                alerts.append({
                    "disease": disease["disease"],
                    "risk": disease["risk"],
                    "reason": disease["reason"],
                    "recommendations": disease["recommendations"]
                })

        return alerts