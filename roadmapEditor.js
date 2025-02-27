const express = require('express');
const fs = require('fs');
const path = require('path');
const bodyParser = require('body-parser');

const app = express();
const PORT = 8080;
const JSON_FILE_PATH = path.join(__dirname, 'roadmap.json');

// Middleware
app.use(express.static('public'));
app.use(bodyParser.json({ limit: '50mb' }));
app.use(bodyParser.urlencoded({ extended: true, limit: '50mb' }));

// Routes
app.get('/api/data', (req, res) => {
  try {
    const data = JSON.parse(fs.readFileSync(JSON_FILE_PATH, 'utf8'));
    res.json(data);
  } catch (error) {
    console.error('Error reading JSON file:', error);
    res.status(500).json({ error: 'Failed to read data file' });
  }
});

app.post('/api/data', (req, res) => {
  try {
    const data = req.body;
    fs.writeFileSync(JSON_FILE_PATH, JSON.stringify(data, null, 2), 'utf8');
    res.json({ success: true, message: 'Data saved successfully' });
  } catch (error) {
    console.error('Error writing JSON file:', error);
    res.status(500).json({ error: 'Failed to save data' });
  }
});

// Start server
app.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}`);
}); 