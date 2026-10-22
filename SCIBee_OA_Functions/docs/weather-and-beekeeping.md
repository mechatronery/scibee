# Weather and Beekeeping Helper Functions

**Module:** `oa_weather.py`

Provides utilities for retrieving weather data from OpenAgri services, analysing weather forecasts, and evaluating forecast suitability for beekeeping activities and formic acid treatment against Varroa mites.

### Features

- **Current weather:** Retrieve current weather conditions for specified geographic coordinates.
- **Weather forecast:** Retrieve forecast data and group measurements by type and timestamp.
- **Normalise forecasts:** Convert API weather data into a consistent internal format.
- **Analyse forecasts:** Calculate summary statistics, including minimum, maximum, range, mean, and total values.
- **Evaluate beekeeping conditions:** Assess weather suitability for bee flight and foraging.
- **Evaluate Varroa treatment conditions:** Assess forecast suitability for formic acid treatment based on temperature, humidity, wind, and precipitation.
- **Generate recommendations:** Convert weather evaluation scores into human-readable interpretations.

### Forecast Input Requirements

Forecast analysis and evaluation functions expect a **list of dictionaries**, with one dictionary per forecast interval.

Each entry must contain the following numeric fields:

| Field         | Unit  | Description                         |
| ------------- | ----- | ----------------------------------- |
| `temperature` | °C    | Ambient air temperature             |
| `humidity`    | %     | Relative humidity                   |
| `wind_speed`  | m/s   | Wind speed                          |
| `rain_mm`     | mm/3h | Precipitation per forecast interval |

#### Example

```python
forecast = [
    {
        "temperature": 18.5,
        "humidity": 65,
        "wind_speed": 2.1,
        "rain_mm": 0.0
    },
    {
        "temperature": 22.0,
        "humidity": 58,
        "wind_speed": 3.0,
        "rain_mm": 0.2
    }
]
```

#### Forecast Normalisation

`normalize_forecast(weather_data)` converts API measurement series into the normalised forecast format.

| API measurement type  | Normalised field |
| --------------------- | ---------------- |
| `ambient_temperature` | `temperature`    |
| `ambient_humidity`    | `humidity`       |
| `wind_speed`          | `wind_speed`     |
| `precipitation`       | `rain_mm`        |

The input must contain a `values` list for each measurement type. All lists must have equal lengths, with corresponding values representing the same forecast intervals.

Forecast entries should contain all four fields, use numeric values, and represent chronological intervals. The forecast should contain at least one entry. Rainfall is expressed per forecast interval, not necessarily as daily precipitation.

### Weather Analysis Models

The module implements two rule-based weather scoring models. Each evaluates forecast statistics against configurable thresholds and calculates a weighted suitability score from 0 to 100.

#### 1. Beekeeping Weather Model

**Function:** `is_good_for_beekeeping(forecast)`

Evaluates weather suitability for bee flight and foraging using:

- **Temperature:** Mean, low-period mean, high-period mean, minimum, maximum, and temperature range.
- **Humidity:** Mean and maximum relative humidity.
- **Wind:** Mean, high-period mean, and maximum wind speed.
- **Precipitation:** Mean, high-period mean, maximum, and total rainfall.
- **Flying conditions:** Proportion of forecast intervals meeting configured temperature, wind, and rainfall criteria.

#### 2. Formic Acid Treatment Model

**Function:** `is_suitable_for_formic_acid_treatment(forecast)`

Evaluates forecast suitability for formic acid treatment against Varroa mites using:

- **Temperature:** Mean, low-period mean, high-period mean, minimum, maximum, and temperature range.
- **Humidity:** Mean and maximum relative humidity.
- **Wind:** Mean and maximum wind speed.
- **Precipitation:** Mean, maximum, and total rainfall.
- **Stable evaporation conditions:** Proportion of forecast intervals meeting configured temperature, humidity, wind, and rainfall criteria.

### Forecast Analysis Functions

- `analyze_forecast(forecast, variable)`: Calculates statistics for a specified variable.
- `analyze_forecast_all(forecast)`: Calculates statistics for all variables in the forecast.

The calculated statistics include the number of values, minimum, maximum, range, mean, mean of the lowest 25% of values, mean of the highest 25% of values, and total.

### Scoring and Interpretation

Each model uses configurable thresholds and weights defined in its corresponding parameter dictionary. Every passed check contributes its assigned weight to the score, which is normalised to a percentage.

| Score    | Beekeeping interpretation      | Formic acid treatment interpretation               |
| -------- | ------------------------------ | -------------------------------------------------- |
| 85–100   | Excellent bee weather          | Excellent conditions for formic acid treatment     |
| 70–84.9  | Acceptable for normal activity | Suitable conditions for formic acid treatment      |
| 50–69.9  | Limited bee activity           | Marginal conditions; monitor evaporation carefully |
| Below 50 | Poor conditions                | Poor conditions for formic acid treatment          |

Each evaluation returns a dictionary containing:

- `interpretation`: Human-readable assessment.
- `score`: Weighted suitability score as a percentage.
- `checks`: Individual threshold results (`True` or `False`).
- `metrics`: Calculated forecast statistics and suitable-period counts or ratios.

Thresholds and weights can be customised through the optional `parameters` and `weights` arguments of the evaluation functions.

**Note:** These models provide rule-based decision support, not guarantees of bee activity or treatment safety. Actual conditions depend on local weather, colony status, and the specific treatment product. Always follow the product label and applicable veterinary guidance before applying formic acid.
