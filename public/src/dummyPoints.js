export const dummyPoints = {
  "type": "FeatureCollection",
  "features": Array.from({ length: 50 }, (_, i) => {
    const lat = +(20.8 + Math.random() * 2.2).toFixed(4);
    const lng = +(77.8 + Math.random() * 2.7).toFixed(4);
    return {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [lng, lat]
      },
      "properties": {
        "name": `Asset ${i + 1}`
      }
    };
  })
};
