import cv2
import numpy as np
import joblib
import pandas as pd
from ultralytics import YOLO
from xgboost import XGBRegressor
from app.knowledge.treatments import TREATMENTS

# ─── PATHS ───────────────────────────────────────────────────────────────────
BASE = "results"
YOLO_MODEL = f"{BASE}/best_yolo11s_final.pt"

OCC  = f"{BASE}/occurrence"
PROG = f"{BASE}/progression"
ECON = f"{BASE}/economic loss"

# ─── LOAD ALL MODELS ONCE AT STARTUP ─────────────────────────────────────────
print("Loading models...")

yolo = YOLO(YOLO_MODEL)

occ_models = {
    "TYLCV":         joblib.load(f"{OCC}/tylcv_rf_model.pkl"),
    "Sheath_Blight": joblib.load(f"{OCC}/sheath_blight_rf_model.pkl"),
}
occ_encoders = {
    "TYLCV": {
        "stage":  joblib.load(f"{OCC}/tylcv_stage_encoder.pkl"),
        "season": joblib.load(f"{OCC}/tylcv_season_encoder.pkl")
    },
    "Sheath_Blight": {
        "stage":  joblib.load(f"{OCC}/sheath_blight_stage_encoder.pkl"),
        "season": joblib.load(f"{OCC}/sheath_blight_season_encoder.pkl")
    },
}

prog_models = {
    "TYLCV":         joblib.load(f"{PROG}/tylcv_progression_model.pkl"),
    "Sheath_Blight": joblib.load(f"{PROG}/sheath_blight_progression_model.pkl"),
}
prog_encoders = {
    "TYLCV":         joblib.load(f"{PROG}/tylcv_progression_encoder.pkl"),
    "Sheath_Blight": joblib.load(f"{PROG}/sheath_blight_progression_encoder.pkl"),
}

econ_model = XGBRegressor()
econ_model.load_model(f"{ECON}/economic_loss_xgb_model.json")
econ_encoders = {
    "crop":              joblib.load(f"{ECON}/crop_encoder.pkl"),
    "disease":           joblib.load(f"{ECON}/disease_encoder.pkl"),
    "severity_class":    joblib.load(f"{ECON}/severity_class_encoder.pkl"),
    "progression_trend": joblib.load(f"{ECON}/progression_trend_encoder.pkl"),
    "crop_stage":        joblib.load(f"{ECON}/crop_stage_encoder.pkl"),
}

CLASS_NAMES = {0: "TYLCV", 1: "Sheath_Blight"}
CROP_MAP    = {"TYLCV": "Tomato", "Sheath_Blight": "Rice"}

# Stage options per crop (exactly as encoder knows them)
TOMATO_STAGES = ["flowering", "fruiting", "harvest", "seedling", "vegetative"]
RICE_STAGES   = ["booting", "heading", "maturity", "seedling", "tillering"]
SEASONS       = ["kharif", "rabi", "summer", "winter"]

print("All models loaded.\n")

# ─── SEVERITY ESTIMATION ──────────────────────────────────────────────────────
def estimate_severity(image_bgr, box, disease):
    x1, y1, x2, y2 = map(int, box)
    crop_img = image_bgr[y1:y2, x1:x2]
    if crop_img.size == 0:
        return 0.0, "Healthy"

    hsv = cv2.cvtColor(crop_img, cv2.COLOR_BGR2HSV)

    if disease == "TYLCV":
        color_mask = cv2.inRange(hsv,
            np.array([15, 60, 80]), np.array([40, 255, 255]))
        green_mask = cv2.inRange(hsv,
            np.array([35, 40, 40]), np.array([85, 255, 255]))
        total = np.sum(green_mask > 0) + np.sum(color_mask > 0)
        color_score = (np.sum(color_mask > 0) / total * 100) if total > 0 else 0

        gray = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        curl_score = 0
        if contours:
            c = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(c)
            peri = cv2.arcLength(c, True)
            if peri > 0:
                circ = 4 * np.pi * area / (peri ** 2)
                curl_score = max(0, (0.7 - circ) / 0.5 * 100)
                curl_score = min(curl_score, 100)

        final = 0.6 * color_score + 0.4 * curl_score
        if color_score > 55:
            final = max(final, 40.1)

    else:  # Sheath_Blight
        brown_mask = cv2.inRange(hsv,
            np.array([10, 40, 60]), np.array([25, 255, 255]))
        total_pixels = crop_img.shape[0] * crop_img.shape[1]
        final = (np.sum(brown_mask > 0) / total_pixels * 100) if total_pixels > 0 else 0

    if final < 20:
        label = "Mild"
    elif final < 45:
        label = "Moderate"
    else:
        label = "Severe"

    return round(final, 2), label

# ─── OCCURRENCE PREDICTION ────────────────────────────────────────────────────
def predict_occurrence(disease, temperature, humidity, rainfall,
                        wind_speed, crop_stage, season):
    enc = occ_encoders[disease]
    # Always lowercase before encoding
    stage_enc  = enc["stage"].transform([crop_stage.lower()])[0]
    season_enc = enc["season"].transform([season.lower()])[0]
    X = pd.DataFrame([{
        "temperature": temperature,
        "humidity":    humidity,
        "rainfall":    rainfall,
        "wind_speed":  wind_speed,
        "crop_stage":  stage_enc,
        "season":      season_enc
    }])
    prob = occ_models[disease].predict_proba(X)[0][1]
    return round(prob * 100, 1)

# ─── PROGRESSION PREDICTION ───────────────────────────────────────────────────
SEASON_MAP = {"kharif": 0, "rabi": 1, "summer": 2, "winter": 3}

