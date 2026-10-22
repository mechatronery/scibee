import requests
from collections import defaultdict

from jsonschema import validate, ValidationError
import copy

from . import oa_function
from . import oa_parcel
from . import oa_activity_type

create_observation_schema = {
    "type": "object",
    "properties": {
        "activityType": {"type": "string"},
        "title": {"type": "string"},
        "details": {"type": "string"},
        "phenomenonTime": {
            "type": "string",
            "pattern": r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$",
        },
        "hasEndDatetime": {
            "type": "string",
            "pattern": r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$",
        },
        "hasAgriParcel": {"type": "string"},
        "madeBySensor": {
            "type": "object",
            "properties": {
                "name": {"type": ["string", "null"]},
            },
            "required": ["name"],
        },
        "hasResult": {
            "type": "object",
            "properties": {
                "unit": {"type": "string"},
                "hasValue": {"type": "string"},
            },
            "required": ["hasValue"],
        },
        "observedProperty": {"type": "string"},
        "isPartOfActivity": {"type": "string"},
    },
    "required": [
        "activityType",
        "phenomenonTime",
        "hasResult",
        "observedProperty",
    ],
}


def group_observations(data):
    grouped = defaultdict(list)
    for observation in data.get("@graph", []):
        if observation.get("@type") != "Observation":
            continue
        name = observation.get("title") or "unknown"
        observation_id = observation.get("@id", "").replace(
            "urn:farmcalendar:Observation:", ""
        )
        if observation_id:
            grouped[name].append(observation_id)
    return dict(grouped)


def get_all_observations_name_id(base_url: str, jwt_token_access: str) -> dict:
    result = {}
    try:
        r = requests.get(
            url=f"{base_url.rstrip('/')}/api/v1/Observations/?format=jsonld",
            headers={"Authorization": f"Bearer {jwt_token_access}"},
            timeout=10,
        )
        r.raise_for_status()
        result = group_observations(r.json())
    except Exception:
        pass

    return result


def get_one_observation_id(base_url: str, jwt_token_access: str, title: str) -> str:
    result = ""
    try:
        r = requests.get(
            url=f"{base_url.rstrip('/')}/api/v1/Observations/?format=jsonld&title={title.replace(' ', '+')}",
            headers={"Authorization": f"Bearer {jwt_token_access}"},
            timeout=10,
        )
        r.raise_for_status()
        data = group_observations(r.json())
        if data:
            result = data.get(title)[0]
    except Exception:
        pass

    return result


def get_one_observation_name(base_url: str, jwt_token_access: str, id: str) -> dict:
    result = {}
    try:
        r = requests.get(
            url=f"{base_url.rstrip('/')}/api/v1/Observations/{id}/?format=jsonld",
            headers={"Authorization": f"Bearer {jwt_token_access}"},
            timeout=10,
        )
        r.raise_for_status()
        data = r.json()
        if data:
            result = data["@graph"][0]["identifier"]

    except Exception:
        pass

    return result


def get_filter_observation(
    base_url: str,
    jwt_token_access: str,
    parcel_name: str,
    type_name: str,
    past_N_days: int,
    future_N_days: int,
) -> dict:
    result = {}
    parcel_id = oa_parcel.get_one_parcel_id(base_url, jwt_token_access, parcel_name)
    type_id = oa_activity_type.get_one_activity_type_id(
        base_url, jwt_token_access, type_name
    )
    time_ISO_from = oa_function.get_ISO_time_n_days_ago(past_N_days)
    time_ISO_to = oa_function.get_ISO_time_n_days_in_future(future_N_days)
    try:
        r = requests.get(
            url=f"{base_url.rstrip('/')}/api/v1/Observations/?format=jsonld&parcel={parcel_id}&activity_type={type_id}&fromDate={time_ISO_from}&toDate={time_ISO_to}",
            headers={"Authorization": f"Bearer {jwt_token_access}"},
            timeout=10,
        )
        r.raise_for_status()
        result = r.json()
    except Exception:
        pass

    return result


def create_observation(base_url: str, jwt_token_access: str, observation_data) -> dict:
    result = {}
    try:
        validate(instance=observation_data, schema=create_observation_schema)
    except ValidationError as e:
        print(f"Invalid observation data: {e}")
        return result

    if get_one_observation_id(
        base_url, jwt_token_access, observation_data.get("title")
    ):
        return result

    try:
        r = requests.post(
            url=f"{base_url.rstrip('/')}/api/v1/Observations/",
            headers={
                "Authorization": f"Bearer {jwt_token_access}",
            },
            json=observation_data,
            timeout=10,
        )
        print("Response:", r.status_code)
        r.raise_for_status()
        result = group_observations(r.json())
    except Exception:
        pass

    return result


