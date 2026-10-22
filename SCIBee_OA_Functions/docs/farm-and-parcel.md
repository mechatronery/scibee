# Farm and Parcel Management

## Farm Helper Functions

**Module:** `oa_farm.py`

Provides utilities for managing farm records in OpenAgri services.

### Features

- **List farms:** Retrieve farm names and IDs.
- **Look up farms:** Find farm IDs by name or farm names by ID.
- **Create farms:** Validate farm data using JSON Schema and create new records, skipping existing farms.
- **Import farms:** Create farm records from a data file.
- **Export farms:** Retrieve existing farm records and save their data to a file.
- **Delete farms:** Delete all accessible farm records.

## Default Farm Data Definition

The following example demonstrates the structure of a farm record for OpenAgri. Personal and identifying information is represented by `XXXX` placeholders.

### Python Definition

```python
farm_data = [
    {
        "status": 1,
        "name": "XXXX",
        "description": "Example data for application development and testing.",
        "administrator": "XXXX",
        "telephone": "XXXX",
        "vatID": "XXXX",
        "contactPerson": {
            "firstname": "XXXX",
            "lastname": "XXXX"
        },
        "address": {
            "adminUnitL1": "XXXX",
            "adminUnitL2": "XXXX",
            "addressArea": "XXXX",
            "municipality": "XXXX",
            "community": "XXXX",
            "locatorName": "XXXX"
        }
    }
]
```

### Usage

Use this list as a template for creating farm records with `oa_farm.py`. Replace the `XXXX` placeholders with valid values that comply with the OpenAgri farm JSON Schema before importing or creating records.

## Parcel Helper Functions

**Module:** `oa_parcel.py`

Provides utilities for managing agricultural parcel records associated with farms in OpenAgri services.

### Features

- **List parcels:** Retrieve active parcel identifiers and IDs for a specified farm.
- **Look up parcels:** Find parcel IDs by identifier or retrieve parcel identifiers and geographic coordinates by ID.
- **Create parcels:** Validate parcel data using JSON Schema, check for duplicates, and associate new parcels with existing farms.
- **Import parcels:** Create parcel records from a data file.
- **Export parcels:** Retrieve parcel records, including farm associations, geometry, and location data.
- **Delete parcels:** Delete active parcels associated with a specified farm.

## Default Parcel Data Definition

The following example demonstrates the structure of a beehive parcel record in OpenAgri. Network addresses, farm names, and location details are replaced with `XXXX` placeholders.

### Python Definition

```python
import json

parcel_data = [
    {
        "status": 1,
        "identifier": "A1",
        "description": json.dumps({
            "IPs": {
                "base": "XXXX",
                "entrance": "XXXX",
                "camera": "XXXX"
            }
        }),
        "validFrom": "2025-01-01T00:00:00Z",
        "validTo": "2099-12-31T23:59:59Z",
        "hasIrrigationFlow": "0",
        "category": "beehive",
        "inRegion": "XXXX",
        "hasToponym": "XXXX",
        "isNitroArea": False,
        "isNatura2000Area": False,
        "isPdopgArea": False,
        "isIrrigated": False,
        "isCultivatedInLevels": False,
        "isGroundSlope": False,
        "hasGeometry": {
            "asWKT": "POINT(XXXX XXXX)"
        },
        "location": {
            "lat": "XXXX",
            "long": "XXXX"
        },
        "farm_name": "XXXX",
        "farm": ""
    }
]
```

### Usage

Use this list as a template for creating parcel records with `oa_parcel.py`. Replace the placeholders with valid values and provide the appropriate farm association before importing or creating the record.

**Note:** Deleting farms or parcels will permanently remove data.