def predict_progression(disease, severity_score, season, weather_5day):
    season_enc = SEASON_MAP.get(season.lower(), 0)
    row = {"initial_severity": severity_score}
    for i, w in enumerate(weather_5day, 1):
        row[f"day{i}_temp"]     = w["temp"]
        row[f"day{i}_humidity"] = w["humidity"]
        row[f"day{i}_rainfall"] = w["rainfall"]
    row["season"] = season_enc
    X = pd.DataFrame([row])
    pred_encoded = prog_models[disease].predict(X)[0]
    pred_label = prog_encoders[disease].inverse_transform([pred_encoded])[0]
    return pred_label
 # "Worsening" / "Stable" / "Improving"

# ─── ECONOMIC LOSS DELTA ──────────────────────────────────────────────────────
def predict_loss_delta(disease, severity_score, severity_class,
                        progression_trend, market_price,
                        farm_area, expected_yield, crop_stage,
                        delay_days_target=7):
    crop = CROP_MAP[disease]
    feature_cols = [
        "severity_score", "delay_days", "market_price", "farm_area",
        "expected_yield", "crop_enc", "disease_enc",
        "severity_class_enc", "progression_trend_enc", "crop_stage_enc"
    ]

    def make_row(delay):
        return pd.DataFrame([{
            "severity_score":         severity_score,
            "delay_days":             delay,
            "market_price":           market_price,
            "farm_area":              farm_area,
            "expected_yield":         expected_yield,
            "crop_enc":               econ_encoders["crop"].transform([crop])[0],
            "disease_enc":            econ_encoders["disease"].transform([disease])[0],
            "severity_class_enc":     econ_encoders["severity_class"].transform([severity_class])[0],
            "progression_trend_enc": econ_encoders["progression_trend"].transform([progression_trend.title()])[0],
            "crop_stage_enc": econ_encoders["crop_stage"].transform([crop_stage.title()])[0],
        }])[feature_cols]

    loss_now     = float(econ_model.predict(make_row(0))[0])
    loss_delayed = float(econ_model.predict(make_row(delay_days_target))[0])
    return {
        "loss_if_act_now":       round(loss_now, 2),
        "loss_if_delayed":       round(loss_delayed, 2),
        "delay_days":            delay_days_target,
        "extra_loss_from_delay": round(loss_delayed - loss_now, 2)
    }

# ─── MASTER PIPELINE ──────────────────────────────────────────────────────────
print("===== RUN PIPELINE CALLED =====")
def run_pipeline(image_path,
                 temperature=28, humidity=75, rainfall=5,
                 wind_speed=10, crop_stage="flowering", season="kharif",
                 market_price=30, farm_area=2, expected_yield=5000,
                 delay_days=7, weather_5day=None):

    if weather_5day is None:
        weather_5day = [{"temp": temperature, "humidity": humidity,
                          "rainfall": rainfall}] * 5

    # 1. Load image
    image = cv2.imread(image_path)
    if image is None:
        return {"error": f"Could not load image: {image_path}"}

    # 2. YOLO detection
    results_yolo = yolo(image, verbose=False)
    boxes = results_yolo[0].boxes

    if boxes is None or len(boxes) == 0:
        return {"error": "No disease detected in image."}

    # Pick highest confidence detection
    best_idx  = int(boxes.conf.argmax())
    best_box  = boxes.xyxy[best_idx].cpu().numpy()
    best_cls  = int(boxes.cls[best_idx].item())
    best_conf = float(boxes.conf[best_idx].item())
    disease   = CLASS_NAMES[best_cls]
    crop      = CROP_MAP[disease]

    # 3. Severity estimation
    severity_score, severity_class = estimate_severity(image, best_box, disease)

    # 4. Occurrence prediction — use crop-appropriate default stage if mismatch
    # (UI will pass the right stage, this is a safety fallback)
    valid_stages = TOMATO_STAGES if disease == "TYLCV" else RICE_STAGES
    if crop_stage.lower() not in valid_stages:
        crop_stage = valid_stages[0]

    # Econ loss encoder uses Title Case stage names mapped to its own vocabulary
    ECON_STAGE_MAP = {
        # Tomato stages → econ encoder labels
        "flowering": "Flowering",
        "fruiting": "Fruiting/Grain-fill",
        "harvest": "Maturity",
        "seedling": "Vegetative",
        "vegetative": "Vegetative",
        # Rice stages → econ encoder labels
        "booting": "Vegetative",
        "heading": "Fruiting/Grain-fill",
        "maturity": "Maturity",
        "tillering": "Vegetative",
    }
    econ_stage = ECON_STAGE_MAP.get(crop_stage.lower(), "Flowering")

    occurrence_prob = predict_occurrence(disease, temperature, humidity,
                                          rainfall, wind_speed, crop_stage, season)

    # 5. Progression prediction
    progression = predict_progression(disease, severity_score, season, weather_5day)

    # 6. Economic loss
    econ = predict_loss_delta(disease, severity_score, severity_class,
                               progression, market_price,
                               farm_area, expected_yield, econ_stage, delay_days)

    print("Disease:", disease)
    print("Severity:", severity_class)
    
    # 7. Treatment recommendation
    treatment = (TREATMENTS.get(disease, {}).get(severity_class, None))

    print("Treatment:", treatment)

    response = {
        "crop":            crop,
        "disease":         disease,
        "confidence":      round(best_conf * 100, 1),
        "severity_score":  severity_score,
        "severity_class":  severity_class,
        "occurrence_prob": occurrence_prob,
        "progression":     progression,
        "economic_loss":   econ,
        "treatment": treatment
    }

    print("===== RETURNING RESPONSE =====")
    print(response) 

    return response
# ─── QUICK TEST ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import json
    test_image = "test.jpg"
    result = run_pipeline(test_image)
    print(json.dumps(result, indent=2))