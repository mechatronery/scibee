import time
from datetime import datetime, timezone, timedelta
import traceback
import logging
from logging.handlers import RotatingFileHandler
from multiprocessing import Pool
from apscheduler.schedulers.background import BackgroundScheduler
import requests
import pandas as pd
import io

import json

from oa_functions import oa_function
from oa_functions import oa_gatekeeper

from oa_functions import oa_weather
from oa_functions import oa_risk

from oa_functions import oa_parcel

from oa_functions import oa_activity_type
from oa_functions import oa_observation

from dotenv import load_dotenv
import os
import math
import tarfile
import cv2
import numpy as np
from edge_impulse_linux.image import ImageImpulseRunner

# =========================================================
# MODE
# =========================================================
EDGE_MODE = False

load_dotenv()
username = os.getenv("ADMIN_USERNAME")
password = os.getenv("ADMIN_PASSWORD")
gatekeeper_base_url = os.getenv("GATEKEEPER_BASE_URL")
weather_base_url = os.getenv("WEATHER_BASE_URL")
farm_calendar_base_url = os.getenv("FARM_CALENDAR_BASE_URL")
risk_base_url = os.getenv("RISK_BASE_URL")


with open("beehive_endpoints.json", "r") as f:
    beehive_endpoints = json.load(f)

if (not EDGE_MODE):
    with open("community_endpoints.json", "r") as f:
        community_endpoints = json.load(f)

# =========================================================
# UTC LOGGING SETUP
# =========================================================
logger = logging.getLogger("scheduler")
logger.setLevel(logging.INFO)

handler = RotatingFileHandler(
    "scheduler.log",
    maxBytes=5 * 1024 * 1024,  # 5MB
    backupCount=5
)

formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(message)s"
)

# UTC timestamps in logs
logging.Formatter.converter = time.gmtime

handler.setFormatter(formatter)
logger.addHandler(handler)


# =========================================================
# FUNCTIONS
# =========================================================
def fetch_csv_observations(url, source_name, beehive_name="", days_range=1):
    data = []

    url = url.removeprefix("http://").removeprefix("https://")
    url = "http://" + url.rstrip("/") + "/getFile"

    for d in range(1, days_range + 1):
        csv_date = (
            datetime.now(timezone.utc) - timedelta(days=d)
        ).date()

        prefix = f"{beehive_name}_" if beehive_name else ""

        csv_file_name = (
            f"{prefix}{source_name}_"
            f"{csv_date.year:04d}_{csv_date.month:02d}_{csv_date.day:02d}.csv"
        )

        params = {
            "file_name": csv_file_name
        }

        if beehive_name:
            params["beehive"] = beehive_name

        try:
            response = requests.get(
                url,
                params=params,
                timeout=30
            )

            response.raise_for_status()

            df = pd.read_csv(io.StringIO(response.text))
            df["Date"] = csv_date
            data.append(df)

        except Exception as e:
            print(f"Failed to fetch {csv_file_name} from {url}: {e}")
            continue

    if not data:
        return pd.DataFrame()

    return pd.concat(data, ignore_index=True)


def _to_python_number(value):
    if value is None:
        return None

    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        return None

    if not math.isfinite(number):
        return None

    if number.is_integer():
        return int(number)

    return number


def get_last_row_value(df, column_name):
    if df.empty or column_name not in df.columns:
        return None

    if "Epoch_time_ms" in df.columns:
        df = df.sort_values(
            "Epoch_time_ms",
            kind="stable",
        )

    values = pd.to_numeric(
        df[column_name],
        errors="coerce",
    )

    values = values[
        values.notna()
        & np.isfinite(values)
    ]

    if values.empty:
        return None

    return _to_python_number(values.iloc[-1])


