# Meadows Community Info

Meadows Community Info is a SCIBee application for reporting mowed meadows, including their approximate location, area, and composition. These observations help characterize meadow management and the potential availability of flowering resources relevant to beekeeping.

## Features

- **Meadow observations** — Record the location and composition of mowed meadows.
- **Composition categories** — Classify meadows as grass-dominated, mixed, flower-rich, or unknown.
- **Area estimates** — Select an approximate meadow area.
- **Recent observations** — Retrieve data for the latest 14 UTC calendar days, including today.
- **Daily archives** — List and download available CSV files.
- **Automatic refresh** — Update displayed observations every 10 seconds.

## Observation Data

Each observation contains the following fields:

| Field   | Description                                                |
| ------- | ---------------------------------------------------------- |
| `epoch` | Observation timestamp in milliseconds since the Unix epoch |
| `type`  | Meadow composition category                                |
| `area`  | Estimated meadow area category                             |
| `lat`   | Latitude                                                   |
| `lng`   | Longitude                                                  |

### Meadow composition categories

| Category                 | Value            | Description                                                |
| ------------------------ | ---------------- | ---------------------------------------------------------- |
| Mostly grass             | `grass_dominant` | Few flowers; the meadow is dominated by grasses.           |
| Mix of grass and flowers | `mixed`          | Grasses and flowering plants occur in similar proportions. |
| Many flowers             | `flower_rich`    | A meadow with abundant flowering plants.                   |
| Not sure                 | `unknown`        | The meadow composition cannot be reliably estimated.       |

### Area categories

Area categories represent approximate surface areas, with square dimensions provided as a practical reference.

| Category | Approximate area | Example dimensions |
| -------- | ----------------:| ------------------ |
| Tiny     | 1 m²             | 1 × 1 m            |
| Mini     | 9 m²             | 3 × 3 m            |
| Small    | 49 m²            | 7 × 7 m            |
| Unit     | 1 a (100 m²)     | 10 × 10 m          |
| Medium   | 9 a (900 m²)     | 30 × 30 m          |
| Large    | 49 a (4,900 m²)  | 70 × 70 m          |
| Huge     | 1 ha (10,000 m²) | 100 × 100 m        |

*Note: 1 are (a) equals 100 m², and 1 hectare (ha) equals 10,000 m². Area values are estimates selected by the contributor.*

## API Endpoints

| Method | Endpoint                    | Description                                                                       |
| ------ | --------------------------- | --------------------------------------------------------------------------------- |
| `GET`  | `/`                         | Serves the web application                                                        |
| `POST` | `/addMeadowData`            | Submits a meadow observation                                                      |
| `GET`  | `/getMeadowData`            | Retrieves 14 daily entries, including today and the previous 13 UTC calendar days |
| `GET`  | `/today`                    | Retrieves observations currently stored for today                                 |
| `GET`  | `/day/<date>`               | Retrieves observations for a specified date                                       |
| `GET`  | `/getFileList`              | Lists available CSV archives                                                      |
| `GET`  | `/getFile?file_name=<name>` | Downloads a CSV archive                                                           |

### Submitting an observation

The `/addMeadowData` endpoint accepts a JSON request containing the meadow composition category, estimated area, and geographic coordinates.

Example:

```json
{
  "type": "flower_rich",
  "area": "medium",
  "lat": 46.05,
  "lng": 14.50
}
```

## Data Storage and Archiving

Current observations are stored in the SQLite database `today.db`, in the `meadowData` table. The `meta` table stores the active UTC calendar day.

Archive filenames follow this pattern:

```text
data/
└── MCI_YYYY_MM_DD.csv
```

CSV archives contain the following columns:

| Column          | Description                                                |
| --------------- | ---------------------------------------------------------- |
| `Epoch_time_ms` | Observation timestamp in milliseconds since the Unix epoch |
| `Type`          | Meadow composition category                                |
| `Area`          | Estimated meadow area category                             |
| `Latitude`      | Latitude of observed meadow location                       |
| `Longitude`     | Longitude of observed meadow area                          |

The historical retrieval endpoints use the CSV archives for previous days. If an archive is unavailable, the corresponding date returns an empty observation list.
