# 🌿 EcooVision Intelligent (EVi)

<div align="center">

**Smart Home Energy Management System Powered by AI**

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Django](https://img.shields.io/badge/Django-5.1.4-green.svg)](https://www.djangoproject.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.51.0-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

*A comprehensive smart home system integrating face recognition, predictive analytics, and energy optimization*

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Project Structure](#-project-structure) • [Tech Stack](#-tech-stack)

</div>

---

## 📖 Overview

**EcooVision Intelligent (EVi)** is an advanced smart home management system that combines artificial intelligence, predictive analytics, and energy optimization to create an intelligent living environment. The system provides real-time occupant tracking, accurate exit duration predictions, and comprehensive energy consumption analysis.

### Core Components

1. **🤖 Intelligent Exit Duration Predictor** - ML-powered prediction system using advanced ensemble models
2. **👤 Face Recognition System** - Real-time occupant identification and activity tracking
3. **⚡ Energy Calculator** - Smart electricity cost optimization and savings analysis
4. **🏠 Smart Home Dashboard** - Django-based web interface for comprehensive home management

---

## ✨ Features

### 🎯 Exit Duration Prediction
- **Advanced ML Models**: Utilizes CatBoost, LightGBM, and Stacking Regressor
- **Multi-Factor Analysis**: Considers weather conditions, temporal patterns, and historical data
- **Feature Engineering**: Automated feature transformation and engineering pipeline
- **Interactive Interface**: User-friendly Streamlit web application
- **Real-time Predictions**: Instant duration forecasts based on current conditions

### 👁️ Face Recognition & Tracking
- **Real-time Recognition**: Live camera feed processing with OpenCV
- **Activity Logging**: Automatic entry/exit tracking for all occupants
- **Room Management**: Smart room assignment and lighting control
- **Data Export**: Excel export functionality for activity reports
- **RESTful API**: Full REST API for integration with other systems

### 💡 Energy Optimization
- **Cost Analysis**: Detailed electricity consumption calculations
- **Tariff Management**: Multi-tier pricing support (First/Second tier)
- **Device Management**: Customizable device power consumption tracking
- **Savings Calculator**: Quantify potential energy savings with EVi system
- **Visual Reports**: Interactive charts and graphs using Plotly

### 🏠 Smart Home Integration
- **Automated Lighting**: Intelligent light control based on occupancy
- **Room Status**: Real-time room availability and status
- **User Authentication**: Secure login and user management system
- **Activity Dashboard**: Comprehensive activity monitoring and reporting

---

## 🚀 Installation

### Prerequisites

- Python 3.10 or higher
- pip package manager
- Git

### Step-by-Step Setup

#### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/EcooVision.git
cd EcooVision
```

#### 2. Create Virtual Environment

```bash
python -m venv myenv

# On Windows
myenv\Scripts\activate

# On macOS/Linux
source myenv/bin/activate
```

#### 3. Install Dependencies

**For Django Application:**
```bash
pip install -r requirements.txt
```

**For Machine Learning Application:**
```bash
cd EviTrain
pip install -r requirements.txt
```

**Additional Dependencies for Full Features:**
```bash
pip install streamlit catboost lightgbm scikit-learn seaborn plotly scipy joblib pandas numpy opencv-python dlib face-recognition matplotlib pillow
```

#### 4. Database Setup (Django)

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

#### 5. Collect Static Files

```bash
python manage.py collectstatic --noinput
```

---

## 💻 Usage

### Running the Streamlit Prediction App

Navigate to the Streamlit application directory and launch:

```bash
cd EviTrain/notebooks
streamlit run app.py
```

Access the application at `http://localhost:8501`

**Features:**
- Input weather conditions (temperature, wind, humidity)
- Select day of week and time
- Get instant exit duration predictions
- View detailed analysis and visualizations

### Running the Django Web Application

Start the Django development server:

```bash
python manage.py runserver
```

Access the application at `http://localhost:8000`

**Features:**
- Home dashboard with real-time data
- Face recognition system
- Activity logging and monitoring
- User management and authentication

### Running the Energy Calculator

Launch the standalone calculator:

```bash
cd elec
python main.py
```

**Features:**
- Configure electrical devices and power consumption
- Load custom consumption data from CSV
- Calculate potential savings
- Generate detailed reports

---

## 📂 Project Structure

```
EcooVision/
│
├── 📁 ai_powered_house/                    # Django Project Configuration
│   ├── __init__.py
│   ├── settings.py                         # Main Django configuration
│   ├── urls.py                             # Root URL routing
│   ├── wsgi.py                             # WSGI entry point for production
│   ├── asgi.py                             # ASGI entry point for WebSockets
│   └── __pycache__/                        # Python bytecode
│
├── 📁 EviTrain/                            # 🤖 Machine Learning Module
│   ├── 📁 data/                            # Training & validation datasets
│   │   ├── Cleaned_synthetic_family_data_less_than_48.csv
│   │   └── holidays.csv
│   │
│   ├── 📁 models/                          # Trained ML models (Pickle files)
│   │   ├── optimized_stacking_regressor_advanced.pkl
│   │   ├── feature_engineering_transformer.pkl
│   │   └── Newfeature_engineering_transformer.pkl
│   │
│   ├── 📁 notebooks/                       # Jupyter notebooks & Streamlit app
│   │   ├── app.py                          # 🎯 Main Streamlit application
│   │   ├── main_notebook.ipynb             # Model training & analysis notebook
│   │   ├── evi_logo.png                    # Application logo
│   │   ├── r2_donut.png                    # Model performance visualization
│   │   ├── outputs/                        # Generated analysis outputs
│   │   └── catboost_info/                  # CatBoost training logs & artifacts
│   │
│   ├── 📁 src/                             # Source code modules
│   │   ├── __init__.py
│   │   ├── transformers.py                 # Feature engineering pipeline
│   │   └── utils.py                        # Utility functions & helpers
│   │
│   ├── requirements.txt                    # ML module dependencies
│   └── README.md                           # Module-specific documentation
│
├── 📁 facerecognition/                     # 👤 Face Recognition Module
│   ├── 📁 ai_models/                       # Computer vision models
│   │   ├── recognize.py                    # Face encoding & recognition core
│   │   ├── simple_facerec.py               # Simplified face recognition
│   │   └── __pycache__/
│   │
│   ├── 📁 migrations/                      # Database migration files
│   │   ├── 0001_initial.py
│   │   ├── 0002_activity_date_alter_activity_enter_date_and_more.py
│   │   ├── 0003_alter_person_image.py
│   │   ├── 0004_person_in_house.py
│   │   ├── 0005_remove_activity_action_delete_action.py
│   │   ├── 0006_activity_action.py
│   │   └── 0007_alter_person_room.py
│   │
│   ├── 📁 static/                          # Face recognition static files
│   │   ├── css/
│   │   ├── images/                         # SVG icons & images
│   │   └── js/                             # JavaScript for face detection UI
│   │       └── home.js
│   │
│   ├── admin.py                            # Django admin configuration
│   ├── apps.py                             # App configuration
│   ├── consumers.py                        # WebSocket consumers
│   ├── models.py                           # Django ORM models
│   ├── routing.py                          # WebSocket routing
│   ├── serializers.py                      # Django REST Framework serializers
│   ├── urls.py                             # URL patterns
│   ├── views.py                            # API views & endpoints
│   └── tests.py                            # Unit tests
│
├── 📁 main/                                # 🏠 Django Main Application
│   ├── 📁 static/                          # App-specific static files
│   │   ├── css/                            # Stylesheets
│   │   │   └── login.css
│   │   └── images/                         # Favicons, logos, placeholders
│   │       ├── favicon_io/
│   │       ├── logo/
│   │       └── placeholder.png
│   │
│   ├── admin.py                            # Admin interface config
│   ├── apps.py                             # App configuration
│   ├── middleware.py                       # Custom middleware
│   ├── models.py                           # Core models
│   ├── urls.py                             # URL routing
│   ├── views.py                            # View functions & classes
│   └── tests.py                            # Unit tests
│
├── 📁 elec/                                # ⚡ Energy Calculator Module
│   ├── main.py                             # Tkinter GUI application
│   ├── config.yaml                         # Configuration (tariffs, defaults)
│   ├── test_config_loading.py              # Config loading tests
│   └── app.log                             # Application logs
│
├── 📁 templates/                           # 📄 HTML Templates
│   ├── base.html                           # Base template
│   ├── header.html                         # Header component
│   ├── footer.html                         # Footer component
│   ├── home.html                           # Home dashboard
│   ├── login.html                          # Login page
│   ├── signup.html                         # Signup page
│   ├── add_person.html                     # Add person form
│   ├── face_recognition.html               # Face recognition interface
│   └── all_activities.html                 # Activities list page
│
├── 📁 static/                              # 🎨 Global Static Files
│   ├── admin/                              # Django admin static files
│   │   ├── css/
│   │   ├── img/
│   │   └── js/
│   ├── css/                                # Global stylesheets
│   ├── images/                             # Shared images & icons
│   ├── js/                                 # Global JavaScript
│   └── rest_framework/                     # DRF static files
│
├── 📁 media/                               # 📁 User Uploaded Media
│   ├── faces/                              # Face profile images
│   ├── simu/                               # Simulation images
│   └── profile_placeholder.png             # Default placeholder
│
├── 📁 assets/                              # 🖼️ Additional Assets
│
├── 📁 bin/                                 # 🛠️ Deployment Scripts
│   ├── post_deploy.sh                      # Post-deployment script
│   └── start.sh                            # Application startup script
│
├── 📄 EDA.ipynb                            # 📊 Exploratory Data Analysis notebook
├── 📄 weather-saudi-arabia.ipynb           # Weather data analysis notebook
│
├── 📄 manage.py                            # Django management script
├── 📄 requirements.txt                     # Python dependencies
├── 📄 Procfile                             # Heroku deployment configuration
├── 📄 runtime.txt                          # Python version (3.11.5)
│
├── 📄 LICENSE                              # MIT License
├── 📄 README.md                            # Main project documentation
└── 📄 CONTRIBUTING.md                      # Contribution guidelines
│
📊 Data Files:
├── db.sqlite3                              # SQLite database
├── Cleaned_synthetic_family_data_less_than_48.csv
├── Newsynthetic_family_data_expanded.csv
├── weather-sa-2017-2019-clean.csv
└── Various analysis CSV outputs...

🔧 Utility Scripts:
├── create_csv.py                           # CSV generation utility
├── single_script_synthetic_data.py         # Synthetic data generator
├── electeric_Evi.py                        # Energy calculator utility
└── my_helpers.py                           # Shared helper functions
```

---

## 🛠️ Tech Stack

### Backend
- **Django 5.1.4** - Web framework
- **Django REST Framework** - API development
- **Channels** - WebSocket support
- **WhiteNoise** - Static file serving

### Machine Learning
- **CatBoost** - Gradient boosting
- **LightGBM** - Gradient boosting
- **Scikit-learn** - Model building & evaluation
- **Stacking Regressor** - Ensemble learning
- **Joblib** - Model serialization

### Data Processing
- **Pandas** - Data manipulation
- **NumPy** - Numerical computing
- **Scipy** - Scientific computing

### Computer Vision
- **OpenCV** - Image processing
- **face-recognition** - Face detection & recognition
- **dlib** - Machine learning tools
- **Pillow** - Image handling

### Visualization & UI
- **Streamlit** - Web application framework
- **Plotly** - Interactive plots
- **Matplotlib** - Static plotting
- **Seaborn** - Statistical visualization
- **Tkinter** - Desktop GUI

### Deployment
- **Gunicorn** - WSGI server
- **Heroku** - Cloud platform
- **SQLite** - Development database

---

## 🤝 Contributing

We welcome contributions to EcooVision! Here's how you can help:

### How to Contribute

1. **Fork the Repository**
   ```bash
   git clone https://github.com/yourusername/EcooVision.git
   ```

2. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make Your Changes**
   - Follow PEP 8 style guide
   - Add comments for complex logic
   - Update documentation as needed

4. **Test Your Changes**
   ```bash
   python manage.py test
   ```

5. **Commit Your Changes**
   ```bash
   git commit -m "Add: Your feature description"
   ```

6. **Push and Create Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```

### Contribution Guidelines

- ✅ Write clear, concise commit messages
- ✅ Test all new features thoroughly
- ✅ Update documentation for new features
- ✅ Follow existing code style
- ✅ Add type hints where possible
- ❌ Don't commit large binary files
- ❌ Don't push to main branch directly

---

## 📊 Model Performance

The **Exit Duration Predictor** has been trained and optimized with the following metrics:

- **Model Type**: Stacking Regressor with multiple base estimators
- **Base Models**: CatBoost, LightGBM, Decision Tree, Random Forest, Ridge
- **Feature Engineering**: Automated transformation pipeline
- **Evaluation**: Cross-validation with R² scoring
- **Data**: Synthetic family data with weather conditions and temporal features

**Key Features:**
- Weather categorization (17 types)
- Temporal features (day of week, hour, holidays)
- Interaction features (temp × humidity)
- Lag features and rolling statistics
- Person-specific historical patterns

---

## 📝 API Documentation

### Face Recognition Endpoints

#### Get All Rooms
```http
GET /face_recognition/rooms/
Authorization: Bearer <token>
```

#### Add Person
```http
POST /face_recognition/add_person/
Content-Type: multipart/form-data

{
  "name": "John Doe",
  "about": "Family member",
  "enter_date": "09:00:00",
  "exit_date": "17:00:00",
  "room_number": 1,
  "image": <file>
}
```

#### Get All Activities
```http
GET /face_recognition/activities/
Authorization: Bearer <token>
```

---

## 🔒 Security

- **Authentication**: Django's built-in authentication system
- **CSRF Protection**: Enabled for all forms
- **Secure Cookies**: HTTPS-only cookies in production
- **Session Management**: Secure session handling
- **File Upload Security**: Validation and sanitization

---

## 🌐 Deployment

### Heroku Deployment

The project is configured for Heroku deployment:

```bash
# Create Heroku app
heroku create your-app-name

# Set environment variables
heroku config:set SECRET_KEY=your-secret-key
heroku config:set ENV=PRODUCTION

# Deploy
git push heroku main

# Run migrations
heroku run python manage.py migrate
```

### Environment Variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key-here
ENV=DEVELOPMENT
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2024 EcooVision Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

---

## 🙏 Acknowledgments

- **OpenCV** community for excellent computer vision libraries
- **Streamlit** team for the amazing ML app framework
- **scikit-learn** contributors for robust ML tools
- All open-source contributors who made this project possible

---

## 📧 Contact

For questions, suggestions, or collaboration opportunities:

- **Project Issues**: [GitHub Issues](https://github.com/yourusername/EcooVision/issues)
- **Email**: contact@ecoovision.ai
- **Website**: [www.ecoovision.ai](https://www.ecoovision.ai)

---

## 🗺️ Roadmap

### Upcoming Features

- [ ] Mobile application (iOS/Android)
- [ ] Voice control integration
- [ ] Advanced energy consumption forecasting
- [ ] Multi-language support
- [ ] Cloud data synchronization
- [ ] IoT device integration
- [ ] Real-time notifications
- [ ] Advanced analytics dashboard
- [ ] Machine learning model retraining pipeline
- [ ] Open-source community platform

---

## 📚 Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [scikit-learn User Guide](https://scikit-learn.org/stable/user_guide.html)
- [OpenCV Documentation](https://docs.opencv.org/)
- [Machine Learning Best Practices](https://developers.google.com/machine-learning/guides)

---

<div align="center">

**Made with ❤️ by the EcooVision Team**

⭐ Star us on GitHub if you find this project useful!

[⬆ Back to Top](#-ecoo-vision-intelligent-evi)

</div>

