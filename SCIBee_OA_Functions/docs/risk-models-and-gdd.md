# Risk Models and Growing Degree Days (GDD)

## Risk Model Helper Functions

**Module:** `oa_risk_model.py`

Provides utilities for managing risk models in OpenAgri services and estimating honey bee seasonal development, bloom availability, bee activity, heat stress, and Varroa brood pressure using Growing Degree Days (GDD).

### Features

- **List risk models:** Retrieve risk model names and their associated IDs.
- **Look up risk models:** Retrieve a risk model ID or description by name.
- **Create risk models:** Validate model data against a JSON Schema and create new records, skipping models that already exist.
- **Create default honey bee models:** Add the predefined honey bee risk models to OpenAgri.
- **Import risk models:** Create risk model records from a data file.
- **Export risk models:** Retrieve risk models, including their GDD thresholds and descriptors, and save them to a file.
- **Delete risk models:** Delete all accessible risk model records.
- **Estimate GDD stages:** Retrieve the latest GDD-based descriptor for a specified parcel and risk model.
- **Determine analysis periods:** Select the start date according to the model's analysis period, such as the start of the year or a recent rolling period.

## Built-in Honey Bee Models

The module defines six predefined models for assessing seasonal conditions and colony development.

| Model                             | Analysis period | Base temperature | Purpose                                                                              |
| --------------------------------- | --------------- | ---------------- | ------------------------------------------------------------------------------------ |
| `Honey Bee Hive Cycle`            | Year to date    | 10°C             | Estimates seasonal colony development, from winter clustering to winter preparation. |
| `Honey Bee Bloom Availability`    | Year to date    | 5°C              | Estimates seasonal nectar and pollen availability.                                   |
| `Honey Bee Bloom Trigger`         | Rolling 14 days | 5°C              | Estimates short-term potential for bloom activation.                                 |
| `Honey Bee Activity`              | Rolling 14 days | 10°C             | Estimates recent bee activity potential.                                             |
| `Honey Bee Heat Stress`           | Rolling 7 days  | 30°C             | Estimates accumulated heat stress from high temperatures.                            |
| `Honey Bee Varroa Brood Pressure` | Rolling 28 days | 10°C             | Estimates brood development and potential for Varroa reproduction.                   |

Each model defines GDD intervals with corresponding descriptors. The GDD calculation and thresholds are handled by the OpenAgri service; this module retrieves the resulting descriptor for a parcel.

## Analysis Functions

- `get_gdd_start_date(model_name)`: Determines the analysis start date for a model based on its configured period.
- `gdd_estimate(base_url, jwt_token_access, parcel_id, model_name)`: Retrieves the latest GDD observation descriptor for a parcel and model.

The `gdd_estimate` function uses the model's configured start date and the previous day's date as the analysis end date. It returns the latest available observation descriptor, or an empty string if no result is available or an error occurs.

## Risk Model Data Requirements

Risk model records must conform to the module's JSON Schema and contain the following fields.

| Field         | Type   | Description                                     |
| ------------- | ------ | ----------------------------------------------- |
| `name`        | String | Risk model name.                                |
| `eppo_code`   | String | EPPO code associated with the model.            |
| `base_gdd`    | Number | Base temperature used for GDD calculations.     |
| `description` | String | Description of the model.                       |
| `gdd_points`  | Array  | GDD intervals and their associated descriptors. |

Each `gdd_points` entry must contain numeric `start` and `end` values and a non-empty string `descriptor`. The array must contain at least one entry. Additional properties are not permitted by the schema.

**Note:** The predefined models provide estimates based on accumulated temperature and configured thresholds. They do not directly measure colony condition, actual bloom availability, bee activity, heat stress, or Varroa population levels. Interpret results alongside local observations and other relevant data.
