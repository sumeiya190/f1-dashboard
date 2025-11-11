# F1 Data Analysis & Dashboard Project
# =====================================

## 🏎️ Project Overview
This project provides a complete F1 data analysis and visualization dashboard using official F1 timing data via FastF1.

## 🛠️ Technology Stack

### Core Tools
- **Python 3.11+**: Programming language
- **FastF1**: F1 data API library
- **Streamlit**: Interactive web dashboard framework
- **Plotly**: Interactive visualizations
- **Pandas**: Data manipulation

### Key Features
- 📊 Interactive race analysis dashboard
- 🏁 Lap time comparisons
- 🚗 Driver telemetry analysis
- 📈 Tire strategy visualization
- 🗺️ Track position mapping
- ⚡ Speed trace analysis

## 📦 Installation

### 1. Create Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv f1_env

# Activate virtual environment
# Windows:
f1_env\Scripts\activate
# Mac/Linux:
source f1_env/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

## 🚀 Quick Start

### Run the Dashboard
```bash
streamlit run app.py
```

The dashboard will open in your browser at `http://localhost:8501`

## 📁 Project Structure
```
F1CODE/
├── app.py                  # Main Streamlit dashboard
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── utils/
│   ├── __init__.py        # Package initialization
│   ├── data_loader.py     # FastF1 data loading functions
│   ├── analysis.py        # Analysis calculations
│   └── visualizations.py  # Plotly chart functions
├── pages/
│   ├── 1_📊_Race_Analysis.py      # Race analysis page
│   ├── 2_🏁_Lap_Times.py          # Lap time comparison
│   ├── 3_🚗_Telemetry.py          # Telemetry analysis
│   └── 4_📈_Tire_Strategy.py      # Tire strategy
└── data/
    └── cache/             # FastF1 cache directory
```

## 📊 Features

### 1. Race Analysis
- View race results and standings
- Analyze race pace by driver
- Compare race strategies
- View lap-by-lap positions

### 2. Lap Time Comparison
- Compare lap times between drivers
- Identify fastest laps
- Analyze sector times
- Tire compound performance

### 3. Telemetry Analysis
- Speed traces on track
- Brake point analysis
- Throttle and gear usage
- Compare driver telemetry

### 4. Tire Strategy
- Visualize pit stop strategies
- Tire compound usage
- Tire life analysis
- Strategy comparison

## 🎯 Usage Examples

### Load Race Data
```python
from utils.data_loader import load_race_session

# Load 2024 Monaco Grand Prix race session
session = load_race_session(2024, 'Monaco', 'R')
```

### Compare Driver Lap Times
```python
from utils.analysis import compare_lap_times

# Compare Verstappen vs Hamilton lap times
comparison = compare_lap_times(session, ['VER', 'HAM'])
```

### Create Speed Trace Chart
```python
from utils.visualizations import create_speed_trace

# Create interactive speed trace chart
fig = create_speed_trace(session, ['VER', 'HAM'], lap_number=30)
```

## 🔧 Configuration

### FastF1 Cache
FastF1 caches data locally to speed up subsequent loads. Cache location:
```
data/cache/
```

To clear cache:
```python
import shutil
shutil.rmtree('data/cache')
```

## 📚 Resources

- **FastF1 Documentation**: https://docs.fastf1.dev/
- **Streamlit Documentation**: https://docs.streamlit.io/
- **Plotly Documentation**: https://plotly.com/python/

## 🐛 Troubleshooting

### Issue: "No module named 'fastf1'"
**Solution**: Activate virtual environment and install dependencies:
```bash
f1_env\Scripts\activate
pip install -r requirements.txt
```

### Issue: "Cache directory not found"
**Solution**: The cache directory is created automatically on first run.

### Issue: "API rate limit exceeded"
**Solution**: FastF1 data is cached locally after first download. Wait a few minutes and try again.

## 🤝 Contributing

Feel free to add new features:
1. Add new analysis pages in `pages/`
2. Create new visualizations in `utils/visualizations.py`
3. Add new data processing functions in `utils/analysis.py`

## 📝 License

This project is for personal use and educational purposes.

## 🏁 Getting Started Checklist

- [ ] Install Python 3.11+
- [ ] Create virtual environment
- [ ] Install dependencies (`pip install -r requirements.txt`)
- [ ] Run dashboard (`streamlit run app.py`)
- [ ] Select a race from the dropdown
- [ ] Explore the different analysis pages

## 💡 Tips

1. **First Load**: The first time you load data for a race, it will take a few minutes to download and cache. Subsequent loads are instant.

2. **Interactive Charts**: All Plotly charts are interactive - zoom, pan, and hover for details.

3. **Driver Selection**: Use the sidebar to select specific drivers for comparison.

4. **Session Types**: You can analyze Practice, Qualifying, Sprint, and Race sessions.

5. **Performance**: For best performance, keep the cache directory intact between runs.

---

**Created with ❤️ for F1 data enthusiasts**
