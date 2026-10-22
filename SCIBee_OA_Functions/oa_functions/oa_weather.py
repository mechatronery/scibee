import requests
from collections import defaultdict
from datetime import datetime
import statistics
import math


def weather_now(base_url: str, jwt_token_access: str, lat: float, lon: float) -> dict:
    result = {}
    try:
        r = requests.get(
            url=f"{base_url.rstrip('/')}/api/data/weather/?lat={lat}&lon={lon}",
            headers={"Authorization": f"Bearer {jwt_token_access}"},
            timeout=10,
        )
        r.raise_for_status()
        data = r.json()

        data_point = data.get("data")
        if not data_point:
            raise RuntimeError(f"Weather API returned invalid data: {data}")

        grouped = defaultdict(lambda: {"values": [], "timestamps": []})

        timestamp = data_point.get("dt")
        iso_time = (
            datetime.utcfromtimestamp(timestamp).isoformat() + "Z" if timestamp else None
        )

        main = data_point.get("main", {})
        mapping = {
            "temp": "ambient_temperature",
            "pressure": "pressure",
            "humidity": "humidity",
        }
        for key, new_key in mapping.items():
            if key in main:
                grouped[new_key]["values"].append(main[key])
                grouped[new_key]["timestamps"].append(iso_time)

        wind = data_point.get("wind", {})
        if "speed" in wind:
            grouped["wind_speed"]["values"].append(wind["speed"])
            grouped["wind_speed"]["timestamps"].append(iso_time)

        weather_list = data_point.get("weather", [])
        if weather_list and "description" in weather_list[0]:
            grouped["weather_description"]["values"].append(weather_list[0]["description"])
            grouped["weather_description"]["timestamps"].append(iso_time)

        result = dict(grouped)
    except Exception:
        pass

    return result


def weather_forecast(
    base_url: str, jwt_token_access: str, lat: float, lon: float
) -> dict:
    result = {}
    try:
        r = requests.get(
            url=f"{base_url.rstrip('/')}/api/data/forecast5?lat={lat}&lon={lon}",
            headers={"Authorization": f"Bearer {jwt_token_access}"},
            timeout=10,
        )
        r.raise_for_status()
        data = r.json()
        if not len(data) > 0:
            raise RuntimeError("Weather failed")

        grouped = defaultdict(lambda: {"values": [], "timestamps": []})

        for item in data:
            measurement_type = item.get("measurement_type")
            if measurement_type:
                grouped[measurement_type]["values"].append(item.get("value"))
                grouped[measurement_type]["timestamps"].append(item.get("timestamp"))

        result = dict(grouped)
    except Exception:
        pass

    return result


# =========================================================
# FORECAST NORMALIZATION
# =========================================================
FORECAST_UNITS = {
    "temperature": "°C",
    "humidity": "%",
    "wind_speed": "m/s",
    "rain_mm": "mm/3h",
}

VARIABLE_MAPPING = {
    "ambient_temperature": "temperature",
    "ambient_humidity": "humidity",
    "wind_speed": "wind_speed",
    "precipitation": "rain_mm",
}


def normalize_forecast(weather_data):
    """Convert API weather format into the internal forecast format."""
    series = [
        weather_data[source]["values"]
        for source in VARIABLE_MAPPING
    ]

    return [
        {
            target: value
            for (source, target), value in zip(VARIABLE_MAPPING.items(), values)
        }
        for values in zip(*series)
    ]


# =========================================================
# ANALYSIS
# =========================================================
def analyze_forecast(forecast, variable):
    """Return summary statistics for a forecast variable."""
    values = [
        x[variable]
        for x in forecast
        if variable in x
    ]

    if not values:
        return {}

    sorted_values = sorted(values)
    n = max(1, math.ceil(len(values) * 0.25))

    low = sorted_values[:n]
    high = sorted_values[-n:]

    return {
        "count": len(values),
        "min": sorted_values[0],
        "max": sorted_values[-1],
        "range": sorted_values[-1] - sorted_values[0],
        "mean": statistics.mean(values),
        "low_mean": statistics.mean(low),
        "high_mean": statistics.mean(high),
        "total": sum(values),
    }


def analyze_forecast_all(forecast):
    """Return summary statistics for all forecast variables."""
    if not forecast:
        return {}

    return {
        variable: analyze_forecast(forecast, variable)
        for variable in forecast[0]
    }


