# SCIBee Helper Functions for OpenAgri Services

Helper functions developed for the SCIBee project to interact with OpenAgri services through their REST APIs. The modules support data synchronisation using JSON files and provide functionality for managing agricultural records, analysing weather conditions, evaluating risk models, and working with observations and alerts.

The helper modules can be downloaded and incorporated into existing Python projects or used as a foundation for applications that build upon OpenAgri services.

## Requirements

- Python 3 (specify the minimum supported version).
- Access to the relevant OpenAgri services.
- A valid JWT access token for authenticated operations.
- Required Python packages, as specified in the relevant module documentation.

## Installation

Download or clone the repository and place the required helper modules in your Python project. Install the dependencies required by the modules you intend to use.

## Available Modules

| Module                | Description                                                                                    |
| --------------------- | ---------------------------------------------------------------------------------------------- |
| `oa_function.py`      | General utilities for JSON files, dates, geographical calculations, hashing, and HTTP logging. |
| `oa_gatekeeper.py`    | Authentication, token management, and OpenAgri service discovery.                              |
| `oa_farm.py`          | Farm record management and data import/export.                                                 |
| `oa_parcel.py`        | Agricultural parcel management and farm associations.                                          |
| `oa_weather.py`       | Weather retrieval, forecast analysis, and beekeeping suitability evaluation.                   |
| `oa_risk_model.py`    | Risk model management and Growing Degree Day (GDD) estimates.                                  |
| `oa_observation.py`   | Observation record management and filtering.                                                   |
| `oa_activity_type.py` | Activity type management.                                                                      |
| `oa_alert.py`         | Alert record management and filtering.                                                         |

## Documentation

See the following guides for detailed descriptions:

- [General Helper Functions](docs/general-functions.md)
- [Authentication and Gatekeeper](docs/authentication.md)
- [Farm and Parcel Management](docs/farm-and-parcel.md)
- [Weather and Beekeeping](docs/weather-and-beekeeping.md)
- [Risk Models and GDD](docs/risk-models-and-gdd.md)
- [Observations, Activity Types, and Alerts](docs/observations-activities-alerts.md)

## Important Notes

Weather and GDD models provide estimates and decision support rather than guarantees of biological conditions or treatment safety. Follow applicable product labels and veterinary guidance when making treatment decisions.

Operations that delete records should be used with care.
