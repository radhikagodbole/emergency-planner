
const fs = require('fs');
const path = require('path');
const csv = require('csv-parser');
const { parse } = require('json2csv');

const inputPath = path.join(__dirname, '../data/nyc_911_raw.csv');
const outputPath = path.join(__dirname, '../data/nyc_911_clean.csv');

// NYC coordinate bounds (approx)
const NYC_BOUNDS = {
    latMin: 40.4774,
    latMax: 40.9176,
    lonMin: -74.2591,
    lonMax: -73.7004
};

const cleanedData = [];

fs.createReadStream(inputPath)
  .pipe(csv())
  .on('data', (row) => {
    const lat = parseFloat(row.Latitude);
    const lon = parseFloat(row.Longitude);

    // 1. Remove rows without valid coordinates
    if (isNaN(lat) || isNaN(lon)) return;

    // 2. Filter valid coordinates inside NYC bounds
    if (
      lat < NYC_BOUNDS.latMin || lat > NYC_BOUNDS.latMax ||
      lon < NYC_BOUNDS.lonMin || lon > NYC_BOUNDS.lonMax
    ) {
      return;
    }

    // 3. Convert Creation Date to ISO format
    let creationDate = new Date(row['Creation Date']);
    if (isNaN(creationDate)) return; // skip if invalid date

    // 4. Extract time-based features
    const hour = creationDate.getHours();
    const dayOfWeek = creationDate.toLocaleString('en-US', { weekday: 'long' });
    const month = creationDate.toLocaleString('en-US', { month: 'long' });
    const isWeekend = (dayOfWeek === 'Saturday' || dayOfWeek === 'Sunday');

    cleanedData.push({
      'Incident Type': row['Incident Type'],
      Location: row.Location,
      Borough: row.Borough,
      'Creation Date': creationDate.toISOString(),
      'Closed Date': row['Closed Date'], // untouched
      Latitude: lat,
      Longitude: lon,
      Hour: hour,
      DayOfWeek: dayOfWeek,
      Month: month,
      IsWeekend: isWeekend
    });
  })
  .on('end', () => {
    // 5. Write to nyc_911_clean.csv
    const csvData = parse(cleanedData);
    fs.writeFileSync(outputPath, csvData);
    console.log(`✅ Data cleaning complete. Output saved to ${outputPath}`);
  });