def get_min_avg_max(df, column_name):
    empty_stats = {
        "min": None,
        "avg": None,
        "max": None,
    }

    if df.empty or column_name not in df.columns:
        return empty_stats.copy()

    values = pd.to_numeric(
        df[column_name],
        errors="coerce",
    )

    values = values[
        values.notna()
        & np.isfinite(values)
    ]

    if values.empty:
        return empty_stats.copy()

    return {
        "min": _to_python_number(values.min()),
        "avg": _to_python_number(values.mean()),
        "max": _to_python_number(values.max()),
    }


def fetch_varroa_data(
    url,
    beehive_name,
    confidence_threshold=0.5,
):
    """Download the previous day's image archive and detect Varroa mites."""
    model_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "varroa_FOMO.eim",
    )

    empty_result = {
        "total_images": None,
        "images_with_varroa": None,
        "total_varroa_detected": None,
        "average_varroa_per_image": None,
    }

    # Normalize the server URL.
    url = url.removeprefix("http://").removeprefix("https://")
    url = "http://" + url.rstrip("/") + "/getFile"

    # Use the previous UTC calendar day's archive.
    tar_date = (
        datetime.now(timezone.utc) - timedelta(days=1)
    ).date()

    tar_file_name = (
        f"{beehive_name}_VVD_"
        f"{tar_date.year:04d}_{tar_date.month:02d}_"
        f"{tar_date.day:02d}.tar"
    )

    params = {
        "file_name": tar_file_name,
        "beehive": beehive_name,
    }

    tar_buffer = io.BytesIO()
    runner = None

    try:
        if not os.path.isfile(model_path):
            raise FileNotFoundError(
                f"Varroa model not found: {model_path}"
            )

        logging.info("Downloading %s", tar_file_name)

        with requests.get(
            url,
            params=params,
            stream=True,
            timeout=(30, 600),
        ) as response:
            response.raise_for_status()

            for chunk in response.iter_content(
                chunk_size=1024 * 1024,
            ):
                if chunk:
                    tar_buffer.write(chunk)

        tar_buffer.seek(0)

        runner = ImageImpulseRunner(model_path)
        runner.init()

        total_varroa = 0
        total_images = 0
        images_with_varroa = 0

        with tarfile.open(
            fileobj=tar_buffer,
            mode="r:*",
        ) as archive:
            image_members = [
                member
                for member in archive
                if member.isfile()
                and member.name.lower().endswith(
                    (".jpg", ".jpeg", ".png")
                )
            ]

            logging.info(
                "Found %d images in %s",
                len(image_members),
                tar_file_name,
            )

            for member in image_members:
                try:
                    image_file = archive.extractfile(member)

                    if image_file is None:
                        continue

                    with image_file:
                        image_bytes = image_file.read()

                    img = cv2.imdecode(
                        np.frombuffer(
                            image_bytes,
                            dtype=np.uint8,
                        ),
                        cv2.IMREAD_COLOR,
                    )

                    if img is None:
                        logging.warning(
                            "Unable to decode image: %s",
                            member.name,
                        )
                        continue

                    img_rgb = cv2.cvtColor(
                        img,
                        cv2.COLOR_BGR2RGB,
                    )

                    features, _ = runner.get_features_from_image(
                        img_rgb
                    )
                    result = runner.classify(features)

                    bounding_boxes = (
                        result.get("result", {})
                        .get("bounding_boxes", [])
                    )

                    count = sum(
                        1
                        for box in bounding_boxes
                        if str(box.get("label", "")).lower()
                        == "varroa"
                        and _to_python_number(
                            box.get("value")
                        ) is not None
                        and _to_python_number(
                            box.get("value")
                        ) >= confidence_threshold
                    )

                    total_varroa += count
                    total_images += 1

                    if count > 0:
                        images_with_varroa += 1

                except Exception:
                    logging.exception(
                        "Failed to process image %s",
                        member.name,
                    )

        # No successfully processed images means the result is unknown,
        # not zero.
        if total_images == 0:
            return empty_result.copy()

        return {
            "total_images": total_images,
            "images_with_varroa": images_with_varroa,
            "total_varroa_detected": total_varroa,
            "average_varroa_per_image": round(
                total_varroa / total_images,
                3,
            ),
        }

    except Exception:
        logging.exception(
            "Failed to process Varroa archive %s",
            tar_file_name,
        )
        return empty_result.copy()

    finally:
        if runner is not None:
            try:
                runner.stop()
            except Exception:
                logging.exception(
                    "Failed to stop the Varroa model runner"
                )

        tar_buffer.close()


