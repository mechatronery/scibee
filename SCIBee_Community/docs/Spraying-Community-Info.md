# Spraying Community Info

Spraying Community Info is a SCIBee application for reporting planned pesticide, herbicide, and fungicide applications, including their planned start time, approximate treatment area, and location. These observations help beekeepers assess potential risks to bees from reported spraying activities.

## Features

- **Spraying observations** — Report planned pesticide, herbicide, and fungicide applications.
- **Application categories** — Classify applications by treatment type.
- **Planned application time** — Display the planned start time in the time zone associated with the selected location.
- **Harmfulness indicator** — Indicate whether the contributor marked the substance as harmful to bees.
- **Area estimates** — Select an approximate treatment area.
- **Recent observations** — Retrieve data for the latest 14 UTC calendar days, including today.
- **Daily archives** — List and download available CSV files.
- **Automatic refresh** — Update displayed observations every 10 seconds.

## Observation Data

Each observation contains the following fields:

| Field     | Description                                                               |
| --------- | ------------------------------------------------------------------------- |
| `epoch`   | Report submission timestamp in milliseconds since the Unix epoch          |
| `start`   | Planned application start time in milliseconds since the Unix epoch       |
| `type`    | Application type category                                                 |
| `harmful` | Indicates whether the contributor marked the substance as harmful to bees |
| `area`    | Estimated treatment area category                                         |
| `lat`     | Latitude                                                                  |
| `lng`     | Longitude                                                                 |

### Application categories

| Category              | Value       | Description                                           |
| --------------------- | ----------- | ----------------------------------------------------- |
| Pesticide application | `pesticide` | Use of chemicals to control insects and other pests   |
| Herbicide application | `herbicide` | Use of chemicals to control weeds and unwanted plants |
| Fungicide application | `fungicide` | Use of chemicals to control fungal diseases           |

### Harmfulness indicator

| Value   | Meaning                                                                                                             |
| ------- | ------------------------------------------------------------------------------------------------------------------- |
| `true`  | The contributor marked the substance as harmful to bees. The interface displays a caution indicator.                |
| `false` | The contributor did not mark the substance as harmful. This does not establish that the substance is safe for bees. |

The indicator reflects the submitted report and is not an independent assessment of the substance's effects.

### Area categories

Area categories represent approximate treatment areas, with square dimensions provided as a practical reference.

| Category | Value    | Approximate area | Example dimensions |
| -------- | -------- | ----------------:| ------------------ |
| Tiny     | `tiny`   | 1 m²             | 1 × 1 m            |
| Mini     | `mini`   | 9 m²             | 3 × 3 m            |
| Small    | `small`  | 49 m²            | 7 × 7 m            |
| Unit     | `unit`   | 1 a (100 m²)     | 10 × 10 m          |
| Medium   | `medium` | 9 a (900 m²)     | 30 × 30 m          |
| Large    | `large`  | 49 a (4,900 m²)  | 70 × 70 m          |
| Huge     | `huge`   | 1 ha (10,000 m²) | 100 × 100 m        |

*Note: 1 are (a) equals 100 m², and 1 hectare (ha) equals 10,000 m². Area values are estimates selected by the contributor.*

## API Endpoints

| Method | Endpoint                    | Description                                                                                          |
| ------ | --------------------------- | ---------------------------------------------------------------------------------------------------- |
| `GET`  | `/`                         | Serves the web application                                                                           |
| `POST` | `/addSprayingData`          | Submits a spraying observation                                                                       |
| `GET`  | `/getSprayingData`          | Retrieves observations for the latest 14 UTC calendar days, including today and the previous 13 days |
| `GET`  | `/today`                    | Retrieves observations currently stored for today                                                    |
| `GET`  | `/day/<date>`               | Retrieves observations for a specified date                                                          |
| `GET`  | `/getFileList`              | Lists available CSV archives                                                                         |
| `GET`  | `/getFile?file_name=<name>` | Downloads a CSV archive                                                                              |

### Submitting an observation

The `/addSprayingData` endpoint accepts a JSON request containing the planned application start time, application type, harmfulness indicator, estimated area, and geographic coordinates.

Example:

```json
{
  "start": 1792504800000,
  "type": "pesticide",
  "harmful": "true",
  "area": "medium",
  "lat": 46.05,
  "lng": 14.50
}
```

## Data Storage and Archiving

Current-day observations are stored in the SQLite database `today.db`, in the `sprayingData` table. The `meta` table stores the active UTC calendar day.

Archive filenames follow this pattern:

```text
data/
└── SCI_YYYY_MM_DD.csv
```

CSV archives contain the following columns:

| Column          | Description                                                               |
| --------------- | ------------------------------------------------------------------------- |
| `Epoch_time_ms` | Report submission timestamp in milliseconds since the Unix epoch          |
| `Start_time_ms` | Planned application start time in milliseconds since the Unix epoch       |
| `Type`          | Application type category                                                 |
| `Harmful`       | Indicates whether the contributor marked the substance as harmful to bees |
| `Area`          | Estimated treatment area category                                         |
| `Latitude`      | Latitude of planned treatment location                                    |
| `Longitude`     | Longitude of planned treatment area                                       |

The historical retrieval endpoints use the CSV archives for previous days. If an archive is unavailable, the corresponding date returns an empty observation list.
