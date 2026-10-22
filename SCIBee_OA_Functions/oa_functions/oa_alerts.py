import requests
from collections import defaultdict

from jsonschema import validate, ValidationError
import copy

from . import oa_function
from . import oa_parcel
from . import oa_activity_type
from . import oa_observation

create_alert_schema = {
    "type": "object",
    "properties": {
        "activityType": {"type": "string"},
        "title": {"type": "string"},
        "details": {"type": "string"},
        "severity": {
            "type": "string",
            "enum": [
                "minor",
                "moderate",
                "severe",
                "major",
                "critical",
            ],
        },
        "hasAgriParcel": {"type": "string"},
        "validFrom": {
            "type": "string",
            "pattern": r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$",
        },
        "validTo": {
            "type": "string",
            "pattern": r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$",
        },
        "quantityValue": {
            "type": "object",
            "properties": {
                "unit": {"type": "string"},
                "hasValue": {"type": "string"},
            },
        },
        "relatedObservation": {"type": "string"},
    },
    "required": [
        "activityType",
        "severity",
        "validFrom",
        "validTo",
    ],
}


def group_alerts(data):
    grouped = defaultdict(list)

    for alert in data.get("@graph", []):
        if alert.get("@type") != "Alert":
            continue
        name = alert.get("title") or "unknown"
        alert_id = alert.get("@id", "").replace(
            "urn:farmcalendar:Alert:", ""
        )
        if alert_id:
            grouped[name].append(alert_id)
    return dict(grouped)


def get_all_alerts_name_id(base_url: str, jwt_token_access: str) -> dict:
    result = {}
    try:
        r = requests.get(
            url=f"{base_url.rstrip('/')}/api/v1/Alerts/?format=jsonld",
            headers={"Authorization": f"Bearer {jwt_token_access}"},
            timeout=10,
        )
        r.raise_for_status()
        result = group_alerts(r.json())
    except Exception:
        pass

    return result


def get_one_alert_id(base_url: str, jwt_token_access: str, title: str) -> str:
    result = ""
    try:
        r = requests.get(
            url=f"{base_url.rstrip('/')}/api/v1/Alerts/?format=jsonld&title={title.replace(' ', '+')}",
            headers={"Authorization": f"Bearer {jwt_token_access}"},
            timeout=10,
        )
        r.raise_for_status()
        data = group_alerts(r.json())
        if data:
            result = data.get(title)[0]
    except Exception:
        pass

    return result


def get_filter_alert(
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
            url=f"{base_url.rstrip('/')}/api/v1/Alerts/?format=jsonld&parcel={parcel_id}&activity_type={type_id}&fromDate={time_ISO_from}&toDate={time_ISO_to}",
            headers={"Authorization": f"Bearer {jwt_token_access}"},
            timeout=10,
        )
        r.raise_for_status()
        result = r.json()
    except Exception:
        pass

    return result


def create_alert(base_url: str, jwt_token_access: str, alert_data) -> dict:
    result = {}
    try:
        validate(instance=alert_data, schema=create_alert_schema)
    except ValidationError as e:
        print(f"Invalid alert data: {e}")
        return result

    if get_one_alert_id(
        base_url, jwt_token_access, alert_data.get("title")
    ):
        return result

    try:
        r = requests.post(
            url=f"{base_url.rstrip('/')}/api/v1/Alerts/",
            headers={
                "Authorization": f"Bearer {jwt_token_access}",
            },
            json=alert_data,
            timeout=10,
        )
        print("Response:", r.status_code)
        r.raise_for_status()
        result = group_alerts(r.json())
    except Exception:
        pass

    return result


def update_alert_from_file(
    base_url: str, jwt_token_access: str, alert_data: dict
) -> dict:
    result = copy.deepcopy(alert_data)
    result.update({"activityType": ""})
    result.update({"hasAgriParcel": ""})
    result.update({"relatedObservation": ""})
    activityType_name = result.pop("activityType_name", "")
    activityType_id = oa_activity_type.get_one_activity_type_id(
        base_url, jwt_token_access, activityType_name
    )
    hasAgriParcel_name = result.pop("hasAgriParcel_name", "")
    hasAgriParcel_id = oa_parcel.get_one_parcel_id(
        base_url, jwt_token_access, hasAgriParcel_name
    )
    relatedObservation_name = result.pop("relatedObservation_name", "")
    relatedObservation_id = oa_observation.get_one_observation_id(
        base_url, jwt_token_access, relatedObservation_name
    )

    result.update({"activityType": activityType_id})
    result.update({"hasAgriParcel": hasAgriParcel_id})
    result.update({"relatedObservation": relatedObservation_id})

    return result


