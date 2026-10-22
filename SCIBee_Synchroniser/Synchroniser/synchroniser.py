from flask import Flask, request, jsonify, send_from_directory
from datetime import datetime, timezone
from dotenv import load_dotenv
import json
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
# DOWNLOAD OBSERVATIONS
# =========================================================

@app.route("/download", methods=["GET"])
def downloadObservations():
    try:
        beehive_name = request.args.get("beehive_name") or ""

        # Number of days to retrieve; defaults to 7.
        days = request.args.get("days", default=7, type=int)

        if days < 1:
            return jsonify({
                "error": "Days must be at least 1"
            }), 400

        app.logger.info(
            "Retrieving observations for the last %s days",
            days
        )

        token = oa_gatekeeper.login(
            gatekeeper_base_url,
            username,
            password
        )

        observations = oa_observation.create_data_from_observations(
            farm_calendar_base_url,
            token["access"],
            days,
            beehive_name
        )

        # Return the observation data directly as a JSON download.
        timestamp = datetime.now(timezone.utc).strftime(
            "%Y_%m_%dT%H_%M_%SZ"
        )
        filename = f"scibee_OBS_sync_{timestamp}.json"

        response = app.response_class(
            response=json.dumps(observations, indent=2),
            status=200,
            mimetype="application/json"
        )
        response.headers["Content-Disposition"] = (
            f'attachment; filename="{filename}"'
        )

        return response

    except Exception:
        app.logger.exception("Failed to retrieve observations")
        return jsonify({
            "error": "Failed to retrieve observations"
        }), 500


# =========================================================
# UPLOAD OBSERVATIONS
# =========================================================

@app.route("/upload", methods=["POST"])
def uploadObservations():
    try:
        uploaded_file = request.files.get("file")
        if uploaded_file:
            observations_data = json.load(uploaded_file)
        else:
            observations_data = request.get_json(silent=True)

        if observations_data is None:
            return jsonify({
                "error": "No JSON file or JSON request body received"
            }), 400

        if not isinstance(observations_data, list):
            return jsonify({
                "error": "Expected a JSON array of observations"
            }), 400

        token = oa_gatekeeper.login(
            gatekeeper_base_url,
            username,
            password
        )

        result = oa_observation.create_observations_from_data(
            farm_calendar_base_url,
            token["access"],
            observations_data
        )

        return jsonify({
            "status": "ok",
            "count": len(result),
            "results": result
        }), 200

    except json.JSONDecodeError:
        return jsonify({
            "error": "Uploaded file is not valid JSON"
        }), 400

    except Exception:
        app.logger.exception("Failed to upload observations")
        return jsonify({
            "error": "Failed to upload observations"
        }), 500
