from typing import Dict


RICE = {
    "recommended_storage": {
        "ambient": {
            "title": "Ambient Warehouse",
            "reason": (
                "Rice stores safely for long periods when grain moisture "
                "is maintained at or below 14%."
            ),
            "expected_shelf_life_days": 180,
        },
        "covered_shed": {
            "title": "Covered Shed",
            "reason": (
                "Provides protection from rain while allowing airflow."
            ),
            "expected_shelf_life_days": 150,
        },
        "cold_room": {
            "title": "Cold Storage",
            "reason": (
                "Suitable for seed rice and premium storage."
            ),
            "expected_shelf_life_days": 240,
        },
        "open": {
            "title": "Open Storage",
            "reason": (
                "Not recommended because grain is exposed to moisture, "
                "birds and insects."
            ),
            "expected_shelf_life_days": 90,
        },
    },

    "recommended_practices": [
        "Dry harvested grain until moisture ≤14%",
        "Remove broken and infected grains",
        "Clean storage area before loading",
        "Use airtight bins or bags",
        "Inspect every 2 weeks for insects",
    ],

    "before_storage_checklist": [
        "Dry grain to ≤14%",
        "Remove damaged grains",
        "Clean storage area",
        "Fill airtight containers",
        "Protect against rodents",
        "Record harvest quantity",
        "Choose storage method",
    ],
}


TOMATO = {
    "recommended_storage": {
        "cold_room": {
            "title": "Cold Storage",
            "reason": (
                "Cold storage slows ripening and greatly extends freshness."
            ),
            "expected_shelf_life_days": 28,
        },
        "ambient": {
            "title": "Ventilated Ambient Storage",
            "reason": (
                "Suitable only for short-term storage."
            ),
            "expected_shelf_life_days": 7,
        },
        "covered_shed": {
            "title": "Covered Ventilated Shed",
            "reason": (
                "Provides shade but limited shelf life."
            ),
            "expected_shelf_life_days": 10,
        },
        "open": {
            "title": "Open Storage",
            "reason": (
                "Strongly discouraged due to rapid spoilage."
            ),
            "expected_shelf_life_days": 3,
        },
    },

    "recommended_practices": [
        "Remove damaged fruits",
        "Sort by ripeness",
        "Avoid stacking heavily",
        "Use ventilated crates",
        "Cool produce immediately after harvest",
    ],

    "before_storage_checklist": [
        "Remove damaged fruits",
        "Sort by ripeness",
        "Wash crates",
        "Use ventilated boxes",
        "Avoid direct sunlight",
        "Record harvest quantity",
        "Choose storage method",
    ],
}


def get_storage_recommendation(
    crop_type: str,
    storage_type: str = "ambient",
) -> Dict:

    crop_type = crop_type.lower()

    kb = RICE if crop_type == "rice" else TOMATO

    storage = kb["recommended_storage"].get(
        storage_type,
        kb["recommended_storage"]["ambient"],
    )

    return {
        "recommended_storage": storage["title"],
        "reason": storage["reason"],
        "expected_shelf_life_days": storage["expected_shelf_life_days"],
        "recommended_practices": kb["recommended_practices"],
        "before_storage_checklist": kb["before_storage_checklist"],
    }