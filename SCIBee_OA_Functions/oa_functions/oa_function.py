import json
from datetime import datetime, timezone, timedelta
from geopy.distance import geodesic
import hashlib


def read_data_file(file_name: str):
    data = []
    try:
        with open(file_name, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("File not found")
    except json.JSONDecodeError as e:
        print("Invalid JSON:", e)
    return data


def write_data_file(file_name: str, data):
    print("C")
    try:
        with open(file_name, "w") as f:
            json.dump(data, f, indent=4)
    except (IOError, OSError) as e:
        print("File error:", e)
    except TypeError as e:
        print("Serialization error:", e)
    return


def get_current_ISO_time() -> str:

    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def get_ISO_time_n_days_ago(days: int) -> str:
    return (
        (datetime.now(timezone.utc) - timedelta(days=days))
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def get_ISO_time_n_days_in_future(days: int) -> str:
    return (
        (datetime.now(timezone.utc) + timedelta(days=days))
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def get_ISO_time_difference(time_A: str, time_B: str) -> float:
    fmt = "%Y-%m-%dT%H:%M:%SZ"
    A = datetime.strptime(time_A, fmt)
    B = datetime.strptime(time_B, fmt)
    return (A - B).total_seconds() / 3600


def get_current_ISO_date() -> str:
    return get_current_ISO_time().split("T")[0]


def get_ISO_date_n_days_ago(days: int) -> str:
    return get_ISO_time_n_days_ago(days).split("T")[0]


def get_start_of_year_ISO_date() -> str:
    return f"{get_current_ISO_date()[:4]}-01-01"


def get_geographical_distance(location_A: dict, location_B: dict) -> float:
    A = (float(location_A["latitude"]), float(location_A["longitude"]))
    B = (float(location_B["latitude"]), float(location_B["longitude"]))
    return geodesic(A, B).kilometers


def get_dict_hash(data: dict):
    serialized = json.dumps(data, sort_keys=True, separators=(",", ":"))
    # SHA256 hash
    return hashlib.sha256(serialized.encode()).hexdigest()


def print_request_info(response):
    print("Request URL:", response.request.url)
    print("Request method:", response.request.method)
    print("Request headers:", response.request.headers)
    print("Request body:", response.request.body)
    print("Status:", response.status_code)
    print("Response:", response.text)


if __name__ == "__main__":
    pass