def update_alert_for_file(
    base_url: str, jwt_token_access: str, alert_data: dict
) -> dict:
    result = copy.deepcopy(alert_data)

    for alert in result:
        activityType_id = alert.get("activityType")
        activityType_name = oa_activity_type.get_one_activity_type_name(
            base_url, jwt_token_access, activityType_id
        )
        hasAgriParcel_id = alert.get("hasAgriParcel")
        hasAgriParcel_name = oa_parcel.get_one_parcel_name(
            base_url, jwt_token_access, hasAgriParcel_id
        )
        relatedObservation_id = alert.get("relatedObservation")
        relatedObservation_name = oa_observation.get_one_observation_name(
            base_url, jwt_token_access, relatedObservation_id
        )

        alert.update({"activityType": ""})
        alert.update({"hasAgriParcel": ""})
        alert.update({"relatedObservation": ""})

        alert.update({"activityType_name": activityType_name})
        alert.update({"hasAgriParcel_name": hasAgriParcel_name})
        alert.update({"relatedObservation_name": relatedObservation_name})

    return result


def create_alerts_from_file(
    base_url: str, jwt_token_access: str, alerts_file
) -> list:
    result = []
    for alert_data in oa_function.read_data_file(alerts_file):
        result.append(
            create_alert(
                base_url,
                jwt_token_access,
                update_alert_from_file(
                    base_url, jwt_token_access, alert_data
                ),
            )
        )
    return result


def create_file_from_alerts(
    base_url: str, jwt_token_access: str, alerts_file: str, start_N_days_ago=28
) -> dict:
    result = {}
    time_ISO_from = oa_function.get_ISO_time_n_days_ago(start_N_days_ago)

    try:
        r = requests.get(
            url=f"{base_url.rstrip('/')}/api/v1/Alerts/?format=jsonld&fromDate={time_ISO_from}",
            headers={"Authorization": f"Bearer {jwt_token_access}"},
            timeout=10,
        )
        r.raise_for_status()
        data = []

        for alert in r.json().get("@graph", []):
            if alert.get("@type") != "Alert":
                continue
            activity_type = alert.get("activityType")
            has_agri_parcel = alert.get("hasAgriParcel")
            related_observation = alert.get("relatedObservation")
            data.append(
                {
                    "activityType": activity_type.get("@id")
                    .replace(
                        "urn:farmcalendar:FarmCalendarActivityType:", ""
                    )
                    if activity_type
                    else None,
                    "title": alert.get("title"),
                    "details": alert.get("details"),
                    "severity": alert.get("severity"),
                    "hasAgriParcel": has_agri_parcel.get("@id")
                    .replace("urn:farmcalendar:Parcel:", "")
                    if has_agri_parcel
                    else None,
                    "validFrom": alert.get("validFrom"),
                    "validTo": alert.get("validTo"),
                    "quantityValue": (
                        {
                            "unit": alert.get("quantityValue").get("unit"),
                            "hasValue": alert.get("quantityValue").get("hasValue"),
                        }
                        if alert.get("quantityValue")
                        else None
                    ),
                    "relatedObservation": related_observation.get("@id")
                    .replace("urn:farmcalendar:Observation:", "")
                    if isinstance(related_observation, dict)
                    else None,
                }
            )
        result = update_alert_for_file(base_url, jwt_token_access, data)
        oa_function.write_data_file(
            alerts_file,
            result,
        )
    except Exception:
        pass

    return result


def delete_all_alerts(base_url: str, jwt_token_access: str) -> list:
    result = []
    data = get_all_alerts_name_id(base_url, jwt_token_access)
    alert_ids = [id_ for value in data.values() for id_ in value]
    for alert_id in alert_ids:
        try:
            r = requests.delete(
                url=f"{base_url.rstrip('/')}/api/v1/alerts/{alert_id}/?format=jsonld",
                headers={"Authorization": f"Bearer {jwt_token_access}"},
                timeout=10,
            )
            r.raise_for_status()
            result.append(alert_id)
        except Exception:
            pass

    return result


if __name__ == "__main__":
    pass