# =========================================================
# SENSORS
# =========================================================
def stop_system(url):
    url = url.removeprefix("http://").removeprefix("https://")
    url = "http://" + url.rstrip("/") + "/stop"

    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.json()


def stop_sensors(beehive_name):
    for sensor in ("entrance", "camera"):
        try:
            url = beehive_endpoints[sensor][beehive_name]
            stop_system(url)
        except Exception:
            logging.exception(
                "Failed to stop %s for %s",
                sensor,
                beehive_name,
            )


def start_system(url):
    url = url.removeprefix("http://").removeprefix("https://")
    url = "http://" + url.rstrip("/") + "/start"

    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.json()


def start_sensors(beehive_name):
    for sensor in ("entrance", "camera"):
        try:
            url = beehive_endpoints[sensor][beehive_name]
            start_system(url)
        except Exception:
            logging.exception(
                "Failed to start %s for %s",
                sensor,
                beehive_name,
            )


def get_sensor_observations(beehive_name):
    try:
        beehive_base_url = beehive_endpoints["base"][beehive_name]
        beehive_entrance_url = beehive_endpoints["entrance"][beehive_name]
        beehive_camera_url = beehive_endpoints["camera"][beehive_name]

        # -------------------------------------------------
        # Base control data
        # -------------------------------------------------
        beehive_base_observations = fetch_csv_observations(
            beehive_base_url,
            "BBC",
            beehive_name,
            days_range=1,
        )

        beehive_base_data = {
            "mass_kg": get_min_avg_max(
                beehive_base_observations,
                "Loadcell_ch1_kg",
            ),
            "temperature_C": get_min_avg_max(
                beehive_base_observations,
                "Temperature_C",
            ),
            "humidity_percent": get_min_avg_max(
                beehive_base_observations,
                "Humidity_%",
            ),
        }

        # -------------------------------------------------
        # Entrance counter data
        # -------------------------------------------------
        beehive_entrance_observations = fetch_csv_observations(
            beehive_entrance_url,
            "BEC",
            beehive_name,
            days_range=1,
        )

        beehive_entrance_data = {
            "total_incoming_bees": get_last_row_value(
                beehive_entrance_observations,
                "In_sum",
            ),
            "total_outgoing_bees": get_last_row_value(
                beehive_entrance_observations,
                "Out_sum",
            ),
        }

        # -------------------------------------------------
        # Visual Varroa detector
        # -------------------------------------------------
        beehive_camera_data = fetch_varroa_data(
            beehive_camera_url,
            beehive_name,
        )

        total_images = beehive_camera_data["total_images"]
        images_with_varroa = beehive_camera_data["images_with_varroa"]

        if (
            total_images is not None
            and images_with_varroa is not None
            and total_images > 0
        ):
            detected_varroa_ratio = _to_python_number(
                images_with_varroa / total_images * 100
            )
        else:
            detected_varroa_ratio = None

        # -------------------------------------------------
        # Observations
        # -------------------------------------------------
        observation_time = oa_function.get_current_ISO_time()

        formatted_data = {
            "observation_type": "sensor",
            "observation_timestamp": observation_time,
            "observation_period": "previous_utc_calendar_day",
            "beehive_name": beehive_name,

            "beehive_mass": {
                "description": (
                    "Total mass of the beehive, measured by load cell "
                    "during the observation period."
                ),
                **beehive_base_data["mass_kg"],
                "unit": "kg",
            },

            "temperature": {
                "description": (
                    "Temperature inside the beehive recorded during "
                    "the observation period."
                ),
                **beehive_base_data["temperature_C"],
                "unit": "°C",
            },

            "humidity": {
                "description": (
                    "Relative humidity inside the beehive recorded "
                    "during the observation period."
                ),
                **beehive_base_data["humidity_percent"],
                "unit": "%",
            },

            "total_incoming_bees": {
                "description": (
                    "Latest cumulative incoming-bee counter value "
                    "recorded during the observation period."
                ),
                "value": beehive_entrance_data[
                    "total_incoming_bees"
                ],
            },

            "total_outgoing_bees": {
                "description": (
                    "Latest cumulative outgoing-bee counter value "
                    "recorded during the observation period."
                ),
                "value": beehive_entrance_data[
                    "total_outgoing_bees"
                ],
            },

            "varroa_detection": {
                "inspected_images": {
                    "description": (
                        "Number of images successfully inspected "
                        "by the Varroa detection model."
                    ),
                    "value": total_images,
                },

                "images_with_varroa": {
                    "description": (
                        "Number of inspected images containing at "
                        "least one detected Varroa mite."
                    ),
                    "value": images_with_varroa,
                },

                "detected_varroa_ratio": {
                    "description": (
                        "Percentage of inspected images in which "
                        "at least one Varroa mite was detected."
                    ),
                    "value": detected_varroa_ratio,
                    "unit": "%",
                },
            },
        }
        details_json = json.dumps(
            formatted_data,
            allow_nan=False,
        )

        formatted_data_hash = oa_function.get_dict_hash(
            formatted_data
        )

        token = oa_gatekeeper.login(
            gatekeeper_base_url,
            username,
            password,
        )

        parcel_id = oa_parcel.get_one_parcel_id(
            farm_calendar_base_url,
            token["access"],
            beehive_name,
        )

        activity_type_id = oa_activity_type.get_one_activity_type_id(
            farm_calendar_base_url,
            token["access"],
            "Hive sensor data aggregation",
        )

        observation_data = {
            "activityType": activity_type_id,
            "title": (
                f"{beehive_name}_beehive data_"
                f"{formatted_data_hash}"
            ),
            "details": details_json,
            "phenomenonTime": observation_time,
            "hasAgriParcel": parcel_id,
            "hasResult": {
                "unit": "1",
                "hasValue": "details",
            },
            "observedProperty": "beehive",
        }

        return oa_observation.create_observation(
            farm_calendar_base_url,
            token["access"],
            observation_data,
        )

    except Exception as e:
        logging.exception(
            "Failed to process sensor observations for %s",
            beehive_name,
        )
        return {"error": str(e)}


