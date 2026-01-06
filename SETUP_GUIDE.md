# AgroVision - Setup & Running Guide

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

If you encounter any errors, install dependencies individually:

```bash
pip install Flask flask-cors tensorflow numpy Pillow h5py google-generativeai
```

### 2. Verify Required Files

Make sure these files exist in the project directory:
- ✅ `app.py` - Main Flask application
- ✅ `plant_disease_model.h5` - ML model for disease detection
- ✅ `templates/` folder with all HTML files
- ✅ `static/` folder with CSS and JS files

### 3. Run the Application

**Option 1: Using run.py (Recommended)**
```bash
python run.py
```

**Option 2: Direct Python**
```bash
python app.py
```

### 4. Access the Website

Once running, open your browser and visit:
- 🏠 **Home**: http://127.0.0.1:5000/
- 🔍 **Disease Detection**: http://127.0.0.1:5000/detect
- 🏛️ **Government Schemes**: http://127.0.0.1:5000/schemes
- 🎤 **Voice Help**: http://127.0.0.1:5000/voice
- 🤖 **Chatbot**: http://127.0.0.1:5000/chatbot

## Troubleshooting

### Common Issues

1. **Module Not Found Error**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

2. **Model File Not Found**
   - Ensure `plant_disease_model.h5` is in the root directory
   - Check the file path in `app.py` (line 329)

3. **Port Already in Use**
   - Change port in `app.py` (last line): `app.run(debug=True, port=5001)`
   - Or stop other applications using port 5000

4. **Chatbot API Error**
   - Verify internet connection
   - Check Google API key is valid
   - Chatbot will show fallback message if API fails

5. **Import Errors**
   ```bash
   # For TensorFlow issues
   pip install tensorflow --upgrade
   
   # For Google Generative AI
   pip install google-generativeai --upgrade
   ```

## Features

✅ **Plant Disease Detection** - Upload images to detect plant diseases  
✅ **Government Schemes** - Browse and apply for agricultural schemes  
✅ **AI Chatbot** - Get agriculture-related answers instantly  
✅ **Voice Help** - Voice assistance for farmers  
✅ **Multi-language Support** - Available in multiple Indian languages  

## Project Structure

```
AgroVision/
├── app.py                    # Main Flask application
├── run.py                    # Quick start script
├── plant_disease_model.h5    # ML model file
├── requirements.txt          # Python dependencies
├── templates/                # HTML templates
│   ├── index.html
│   ├── detect.html
│   ├── schemes.html
│   ├── voice.html
│   └── chatbot.html
├── static/                   # Static files
│   ├── css/
│   ├── js/
│   └── uploads/
└── README.md

```

## Notes

- The chatbot requires internet connection for Google Gemini API
- Disease detection works offline after model loads
- Upload folder is automatically created at `static/uploads/`
- Model loading happens on first prediction request

---

**Need Help?** Check the error messages in the terminal for specific issues.
