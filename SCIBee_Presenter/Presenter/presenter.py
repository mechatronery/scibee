from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv
import os

from oa_functions import oa_gatekeeper
from oa_functions import oa_observation


# =========================================================
# CONFIGURATION
# =========================================================

app = Flask(__name__, static_folder="www", static_url_path="")

load_dotenv()

username = os.getenv("ADMIN_USERNAME")
password = os.getenv("ADMIN_PASSWORD")
gatekeeper_base_url = os.getenv("GATEKEEPER_BASE_URL")
farm_calendar_base_url = os.getenv("FARM_CALENDAR_BASE_URL")


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():
    return send_from_directory("www", "index.html")


# =========================================================
# HEALTH CHECK
# =========================================================

@app.route("/health")
def health():
    return {"status": "ok"}, 200


# =========================================================
# GET SUMMARY
# =========================================================

@app.route("/summary", methods=["GET"])
def getSummary():
    try:
        beehive_name = request.args.get("beehive_name") or ""

        token = oa_gatekeeper.login(
            gatekeeper_base_url,
            username,
            password
        )

        observations = oa_observation.create_data_from_observations(
            farm_calendar_base_url,
            token["access"],
            14,
            beehive_name
        )

        # Filter observations by activity type
        evaluation_observations = [
            observation
            for observation in observations
            if observation.get("activityType_name") == "Hive data evaluation"
        ]

        # Find the latest observation
        latest_observation = max(
            evaluation_observations,
            key=lambda observation: observation.get("phenomenonTime", ""),
            default=None
        )

        # Return only the required fields
        if latest_observation:
            result = {
                "name": latest_observation.get("hasAgriParcel_name"),
                "time": latest_observation.get("phenomenonTime"),
                "summary": latest_observation.get("details")
            }
        else:
            result = None

        return jsonify(result), 200

    except Exception:
        app.logger.exception("Failed to retrieve summary.")
        return jsonify({
            "error": "Failed to retrieve summary"
        }), 500