# =========================================================
# WEATHER
# =========================================================
def get_weather_observations(beehive_name):
    try:
        result = {}
        data = {}

        token = oa_gatekeeper.login(
            gatekeeper_base_url,
            username,
            password
        )

        parcel_id = oa_parcel.get_one_parcel_id(
            farm_calendar_base_url,
            token["access"],
            beehive_name
        )

        location = oa_parcel.get_one_parcel_location(
            farm_calendar_base_url,
            token["access"],
            parcel_id
        )

        forecast = oa_weather.weather_forecast(
            weather_base_url,
            token["access"],
            location["latitude"],
            location["longitude"]
        )

        normalized_forecast = oa_weather.normalize_forecast(
            forecast
        )

        data["Good Beekeeping Weather"] = (
            oa_weather.is_good_for_beekeeping(
                normalized_forecast
            )
        )

        data["Formic Acid Treatment Weather"] = (
            oa_weather.is_suitable_for_formic_acid_treatment(
                normalized_forecast
            )
        )

        model_names = [
            "Honey Bee Hive Cycle",
            "Honey Bee Bloom Availability",
            "Honey Bee Bloom Trigger",
            "Honey Bee Activity",
            "Honey Bee Heat Stress",
            "Honey Bee Varroa Brood Pressure"
        ]

        for model_name in model_names:
            data[model_name] = {
                "description": oa_risk.get_one_risk_model_description(
                    risk_base_url,
                    token["access"],
                    model_name
                ),
                "descriptor": oa_risk.gdd_estimate(
                    risk_base_url,
                    token["access"],
                    parcel_id,
                    model_name
                )
            }

        formatted_data = data

        formatted_data_hash = oa_function.get_dict_hash(
            formatted_data
        )

        activity_type_id = oa_activity_type.get_one_activity_type_id(
            farm_calendar_base_url,
            token["access"],
            "Hive weather data aggregation"
        )

        observation_time = oa_function.get_current_ISO_time()

        observation_data = {
            "activityType": activity_type_id,
            "title": (
                beehive_name +
                "_weather data_" +
                formatted_data_hash
            ),
            "details": json.dumps(formatted_data),
            "phenomenonTime": observation_time,
            "hasAgriParcel": parcel_id,
            "hasResult": {
                "unit": "1",
                "hasValue": "details"
            },
            "observedProperty": "weather"
        }

        result = oa_observation.create_observation(
            farm_calendar_base_url,
            token["access"],
            observation_data
        )

        return result

    except Exception as e:
        logging.exception(
            "Failed to process weather observations for %s",
            beehive_name,
        )
        return {"error": str(e)}


