# Yoel's AI Fitness Coach

A personalized AI fitness coach that learns from daily logs to provide tailored training and nutrition advice.

## Features

- **Smart Logging**: Quick-log presets and detailed daily tracking
- **AI Analysis**: Trend detection, progression analysis, and personalized recommendations
- **Mobile-Friendly**: Streamlit web app accessible on any device
- **Data Visualization**: Progress charts and insights
- **Cloud Ready**: Deploy to Render for always-on access

## Quick Start

### Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the mobile app:
```bash
streamlit run mobile_logger.py --server.port 8501 --server.address 0.0.0.0
```

3. Access on your phone: `http://[your-computer-ip]:8501`

### Cloud Deployment (Render)

See `render_deploy.md` for detailed deployment instructions to Render.

## Usage

### Quick Logging
- Use "Quick Log" for fast preset entries
- Choose from "Great Day", "Recovery Day", or "Rest Day"

### Full Logging
- Detailed tracking of 15+ metrics
- Smart defaults from previous logs
- AI-powered insights

### AI Chat
- Ask about training, nutrition, recovery
- Get personalized advice based on your data
- Context-aware recommendations

### Trends & Analysis
- Progress charts and visualizations
- Training split analysis
- Recovery pattern insights

## Data Files

- `yoel_profile.json`: Your personal profile and preferences
- `daily_logs.json`: All your daily logs and progress data

## Next Steps

- [ ] Deploy to Render for always-on access
- [ ] Add notification system
- [ ] Integrate with fitness trackers
- [ ] Advanced AI recommendations 