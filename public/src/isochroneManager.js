// IsochroneManager.js

const IsochroneManager = (function () {
  let mapInstance = null;

  function init(map) {
    mapInstance = map;
  }

  function addIsochrone(geojson, color = '#ff0000') {
  if (!mapInstance) {
    console.error('Map instance not initialized!');
    return;
  }

  const layer = L.geoJSON(geojson, {
    style: {
      color: color,
      weight: 2,
      fillOpacity: 0.3
    }
  }).addTo(mapInstance);

  
  

  // Auto-fit map to polygon bounds
  mapInstance.fitBounds(layer.getBounds());

  return layer;
}

  return {
    init,
    addIsochrone
  };
})();

window.IsochroneManager = IsochroneManager;