# =========================================================
# COMMUNITY
# =========================================================
def get_community_observations(beehive_name):
    try:
        token = oa_gatekeeper.login(
            gatekeeper_base_url,
            username,
            password
        )

        parcel_id = oa_parcel.get_one_parcel_id(
            farm_calendar_base_url,
            token["access"],
            beehive_name
        )

        location = oa_parcel.get_one_parcel_location(
            farm_calendar_base_url,
            token["access"],
            parcel_id
        )

        blooming_url = community_endpoints["community"]["blooming"]
        meadows_url = community_endpoints["community"]["meadows"]
        varroa_url = community_endpoints["community"]["varroa"]
        spraying_url = community_endpoints["community"]["spraying"]

        blooming_observations = fetch_csv_observations(
            blooming_url,
            "BCI",
            "",
            days_range=14
        )

        meadows_observations = fetch_csv_observations(
            meadows_url,
            "MCI",
            "",
            days_range=14
        )

        varroa_observations = fetch_csv_observations(
            varroa_url,
            "VCI",
            "",
            days_range=14
        )

        spraying_observations = fetch_csv_observations(
            spraying_url,
            "SCI",
            "",
            days_range=14
        )

        latitude = location["latitude"]
        longitude = location["longitude"]

        blooming_radius_km = 3.0
        meadows_radius_km = 3.0
        varroa_radius_km = 3.0
        spraying_radius_km = 3.0

        blooming_estimation = estimate_blooming_area(
            blooming_observations,
            latitude,
            longitude,
            blooming_radius_km
        )

        meadows_estimation = estimate_mowing_area(
            meadows_observations,
            latitude,
            longitude,
            meadows_radius_km
        )

        varroa_estimation = estimate_varroa_mite_presence(
            varroa_observations,
            latitude,
            longitude,
            varroa_radius_km
        )

        spraying_estimation = estimate_spraying_area(
            spraying_observations,
            latitude,
            longitude,
            spraying_radius_km
        )

        observation_time = oa_function.get_current_ISO_time()

        formatted_data = {
            "observation_type": "community",
            "observation_timestamp": observation_time,

            "observation_radius": {
                "blooming": {
                    "value": blooming_radius_km,
                    "unit": "km",
                    "description": (
                        "Radius around the beehive within which "
                        "community blooming observations are considered."
                    )
                },
                "meadows": {
                    "value": meadows_radius_km,
                    "unit": "km",
                    "description": (
                        "Radius around the beehive within which "
                        "community meadow observations are considered."
                    )
                },
                "varroa": {
                    "value": varroa_radius_km,
                    "unit": "km",
                    "description": (
                        "Radius around the beehive within which "
                        "community Varroa observations are considered."
                    )
                },
                "spraying": {
                    "value": spraying_radius_km,
                    "unit": "km",
                    "description": (
                        "Radius around the beehive within which "
                        "community spraying observations are considered."
                    )
                }
            },

            "estimated_blooming_area": {
                "description": (
                    f"Estimated area of blooming vegetation within "
                    f"{blooming_radius_km} km of the beehive. The estimate "
                    "is based on recent community blooming observations "
                    "weighted by reported area and confidence."
                ),
                "value": blooming_estimation,
                "unit": "m2"
            },

            "estimated_mowing_area": {
                "description": (
                    f"Estimated area of meadows that may be affected by "
                    f"mowing within {meadows_radius_km} km of the beehive. "
                    "The estimate is based on recent community meadow "
                    "observations weighted by reported area, confidence, "
                    "and vegetation type."
                ),
                "value": meadows_estimation,
                "unit": "m2"
            },

            "varroa_mite_presence": {
                "description": (
                    f"Number of community beehives within "
                    f"{varroa_radius_km} km of the beehive in which a "
                    "Varroa mite type was detected. Values are grouped "
                    "by reported mite type."
                ),
                "value": varroa_estimation,
                "unit": "beehives"
            },

            "estimated_spraying_area": {
                "description": (
                    f"Estimated area affected by planned pesticide "
                    f"spraying within {spraying_radius_km} km of the "
                    "beehive. Only pesticide events planned from one "
                    "to seven days ahead are included. The estimate "
                    "is weighted by reported area, confidence, and "
                    "harmfulness."
                ),
                "value": spraying_estimation,
                "unit": "m2"
            }
        }

        formatted_data_hash = oa_function.get_dict_hash(
            formatted_data
        )

        activity_type_id = oa_activity_type.get_one_activity_type_id(
            farm_calendar_base_url,
            token["access"],
            "Hive community data aggregation"
        )

        observation_data = {
            "activityType": activity_type_id,
            "title": (
                beehive_name +
                "_community data_" +
                formatted_data_hash
            ),
            "details": json.dumps(formatted_data),
            "phenomenonTime": observation_time,
            "hasAgriParcel": parcel_id,
            "hasResult": {
                "unit": "1",
                "hasValue": "details"
            },
            "observedProperty": "community"
        }

        result = oa_observation.create_observation(
            farm_calendar_base_url,
            token["access"],
            observation_data
        )

        return result

    except Exception as e:
        logging.exception(
            "Failed to process community observations for %s",
            beehive_name,
        )
        return {"error": str(e)}


