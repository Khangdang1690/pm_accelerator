# Weather App - Full Stack Application

A comprehensive weather application with AI-powered features, built with React frontend and FastAPI backend.

## 🌟 Features

- **Real-time Weather Data**: Get current weather and 5-day forecasts using Open-Meteo API
- **AI Weather Assistant**: Google Gemini-powered conversational weather queries
- **YouTube Integration**: Find location-related videos using SerpAPI or YouTube Data API
- **Google Maps Integration**: Location data and mapping using Agno tools
- **CRUD Operations**: Full database management for weather requests
- **Data Export**: Export data in multiple formats (JSON, XML, CSV, PDF, Markdown)
- **Modern UI**: Beautiful React interface with responsive design

## 🚀 Quick Start

### Prerequisites

- **Python 3.12+**
- **Node.js 16+**
- **uv** (Python package manager) - [Install uv](https://docs.astral.sh/uv/getting-started/installation/)

### 1. Clone the Repository

```bash
git clone <repository-url>
cd pm_accelerator
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment with Python 3.12
uv venv --python 3.12

# Activate virtual environment
# Windows:
.venv/Scripts/activate
# Linux/Mac:
source .venv/bin/activate

# Install dependencies
uv pip install -r requirements.txt

# Set up environment variables (see Environment Variables section below)
# Create a .env file or set environment variables

# Run the backend server
python agent.py
```

The backend will be available at `http://localhost:8001`

### 3. Frontend Setup

```bash
# Navigate to frontend directory (from root)
cd frontend/weather-app

# Install dependencies
npm install

# Start the development server
npm start
```

The frontend will be available at `http://localhost:3000`

## 🔧 Environment Variables

Create a `.env` file in the `backend` directory with the following variables:

### Required

```env
# Google Gemini AI (Required for AI assistant)
GOOGLE_API_KEY=your_google_gemini_api_key_here
```

### Optional (for enhanced features)

```env
# YouTube Video Search (Choose one option)

# Option 1: SerpAPI (Recommended - 100 free searches/month)
SERPAPI_API_KEY=your_serpapi_key_here

# Option 2: YouTube Data API v3 (Alternative)
YOUTUBE_API_KEY=your_youtube_api_key_here

# Google Maps Integration
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here

# News Integration (Future feature)
NEWS_API_KEY=your_news_api_key_here
```

## 🔑 Getting API Keys

### Google Gemini API (Required)
1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Create a new API key
3. Set `GOOGLE_API_KEY` environment variable

### SerpAPI (Recommended for YouTube)
1. Go to [SerpAPI](https://serpapi.com/)
2. Sign up for free account (100 searches/month free)
3. Get your API key from dashboard
4. Set `SERPAPI_API_KEY` environment variable
5. Install dependency: `uv pip install google-search-results`

### YouTube Data API v3 (Alternative)
1. Go to [Google Cloud Console](https://console.developers.google.com/)
2. Create a new project or select existing one
3. Enable "YouTube Data API v3"
4. Create credentials (API Key)
5. Set `YOUTUBE_API_KEY` environment variable

### Google Maps API (Optional)
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Enable the following APIs:
   - Places API
   - Directions API
   - Geocoding API
   - Maps JavaScript API
3. Create API key
4. Set `GOOGLE_MAPS_API_KEY` environment variable

## 📁 Project Structure

```
pm_accelerator/
├── backend/                 # FastAPI backend
│   ├── agent.py            # Main FastAPI application
│   ├── api_integrations.py # External API integrations
│   ├── database.py         # Database operations
│   ├── data_export.py      # Data export functionality
│   ├── open_meteo_tool.py  # Weather data tool
│   ├── requirements.txt    # Python dependencies
│   └── README.md          # Backend documentation
├── frontend/               # React frontend
│   └── weather-app/
│       ├── src/
│       ├── public/
│       ├── package.json
│       └── ...
└── README.md              # This file
```

## 🛠️ Development

### Backend Development

```bash
cd backend
.venv/Scripts/activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Install new dependencies
uv pip install package_name

# Update requirements.txt
uv pip freeze > requirements.txt

# Run with auto-reload
python agent.py
```

### Frontend Development

```bash
cd frontend/weather-app

# Install new dependencies
npm install package_name

# Run development server
npm start

# Build for production
npm run build
```

## 🔍 API Endpoints

### Core Endpoints
- `POST /chat` - AI weather assistant
- `GET /test` - Health check

### CRUD Operations
- `POST /weather-requests` - Create weather request
- `GET /weather-requests` - List all requests
- `GET /weather-requests/{id}` - Get specific request
- `PUT /weather-requests/{id}` - Update request
- `DELETE /weather-requests/{id}` - Delete request

### API Integrations
- `GET /youtube-videos/{location}` - Get YouTube videos
- `GET /google-maps/{location}` - Get Google Maps data
- `GET /location-enrichment/{location}` - Get comprehensive location data

### Data Export
- `GET /export/weather-requests?format={json|xml|csv|pdf|markdown}` - Export data

## 🐛 Troubleshooting

### Backend Issues

**"Module not found" errors:**
```bash
# Make sure virtual environment is activated
.venv/Scripts/activate
# Reinstall dependencies
uv pip install -r requirements.txt
```

**"YouTube API unavailable" error:**
- Set `SERPAPI_API_KEY` or `YOUTUBE_API_KEY` environment variable
- Restart the backend server after setting environment variables

**"Google API key not found" error:**
- Set `GOOGLE_API_KEY` environment variable
- Verify the API key is valid

### Frontend Issues

**"npm command not found":**
- Install Node.js from [nodejs.org](https://nodejs.org/)

**Dependencies issues:**
```bash
# Clear npm cache and reinstall
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

**CORS errors:**
- Make sure backend is running on port 8001
- Check that frontend is running on port 3000

## 🚀 Production Deployment

### Backend
```bash
# Install production dependencies
uv pip install gunicorn

# Run with Gunicorn
gunicorn agent:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8001
```

### Frontend
```bash
# Build for production
npm run build

# Serve static files (example with serve)
npm install -g serve
serve -s build -l 3000
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

If you encounter any issues:

1. Check the troubleshooting section above
2. Verify all environment variables are set correctly
3. Ensure all dependencies are installed
4. Check that both frontend and backend servers are running
5. Open an issue on GitHub with detailed error information

## 🎯 What's New

- ✅ **Fixed YouTube Integration**: Now uses proper SerpAPI or YouTube Data API
- ✅ **No More Fake URLs**: Real YouTube videos or proper error messages
- ✅ **Improved Error Handling**: Clear messages when API keys are missing
- ✅ **Better Documentation**: Comprehensive setup instructions 