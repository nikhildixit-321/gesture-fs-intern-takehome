const express = require('express');
const cors = require('cors');
const axios = require('axios');

const app = express();
const PORT = process.env.PORT || 5000;
const PYTHON_API_URL = 'http://127.0.0.1:8000/ask';

app.use(cors());
app.use(express.json());

app.post('/api/chat', async (req, res) => {
  try {
    const { question } = req.body;
    
    if (!question) {
      return res.status(400).json({ error: 'Question is required' });
    }

    // Forward the request to the Python FastAPI microservice
    const response = await axios.post(PYTHON_API_URL, { question });
    
    // Return the response from the Python backend
    return res.json(response.data);
  } catch (error) {
    console.error('Error talking to Python backend:', error.message);
    
    if (error.response) {
      return res.status(error.response.status).json(error.response.data);
    }
    
    res.status(500).json({ error: 'Internal Server Error. Is the Python backend running?' });
  }
});

app.listen(PORT, () => {
  console.log(`Node Express backend running on http://localhost:${PORT}`);
});