def estimate_blooming_area(observations, latitude, longitude, radius_km):
    if observations.empty:
        return 0

    area_values = {
        "tiny": 1,
        "mini": 9,
        "small": 49,
        "unit": 100,
        "medium": 900,
        "large": 4900,
        "huge": 10000
    }

    confidence_weights = {
        "tiny": 0.95,
        "mini": 0.90,
        "small": 0.85,
        "unit": 0.75,
        "medium": 0.60,
        "large": 0.40,
        "huge": 0.25
    }

    observations = observations.copy()
    observations["distance"] = observations.apply(
        lambda row: oa_function.get_geographical_distance(
            {
                "latitude": latitude,
                "longitude": longitude
            },
            {
                "latitude": row["Latitude"],
                "longitude": row["Longitude"]
            }
        ),
        axis=1
    )
    observations = observations[observations["distance"] <= radius_km]
    if observations.empty:
        return 0

    observations["weighted_area"] = (
        observations["Area"].map(area_values) *
        observations["Area"].map(confidence_weights)
    )

    return observations["weighted_area"].sum()


def estimate_spraying_area(observations, latitude, longitude, radius_km):
    if observations.empty:
        return 0

    area_values = {
        "tiny": 1,
        "mini": 9,
        "small": 49,
        "unit": 100,
        "medium": 900,
        "large": 4900,
        "huge": 10000
    }

    confidence_weights = {
        "tiny": 0.95,
        "mini": 0.90,
        "small": 0.85,
        "unit": 0.75,
        "medium": 0.60,
        "large": 0.40,
        "huge": 0.25
    }

    harmful_weights = {
        True: 2.0,
        False: 1.0
    }

    now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
    start_ms = now_ms + 1 * 24 * 60 * 60 * 1000
    end_ms = now_ms + 7 * 24 * 60 * 60 * 1000

    observations = observations.copy()

    observations["distance"] = observations.apply(
        lambda row: oa_function.get_geographical_distance(
            {
                "latitude": latitude,
                "longitude": longitude
            },
            {
                "latitude": row["Latitude"],
                "longitude": row["Longitude"]
            }
        ),
        axis=1
    )

    observations = observations[
        (observations["distance"] <= radius_km) &
        (observations["Type"] == "pesticide") &
        (observations["Start_time_ms"] >= start_ms) &
        (observations["Start_time_ms"] <= end_ms)
    ]

    if observations.empty:
        return 0

    observations["weighted_area"] = (
        observations["Area"].map(area_values) *
        observations["Area"].map(confidence_weights) *
        observations["Harmful"].map(harmful_weights)
    )

    return observations["weighted_area"].sum()


