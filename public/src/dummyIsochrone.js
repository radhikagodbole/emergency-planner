export const dummyIsochrones = {
  type: 'FeatureCollection',
  features: [
    {
      type: 'Feature',
      geometry: {
        type: 'Polygon',
        coordinates: [[[78.9, 21.1], [78.9, 21.3], [79.1, 21.3], [79.1, 21.1], [78.9, 21.1]]]
      },
      properties: {
        station: 'Station A',
        color: 'orange',
        description: 'Emergency Response Station A covering Nagpur sector'
      }
    },
    {
      type: 'Feature',
      geometry: {
        type: 'Polygon',
        coordinates: [[[80.0, 22.0], [80.0, 22.2], [80.2, 22.2], [80.2, 22.0], [80.0, 22.0]]]
      },
      properties: {
        station: 'Station B',
        color: 'green',
        description: 'Emergency Response Station B covering Jabalpur sector'
      }
    }
  ]
};
