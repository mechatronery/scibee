import requests
from collections import defaultdict

import json
from jsonschema import validate, ValidationError

from . import oa_function

create_risk_model_schema = {
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "minLength": 1
        },
        "eppo_code": {
            "type": "string",
            "minLength": 1
        },
        "base_gdd": {
            "type": "number"
        },
        "description": {
            "type": "string"
        },
        "gdd_points": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "properties": {
                    "start": {
                        "type": "number"
                    },
                    "end": {
                        "type": "number"
                    },
                    "descriptor": {
                        "type": "string",
                        "minLength": 1
                    }
                },
                "required": ["start", "end", "descriptor"],
                "additionalProperties": False
            }
        }
    },
    "required": [
        "name",
        "eppo_code",
        "base_gdd",
        "description",
        "gdd_points"
    ],
    "additionalProperties": False
}

# =========================================================
# HONEY BEE HIVE CYCLE MODEL
# Annual GDD
# =========================================================
HONEY_BEE_HIVE_CYCLE_MODEL = {
    "name": "Honey Bee Hive Cycle",
    "eppo_code": "APISME",
    "base_gdd": 10,
    "description": (
        "Estimation of seasonal honey bee colony development from start of year."
    ),
    "gdd_points": [
        {
            "start": 0,
            "end": 80,
            "descriptor": "Winter Cluster"
        },
        {
            "start": 80,
            "end": 200,
            "descriptor": "Brood Initiation"
        },
        {
            "start": 200,
            "end": 400,
            "descriptor": "Spring Build-up"
        },
        {
            "start": 400,
            "end": 700,
            "descriptor": "Rapid Expansion"
        },
        {
            "start": 700,
            "end": 1100,
            "descriptor": "Swarm Risk Period"
        },
        {
            "start": 1100,
            "end": 1600,
            "descriptor": "Peak Colony"
        },
        {
            "start": 1600,
            "end": 2100,
            "descriptor": "Summer Production"
        },
        {
            "start": 2100,
            "end": 2600,
            "descriptor": "Late Summer"
        },
        {
            "start": 2600,
            "end": 9999,
            "descriptor": "Winter Preparation"
        }
    ]
}

# =========================================================
# HONEY BEE BLOOM AVAILABILITY MODEL
# Annual GDD
# =========================================================
HONEY_BEE_BLOOM_AVAILABILITY_MODEL = {
    "name": "Honey Bee Bloom Availability",
    "eppo_code": "APISME",
    "base_gdd": 5,
    "description": (
        "Estimation of seasonal nectar and pollen availability from start of year."
    ),
    "gdd_points": [
        {
            "start": 0,
            "end": 100,
            "descriptor": "Dormant"
        },
        {
            "start": 100,
            "end": 250,
            "descriptor": "Early Bloom"
        },
        {
            "start": 250,
            "end": 500,
            "descriptor": "Spring Bloom"
        },
        {
            "start": 500,
            "end": 800,
            "descriptor": "Main Nectar Flow"
        },
        {
            "start": 800,
            "end": 1200,
            "descriptor": "Peak Nectar Flow"
        },
        {
            "start": 1200,
            "end": 1700,
            "descriptor": "Summer Forage"
        },
        {
            "start": 1700,
            "end": 2200,
            "descriptor": "Late Summer Forage"
        },
        {
            "start": 2200,
            "end": 2700,
            "descriptor": "Declining Forage"
        },
        {
            "start": 2700,
            "end": 3200,
            "descriptor": "Autumn Forage"
        },
        {
            "start": 3200,
            "end": 9999,
            "descriptor": "Dormant Season"
        }
    ]
}

# =========================================================
# HONEY BEE BLOOM TRIGGER MODEL
# Rolling 14-day GDD
# =========================================================
HONEY_BEE_BLOOM_TRIGGER_MODEL = {
    "name": "Honey Bee Bloom Trigger",
    "eppo_code": "APISME",
    "base_gdd": 5,
    "description": (
        "Short-term estimation of bloom activation potential using rolling 14-day thermal accumulation."
    ),
    "gdd_points": [
        {
            "start": 0,
            "end": 25,
            "descriptor": "No Bloom Trigger"
        },
        {
            "start": 25,
            "end": 60,
            "descriptor": "Low Bloom Potential"
        },
        {
            "start": 60,
            "end": 120,
            "descriptor": "Active Bloom Trigger"
        },
        {
            "start": 120,
            "end": 200,
            "descriptor": "Strong Bloom Trigger"
        },
        {
            "start": 200,
            "end": 300,
            "descriptor": "Rapid Bloom Progression"
        },
        {
            "start": 300,
            "end": 400,
            "descriptor": "Late Season Bloom Acceleration"
        },
        {
            "start": 400,
            "end": 9999,
            "descriptor": "Heat Limited Bloom"
        }
    ]
}

