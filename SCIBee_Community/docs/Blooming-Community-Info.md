# Blooming Community Info

Blooming Community Info is a SCIBee application for reporting blooming plants and crops, including their approximate location, area, and category. These observations help characterize the availability of flowering resources relevant to beekeeping.

## Features

- **Blooming observations** — Record the location and category of blooming plants and crops.
- **Plant categories** — Classify blooming plants and crops by type.
- **Area estimates** — Select an approximate blooming area.
- **Recent observations** — Retrieve data for the latest 14 UTC calendar days, including today.
- **Daily archives** — List and download available CSV files.
- **Automatic refresh** — Update displayed observations every 10 seconds.

## Observation Data

Each observation contains the following fields:

| Field   | Description                                                |
| ------- | ---------------------------------------------------------- |
| `epoch` | Observation timestamp in milliseconds since the Unix epoch |
| `type`  | Blooming plant or crop category                            |
| `area`  | Estimated blooming area category                           |
| `lat`   | Latitude                                                   |
| `lng`   | Longitude                                                  |

### Plant categories

| Category          | Value               | Description and examples                                                                                      |
| ----------------- | ------------------- | ------------------------------------------------------------------------------------------------------------- |
| Meadow            | `meadow`            | Flowering plants growing in meadows, such as clover, dandelions, and meadow buttercups.                       |
| Decorative plants | `decorative_plants` | Ornamental plants in gardens, parks, and landscaped areas, such as lavender, roses, and ornamental daisies.   |
| Herbs             | `herbs`             | Culinary and aromatic herbs, such as thyme, oregano, and sage.                                                |
| Vegetable crops   | `vegetable_crops`   | Flowering vegetable crops, such as pumpkins, cucumbers, and courgettes.                                       |
| Legumes           | `legumes`           | Flowering leguminous crops, such as clover, alfalfa, beans, and peas.                                         |
| Oilseed crops     | `oilseed_crops`     | Crops grown for oil-rich seeds, such as oilseed rape (canola), sunflowers, and mustard.                       |
| Orchard trees     | `orchard_trees`     | Flowering fruit and nut trees, such as apple, cherry, pear, and plum trees.                                   |
| Berry crops       | `berry_crops`       | Flowering berry-producing plants, such as raspberries, strawberries, blackberries, and currants.              |
| Pseudocereals     | `pseudocereals`     | Broad-leaved plants whose seeds are used similarly to cereal grains, such as buckwheat, quinoa, and amaranth. |
| Forest trees      | `forest_trees`      | Flowering or pollen-producing forest trees, such as willow, maple, chestnut, and linden (lime).               |
| Forest shrubs     | `forest_shrubs`     | Flowering woody shrubs found in forests and woodland edges, such as hazel, elderberry, and wild raspberry.    |

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
| `POST` | `/addBloomingData`          | Submits a blooming observation                                                    |
| `GET`  | `/getBloomingData`          | Retrieves 14 daily entries, including today and the previous 13 UTC calendar days |
| `GET`  | `/today`                    | Retrieves observations currently stored for today                                 |
| `GET`  | `/day/<date>`               | Retrieves observations for a specified date                                       |
| `GET`  | `/getFileList`              | Lists available CSV archives                                                      |
| `GET`  | `/getFile?file_name=<name>` | Downloads a CSV file                                                              |

### Submitting an observation

The `/addBloomingData` endpoint accepts a JSON request containing the blooming plant or crop category, estimated area, and geographic coordinates.

Example:

```json
{
  "type": "meadow",
  "area": "medium",
  "lat": 46.05,
  "lng": 14.50
}
```

## Data Storage and Archiving

Current observations are stored in the SQLite database `today.db`, in the `bloomingData` table. The `meta` table stores the active UTC calendar day.

Archive filenames follow this pattern:

```text
data/
└── BCI_YYYY_MM_DD.csv
```

CSV archives contain the following columns:

| Column          | Description                                                |
| --------------- | ---------------------------------------------------------- |
| `Epoch_time_ms` | Observation timestamp in milliseconds since the Unix epoch |
| `Type`          | Blooming plant or crop category                            |
| `Area`          | Estimated blooming area category                           |
| `Latitude`      | Latitude of observed blooming location                     |
| `Longitude`     | Longitude of observed blooming area                        |

The historical retrieval endpoints use CSV archives for previous days. If an archive is unavailable, the corresponding date returns an empty observation list.
