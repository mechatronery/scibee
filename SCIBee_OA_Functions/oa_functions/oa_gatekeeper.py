import requests
import math


def login(
    base_url: str,
    username: str,
    password: str,
) -> dict[str, str]:
    result = {}
    try:
        r = requests.post(
            url=f"{base_url.rstrip('/')}/api/login/",
            json={"username": username, "password": password},
            timeout=10,
        )
        r.raise_for_status()
        data = r.json()
        if not data.get("success"):
            raise RuntimeError("Login failed")
        result = {"access": data["access"], "refresh": data["refresh"]}
    except Exception:
        pass

    return result


def validate(base_url: str, jwt_token_access: str) -> dict[str, int]:
    result = {}
    try:
        r = requests.post(
            url=f"{base_url.rstrip('/')}/api/validate_token/",
            json={"token": jwt_token_access, "token_type": "access"},
            timeout=10,
        )
        r.raise_for_status()
        data = r.json()
        if not data.get("success"):
            raise RuntimeError("Validation failed")
        result = {"remaining_time_in_seconds": math.floor(data["remaining_time_in_seconds"])}
    except Exception:
        pass

    return result


def refresh(base_url: str, jwt_token_refresh: str) -> dict[str, str]:
    result = {}
    try:
        r = requests.post(
            url=f"{base_url.rstrip('/')}/api/token/refresh/",
            json={"refresh": jwt_token_refresh},
            timeout=10,
        )
        r.raise_for_status()
        data = r.json()
        if not data.get("access"):
            raise RuntimeError("Refresh failed")
        result = {"access": data["access"]}
    except Exception:
        pass

    return result


def logout(base_url: str, jwt_token_refresh: str) -> dict[str, str]:
    result = {}
    try:
        r = requests.post(
            url=f"{base_url.rstrip('/')}/api/logout/",
            json={"refresh": jwt_token_refresh},
            timeout=10,
        )
        r.raise_for_status()
        data = r.json()
        if not data.get("success"):
            raise RuntimeError("Logout failed")
        result = {"success": data.get("success")}
    except Exception:
        pass

    return result


def getServices(base_url: str, jwt_token_access: str) -> dict[str, str]:
    result = {}
    try:
        r = requests.get(
            url=f"{base_url.rstrip('/')}/api/service_directory/",
            headers={"Authorization": f"Bearer {jwt_token_access}"},
            timeout=10,
        )
        r.raise_for_status()
        result = r.json()
    except Exception:
        pass

    return result


if __name__ == "__main__":
    pass
