/*
 * NYC Public Space Explorer
 * Loads the cleaned parks GeoJSON and lets you filter it on a Leaflet map by
 * borough, space type, size, waterfront, and name search.
 */

// Group the 20-plus source categories into a handful of families so the map
// stays readable and the legend stays short. Each family gets one color.
const TYPE_GROUPS = [
  { label: "Parks", color: "#2e7d32", match: ["Community Park", "Neighborhood Park", "Regional Park", "Flagship Park"] },
  { label: "Playgrounds", color: "#f9a825", match: ["Playground", "Jointly Operated Playground"] },
  { label: "Gardens", color: "#7cb342", match: ["Garden"] },
  { label: "Plazas & malls", color: "#8d6e63", match: ["Triangle/Plaza", "Mall", "Strip"] },
  { label: "Nature areas", color: "#00838f", match: ["Nature Area", "Forest", "Wetland", "Lake/Pond"] },
  { label: "Recreation", color: "#1565c0", match: ["Recreational Field/Courts", "Pool", "Beach"] },
  { label: "Other", color: "#8e24aa", match: [] }, // catch-all
];

const OTHER = TYPE_GROUPS[TYPE_GROUPS.length - 1];

function groupFor(category) {
  return TYPE_GROUPS.find((g) => g.match.includes(category)) || OTHER;
}

// Current filter state, updated by the controls.
const filters = {
  search: "",
  boroughs: new Set(),
  groups: new Set(TYPE_GROUPS.map((g) => g.label)),
  minAcres: 0,
  waterfrontOnly: false,
};

let allFeatures = [];
let markerLayer;

const map = L.map("map", { center: [40.7128, -73.96], zoom: 11 });

L.tileLayer("https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png", {
  attribution:
    '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>',
  maxZoom: 19,
}).addTo(map);

// ---- Load and render ------------------------------------------------

fetch("data/public_spaces.geojson")
  .then((response) => {
    if (!response.ok) throw new Error(`Could not load data (${response.status})`);
    return response.json();
  })
  .then((collection) => {
    allFeatures = collection.features;
    buildBoroughFilters();
    buildTypeFilters();
    addLegend();
    render();
  })
  .catch((error) => {
    document.getElementById("result-count").textContent = error.message;
  });

function render() {
  const visible = allFeatures.filter(passesFilters);

  if (markerLayer) markerLayer.remove();
  markerLayer = L.layerGroup(visible.map(toMarker)).addTo(map);

  const count = visible.length.toLocaleString();
  const total = allFeatures.length.toLocaleString();
  document.getElementById("result-count").textContent =
    `Showing ${count} of ${total} public spaces`;
}

function passesFilters(feature) {
  const p = feature.properties;

  if (filters.search && !p.name.toLowerCase().includes(filters.search)) return false;
  if (filters.boroughs.size && !filters.boroughs.has(p.borough)) return false;
  if (!filters.groups.has(groupFor(p.category).label)) return false;
  if (filters.waterfrontOnly && !p.waterfront) return false;
  if (filters.minAcres > 0 && (p.acres === null || p.acres < filters.minAcres)) return false;

  return true;
}

function toMarker(feature) {
  const [lon, lat] = feature.geometry.coordinates;
  const p = feature.properties;
  const color = groupFor(p.category).color;

  return L.circleMarker([lat, lon], {
    radius: radiusFor(p.acres),
    color: "#ffffff",
    weight: 1,
    fillColor: color,
    fillOpacity: 0.85,
  }).bindPopup(popupHtml(p));
}

// Bigger parks get slightly bigger dots, capped so nothing dominates the map.
function radiusFor(acres) {
  if (!acres) return 4;
  return Math.min(4 + Math.sqrt(acres), 14);
}

function popupHtml(p) {
  const rows = [`<div class="popup-name">${escapeHtml(p.name)}</div>`];
  rows.push(`<div class="popup-meta">${escapeHtml(p.category)} &middot; ${p.borough}</div>`);
  if (p.acres !== null) rows.push(`<div>${p.acres.toLocaleString()} acres</div>`);
  if (p.address) rows.push(`<div>${escapeHtml(p.address)}</div>`);
  if (p.waterfront) rows.push(`<div>&#127754; Waterfront</div>`);
  return rows.join("");
}

// ---- Filter controls ------------------------------------------------

function buildBoroughFilters() {
  const boroughs = [...new Set(allFeatures.map((f) => f.properties.borough))].sort();
  const container = document.getElementById("borough-filters");

  boroughs.forEach((borough) => {
    const id = `bor-${borough.replace(/\s+/g, "-")}`;
    const label = document.createElement("label");
    label.innerHTML = `<input type="checkbox" id="${id}" value="${borough}" /> ${borough}`;
    container.appendChild(label);

    label.querySelector("input").addEventListener("change", (e) => {
      if (e.target.checked) filters.boroughs.add(borough);
      else filters.boroughs.delete(borough);
      render();
    });
  });
}

function buildTypeFilters() {
  const container = document.getElementById("type-filters");

  TYPE_GROUPS.forEach((group) => {
    const label = document.createElement("label");
    label.innerHTML =
      `<input type="checkbox" value="${group.label}" checked />` +
      `<span class="swatch" style="background:${group.color}"></span>${group.label}`;
    container.appendChild(label);

    label.querySelector("input").addEventListener("change", (e) => {
      if (e.target.checked) filters.groups.add(group.label);
      else filters.groups.delete(group.label);
      render();
    });
  });
}

// ---- Legend ---------------------------------------------------------

function addLegend() {
  const legend = L.control({ position: "bottomright" });
  legend.onAdd = () => {
    const div = L.DomUtil.create("div", "legend");
    const rows = TYPE_GROUPS.map(
      (g) =>
        `<div class="legend-row"><span class="swatch" style="background:${g.color}"></span>${g.label}</div>`
    ).join("");
    div.innerHTML = `<h2>Space type</h2>${rows}`;
    return div;
  };
  legend.addTo(map);
}

// ---- Wire up the standalone inputs ---------------------------------

document.getElementById("search").addEventListener("input", (e) => {
  filters.search = e.target.value.trim().toLowerCase();
  render();
});

document.getElementById("acres").addEventListener("input", (e) => {
  filters.minAcres = parseFloat(e.target.value);
  document.getElementById("acres-value").textContent = filters.minAcres;
  render();
});

document.getElementById("waterfront").addEventListener("change", (e) => {
  filters.waterfrontOnly = e.target.checked;
  render();
});

document.getElementById("reset").addEventListener("click", () => {
  filters.search = "";
  filters.boroughs.clear();
  filters.groups = new Set(TYPE_GROUPS.map((g) => g.label));
  filters.minAcres = 0;
  filters.waterfrontOnly = false;

  document.getElementById("search").value = "";
  document.getElementById("acres").value = 0;
  document.getElementById("acres-value").textContent = "0";
  document.getElementById("waterfront").checked = false;
  document.querySelectorAll("#borough-filters input").forEach((c) => (c.checked = false));
  document.querySelectorAll("#type-filters input").forEach((c) => (c.checked = true));

  render();
});

// Small helper so park names with odd characters can't break the popup markup.
function escapeHtml(value) {
  const div = document.createElement("div");
  div.textContent = value;
  return div.innerHTML;
}
