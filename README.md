# Yoel's AI Fitness Coach

A personalized AI fitness coach that learns from daily logs to provide tailored training and nutrition advice.

## Features

- **Smart Logging**: Quick-log presets and detailed daily tracking
- **AI Analysis**: Trend detection, progression analysis, and personalized recommendations
- **Mobile-Friendly**: Streamlit web app accessible on any device
- **Data Visualization**: Progress charts and insights
- **Cloud Ready**: Deploy to always-on cloud platforms

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

### Cloud Deployment

#### Option 1: Heroku (Recommended)

1. Install Heroku CLI and login
2. Create new Heroku app:
```bash
heroku create yoel-ai-coach
```

3. Deploy:
```bash
git add .
git commit -m "Deploy AI coach"
git push heroku main
```

4. Open your app:
```bash
heroku open
```

#### Option 2: Railway

1. Connect your GitHub repo to Railway
2. Railway will auto-deploy from your main branch
3. Get your always-on URL from Railway dashboard

#### Option 3: Vercel

1. Install Vercel CLI
2. Deploy:
```bash
vercel --prod
```

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

- [ ] Add notification system
- [ ] Integrate with fitness trackers
- [ ] Advanced AI recommendations
- [ ] Social features and sharing 