# =========================================================
# HONEY BEE ACTIVITY MODEL
# Rolling 14-day GDD
# =========================================================
HONEY_BEE_ACTIVITY_MODEL = {
    "name": "Honey Bee Activity",
    "eppo_code": "APISME",
    "base_gdd": 10,
    "description": (
        "Estimation of recent bee activity potential using rolling 14-day thermal accumulation."
    ),
    "gdd_points": [
        {
            "start": 0,
            "end": 60,
            "descriptor": "Inactive"
        },
        {
            "start": 60,
            "end": 150,
            "descriptor": "Low Activity"
        },
        {
            "start": 150,
            "end": 300,
            "descriptor": "Active"
        },
        {
            "start": 300,
            "end": 500,
            "descriptor": "High Activity"
        },
        {
            "start": 500,
            "end": 9999,
            "descriptor": "Heat Limited"
        }
    ]
}

# =========================================================
# HONEY BEE HEAT STRESS MODEL
# Rolling 7-day GDD above 30°C
# =========================================================
HONEY_BEE_HEAT_STRESS_MODEL = {
    "name": "Honey Bee Heat Stress",
    "eppo_code": "APISME",
    "base_gdd": 30,
    "description": (
        "Estimation of colony heat stress accumulation from recent high temperatures."
    ),
    "gdd_points": [
        {
            "start": 0,
            "end": 20,
            "descriptor": "No Stress"
        },
        {
            "start": 20,
            "end": 50,
            "descriptor": "Low Stress"
        },
        {
            "start": 50,
            "end": 100,
            "descriptor": "Moderate Stress"
        },
        {
            "start": 100,
            "end": 180,
            "descriptor": "High Stress"
        },
        {
            "start": 180,
            "end": 9999,
            "descriptor": "Extreme Stress"
        }
    ]
}

# =========================================================
# VARROA BROOD PRESSURE MODEL
# Rolling 30-day GDD
# =========================================================
HONEY_BEE_VARROA_BROOD_PRESSURE_MODEL = {
    "name": "Honey Bee Varroa Brood Pressure",
    "eppo_code": "APISME",
    "base_gdd": 10,
    "description": (

    ),
    "gdd_points": [
        {
            "start": 0,
            "end": 75,
            "descriptor": "Minimal Brood"
        },
        {
            "start": 75,
            "end": 185,
            "descriptor": "Brood Increasing"
        },
        {
            "start": 185,
            "end": 370,
            "descriptor": "Active Brood Production"
        },
        {
            "start": 370,
            "end": 560,
            "descriptor": "High Varroa Reproduction Potential"
        },
        {
            "start": 560,
            "end": 750,
            "descriptor": "Maximum Brood Availability"
        },
        {
            "start": 750,
            "end": 9999,
            "descriptor": "Brood Decline / Heat Limited"
        }
    ]
}

HONEY_BEE_MODELS = [
    HONEY_BEE_HIVE_CYCLE_MODEL,
    HONEY_BEE_BLOOM_AVAILABILITY_MODEL,
    HONEY_BEE_BLOOM_TRIGGER_MODEL,
    HONEY_BEE_ACTIVITY_MODEL,
    HONEY_BEE_HEAT_STRESS_MODEL,
    HONEY_BEE_VARROA_BROOD_PRESSURE_MODEL,
]


def group_risk_models(data) -> dict:
    grouped = defaultdict(list)

    risk_models = data.get("diseases", [])
    if not risk_models and data.get("name"):
        risk_models = [data]

    for risk_model in risk_models:
        name = risk_model.get("name") or "unknown"
        risk_model_id = risk_model.get("id")
        grouped[name].append(risk_model_id)

    return dict(grouped)


def get_one_risk_model_id(base_url: str, jwt_token_access: str, name: str) -> str:
    result = ""
    try:
        r = requests.get(
            url=f"{base_url.rstrip('/')}/api/v1/disease/{name.replace(' ', '%20')}/", headers={"Authorization": f"Bearer {jwt_token_access}"},
            timeout=10,
        )
        r.raise_for_status()
        data = group_risk_models(r.json())
        if data:
            result = data.get(name)[0]
    except Exception:
        pass

    return result


def get_one_risk_model_description(base_url: str, jwt_token_access: str, name: str) -> str:
    result = ""
    try:
        r = requests.get(
            url=f"{base_url.rstrip('/')}/api/v1/disease/{name.replace(' ', '%20')}/", headers={"Authorization": f"Bearer {jwt_token_access}"},
            timeout=10,
        )
        r.raise_for_status()
        data = r.json()
        if data:
            result = data.get("description")
    except Exception:
        pass

    return result


def get_all_risk_models_name_id(base_url: str, jwt_token_access: str) -> dict:
    result = {}
    try:
        r = requests.get(
            url=f"{base_url.rstrip('/')}/api/v1/disease/",
            headers={"Authorization": f"Bearer {jwt_token_access}"},
            timeout=10,
        )
        r.raise_for_status()
        result = group_risk_models(r.json())
    except Exception:
        pass

    return result


