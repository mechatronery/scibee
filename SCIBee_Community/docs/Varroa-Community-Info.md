# Varroa Community Info

Varroa Community Info (VCI) is a SCIBee application for anonymously reporting Varroa mite findings and control actions in honey bee colonies. These observations help beekeepers anonymously share information about reported mite presence, infestation levels, and treatments at selected locations.

## Features

- **Varroa observations** — Report mite findings and control actions.
- **Action categories** — Classify reports by finding or treatment type.
- **Affected colony count** — Specify the number of bee colonies associated with a report.
- **Location reporting** — Record observations at a selected map location.
- **Recent observations** — Retrieve data for the latest 28 UTC calendar days, including today.
- **Daily archives** — List and download available CSV files.
- **Automatic refresh** — Update displayed observations every 10 seconds.

## Observation Data

Each observation contains the following fields:

| Field      | Description                                                      |
| ---------- | ---------------------------------------------------------------- |
| `epoch`    | Report submission timestamp in milliseconds since the Unix epoch |
| `type`     | Reported Varroa mite finding or treatment category               |
| `quantity` | Number of affected bee colonies                                  |
| `lat`      | Latitude                                                         |
| `lng`      | Longitude                                                        |

### Action categories

| Category              | Value         | Description                                                     |
| --------------------- | ------------- | --------------------------------------------------------------- |
| Mite presence         | `presence`    | Varroa mites detected below the recommended treatment threshold |
| Infestation           | `infestation` | Infestation at or above the applicable treatment threshold      |
| Formic acid treatment | `formic`      | Treatment using formic acid                                     |
| Oxalic acid treatment | `oxalic`      | Treatment using oxalic acid                                     |
| Miticide treatment    | `miticide`    | Treatment using a commercial miticide                           |

Treatment decisions should follow product instructions and applicable local beekeeping guidance.

## API Endpoints

| Method | Endpoint                    | Description                                                                                          |
| ------ | --------------------------- | ---------------------------------------------------------------------------------------------------- |
| `GET`  | `/`                         | Serves the web application                                                                           |
| `POST` | `/addVarroaData`            | Submits a Varroa observation                                                                         |
| `GET`  | `/getVarroaData`            | Retrieves observations for the latest 28 UTC calendar days, including today and the previous 27 days |
| `GET`  | `/today`                    | Retrieves observations currently stored for today                                                    |
| `GET`  | `/day/<date>`               | Retrieves observations for a specified date                                                          |
| `GET`  | `/getFileList`              | Lists available CSV archives                                                                         |
| `GET`  | `/getFile?file_name=<name>` | Downloads a CSV archive                                                                              |

### Submitting an observation

The `/addVarroaData` endpoint accepts a JSON request containing the action category, number of affected colonies, and geographic coordinates.

Example:

```json
{
  "type": "formic",
  "quantity": "2",
  "lat": 46.05,
  "lng": 14.50
}
```

The `quantity` field represents the number of bee colonies associated with the report. 

## Data Storage and Archiving

Current-day observations are stored in the SQLite database `today.db`, in the `varroaData` table. The `meta` table stores the active UTC calendar day.

Archive filenames follow this pattern:

```text
data/
└── VCI_YYYY_MM_DD.csv
```

CSV archives contain the following columns:

| Column          | Description                                                      |
| --------------- | ---------------------------------------------------------------- |
| `Epoch_time_ms` | Report submission timestamp in milliseconds since the Unix epoch |
| `Type`          | Reported Varroa mite finding or treatment category               |
| `Quantity`      | Number of affected bee colonies                                  |
| `Latitude`      | Latitude of observed beehive location                            |
| `Longitude`     | Longitude of observed beehive location                           |

Historical retrieval uses the daily CSV archives. If an archive is missing, the corresponding historical request returns an empty observation list.
