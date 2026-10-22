import requests
from collections import defaultdict

from jsonschema import validate, ValidationError

from . import oa_farm
from . import oa_function

create_parcel_schema = {
    "type": "object",
    "properties": {
        "status": {"type": "integer"},
        "identifier": {"type": "string"},
        "description": {"type": "string"},
        "validFrom": {
            "type": "string",
            "pattern": r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$",
        },
        "validTo": {
            "type": "string",
            "pattern": r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$",
        },
        "hasIrrigationFlow": {"type": "string"},
        "category": {"type": "string"},
        "inRegion": {"type": "string"},
        "hasToponym": {"type": "string"},
        "isNitroArea": {"type": "boolean"},
        "isNatura2000Area": {"type": "boolean"},
        "isPdopgArea": {"type": "boolean"},
        "isIrrigated": {"type": "boolean"},
        "isCultivatedInLevels": {"type": "boolean"},
        "isGroundSlope": {"type": "boolean"},
        "hasGeometry": {
            "type": "object",
            "properties": {"asWKT": {"type": "string"}},
            "required": ["asWKT"],
        },
        "location": {
            "type": "object",
            "properties": {
                "lat": {"type": "string", "pattern": "^-?\\d{0,3}(?:\\.\\d{0,14})?$"},
                "long": {"type": "string", "pattern": "^-?\\d{0,3}(?:\\.\\d{0,14})?$"},
            },
            "required": ["lat", "long"],
        },
        "farm": {"type": "string"},
    },
    "required": ["status", "identifier", "description", "category", "hasGeometry", "location", "farm"],
}


def group_parcels(data) -> dict:
    grouped = defaultdict(list)
    for parcel in data.get("@graph", []):
        if parcel.get("@type") != "Parcel":
            continue
        name = parcel.get("identifier") or "unknown"
        parcel_id = parcel.get("@id", "").replace("urn:farmcalendar:FarmParcel:", "")
        if parcel_id:
            grouped[name].append(parcel_id)
    return dict(grouped)


def get_all_active_parcels_name_id_of_one_farm_name(
    base_url: str, jwt_token_access: str, farm_name
) -> dict:
    result = {}
    farm_id = oa_farm.get_one_farm_id(base_url, jwt_token_access, farm_name)
    if not farm_id:
        return result
    try:
        r = requests.get(
            url=f"{base_url.rstrip('/')}/api/v1/FarmParcels/?format=jsonld&status=1&farm={farm_id}",
            headers={"Authorization": f"Bearer {jwt_token_access}"},
            timeout=10,
        )
        r.raise_for_status()
        result = group_parcels(r.json())
    except Exception:
        pass

    return result


def get_one_parcel_id(base_url: str, jwt_token_access: str, identifier: str) -> str:
    result = ""
    try:
        r = requests.get(
            url=f"{base_url.rstrip('/')}/api/v1/FarmParcels/?format=jsonld&identifier={identifier.replace(' ', '+')}",
            headers={"Authorization": f"Bearer {jwt_token_access}"},
            timeout=10,
        )
        r.raise_for_status()
        data = group_parcels(r.json())

        if data:
            result = data.get(identifier)[0]
    except Exception:
        pass

    return result


