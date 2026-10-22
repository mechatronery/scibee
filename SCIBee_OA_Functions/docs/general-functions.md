# General Helper Functions

**Module:** `oa_function.py`

Provides general-purpose utilities for JSON file handling, date and time calculations, geographical distance measurement, data hashing, and HTTP request logging.

### Features

- **Read JSON files:** Load data from JSON files.

- **Write JSON files:** Save data to JSON files with formatted indentation.

- **Get ISO timestamps:** Generate the current UTC timestamp or timestamps a specified number of days in the past or future.

- **Calculate time differences:** Calculate the difference between two ISO timestamps in hours.

- **Get ISO dates:** Retrieve the current date, a date a specified number of days ago, or the start of the current year.

- **Calculate geographical distance:** Compute the geodesic distance between two coordinates in kilometres.

- **Hash data:** Generate a SHA-256 hash of a dictionary for data comparison.

- **Log HTTP requests:** Print request details, response status codes, and response content for debugging.

### Additional Requirements

- `geopy`
