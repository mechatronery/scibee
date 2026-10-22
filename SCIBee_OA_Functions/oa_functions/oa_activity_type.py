import requests
from collections import defaultdict

from jsonschema import validate, ValidationError

from . import oa_function

create_activity_type_schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string", "minLength": 1},
        "description": {"type": ["string", "null"]},
        "category": {
            "type": "string",
            "enum": ["activity", "observation", "alert"],
        },
        "background_color": {"type": "string", "pattern": "^#[0-9a-fA-F]{6}$"},
        "border_color": {"type": "string", "pattern": "^#[0-9a-fA-F]{6}$"},
        "text_color": {"type": "string", "pattern": "^#[0-9a-fA-F]{6}$"},
    },
    "required": ["name", "category", "background_color", "border_color", "text_color"],
}


def group_activity_types(data) -> dict:
    grouped = defaultdict(list)
    for activity_type in data.get("@graph", []):
        if activity_type.get("@type") != "FarmActivityType":
            continue
        name = activity_type.get("name") or "unknown"
        activity_type_id = activity_type.get("@id", "").replace(
            "urn:farmcalendar:FarmActivityType:", ""
        )
        if activity_type_id:
            grouped[name].append(activity_type_id)
    return dict(grouped)


def get_all_activity_type_name_id(base_url: str, jwt_token_access: str) -> dict:
    result = {}
    try:
        r = requests.get(
            url=f"{base_url.rstrip('/')}/api/v1/FarmCalendarActivityTypes/?format=jsonld",
            headers={"Authorization": f"Bearer {jwt_token_access}"},
            timeout=10,
        )
        r.raise_for_status()
        result = group_activity_types(r.json())
    except Exception:
        pass
    return result


def get_one_activity_type_id(base_url: str, jwt_token_access: str, name: str) -> str:
    result = ""
    try:
        r = requests.get(
            url=f"{base_url.rstrip('/')}/api/v1/FarmCalendarActivityTypes/?format=jsonld&name={name.replace(' ', '+')}",
            headers={"Authorization": f"Bearer {jwt_token_access}"},
            timeout=10,
        )
        r.raise_for_status()
        data = group_activity_types(r.json())
        if data:
            result = data.get(name)[0]
    except Exception:
        pass

    return result


def get_one_activity_type_name(base_url: str, jwt_token_access: str, id: str) -> str:
    result = ""
    try:
        r = requests.get(
            url=f"{base_url.rstrip('/')}/api/v1/FarmCalendarActivityTypes/{id}/?format=jsonld",
            headers={"Authorization": f"Bearer {jwt_token_access}"},
            timeout=10,
        )
        r.raise_for_status()

        data = group_activity_types(r.json())
        if data:
            result = list(data.keys())[0]
    except Exception:
        pass

    return result


def create_activity_type(
    base_url: str, jwt_token_access: str, activity_type_data
) -> dict:
    result = {}
    try:
        validate(instance=activity_type_data, schema=create_activity_type_schema)
    except ValidationError as e:
        print(f"Invalid activity_type data: {e}")
        return result

    if get_one_activity_type_id(
        base_url, jwt_token_access, activity_type_data.get("name")
    ):
        return result

    try:
        r = requests.post(
            url=f"{base_url.rstrip('/')}/api/v1/FarmCalendarActivityTypes/",
            headers={
                "Authorization": f"Bearer {jwt_token_access}",
            },
            json=activity_type_data,
            timeout=10,
        )
        r.raise_for_status()
        result = group_activity_types(r.json())
    except Exception:
        pass

    return result


def create_activity_types_from_file(
    base_url: str, jwt_token_access: str, activity_types_file
) -> list:
    result = []
    for activity_type_data in oa_function.read_data_file(activity_types_file):
        result.append(
            create_activity_type(base_url, jwt_token_access, activity_type_data)
        )
    return result


def create_file_from_all_activity_types(
    base_url: str, jwt_token_access: str, activity_types_file: str
) -> list:
    result = []
    try:
        r = requests.get(
            url=f"{base_url.rstrip('/')}/api/v1/FarmCalendarActivityTypes/?format=jsonld",
            headers={"Authorization": f"Bearer {jwt_token_access}"},
            timeout=10,
        )
        r.raise_for_status()

        for activity_type in r.json().get("@graph", []):
            if activity_type.get("@type") != "FarmActivityType":
                continue

            result.append(
                {
                    "name": activity_type.get("name"),
                    "description": activity_type.get("description"),
                    "category": activity_type.get("category"),
                    "background_color": activity_type.get("background_color"),
                    "border_color": activity_type.get("border_color"),
                    "text_color": activity_type.get("text_color"),
                }
            )

        oa_function.write_data_file(activity_types_file, result)
    except Exception:
        pass

    return result


def delete_all_activity_types(base_url: str, jwt_token_access: str) -> list:
    result = []
    data = get_all_activity_type_name_id(base_url, jwt_token_access)
    activity_type_ids = [id_ for value in data.values() for id_ in value]
    for activity_type_id in activity_type_ids:
        try:
            r = requests.delete(
                url=f"{base_url.rstrip('/')}/api/v1/FarmCalendarActivityTypes/{activity_type_id}/?format=jsonld",
                headers={"Authorization": f"Bearer {jwt_token_access}"},
                timeout=10,
            )
            r.raise_for_status()
            result.append(activity_type_id)
        except Exception:
            pass

    return result


if __name__ == "__main__":
    pass