def estimate_mowing_area(observations, latitude, longitude, radius_km):
    if observations.empty:
        return 0

    area_values = {
        "tiny": 1,
        "mini": 9,
        "small": 49,
        "unit": 100,
        "medium": 900,
        "large": 4900,
        "huge": 10000
    }

    confidence_weights = {
        "tiny": 0.95,
        "mini": 0.90,
        "small": 0.85,
        "unit": 0.75,
        "medium": 0.60,
        "large": 0.40,
        "huge": 0.25
    }

    type_weights = {
        "grass_dominant": 0.30,
        "mixed": 0.70,
        "flower_rich": 1.00,
        "unknown": 0.50
    }

    observations = observations.copy()

    observations["distance"] = observations.apply(
        lambda row: oa_function.get_geographical_distance(
            {
                "latitude": latitude,
                "longitude": longitude
            },
            {
                "latitude": row["Latitude"],
                "longitude": row["Longitude"]
            }
        ),
        axis=1
    )
    observations = observations[observations["distance"] <= radius_km]
    if observations.empty:
        return 0

    observations["weighted_area"] = (
        observations["Area"].map(area_values) *
        observations["Area"].map(confidence_weights) *
        observations["Type"].map(type_weights)
    )

    return observations["weighted_area"].sum()


def estimate_varroa_mite_presence(observations, latitude, longitude, radius_km):
    if observations.empty:
        return {}

    observations = observations.copy()

    observations["distance"] = observations.apply(
        lambda row: oa_function.get_geographical_distance(
            {
                "latitude": latitude,
                "longitude": longitude
            },
            {
                "latitude": row["Latitude"],
                "longitude": row["Longitude"]
            }
        ),
        axis=1
    )
    observations = observations[observations["distance"] <= radius_km]
    if observations.empty:
        return {}

    observations = observations.dropna(subset=["Type", "Quantity"])

    return (
        observations
        .groupby("Type", sort=False)["Quantity"]
        .sum()
        .to_dict()
    )


# =========================================================
# TASKS
# =========================================================
def task_a():
    time.sleep(2)
    if (not EDGE_MODE):
        get_community_observations("A1")
        get_weather_observations("A1")

    stop_sensors("A1")
    get_sensor_observations("A1")
    start_sensors("A1")


def task_b():
    time.sleep(2)


def task_c():
    time.sleep(2)


def task_d():
    time.sleep(2)