# =========================================================
# GOOD BEEKEEPING WEATHER FORECAST
# =========================================================
GOOD_BEEKEEPING_WEATHER = {
    "temperature": {
        # Average conditions during forecast period
        "mean": {"min": 15, "max": 28},
        # Night / early morning temperatures
        "low_mean": {"min": 10},
        # Main foraging periods
        "high_mean": {"min": 18, "max": 32},
        # Absolute limits
        "min": {"min": 8},
        "max": {"max": 35},
        # Avoid large temperature swings
        "range": {"max": 15},
    },
    "humidity": {
        # Bees tolerate a wide range, but moderate humidity
        # is better for flight
        "mean": {"min": 40, "max": 85},
        # Very high humidity often means poor flying
        "max": {"max": 95},
    },
    "wind_speed": {
        # m/s
        # Ideal average wind for foraging
        "mean": {"max": 3},
        # Short periods of higher wind acceptable
        "high_mean": {"max": 5},
        # Strong wind reduces bee flight
        "max": {"max": 7},
    },
    "rain_mm": {
        # OpenWeather precipitation values
        # are mm per forecast interval
        "mean": {"max": 0.5},
        "high_mean": {"max": 2},
        "max": {"max": 5},
        # Total forecast rainfall
        "total": {"max": 15},
    },
    # Conditions specifically related to bee activity
    "flying": {
        # Minimum temperature for active flight
        "temperature_min": 15,
        # Bees avoid strong wind
        "wind_max": 5,
        # No significant rain during flight
        "rain_max": 0,
        # Percentage of forecast periods suitable
        "min_ratio": 0.5,
    },
}

GOOD_BEEKEEPING_WEATHER_WEIGHTS = {
    "temperature_mean": 15,
    "temperature_low_mean": 5,
    "temperature_high_mean": 10,
    "temperature_min": 5,
    "temperature_max": 5,
    "temperature_range": 5,

    "humidity_mean": 10,
    "humidity_max": 5,

    # Wind is more important for bee activity
    "wind_mean": 15,
    "wind_high_mean": 5,
    "wind_max": 5,

    "rain_mean": 5,
    "rain_high_mean": 5,
    "rain_max": 5,
    "rain_total": 5,

    "good_flying_conditions": 10,
}


def interpret_beekeeping_weather_score(score):
    """
    Convert weather score into beekeeper-friendly interpretation.
    """
    if score >= 85:
        return "Excellent bee weather"

    if score >= 70:
        return "Acceptable for normal activity"

    if score >= 50:
        return "Limited bee activity"

    return "Poor conditions"


def is_good_for_beekeeping(
    forecast,
    parameters=None,
    weights=None
):
    """
    Evaluate whether the forecast provides generally good
    weather conditions for beekeeping.
    """
    if parameters is None:
        parameters = GOOD_BEEKEEPING_WEATHER

    if weights is None:
        weights = GOOD_BEEKEEPING_WEATHER_WEIGHTS

    if not forecast:
        return {
            "interpretation": "Poor conditions",
            "score": 0,
            "checks": {},
            "metrics": {},
        }

    metrics = analyze_forecast_all(forecast)

    # -----------------------------------------------------
    # Bee flying conditions
    # -----------------------------------------------------
    good_flying_periods = [
        x for x in forecast
        if (
            x["temperature"]
            >= parameters["flying"]["temperature_min"]
            and x["wind_speed"]
            <= parameters["flying"]["wind_max"]
            and x["rain_mm"]
            <= parameters["flying"]["rain_max"]
        )
    ]

    flying_ratio = (
        len(good_flying_periods) / len(forecast)
    )

    metrics["good_flying_periods"] = len(good_flying_periods)
    metrics["flying_ratio"] = flying_ratio

    # -----------------------------------------------------
    # Weather checks
    # -----------------------------------------------------
    checks = {
        # Temperature
        "temperature_mean":
            parameters["temperature"]["mean"]["min"] <= metrics["temperature"]["mean"] <= parameters["temperature"]["mean"]["max"],
        "temperature_low_mean":
            metrics["temperature"]["low_mean"] >= parameters["temperature"]["low_mean"]["min"],
        "temperature_high_mean":
            parameters["temperature"]["high_mean"]["min"] <= metrics["temperature"]["high_mean"] <= parameters["temperature"]["high_mean"]["max"],
        "temperature_min":
            metrics["temperature"]["min"] >= parameters["temperature"]["min"]["min"],
        "temperature_max":
            metrics["temperature"]["max"] <= parameters["temperature"]["max"]["max"],
        "temperature_range":
            metrics["temperature"]["range"] <= parameters["temperature"]["range"]["max"],
        # Humidity
        "humidity_mean":
            parameters["humidity"]["mean"]["min"] <= metrics["humidity"]["mean"] <= parameters["humidity"]["mean"]["max"],
        "humidity_max":
            metrics["humidity"]["max"] <= parameters["humidity"]["max"]["max"],
        # Wind
        "wind_mean":
            metrics["wind_speed"]["mean"] <= parameters["wind_speed"]["mean"]["max"],
        "wind_high_mean":
            metrics["wind_speed"]["high_mean"] <= parameters["wind_speed"]["high_mean"]["max"],
        "wind_max":
            metrics["wind_speed"]["max"] <= parameters["wind_speed"]["max"]["max"],
        # Rain
        "rain_mean":
            metrics["rain_mm"]["mean"] <= parameters["rain_mm"]["mean"]["max"],
        "rain_high_mean":
            metrics["rain_mm"]["high_mean"] <= parameters["rain_mm"]["high_mean"]["max"],
        "rain_max":
            metrics["rain_mm"]["max"] <= parameters["rain_mm"]["max"]["max"],
        "rain_total":
            metrics["rain_mm"]["total"] <= parameters["rain_mm"]["total"]["max"],
        # Bee activity
        "good_flying_conditions":
            flying_ratio >= parameters["flying"]["min_ratio"],
    }

    # -----------------------------------------------------
    # Calculate normalized score
    # -----------------------------------------------------
    score = sum(
        weights.get(key, 0)
        for key, passed in checks.items()
        if passed
    )

    max_score = sum(
        weights.get(key, 0)
        for key in checks
    )

    percentage = (
        score / max_score * 100
        if max_score
        else 0
    )

    return {
        "interpretation": interpret_beekeeping_weather_score(percentage),
        "score": round(percentage, 1),
        "checks": checks,
        "metrics": metrics,
    }


