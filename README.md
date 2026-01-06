# 🌾 AgroVision - AI-Powered Agricultural Disease Detection

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)](https://flask.palletsprojects.com/)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-Ready-orange.svg)](https://www.tensorflow.org/)

> **Empowering farmers with AI-driven crop disease detection, government scheme access, and multi-language support.**

---

## 🎯 Overview

**AgroVision** is a comprehensive web-based platform designed to help farmers identify crop diseases using AI-powered image analysis. Built with a **Modern Agritech theme**, the application prioritizes outdoor usability, accessibility, and inclusive design for farmers of all literacy levels.

### 🌟 Key Features

- 🤖 **AI Disease Detection** - Upload crop images for instant disease identification
- 📊 **Confidence Gauge** - Transparent circular indicator showing AI certainty
- 🔊 **Text-to-Speech** - Audio output for illiterate farmers
- 🌐 **Multi-Language Support** - English, Hindi, Telugu with TTS integration
- 🌾 **Government Schemes** - Direct access to subsidies, insurance, and training programs
- ♿ **High Contrast Mode** - Accessibility for visually impaired users
- 📱 **Mobile-First Design** - Responsive UI with thumb-zone navigation
- 📡 **Offline Detection** - Visual indicator for connectivity status
- 🎨 **Modern UX** - Glassmorphism effects, scanning animations, filter pills

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install flask pillow numpy tensorflow
```

### 2. Run the Application

```bash
cd c:\Users\ASUS\Desktop\AgroVision
python app.py
```

### 3. Open Browser

Navigate to **http://127.0.0.1:5000**

---

## 📂 Project Structure

```
AgroVision/
│
├── 📄 app.py                           # Flask backend with AI integration
│
├── 📁 static/
│   ├── 📁 css/
│   │   └── style.css                   # Modern Agritech theme (1400+ lines)
│   │
│   ├── 📁 js/
│   │   ├── script.js                   # Core functionality (TTS, high contrast)
│   │   ├── lang.js                     # Multi-language translations
│   │   └── enhanced.js                 # Advanced features (gauge, greeting)
│   │
│   └── 📁 uploads/                     # User-uploaded images
│
├── 📁 templates/
│   ├── index.html                      # Landing page with hero section
│   ├── detect.html                     # Disease detection interface
│   ├── result.html                     # Results with confidence gauge
│   ├── schemes.html                    # Government schemes with filters
│   └── voice.html                      # Voice assistance information
│
├── 📄 QUICKSTART.md                    # Quick start guide
├── 📄 TESTING_GUIDE.md                 # Comprehensive testing instructions
└── 📄 THEME_IMPLEMENTATION.md          # Design system documentation
```

---

## 🎨 Design System

### Color Palette

| Color | Hex | Usage |
|-------|-----|-------|
| **Forest Green** | `#2E7D32` | Primary buttons, accents, healthy indicators |
| **Golden Wheat** | `#F9A825` | CTAs, warnings, highlights |
| **Mint Cream** | `#F4F7F6` | Background (anti-glare for outdoor use) |
| **Dark Charcoal** | `#1C2833` | Primary text |
| **Alert Red** | `#D32F2F` | Urgent treatment cards |
| **Healthy Green** | `#388E3C` | Prevention cards |

### Typography

- **Headings**: Roboto Slab (serif) - Professional trust
- **Body**: Inter (sans-serif) - Easy readability
- **Minimum Size**: 16px for accessibility

### UI Components

- **Glassmorphism Navbar** - Frosted glass with `backdrop-filter: blur(10px)`
- **Scanning Animation** - Green laser effect with CSS keyframes
- **Confidence Gauge** - Circular SVG progress indicator
- **Filter Pills** - Horizontal scrollable navigation
- **Mobile Bottom Nav** - Thumb-zone design (48x48px touch targets)
- **Color-Coded Cards** - Red borders (urgent), Blue borders (preventive)

---

## 🛠️ Tech Stack

### Backend
- **Flask** - Python web framework
- **TensorFlow/Keras** - AI model support (ready for real models)
- **PIL (Pillow)** - Image preprocessing
- **NumPy** - Data manipulation

### Frontend
- **HTML5** - Semantic markup
- **CSS3** - Custom properties, animations, glassmorphism
- **Vanilla JavaScript** - No dependencies
- **Google Fonts** - Roboto Slab, Inter

### APIs & Features
- **Web Speech API** - Text-to-speech functionality
- **localStorage** - User preferences (language, high contrast)
- **Drag-and-Drop API** - Image upload UX

---

## 🎯 Features Deep Dive

### 1. AI Disease Detection

**How it works:**
1. User uploads crop/seed image (drag-drop or click)
2. Image is preprocessed (resized to 224x224, normalized)
3. AI model predicts disease (currently demo mode)
4. Results display with confidence percentage

**Categories:**
- 🌱 Leaf Diseases (tomato blight, wheat rust, rice blast, etc.)
- 🌾 Seed Defects (discoloration, damage, mold, etc.)

### 2. Text-to-Speech (TTS)

**Features:**
- Speaks disease name, treatment, and prevention
- Supports multiple languages (EN, HI, TE)
- Automatic language detection from user preference
- Click "🔊 Read Results Aloud" button

**Accessibility Impact:**
- Helps illiterate farmers (40% of Indian farmers)
- Works in noisy field environments
- Audio reinforces visual information

### 3. Multi-Language Support

**Supported Languages:**
- 🇬🇧 English (en-US)
- 🇮🇳 Hindi (hi-IN)
- 🇮🇳 Telugu (te-IN)

### 4. Government Schemes

**Filter Categories:**
- 📋 All Schemes
- 💰 Subsidies
- 🛡️ Insurance
- 📚 Training
- 🌱 Organic Farming
- 🚜 Equipment

---

## 🛠 Current Mode: Demo/Hackathon
The application currently runs in **demo mode** without actual AI models. This is perfect for:
- Testing the workflow
- Demonstrating the system architecture
- Hackathon presentations

### To Use Real AI Models:
1. Train your models using TensorFlow/Keras
2. Save models as `leaf_model.h5` and `seed_model.h5` in the `model/` directory
3. Uncomment model loading lines in `app.py`

## 🎤 Judge Presentation Points
✅ **Working System**: Upload → Process → Result  
✅ **Modular Design**: Easy to extend to other plant parts  
✅ **Scalable Architecture**: Can add more disease types  
✅ **Future Scope**: Offline mode, IVR support, multilingual  

## 🔮 Future Enhancements
- [ ] Stem, root, and branch disease detection
- [ ] Government schemes integration
- [ ] Multi-language support (Hindi, regional languages)
- [ ] Voice-based interaction (IVR)
- [ ] Offline inference capability
- [ ] Mobile app version
- [ ] Community forum for farmers

## 📚 Technology Stack
- **Backend**: Flask (Python)
- **AI/ML**: TensorFlow, Keras
- **Frontend**: HTML, CSS, JavaScript
- **Image Processing**: PIL (Pillow)

## 🤝 Contributing
This is a modular framework designed for easy expansion. Add new detection modules by:
1. Creating new model endpoints
2. Adding corresponding templates
3. Updating the category dropdown

## 📄 License
Educational/Hackathon Project

## 👥 Team
AgroVision Development Team

---
**Note**: Remember to add your trained models to the `model/` directory before production use!
