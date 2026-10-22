# SCIBee Community Info System

The **SCIBee Community Info System** is a modular platform for anonymous, community-based collection and sharing of local environmental information relevant to beekeeping. It consists of a central hub and four independent web applications, each focused on a different topic.

## Applications

- **Blooming** — Observations of blooming plants and crops.
- **Meadows** — Observations of meadow mowing and meadow composition.
- **Varroa** — Reports of Varroa mite detections and management actions.
- **Spraying** — Reports of planned pesticide, herbicide, and fungicide applications.

See the individual application documentation for details:

- [Blooming Community Info](docs/Blooming-Community-Info.md)
- [Meadows Community Info](docs/Meadows-Community-Info.md)
- [Varroa Community Info](docs/Varroa-Community-Info.md)
- [Spraying Community Info](docs/Spraying-Community-Info.md)

## Architecture

The system uses a modular architecture. Each community application has its own backend, frontend, and data storage and can be developed, deployed, and maintained independently. The **Community Hub** provides centralized navigation between the applications.

```text
SCIBee Community Info System
│
├── Community Hub
│
├── Blooming Community Info
├── Meadows Community Info
├── Varroa Community Info
└── Spraying Community Info
```

## Common Technology

The applications share a common technology approach:

- **Backend:** Python and Flask
- **Frontend:** HTML, CSS, and JavaScript
- **Web server:** Gunicorn for production deployments
- **Containerization:** Docker
- **Database:** SQLite for current-day observations
- **Historical storage:** Daily CSV archives where supported
- **Mapping:** Leaflet and Leaflet.markercluster where implemented
- **Map layers:** Esri World Imagery and World Boundaries and Places

Individual applications may use additional libraries depending on their functionality, such as date and time selection or time zone conversion.

## Common Data Handling

The community applications collect observations submitted by contributors. Depending on the application, records may include a timestamp, geographic coordinates, and topic-specific information.

Current-day observations are stored in SQLite databases. Applications that support historical archiving export daily observations to CSV files when the UTC calendar day changes.

Common data-handling principles include:

- **Daily archiving** — Store historical observations in date-based CSV files where supported.
- **Historical retrieval** — Provide access to available observations from previous days.
- **Data export** — Allow available archives to be downloaded as CSV files.
- **Persistent storage** — Use persistent storage for databases and archives in containerized deployments.

Archive retention, observation history, database tables, CSV formats, and API endpoints may differ between applications. Refer to each application's documentation for its specific implementation.

## Common Mapping Interface

The map-based applications use Leaflet to display geographically located community observations.

Common interface features include:

- Interactive map navigation and zoom.
- Geographic markers representing submitted observations.
- Marker clustering to improve readability where implemented.
- A map-center indicator for selecting a reporting location.
- Browser geolocation to help users navigate to their current location, when supported and permitted.
- Observation details displayed when a marker is selected.
- Periodic data refresh where implemented.

Map imagery, geographic labels, and external JavaScript libraries may be provided by third-party services. An internet connection is required for these external resources.

## Anonymous Participation

The community applications do not require user accounts or personal identification to submit observations.

However, submitted records may include geographic coordinates, timestamps, and other observation details. Users should consider the location information they submit when reporting observations.

## Deployment and Data Persistence

The applications can be deployed independently, including in Docker containers. Gunicorn can be used as the production application server.

Databases and archive directories should be stored on persistent volumes when using containers. Otherwise, replacing a container may result in the loss of data stored only within its filesystem.

External map services and frontend libraries require internet connectivity.

## Purpose

The SCIBee project provides a shared platform for exchanging local environmental information relevant to beekeeping. By separating topics into independent applications, the system supports focused and expandable community reporting while maintaining a consistent overall structure.