# =========================================================
# FORMIC ACID VARROA TREATMENT WEATHER FORECAST
# =========================================================
FORMIC_ACID_TREATMENT_WEATHER = {
    "temperature": {
        # Average temperature during treatment period
        # Formic acid evaporation works best in moderate warmth
        "mean": {"min": 15, "max": 25},
        # Overnight temperatures
        # Too cold reduces evaporation efficiency
        "low_mean": {"min": 12},
        # Daytime evaporation conditions
        "high_mean": {"min": 18, "max": 30},
        # Absolute lower limit
        "min": {"min": 10},
        # Avoid excessive evaporation and colony stress
        "max": {"max": 32},
        # Stable temperatures are important for controlled evaporation
        "range": {"max": 10},
    },
    "humidity": {
        # High humidity slows formic acid evaporation
        "mean": {"min": 40, "max": 75},
        # Very humid periods reduce treatment efficiency
        "max": {"max": 90},
    },
    "wind_speed": {
        # Wind in m/s
        # Low wind helps maintain stable hive conditions
        # Preferred average wind
        "mean": {"max": 3},
        # Occasional stronger wind periods acceptable
        "high_mean": {"max": 5},
        # Avoid treatment during strong wind
        "max": {"max": 7},
    },
    "rain_mm": {
        # Rain indicates unstable conditions
        "mean": {"max": 1},
        # Short rain events
        "high_mean": {"max": 3},
        # Heavy rain event
        "max": {"max": 5},
        # Total precipitation during forecast period
        "total": {"max": 15},
    },
    # Specific evaporation and application conditions
    "treatment": {
        # Percentage of forecast periods that should
        # have acceptable treatment conditions
        "min_stable_period_ratio": 0.7,
        # Safe evaporation temperature window
        "temperature_min": 15,
        "temperature_max": 28,
        # Humidity limit
        "humidity_max": 80,
        # Wind limit during suitable periods
        "wind_max": 4,
        # No rain during application period
        "rain_max": 0,
    },
    "min_score": 75,
}

# =========================================================
# WEIGHTS
# =========================================================

FORMIC_ACID_TREATMENT_WEATHER_WEIGHTS = {
    # Temperature is the most important factor
    "temperature_mean": 15,
    "temperature_low_mean": 10,
    "temperature_high_mean": 15,
    "temperature_min": 5,
    "temperature_max": 5,
    # Stable temperature affects evaporation consistency
    "temperature_range": 10,
    # Humidity directly affects evaporation
    "humidity_mean": 10,
    "humidity_max": 5,
    # Wind affects hive stability and application conditions
    "wind_mean": 10,
    "wind_high_mean": 5,
    "wind_max": 5,
    # Rain indicates unstable weather
    "rain_mean": 5,
    "rain_high_mean": 3,
    "rain_max": 2,
    "rain_total": 5,
    # Most important practical indicator
    "stable_evaporation_conditions": 15,
}