def get_one_parcel_name(base_url: str, jwt_token_access: str, id: str) -> dict:
    result = {}
    try:
        r = requests.get(
            url=f"{base_url.rstrip('/')}/api/v1/FarmParcels/{id}/?format=jsonld",
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


def get_one_parcel_location(base_url: str, jwt_token_access: str, id: str) -> dict:
    result = {}
    try:
        r = requests.get(
            url=f"{base_url.rstrip('/')}/api/v1/FarmParcels/{id}/?format=jsonld",
            headers={"Authorization": f"Bearer {jwt_token_access}"},
            timeout=10,
        )
        r.raise_for_status()
        data = r.json()
        if data:
            location = data["@graph"][0]["location"]
            result = {
                "latitude": location["lat"],
                "longitude": location["long"]
            }

    except Exception:
        pass

    return result


def create_parcel(base_url: str, jwt_token_access: str, parcel_data) -> dict:
    result = {}
    try:
        validate(instance=parcel_data, schema=create_parcel_schema)
    except ValidationError as e:
        print(f"Invalid parcel data: {e}")
        return result

    if get_one_parcel_id(base_url, jwt_token_access, parcel_data.get("identifier")):
        return result
    farm_id = oa_farm.get_one_farm_id(
        base_url, jwt_token_access, parcel_data.get("farm_name")
    )

    if not farm_id:
        return result

    parcel_data.update({"farm": farm_id})
    try:
        r = requests.post(
            url=f"{base_url.rstrip('/')}/api/v1/FarmParcels/",
            headers={
                "Authorization": f"Bearer {jwt_token_access}",
            },
            json=parcel_data,
            timeout=10,
        )
        oa_function.print_request_info(r)
        r.raise_for_status()
        result = group_parcels(r.json())
    except Exception:
        pass

    return result


def create_parcels_from_file(
    base_url: str, jwt_token_access: str, parcels_file: str
) -> list:
    result = []
    for parcel_data in oa_function.read_data_file(parcels_file):
        result.append(create_parcel(base_url, jwt_token_access, parcel_data))
    return result


def create_file_from_all_parcels(
    base_url: str, jwt_token_access: str, parcels_file: str
) -> list:
    result = []
    try:
        r = requests.get(
            url=f"{base_url.rstrip('/')}/api/v1/FarmParcels/?format=jsonld",
            headers={"Authorization": f"Bearer {jwt_token_access}"},
            timeout=10,
        )
        r.raise_for_status()

        for parcel in r.json().get("@graph", []):
            if parcel.get("@type") != "Parcel":
                continue
            farm_id = (
                parcel.get("farm").get("@id", "").replace("urn:farmcalendar:Farm:", "")
            )
            farm_name = oa_farm.get_one_farm_name(base_url, jwt_token_access, farm_id)
            result.append(
                {
                    "status": parcel.get("status"),
                    "identifier": parcel.get("identifier"),
                    "description": parcel.get("description"),
                    "validFrom": parcel.get("validFrom"),
                    "validTo": parcel.get("validTo"),
                    "hasIrrigationFlow": parcel.get("hasIrrigationFlow"),
                    "category": parcel.get("category"),
                    "inRegion": parcel.get("inRegion"),
                    "hasToponym": parcel.get("hasToponym"),
                    "isNitroArea": parcel.get("isNitroArea"),
                    "isNatura2000Area": parcel.get("isNatura2000Area"),
                    "isPdopgArea": parcel.get("isPdopgArea"),
                    "isIrrigated": parcel.get("isIrrigated"),
                    "isCultivatedInLevels": parcel.get("isCultivatedInLevels"),
                    "isGroundSlope": parcel.get("isGroundSlope"),
                    "hasGeometry": {"asWKT": parcel.get("hasGeometry").get("asWKT")},
                    "location": {
                        "lat": parcel.get("location").get("lat"),
                        "long": parcel.get("location").get("long"),
                    },
                    "farm_name": farm_name,
                    "farm": farm_id,
                }
            )

        oa_function.write_data_file
    except Exception:
        pass

    return result


def delete_all_parcels_of_one_farm(base_url: str, jwt_token_access: str, farm_name: str) -> list:
    result = []
    data = get_all_active_parcels_name_id_of_one_farm_name(base_url, jwt_token_access, farm_name)
    parcel_ids = [id_ for value in data.values() for id_ in value]
    for parcel_id in parcel_ids:
        try:
            r = requests.delete(
                url=f"{base_url.rstrip('/')}/api/v1/FarmParcels/{parcel_id}/?format=jsonld",
                headers={"Authorization": f"Bearer {jwt_token_access}"},
                timeout=10,
            )
            r.raise_for_status()
            result.append(parcel_id)
        except Exception:
            pass

    return result


if __name__ == "__main__":
    pass
