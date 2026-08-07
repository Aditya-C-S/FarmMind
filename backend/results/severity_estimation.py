import cv2
import numpy as np

def estimate_severity_final_v3(image_path, model, conf_threshold=0.25):
    """
    Final severity estimation v3:
    1. Color Analysis (HSV) — yellowing/browning
    2. Shape Analysis (Contour on leaf mask) — leaf curling
    3. Color override — if yellowing > 55%, force Severe
    
    Final Score = 0.6 × Color + 0.4 × Curl (TYLCV)
                = 0.85 × Color + 0.15 × Curl (Sheath Blight)
    
    Override: color_score > 55% → Severe regardless of curl
    
    Severity Levels (ICAR based):
    - Healthy  : no disease detected
    - Mild     : final score < 15
    - Moderate : final score 15-40
    - Severe   : final score > 40 OR color > 55%
    """

    image_bgr = cv2.imread(image_path)
    if image_bgr is None:
        return None

    image_height, image_width = image_bgr.shape[:2]
    results = model(image_path, conf=conf_threshold, verbose=False)
    detections = results[0].boxes

    if detections is None or len(detections) == 0:
        return {
            'disease': None,
            'severity': 'Healthy',
            'severity_score': 0,
            'color_score': 0.0,
            'curl_score': 0.0,
            'final_score': 0.0,
            'num_detections': 0,
            'confidence': 0.0,
            'message': 'No disease detected'
        }

    total_pixels = 0
    diseased_pixels = 0
    curl_scores = []
    confidences = []
    detected_classes = []

    for box in detections:
        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
        x1 = max(0, x1); y1 = max(0, y1)
        x2 = min(image_width, x2); y2 = min(image_height, y2)

        crop = image_bgr[y1:y2, x1:x2]
        if crop.size == 0:
            continue

        class_idx = int(box.cls[0])
        hsv_crop = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)

        # ── COLOR ANALYSIS ──
        if class_idx == 0:  # TYLCV
            lower = np.array([15, 60, 80])
            upper = np.array([40, 255, 255])
        else:  # Sheath Blight
            lower = np.array([10, 40, 60])
            upper = np.array([25, 255, 255])

        color_mask = cv2.inRange(hsv_crop, lower, upper)
        total_pixels += crop.shape[0] * crop.shape[1]
        diseased_pixels += cv2.countNonZero(color_mask)

        # ── CURL ANALYSIS — leaf mask only ──
        green_lower = np.array([25, 20, 20])
        green_upper = np.array([95, 255, 255])
        leaf_mask = cv2.inRange(hsv_crop, green_lower, green_upper)

        if class_idx == 0:
            yellow_lower = np.array([15, 30, 80])
            yellow_upper = np.array([45, 255, 255])
            yellow_mask = cv2.inRange(hsv_crop, yellow_lower, yellow_upper)
            leaf_mask = cv2.bitwise_or(leaf_mask, yellow_mask)

        kernel = np.ones((5, 5), np.uint8)
        leaf_mask = cv2.morphologyEx(leaf_mask, cv2.MORPH_CLOSE, kernel)
        leaf_mask = cv2.morphologyEx(leaf_mask, cv2.MORPH_OPEN, kernel)

        contours, _ = cv2.findContours(
            leaf_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        if contours:
            largest = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(largest)
            perimeter = cv2.arcLength(largest, True)

            if perimeter > 0 and area > 100:
                circularity = (4 * np.pi * area) / (perimeter ** 2)
                circularity = min(circularity, 1.0)
                curl_score = max(0, (0.75 - circularity) / 0.75) * 100
                curl_scores.append(curl_score)
            else:
                curl_scores.append(0)
        else:
            curl_scores.append(0)

        confidences.append(float(box.conf[0]))
        detected_classes.append(class_idx)

    # ── COMBINE SCORES ──
    color_score = (diseased_pixels / total_pixels * 100) if total_pixels > 0 else 0
    avg_curl_score = sum(curl_scores) / len(curl_scores) if curl_scores else 0

    most_common_class = max(set(detected_classes), key=detected_classes.count)
    disease_name = model.names[most_common_class]
    avg_confidence = sum(confidences) / len(confidences)

    if disease_name == 'TYLCV':
        final_score = 0.6 * color_score + 0.4 * avg_curl_score
    else: # Sheath Blight — no curl, color only
        final_score = color_score

    # ── COLOR OVERRIDE ──
    # Extreme yellowing alone = Severe regardless of curl
    if color_score > 55:
        final_score = max(final_score, 41)

    # Severity classification
    if final_score < 15:
        severity = 'Mild'
        severity_score = 1
    elif final_score < 40:
        severity = 'Moderate'
        severity_score = 2
    else:
        severity = 'Severe'
        severity_score = 3

    return {
        'disease': disease_name,
        'severity': severity,
        'severity_score': severity_score,
        'color_score': round(color_score, 2),
        'curl_score': round(avg_curl_score, 2),
        'final_score': round(final_score, 2),
        'num_detections': len(detections),
        'confidence': round(avg_confidence, 3),
        'message': f'{disease_name} detected — {severity} severity (color: {color_score:.1f}%, curl: {avg_curl_score:.1f}%)'
    }