# =========================================================
# EXECUTOR
# =========================================================
def execute_task(task):
    try:
        result = task()
        return {
            "task": task.__name__,
            "status": "success",
            "result": result
        }
    except Exception as e:
        return {
            "task": task.__name__,
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc()
        }


# =========================================================
# Aggregation JOB DEFINITIONS (UTC hour -> tasks)
# =========================================================
JOB_MAP = {
    0: [task_a, task_b],
    1: [task_c],
    2: [task_d],
}


# =========================================================
# Aggregation JOB EXECUTION
# =========================================================
def job(hour, tasks):
    job_name = f"Aggregation Job {hour}"
    start_time = datetime.now(timezone.utc)

    logger.info(f"[{job_name}] START | time={start_time.isoformat()}")

    if not tasks:
        logger.info(f"[{job_name}] EMPTY_TASK_LIST")
        return

    with Pool(processes=3) as pool:
        results = pool.map(execute_task, tasks)

    end_time = datetime.now(timezone.utc)

    successes = [r for r in results if r["status"] == "success"]
    failures = [r for r in results if r["status"] == "error"]

    logger.info(
        f"[{job_name}] END | time={end_time.isoformat()} | "
        f"success={len(successes)} failed={len(failures)}"
    )

    for f in failures:
        logger.error(
            f"[{job_name}] TASK_FAIL | task={f['task']} | error={f['error']}"
        )
        logger.debug(
            f"[{job_name}] TRACEBACK\n{f['traceback']}"
        )


# =========================================================
# setTime TARGET IPs
# =========================================================
broadcast_utc_time_address_list = list(dict.fromkeys(
    address
    for section in ("base", "entrance", "camera")
    for address in beehive_endpoints[section].values()
))


# =========================================================
# setTime JOB
# =========================================================
def send_time_to_address(address):
    job_name = "setTime Job"
    try:
        utc_now = datetime.now(timezone.utc).isoformat()

        url = f"{address}/setTime"

        response = requests.get(
            url,
            params={"utc_time": utc_now},
            timeout=5
        )

        logger.info(
            f"[{job_name}] SEND_SUCCESS | address={address} | status={response.status}"
        )

        return {"address": address, "status": "ok"}

    except Exception as e:
        logger.error(
            f"[{job_name}] SEND_FAIL | address={address} | error={str(e)}"
        )
        return {"address": address, "status": "error", "error": str(e)}


def broadcast_utc_time():
    job_name = "setTime Job"
    start_time = datetime.now(timezone.utc)

    logger.info(f"[{job_name}] START | time={start_time.isoformat()}")

    with Pool(processes=3) as pool:
        results = pool.map(send_time_to_address, broadcast_utc_time_address_list)

    success = sum(1 for r in results if r["status"] == "ok")
    failed = len(results) - success

    logger.info(
        f"[{job_name}] END | success={success} failed={failed}"
    )


# =========================================================
# SCHEDULER ENTRY
# =========================================================
def start_job(hour):
    logger.info(f"Trigger received for hour {hour}")
    tasks = JOB_MAP.get(hour, [])
    job(hour, tasks)


# =========================================================
# START
# =========================================================
def start_aggregator():
    logger.info("Scheduler started (UTC mode)")

    scheduler = BackgroundScheduler(timezone=timezone.utc)

    for hour in JOB_MAP.keys():
        scheduler.add_job(
            func=start_job,
            trigger="cron",
            hour=hour,
            minute=0,
            id=f"job_{hour}",
            args=[hour],
            max_instances=1,
            coalesce=False,
            replace_existing=True
        )

    scheduler.add_job(
        func=broadcast_utc_time,
        trigger="cron",
        minute="*/10",
        id="utc_broadcast",
        max_instances=1,
        coalesce=False,
        replace_existing=True
    )

    scheduler.start()

    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler shutting down")
        scheduler.shutdown()


# =========================================================
# MAIN
# =========================================================
def main():
    start_aggregator()


if __name__ == "__main__":
    main()