def create_risk_model(
    base_url: str, jwt_token_access: str, risk_model_data
) -> dict:
    result = {}
    try:
        validate(instance=risk_model_data, schema=create_risk_model_schema)
    except ValidationError as e:
        print(f"Invalid risk_model data: {e}")
        return result
    if get_one_risk_model_id(
        base_url, jwt_token_access, risk_model_data.get("name")
    ):
        return result
    try:
        r = requests.post(
            url=f"{base_url.rstrip('/')}/api/v1/disease/",
            headers={
                "Authorization": f"Bearer {jwt_token_access}",
            },
            json=risk_model_data,
            timeout=10,
        )
        oa_function.print_request_info(r)
        r.raise_for_status()

        result = group_risk_models(r.json())
    except Exception:
        pass

    return result


def create_default_risk_models(base_url: str, jwt_token_access: str) -> list:
    result = []
    for risk_model_data in HONEY_BEE_MODELS:
        result.append(
            create_risk_model(base_url, jwt_token_access, risk_model_data)
        )
    return result


def create_risk_models_from_file(
    base_url: str, jwt_token_access: str, risk_models_file: str
) -> dict:
    data = []
    for risk_model_data in oa_function.read_data_file(risk_models_file):
        data.append(
            create_risk_model(base_url, jwt_token_access, risk_model_data)
        )
    return data


def create_file_from_all_risk_models(
    base_url: str, jwt_token_access: str, risk_models_file: str
) -> list:
    result = []
    try:
        r = requests.get(
            url=f"{base_url.rstrip('/')}/api/v1/disease/",
            headers={
                "Authorization": f"Bearer {jwt_token_access}",
                "accept": "application/json",
            },
            timeout=10,
        )
        r.raise_for_status()

        for disease in r.json().get("diseases", []):
            gdd_points = []
            for point in disease.get("gdd_points", []):
                gdd_points.append(
                    {
                        "start": point.get("start"),
                        "end": point.get("end"),
                        "descriptor": point.get("descriptor"),
                    }
                )

            result.append(
                {
                    "name": disease.get("name"),
                    "eppo_code": disease.get("eppo_code"),
                    "base_gdd": disease.get("base_gdd"),
                    "description": disease.get("description"),
                    "gdd_points": gdd_points,
                }
            )

        oa_function.write_data_file(risk_models_file, result)
    except Exception:
        pass

    return result


def delete_all_risk_models(base_url: str, jwt_token_access: str) -> list:
    result = []
    data = get_all_risk_models_name_id(base_url, jwt_token_access)
    risk_model_ids = [id_ for value in data.values() for id_ in value]
    for risk_model_id in risk_model_ids:
        try:
            print(risk_model_id)
            r = requests.delete(
                url=f"{base_url.rstrip('/')}/api/v1/disease/{risk_model_id}",
                headers={"Authorization": f"Bearer {jwt_token_access}"},
                timeout=10,
            )
            oa_function.print_request_info(r)
            r.raise_for_status()
            result.append(risk_model_id)
        except Exception:
            pass

    return result


# =========================================================
# ANALYSIS FUNCTIONS
# =========================================================
def get_gdd_start_date(model_name: str) -> str:
    start_date_rules = {
        "Honey Bee Hive Cycle":
            lambda: oa_function.get_start_of_year_ISO_date(),
        "Honey Bee Bloom Availability":
            lambda: oa_function.get_start_of_year_ISO_date(),
        "Honey Bee Bloom Trigger":
            lambda: oa_function.get_ISO_date_n_days_ago(14),
        "Honey Bee Activity":
            lambda: oa_function.get_ISO_date_n_days_ago(14),
        "Honey Bee Heat Stress":
            lambda: oa_function.get_ISO_date_n_days_ago(7),
        "Honey Bee Varroa Brood Pressure":
            lambda: oa_function.get_ISO_date_n_days_ago(28),
    }

    if model_name not in start_date_rules:
        return oa_function.get_start_of_year_ISO_date()

    return start_date_rules[model_name]()


def gdd_estimate(
    base_url: str,
    jwt_token_access: str,
    parcel_id: str,
    model_name: str,
) -> str:
    result = ""
    start = get_gdd_start_date(model_name)
    end = oa_function.get_ISO_date_n_days_ago(1)

    model_id = get_one_risk_model_id(
        base_url,
        jwt_token_access,
        model_name,
    )
    try:
        r = requests.get(
            url=(
                f"{base_url.rstrip('/')}/api/v1/model/{model_id}/gdd/"
                f"?parcel_id={parcel_id}"
                f"&from_date={start}"
                f"&to_date={end}"
                f"&formating=jsonld"
            ),
            headers={"Authorization": f"Bearer {jwt_token_access}"},
            timeout=10,
        )
        r.raise_for_status()
        data = r.json()

        observations = []

        for graph_item in data.get("@graph", []):
            for collection in graph_item:
                if collection.get("@type") != "ObservationCollection":
                    continue

                observations.extend(collection.get("hasMember", []))

        if not observations:
            return result

        last_observation = max(
            observations,
            key=lambda obs: obs.get("phenomenonTime", "")
        )
        result = last_observation.get("descriptor", "")
    except Exception:
        pass

    return result


if __name__ == "__main__":
    pass
