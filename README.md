# LocaLens 🗺️

> **AI-Powered Geospatial Intelligence Platform** - A HERE Technologies project delivering actionable location insights for modern businesses.

![LocaLens Banner](https://img.shields.io/badge/LocaLens-HERE%20Technologies-4A7C59?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEyIDJDMTMuMSAyIDE0IDIuOSAxNCA0VjE2QzE0IDE3LjEgMTMuMSAxOCA5LjUgMThIMTUuNUMxNi45IDE4IDE4IDE3LjEgMTggMTZWMTRDMTggMi45IDE2LjkgMiAxNS41IDJIMTIiIGZpbGw9IiM0QTdDNTkiLz4KPHBhdGggZD0iTTEyIDJDMTMuMSAyIDE0IDIuOSAxNCA0VjE2QzE0IDE3LjEgMTMuMSAxOCA5LjUgMThIMTUuNUMxNi45IDE4IDE4IDE3LjEgMTggMTZWMTRDMTggMi45IDE2LjkgMiAxNS41IDJIMTIiIGZpbGw9IiNGOUY5RjkiIHN0cm9rZT0iIzRBN0M1OSIgc3Ryb2tlLXdpZHRoPSIyIi8+Cjwvc3ZnPgo=)

## 🌟 Overview

LocaLens is an intelligent geospatial analysis platform built for HERE Technologies that transforms raw address data into actionable business intelligence. Using advanced machine learning and HERE Maps integration, LocaLens provides comprehensive location validation, risk assessment, and delivery optimization insights.

### 🎯 Key Capabilities

- **Address Intelligence**: Multi-source geocoding with confidence scoring
- **Risk Assessment**: Fraud detection, safety analysis, and property risk evaluation
- **Delivery Optimization**: Route planning, warehouse selection, and logistics intelligence
- **Real-time Monitoring**: Anomaly detection and predictive analytics
- **HERE Integration**: Native support for HERE Maps, Routing, and Geocoding APIs

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   HERE APIs     │
│   (React/TS)    │◄──►│   (FastAPI)     │◄──►│   (Maps,        │
│                 │    │                 │    │    Routing)     │
│ • Clean UI      │    │ • ML Pipeline   │    │                 │
│ • Real-time     │    │ • Geospatial    │    │                 │
│ • HERE Maps     │    │ • Monitoring    │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Data Flow     │
                    │ • Address       │
                    │ • Coordinates   │
                    │ • Intelligence  │
                    │ • Analytics     │
                    └─────────────────┘
```

## 🚀 Features

### Core Intelligence
- **Multi-Source Geocoding**: HERE Maps + ML-powered address resolution
- **Confidence Fusion**: Intelligent combination of multiple geocoding sources
- **Address Quality Scoring**: Comprehensive validation and integrity checks
- **Geospatial Analysis**: Location-based insights and spatial relationships

### Business Intelligence
- **Deliverability Assessment**: Route optimization and delivery success prediction
- **Safety & Risk Analysis**: Crime data, traffic patterns, and neighborhood insights
- **Fraud Detection**: Anomaly detection for suspicious address patterns
- **Property Intelligence**: Risk assessment and market analysis

### Advanced Analytics
- **Predictive Modeling**: ML-driven insights and trend analysis
- **Real-time Monitoring**: Prometheus metrics and alerting
- **Anomaly Detection**: Automated identification of unusual patterns
- **Performance Analytics**: System health and processing metrics

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI (Python async web framework)
- **ML/AI**: scikit-learn, sentence-transformers, OpenAI API
- **Geospatial**: HERE Maps API, custom ML geocoding models
- **Monitoring**: Prometheus, custom metrics collection
- **Database**: File-based storage with pandas for analytics

### Frontend
- **Framework**: React 18 with TypeScript
- **Styling**: Tailwind CSS with custom design system
- **State Management**: React Context + React Query
- **Maps**: HERE Maps JavaScript API integration
- **Build Tool**: Vite for fast development and optimized builds

### Infrastructure
- **Containerization**: Docker support
- **API Documentation**: Auto-generated OpenAPI/Swagger
- **Testing**: pytest for backend, comprehensive test coverage
- **Code Quality**: ESLint, Prettier, Black

## 📦 Installation

### Prerequisites
- Python 3.8+
- Node.js 18+
- HERE Maps API credentials
- OpenAI API key (optional, for enhanced features)

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/rafainamdar04/locaLens.git
   cd locaLens
   ```

2. **Set up Python environment**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys:
   # HERE_API_KEY=your_here_api_key
   # OPENAI_API_KEY=your_openai_api_key
   ```

4. **Run the backend**
   ```bash
   python main.py
   ```
   Server will start at `http://localhost:8000`

### Frontend Setup

1. **Install dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Configure API endpoint**
   ```bash
   # Update src/api/client.ts if needed
   const API_BASE_URL = 'http://localhost:8000';
   ```

3. **Start development server**
   ```bash
   npm run dev
   ```
   Frontend will be available at `http://localhost:5173`

## 🎮 Usage

### Basic Address Analysis

1. **Access the application** at `http://localhost:5173`
2. **Login** with default credentials (admin/admin123)
3. **Enter an address** in the main input field
4. **View comprehensive results** including:
   - Geocoding confidence scores
   - HERE Maps integration
   - Safety and risk assessments
   - Delivery optimization insights

### API Usage

```python
import requests

# Process an address
response = requests.post('http://localhost:8000/process_v3', json={
    'raw_address': 'Connaught Place, New Delhi 110001',
    'addons': ['deliverability', 'safety']
})

result = response.json()
print(f"Confidence: {result['confidence']}")
print(f"HERE Coordinates: {result['here_results']['primary_result']}")
```

### Advanced Features

- **Batch Processing**: Process multiple addresses simultaneously
- **Custom Add-ons**: Extend functionality with custom analysis modules
- **Real-time Monitoring**: Access admin dashboard for system metrics
- **Anomaly Detection**: Automated alerts for unusual patterns

## 📊 API Reference

### Core Endpoints

#### `POST /process_v3`
Process an address with comprehensive analysis.

**Request:**
```json
{
  "raw_address": "123 Main St, Anytown, USA",
  "addons": ["deliverability", "safety", "fraud"]
}
```

**Response:**
```json
{
  "event": {
    "raw_address": "123 Main St, Anytown, USA",
    "confidence": 0.95,
    "health": "OK",
    "here_results": {...},
    "ml_results": {...},
    "addons": {...}
  },
  "processing_time_ms": 245
}
```

#### `GET /health`
System health and metrics.

#### `GET /metrics`
Prometheus-compatible metrics.

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `HERE_API_KEY` | HERE Maps API key | Yes |
| `OPENAI_API_KEY` | OpenAI API key for enhanced features | No |
| `PORT` | Server port (default: 8000) | No |
| `LOG_LEVEL` | Logging level | No |

### HERE API Setup

1. Sign up at [HERE Developer Portal](https://developer.here.com/)
2. Create a project and get API credentials
3. Enable required APIs: Geocoding, Routing, Places
4. Add credentials to `.env` file

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v
```

### Frontend Tests
```bash
cd frontend
npm test
```

### Integration Tests
```bash
# Run both backend and frontend tests
npm run test:all
```

## 📈 Monitoring & Analytics

### System Metrics
- Request throughput and latency
- Geocoding success rates
- ML model performance
- Error rates and anomalies

### Business Intelligence
- Address quality trends
- Delivery success rates
- Geographic coverage analysis
- Risk assessment patterns

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** and add tests
4. **Commit your changes**: `git commit -m 'Add amazing feature'`
5. **Push to the branch**: `git push origin feature/amazing-feature`
6. **Open a Pull Request**

### Development Guidelines
- Follow PEP 8 for Python code
- Use TypeScript strict mode
- Add comprehensive tests
- Update documentation
- Ensure cross-platform compatibility

## 📄 License

This project is proprietary software developed for HERE Technologies. All rights reserved.

## 🙏 Acknowledgments

- **HERE Technologies** for Maps API and platform support
- **OpenAI** for language model integration
- **FastAPI** and **React** communities for excellent frameworks
- **Scikit-learn** and **Hugging Face** for ML capabilities

## 📞 Support

For support and questions:
- **Documentation**: See individual README files in backend/ and frontend/
- **Issues**: Use GitHub Issues for bug reports and feature requests
- **Discussions**: GitHub Discussions for general questions

---

**Built with ❤️ for HERE Technologies** | **Empowering Location Intelligence** 🗺️</content>
<parameter name="filePath">d:\locaLens\README.md