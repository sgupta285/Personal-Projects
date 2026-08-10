# Data Dictionary: NYC Public Spaces

- **Source:** NYC Open Data, Parks Properties (dataset `enfh-gkve`)
- **Prepared:** 2026-08-10 by `scripts/prepare_data.py`
- **Records:** 2058 public spaces
- **Geometry:** one Point per space (centroid of the original park polygon)

| Field | Type | Description |
| --- | --- | --- |
| `name` | string | Official sign name of the public space |
| `borough` | string | Borough, spelled out (Bronx, Brooklyn, Manhattan, Queens, Staten Island) |
| `category` | string | Park type, e.g. Neighborhood Park, Garden, Triangle/Plaza |
| `acres` | number \| null | Size in acres; null where the source value was missing or invalid |
| `address` | string \| null | Nearest street address, title-cased |
| `zipcode` | string \| null | ZIP code |
| `community_board` | string \| null | NYC community board |
| `waterfront` | boolean | Whether the space is on the waterfront |

### Categories (21)

Buildings/Institutions, Cemetery, Community Park, Flagship Park, Garden, Historic House Park, Jointly Operated Playground, Lot, Mall, Managed Sites, Nature Area, Neighborhood Park, Operations, Parkway, Playground, Recreational Field/Courts, Retired N/A, Strip, Triangle/Plaza, Undeveloped, Waterfront Facility

### Cleaning steps

1. Dropped records with no sign name or no geometry.
2. Computed a centroid for each park polygon; repaired invalid rings with a zero-width buffer.
3. Dropped centroids that fell outside the NYC bounding box (bad coordinates).
4. Removed duplicates keyed on name plus rounded coordinates.
5. Coerced `acres` to a non-negative number, else null; spelled out borough codes; normalized text fields.