def interpret_formic_acid_treatment_score(score):
    """
    Convert score into treatment recommendation.
    """
    if score >= 85:
        return "Excellent conditions for formic acid treatment"
    if score >= 70:
        return "Suitable conditions for formic acid treatment"
    if score >= 50:
        return "Marginal conditions - monitor evaporation carefully"
    return "Poor conditions for formic acid treatment"


def is_suitable_for_formic_acid_treatment(
    forecast,
    parameters=None,
    weights=None
):
    """
    Evaluate forecast suitability for Varroa treatment
    using formic acid evaporation.
    """
    if parameters is None:
        parameters = FORMIC_ACID_TREATMENT_WEATHER

    if weights is None:
        weights = FORMIC_ACID_TREATMENT_WEATHER_WEIGHTS

    if not forecast:
        return {
            "interpretation": "Poor conditions for formic acid treatment",
            "score": 0,
            "checks": {},
            "metrics": {},
        }
    metrics = analyze_forecast_all(forecast)

    # -----------------------------------------------------
    # Stable evaporation periods
    # -----------------------------------------------------
    stable_periods = [
        x for x in forecast
        if (
            parameters["treatment"]["temperature_min"]
            <= x["temperature"]
            <= parameters["treatment"]["temperature_max"]

            and x["humidity"]
            <= parameters["treatment"]["humidity_max"]

            and x["wind_speed"]
            <= parameters["treatment"]["wind_max"]

            and x["rain_mm"]
            <= parameters["treatment"]["rain_max"]
        )
    ]

    stable_ratio = (
        len(stable_periods) / len(forecast)
    )

    metrics["stable_evaporation_periods"] = len(stable_periods)
    metrics["stable_evaporation_ratio"] = stable_ratio

    # -----------------------------------------------------
    # Checks
    # -----------------------------------------------------
    checks = {
        # Temperature
        "temperature_mean":
            parameters["temperature"]["mean"]["min"] <= metrics["temperature"]["mean"] <= parameters["temperature"]["mean"]["max"],
        "temperature_low_mean":
            metrics["temperature"]["low_mean"] >= parameters["temperature"]["low_mean"]["min"],
        "temperature_high_mean":
            parameters["temperature"]["high_mean"]["min"] <= metrics["temperature"]["high_mean"] <= parameters["temperature"]["high_mean"]["max"],
        "temperature_min":
            metrics["temperature"]["min"] >= parameters["temperature"]["min"]["min"],
        "temperature_max":
            metrics["temperature"]["max"] <= parameters["temperature"]["max"]["max"],
        "temperature_range":
            metrics["temperature"]["range"] <= parameters["temperature"]["range"]["max"],
        # Humidity
        "humidity_mean":
            parameters["humidity"]["mean"]["min"] <= metrics["humidity"]["mean"] <= parameters["humidity"]["mean"]["max"],
        "humidity_max":
            metrics["humidity"]["max"] <= parameters["humidity"]["max"]["max"],
        # Wind
        "wind_mean":
            metrics["wind_speed"]["mean"] <= parameters["wind_speed"]["mean"]["max"],
        "wind_max":
            metrics["wind_speed"]["max"] <= parameters["wind_speed"]["max"]["max"],
        # Rain
        "rain_mean":
            metrics["rain_mm"]["mean"] <= parameters["rain_mm"]["mean"]["max"],
        "rain_total":
            metrics["rain_mm"]["total"] <= parameters["rain_mm"]["total"]["max"],
        # Evaporation conditions
        "stable_evaporation_conditions":
            stable_ratio >= parameters["treatment"]["min_stable_period_ratio"],
    }

    score = sum(
        weights.get(key, 0)
        for key, passed in checks.items()
        if passed
    )

    max_score = sum(
        weights.get(key, 0)
        for key in checks
    )

    percentage = (
        score / max_score * 100
        if max_score
        else 0
    )

    return {
        "interpretation": interpret_formic_acid_treatment_score(percentage),
        "score": round(percentage, 1),
        "checks": checks,
        "metrics": metrics,
    }


if __name__ == "__main__":
    pass
