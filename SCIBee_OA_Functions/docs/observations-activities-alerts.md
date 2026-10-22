# Observations, Activity Types, and Alerts

## Observation Helper Functions

**Module:** `oa_observation.py`

Provides utilities for managing observation records associated with agricultural parcels and activity types in OpenAgri services.

### Features

- **List observations:** Retrieve observation titles and IDs.
- **Look up observations:** Find observation IDs by title or retrieve observation identifiers by ID.
- **Filter observations:** Retrieve observations by parcel, activity type, and date range.
- **Create observations:** Validate observation data using JSON Schema and create new records, skipping existing observations.
- **Import observations:** Create observation records from a data file or a list of dictionaries, resolving parcel and activity type names to IDs.
- **Export observations:** Retrieve observations from a specified date range, optionally filter by title prefix, and save their data to a file or pass as a list of dictionaries.
- **Delete observations:** Delete all accessible observation records.

## Activity Type Helper Functions

**Module:** `oa_activity_type.py`

Provides utilities for managing activity type records in OpenAgri services.

### Features

- **List activity types:** Retrieve activity type names and IDs.
- **Look up activity types:** Find activity type IDs by name or activity type names by ID.
- **Create activity types:** Validate activity type data using JSON Schema and create new records, skipping existing activity types.
- **Import activity types:** Create activity type records from a data file.
- **Export activity types:** Retrieve existing activity types and save their names, descriptions, categories, and colour settings to a file.
- **Delete activity types:** Delete all accessible activity type records.

### Default Activity Type Definitions

The following predefined activity types support hive-related data aggregation, evaluation, and alerting in OpenAgri. They can be created using the SCIBee `oa_activity_type.py` helper module.

# 

```python
activity_type_data = [
    {
        "name": "Hive sensor data aggregation",
        "description": "Aggregation of sensor data for a specific hive.",
        "category": "observation",
        "background_color": "#D6EAF8",
        "border_color": "#7FB3D5",
        "text_color": "#1F4E79"
    },
    {
        "name": "Hive weather data aggregation",
        "description": "Aggregation of weather-based data for a specific hive.",
        "category": "observation",
        "background_color": "#D6F5F5",
        "border_color": "#76C7C0",
        "text_color": "#2E5E5E"
    },
    {
        "name": "Hive community data aggregation",
        "description": "Aggregation of community data relevant to a specific hive.",
        "category": "observation",
        "background_color": "#DDF3D8",
        "border_color": "#8BC48A",
        "text_color": "#2F5D34"
    },
    {
        "name": "Hive data evaluation",
        "description": "Evaluation of the available data for a specific hive.",
        "category": "observation",
        "background_color": "#FFF2CC",
        "border_color": "#E6C76E",
        "text_color": "#6E4E00"
    },
    {
        "name": "Hive alert",
        "description": "Warning or alert requiring attention for a specific hive.",
        "category": "alert",
        "background_color": "#F8D7DA",
        "border_color": "#D98880",
        "text_color": "#7B241C"
    }
]
```

### Usage

Create the activity types in OpenAgri by passing each dictionary to `create_activity_type()`, or save the list as a JSON file and use `create_activity_types_from_file()` to import the definitions.

## Alert Helper Functions

**Module:** `oa_alert.py`

Provides utilities for managing alert records associated with agricultural parcels, activity types, and observations in OpenAgri services.

### Features

- **List alerts:** Retrieve alert titles and IDs.
- **Look up alerts:** Find alert IDs by title.
- **Filter alerts:** Retrieve alerts by parcel, activity type, and date range.
- **Create alerts:** Validate alert data using JSON Schema and create new records, skipping existing alerts.
- **Import alerts:** Create alert records from a data file, resolving activity type names, parcel names, and observation references to OpenAgri IDs.
- **Export alerts:** Retrieve alerts from a specified look-back period and save their details, severity, validity period, and related references to a file.
- **Delete alerts:** Delete all accessible alert records.

**Note:** Deleting records may permanently remove data. Ensure that observations, activity types, and alerts conform to the JSON Schemas expected by the relevant OpenAgri services.
