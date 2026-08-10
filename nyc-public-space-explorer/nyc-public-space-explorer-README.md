# NYC Public Space Explorer

An interactive web map of New York City's public spaces — parks, gardens,
plazas, and playgrounds — built from NYC Open Data. Filter the ~2,000 spaces by
borough, type, size, and waterfront access, or search by name.

Built with plain HTML/CSS/JavaScript and [Leaflet](https://leafletjs.com/); the
data is cleaned and structured with a small Python pipeline.

## Features

- Every public space rendered as a point, colored by type, sized by acreage.
- Filters for borough, space type, minimum size, and waterfront, plus name search.
- A live count of how many spaces match the current filters.
- Popups with each space's type, borough, size, and address.
- Responsive layout and a legend; works on desktop and mobile.

## Run it locally

The page loads a local data file, so it needs to be served over HTTP (opening
`index.html` directly will be blocked by the browser).

```bash
git clone https://github.com/sgupta285/nyc-public-space-explorer.git
cd nyc-public-space-explorer
python -m http.server 8000
# then open http://localhost:8000
```

## Data pipeline

The map reads `data/public_spaces.geojson`, which is produced from the raw NYC
Open Data export by `scripts/prepare_data.py`. To regenerate it from source:

```bash
pip install shapely
bash scripts/fetch_data.sh        # downloads data/parks_raw.json
python scripts/prepare_data.py    # writes public_spaces.geojson + data_dictionary.md
```

`prepare_data.py` handles the cleaning and QA:

1. Drops records with no name or geometry.
2. Computes a point (polygon centroid) for each space, repairing invalid rings.
3. Removes points that fall outside the NYC bounding box.
4. De-duplicates on name plus coordinates.
5. Normalizes fields — spells out borough codes, coerces acreage to a number,
   title-cases addresses — and prints a QA report of what was kept and dropped.

Field definitions are in [`data/data_dictionary.md`](data/data_dictionary.md).

## Project structure

```
nyc-public-space-explorer/
├── index.html                 # page layout
├── css/style.css              # styles
├── js/app.js                  # map, filters, and rendering
├── data/
│   ├── public_spaces.geojson  # cleaned data the map loads
│   └── data_dictionary.md     # field descriptions and provenance
└── scripts/
    ├── fetch_data.sh          # download the raw source data
    └── prepare_data.py        # clean + QA + build the GeoJSON
```

## Data source

[NYC Open Data — Parks Properties](https://data.cityofnewyork.us/) (dataset
`enfh-gkve`), maintained by NYC Parks. Point coordinates are centroids computed
from the source polygons.

## Possible extensions

- Draw the original park boundaries instead of centroids at high zoom.
- Add a detail panel with charts (acreage by borough, counts by type).
- Join in a second dataset (e.g. census tracts) to compare access across areas.

## License

MIT — see [LICENSE](LICENSE).
