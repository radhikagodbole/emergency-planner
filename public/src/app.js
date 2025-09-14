import * as L from 'https://unpkg.com/leaflet@1.9.4/dist/leaflet-src.esm.js';
import { dummyPoints } from './dummyPoints.js';

const map = L.map('map').setView([21.1466, 79.0888], 7);

const allBuffers = [];
const dummyPointsLayer = L.layerGroup().addTo(map);
const overlapLayers = [];
let addingUserStation = false;
let uncoveredHeatmapLayer;

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '© OpenStreetMap contributors'
}).addTo(map);

L.geoJSON(dummyPoints, {
  pointToLayer: (feature, latlng) =>
    L.circleMarker(latlng, {
      radius: 5,
      fillColor: 'blue',
      color: 'blue',
      fillOpacity: 1
    }).bindPopup(`<b>${feature.properties.name}</b>`)
}).addTo(map);

function addStationWithBuffers(lat, lng, stationName) {
  let markerColor;
  if (stationName.startsWith('Suggested Station')) {
    markerColor = 'darkgreen';
  } else if (stationName.startsWith('User Station')) {
    markerColor = 'black';
  } else {
    markerColor = 'grey';
  }

  L.circleMarker([lat, lng], {
    radius: 6,
    color: markerColor,
    fillColor: markerColor,
    fillOpacity: 1
  }).addTo(map)
    .bindPopup(`<b>${stationName}</b>`);

  const center = turf.point([lng, lat]);

  const buffer5 = turf.buffer(center, 5, { units: 'kilometers' });
  L.geoJSON(buffer5, { style: { color: 'green', fillOpacity: 0.2 } }).addTo(map);

  const buffer10 = turf.buffer(center, 10, { units: 'kilometers' });
  L.geoJSON(buffer10, { style: { color: 'orange', fillOpacity: 0.1 } }).addTo(map);

  allBuffers.forEach(existingBuffer => {
    const intersection5 = turf.intersect(buffer5, existingBuffer);
    if (intersection5) {
      const overlapLayer5 = L.geoJSON(intersection5, { style: { color: 'purple', fillOpacity: 0.4 } });
      overlapLayer5.addTo(map);
      overlapLayers.push(overlapLayer5);
    }
  });

  allBuffers.forEach(existingBuffer => {
    const intersection10 = turf.intersect(buffer10, existingBuffer);
    if (intersection10) {
      const overlapLayer10 = L.geoJSON(intersection10, { style: { color: 'purple', fillOpacity: 0.3 } });
      overlapLayer10.addTo(map);
      overlapLayers.push(overlapLayer10);
    }
  });

  allBuffers.push(buffer5, buffer10);

  const within5km = turf.pointsWithinPolygon(dummyPoints, buffer5);
  const within10km = turf.pointsWithinPolygon(dummyPoints, buffer10);

  console.log(`Station: ${stationName}`);
  console.log(`Within 5km: ${within5km.features.length}`);
  console.log(`Within 10km: ${within10km.features.length}`);

  alert(`${stationName}
Buildings within 5km: ${within5km.features.length}
Buildings within 10km: ${within10km.features.length}`);

  dummyPointsLayer.clearLayers();

  dummyPoints.features.forEach(point => {
    const isCovered = allBuffers.some(buffer => turf.booleanPointInPolygon(point, buffer));
    const [lng, lat] = point.geometry.coordinates;
    const marker = L.circleMarker([lat, lng], {
      radius: 5,
      color: isCovered ? 'blue' : 'red',
      fillColor: isCovered ? 'blue' : 'red',
      fillOpacity: 1
    });
    if (!isCovered) marker.addTo(dummyPointsLayer);
  });

  updateCoverageSummary();
  updateUncoveredHeatmap();
}

function updateCoverageSummary() {
  const total = dummyPoints.features.length;
  const uncovered = dummyPointsLayer.getLayers().length;
  const covered = total - uncovered;

  document.getElementById('total-assets').textContent = total;
  document.getElementById('covered-assets').textContent = covered;
  document.getElementById('uncovered-assets').textContent = uncovered;
}

function updateUncoveredHeatmap() {
  const heatPoints = [];

  dummyPoints.features.forEach(point => {
    const isCovered = allBuffers.some(buffer => turf.booleanPointInPolygon(point, buffer));
    if (!isCovered) {
      const [lng, lat] = point.geometry.coordinates;
      heatPoints.push([lat, lng, 0.5]);
    }
  });

  if (uncoveredHeatmapLayer) map.removeLayer(uncoveredHeatmapLayer);

  uncoveredHeatmapLayer = L.heatLayer(heatPoints, {
    radius: 25,
    blur: 15,
    maxZoom: 13
  });

  if (document.getElementById('toggle-heatmap').checked) {
    uncoveredHeatmapLayer.addTo(map);
  }
}

function suggestNewStationLocation() {
  if (dummyPointsLayer.getLayers().length === 0) {
    alert("All assets are already covered.");
    return;
  }

  let bestPoint = null;
  let maxCovered = 0;

  dummyPoints.features.forEach(candidate => {
    const isCovered = allBuffers.some(buffer => turf.booleanPointInPolygon(candidate, buffer));
    if (isCovered) return;

    const center = turf.point(candidate.geometry.coordinates);
    const buffer = turf.buffer(center, 5, { units: 'kilometers' });

    const nearby = turf.pointsWithinPolygon(dummyPoints, buffer);
    let count = 0;
    nearby.features.forEach(p => {
      const pCovered = allBuffers.some(b => turf.booleanPointInPolygon(p, b));
      if (!pCovered) count++;
    });

    if (count > maxCovered) {
      maxCovered = count;
      bestPoint = candidate;
    }
  });

  if (bestPoint) {
    const [lng, lat] = bestPoint.geometry.coordinates;
    addStationWithBuffers(lat, lng, `Suggested Station (covers ${maxCovered})`);
  } else {
    alert("No suitable uncovered cluster found.");
  }
}

map.on('click', function(e) {
  if (addingUserStation) {
    const { lat, lng } = e.latlng;
    addStationWithBuffers(lat, lng, `User Station at (${lat.toFixed(3)}, ${lng.toFixed(3)})`);
  }
});

document.getElementById('toggle-overlaps').addEventListener('change', e => {
  if (e.target.checked) {
    overlapLayers.forEach(layer => map.addLayer(layer));
  } else {
    overlapLayers.forEach(layer => map.removeLayer(layer));
  }
});

document.getElementById('toggle-heatmap').addEventListener('change', () => updateUncoveredHeatmap());
document.getElementById('suggest-location-btn').addEventListener('click', suggestNewStationLocation);
document.getElementById('add-user-station-toggle').addEventListener('change', e => addingUserStation = e.target.checked);

addStationWithBuffers(21.1466, 79.0888, 'User Station: Nagpur Fire Station');
addStationWithBuffers(22.7179, 75.8577, 'User Station: Indore Ambulance HQ');

updateCoverageSummary();
