const express = require('express');
const { readJsonFile, writeJsonFile } = require('./fileHandler');

const router = express.Router();

// Get all data
router.get('/data', (req, res) => {
  try {
    const data = readJsonFile();
    res.json(data);
  } catch (error) {
    res.status(500).json({ error: 'Failed to read data file' });
  }
});

// Save data
router.post('/data', (req, res) => {
  try {
    const data = req.body;
    writeJsonFile(data);
    res.json({ success: true, message: 'Data saved successfully' });
  } catch (error) {
    res.status(500).json({ error: 'Failed to save data' });
  }
});

module.exports = router; 