def update_observation_from_file(
    base_url: str, jwt_token_access: str, observation_data: dict
) -> dict:
    result = copy.deepcopy(observation_data)
    result.update({"activityType": ""})
    result.update({"hasAgriParcel": ""})
    activityType_name = result.pop("activityType_name", "")
    activityType_id = oa_activity_type.get_one_activity_type_id(
        base_url, jwt_token_access, activityType_name
    )
    hasAgriParcel_name = result.pop("hasAgriParcel_name", "")
    hasAgriParcel_id = oa_parcel.get_one_parcel_id(
        base_url, jwt_token_access, hasAgriParcel_name
    )

    result.update({"activityType": activityType_id})
    result.update({"hasAgriParcel": hasAgriParcel_id})

    return result


def update_observation_for_file(
    base_url: str, jwt_token_access: str, observation_data: dict
) -> dict:
    result = copy.deepcopy(observation_data)

    for observation in result:
        activityType_id = observation.get("activityType")
        activityType_name = oa_activity_type.get_one_activity_type_name(
            base_url, jwt_token_access, activityType_id
        )
        hasAgriParcel_id = observation.get("hasAgriParcel")
        hasAgriParcel_name = oa_parcel.get_one_parcel_name(
            base_url, jwt_token_access, hasAgriParcel_id
        )
        observation.update({"activityType": ""})
        observation.update({"hasAgriParcel": ""})

        observation.update({"activityType_name": activityType_name})
        observation.update({"hasAgriParcel_name": hasAgriParcel_name})

    return result


def create_observations_from_file(
    base_url: str, jwt_token_access: str, observations_file
) -> list:
    result = []
    for observation_data in oa_function.read_data_file(observations_file):
        result.append(
            create_observation(
                base_url,
                jwt_token_access,
                update_observation_from_file(
                    base_url, jwt_token_access, observation_data
                ),
            )
        )
    return result


def create_observations_from_data(
    base_url: str,
    jwt_token_access: str,
    observations_data: list
) -> list:
    result = []

    for observation_data in observations_data:
        result.append(
            create_observation(
                base_url,
                jwt_token_access,
                update_observation_from_file(
                    base_url,
                    jwt_token_access,
                    observation_data
                )
            )
        )

    return result


def create_file_from_observations(
    base_url: str,
    jwt_token_access: str,
    observations_file: str,
    start_N_days_ago=28,
    title_start=""
) -> list:
    result = create_data_from_observations(
        base_url,
        jwt_token_access,
        start_N_days_ago,
        title_start
    )

    oa_function.write_data_file(observations_file, result)

    return result


def create_data_from_observations(
    base_url: str,
    jwt_token_access: str,
    start_N_days_ago=28,
    title_start=""
) -> list:
    result = []
    time_ISO_from = oa_function.get_ISO_time_n_days_ago(
        start_N_days_ago
    )

    r = requests.get(
        url=(
            f"{base_url.rstrip('/')}/api/v1/Observations/"
            f"?format=jsonld&fromDate={time_ISO_from}"
        ),
        headers={
            "Authorization": f"Bearer {jwt_token_access}"
        },
        timeout=10,
    )
    r.raise_for_status()

    data = []

    for observation in r.json().get("@graph", []):
        if observation.get("@type") != "Observation":
            continue

        title = observation.get("title") or ""

        if not title.startswith(title_start):
            continue

        activity_type = observation.get("activityType") or {}
        parcel = observation.get("hasAgriParcel") or {}
        sensor = observation.get("madeBySensor") or {}
        has_result = observation.get("hasResult") or {}

        data.append({
            "activityType": activity_type.get("@id", "").replace(
                "urn:farmcalendar:FarmCalendarActivityType:", ""
            ),
            "title": title,
            "details": observation.get("details"),
            "phenomenonTime": observation.get("phenomenonTime"),
            "hasAgriParcel": parcel.get("@id", "").replace(
                "urn:farmcalendar:Parcel:", ""
            ),
            "madeBySensor": {
                "name": sensor.get("name")
            },
            "hasResult": {
                "unit": has_result.get("unit"),
                "hasValue": has_result.get("hasValue"),
            },
            "observedProperty": observation.get("observedProperty"),
        })

    result = update_observation_for_file(
        base_url,
        jwt_token_access,
        data
    )

    return result


def delete_all_observations(base_url: str, jwt_token_access: str) -> list:
    result = []
    data = get_all_observations_name_id(base_url, jwt_token_access)
    observation_ids = [id_ for value in data.values() for id_ in value]
    for observation_id in observation_ids:
        try:
            r = requests.delete(
                url=f"{base_url.rstrip('/')}/api/v1/observations/{observation_id}/?format=jsonld",
                headers={"Authorization": f"Bearer {jwt_token_access}"},
                timeout=10,
            )
            r.raise_for_status()
            result.append(observation_id)
        except Exception:
            pass

    return result


if __name__ == "__main__":
    pass
