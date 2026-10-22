import requests
from collections import defaultdict

from jsonschema import validate, ValidationError

from . import oa_function

create_farm_schema = {
    "type": "object",
    "properties": {
        "status": {"type": "integer"},
        "name": {"type": "string"},
        "description": {"type": "string"},
        "administrator": {"type": "string"},
        "telephone": {"type": "string"},
        "vatID": {"type": "string"},
        "contactPerson": {
            "type": "object",
            "properties": {
                "firstname": {"type": "string"},
                "lastname": {"type": "string"},
            },
            "required": ["firstname", "lastname"],
        },
        "address": {
            "type": "object",
            "properties": {
                "adminUnitL1": {"type": "string"},
                "adminUnitL2": {"type": "string"},
                "addressArea": {"type": "string"},
                "municipality": {"type": "string"},
                "community": {"type": "string"},
                "locatorName": {"type": "string"},
            },
            "required": [
                "adminUnitL1",
                "adminUnitL2",
                "addressArea",
                "municipality",
                "community",
                "locatorName",
            ],
        },
    },
    "required": [
        "status",
        "name",
        "description",
        "administrator",
        "telephone",
        "vatID",
        "contactPerson",
        "address",
    ],
}


def group_farms(data) -> dict:
    grouped = defaultdict(list)
    for farm in data.get("@graph", []):
        if farm.get("@type") != "Farm":
            continue
        name = farm.get("name") or "unknown"
        farm_id = farm.get("@id", "").replace("urn:farmcalendar:Farm:", "")
        if farm_id:
            grouped[name].append(farm_id)
    return dict(grouped)


def get_all_farms_name_id(base_url: str, jwt_token_access: str) -> dict:
    result = {}
    try:
        r = requests.get(
            url=f"{base_url.rstrip('/')}/api/v1/Farm/?format=jsonld",
            headers={"Authorization": f"Bearer {jwt_token_access}"},
            timeout=10,
        )
        r.raise_for_status()
        result = group_farms(r.json())
    except Exception:
        pass

    return result


def get_one_farm_id(base_url: str, jwt_token_access: str, name: str) -> str:
    result = ""
    try:
        r = requests.get(
            url=f"{base_url.rstrip('/')}/api/v1/Farm/?format=jsonld&name={name.replace(' ', '+')}",
            headers={"Authorization": f"Bearer {jwt_token_access}"},
            timeout=10,
        )
        r.raise_for_status()
        data = group_farms(r.json())
        if data:
            result = data.get(name)[0]
    except Exception:
        pass

    return result


def get_one_farm_name(base_url: str, jwt_token_access: str, id: str) -> str:
    result = ""
    try:
        r = requests.get(
            url=f"{base_url.rstrip('/')}/api/v1/Farm/{id}/?format=jsonld",
            headers={"Authorization": f"Bearer {jwt_token_access}"},
            timeout=10,
        )
        r.raise_for_status()
        data = group_farms(r.json())
        if data:
            result = list(data.keys())[0]
    except Exception:
        pass

    return result


def create_farm(base_url: str, jwt_token_access: str, farm_data) -> dict:
    result = {}
    try:
        validate(instance=farm_data, schema=create_farm_schema)
    except ValidationError as e:
        print(f"Invalid farm data: {e}")
        return result
    if get_one_farm_id(base_url, jwt_token_access, farm_data["name"]):
        return result
    try:
        r = requests.post(
            url=f"{base_url.rstrip('/')}/api/v1/Farm/",
            headers={
                "Authorization": f"Bearer {jwt_token_access}",
            },
            json=farm_data,
            timeout=10,
        )
        oa_function.print_request_info(r)
        r.raise_for_status()
        result = group_farms(r.json())
    except Exception:
        pass

    return result


def create_farms_from_file(
    base_url: str, jwt_token_access: str, farms_file: str
) -> list:
    result = []
    for farm_data in oa_function.read_data_file(farms_file):
        result.append(create_farm(base_url, jwt_token_access, farm_data))
    return result


def create_file_from_all_farms(base_url: str, jwt_token_access: str, farms_file: str) -> list:
    result = []
    try:
        r = requests.get(
            url=f"{base_url.rstrip('/')}/api/v1/Farm/?format=jsonld",
            headers={"Authorization": f"Bearer {jwt_token_access}"},
            timeout=10,
        )
        r.raise_for_status()

        for farm in r.json().get("@graph", []):
            if farm.get("@type") != "Farm":
                continue

            result.append(
                {
                    "status": farm.get("status"),
                    "name": farm.get("name"),
                    "description": farm.get("description"),
                    "administrator": farm.get("administrator"),
                    "telephone": farm.get("telephone"),
                    "vatID": farm.get("vatID"),
                    "contactPerson": {
                        "firstname": farm.get("contactPerson").get("firstname"),
                        "lastname": farm.get("contactPerson").get("lastname"),
                    },
                    "address": {
                        "adminUnitL1": farm.get("address").get("adminUnitL1"),
                        "adminUnitL2": farm.get("address").get("adminUnitL2"),
                        "addressArea": farm.get("address").get("addressArea"),
                        "municipality": farm.get("address").get("municipality"),
                        "community": farm.get("address").get("community"),
                        "locatorName": farm.get("address").get("locatorName"),
                    },
                }
            )
        oa_function.write_data_file(farms_file, result)
    except Exception:
        pass

    return result


def delete_all_farms(base_url: str, jwt_token_access: str) -> list:
    result = []
    data = get_all_farms_name_id(base_url, jwt_token_access)
    farm_ids = [id_ for value in data.values() for id_ in value]
    for farm_id in farm_ids:
        try:
            r = requests.delete(
                url=f"{base_url.rstrip('/')}/api/v1/Farm/{farm_id}/?format=jsonld",
                headers={"Authorization": f"Bearer {jwt_token_access}"},
                timeout=10,
            )
            r.raise_for_status()
            result.append(farm_id)
        except Exception:
            pass

    return result


if __name__ == "__main__":
    pass
