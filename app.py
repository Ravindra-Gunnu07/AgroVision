import os
import logging
import random
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from PIL import Image
import numpy as np

# --- CONFIGURATION ---
app = Flask(__name__)

# Enable CORS for frontend-backend communication
CORS(app)

# Configuration
app.config["UPLOAD_FOLDER"] = "static/uploads"
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB Limit
app.config["ALLOWED_EXTENSIONS"] = {'png', 'jpg', 'jpeg', 'webp'}

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = app.logger

# Ensure upload directory exists
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# --- LAZY-LOADED ML MODELS ---
_plant_disease_model = None
_plant_disease_target_size = (224, 224)  # (width, height)
_plant_disease_classes = None  # Will be populated from model

# --- DISEASE DATABASE (Comprehensive) ---
# Common plant diseases with cure and prevention information
DISEASE_DATABASE = {
    # Healthy
    "Healthy": {
        "cure": "N/A",
        "prevention": "Continue maintaining current care routine. Monitor regularly for early signs of disease.",
        "description": "Your plant appears healthy with no visible signs of disease."
    },
    # Tomato Diseases
    "Tomato___Bacterial_spot": {
        "name": "Bacterial Spot",
        "cure": "Remove infected leaves. Apply copper-based bactericides. Avoid overhead watering.",
        "prevention": "Use disease-free seeds. Rotate crops. Space plants properly for air circulation.",
        "description": "Bacterial spot causes dark, water-soaked lesions on leaves and fruits."
    },
    "Tomato___Early_blight": {
        "name": "Early Blight",
        "cure": "Apply fungicides containing chlorothalonil or mancozeb. Remove lower infected leaves.",
        "prevention": "Use resistant varieties. Ensure proper spacing. Use drip irrigation to keep foliage dry.",
        "description": "Early blight causes dark brown spots with concentric rings on lower leaves."
    },
    "Tomato___Late_blight": {
        "name": "Late Blight",
        "cure": "Apply fungicides immediately (copper-based or systemic fungicides). Remove and destroy infected plants.",
        "prevention": "Plant resistant varieties. Avoid overhead watering. Ensure good air circulation.",
        "description": "Late blight causes water-soaked lesions that turn brown and spread rapidly."
    },
    "Tomato___Leaf_Mold": {
        "name": "Leaf Mold",
        "cure": "Apply fungicides containing chlorothalonil. Improve air circulation and reduce humidity.",
        "prevention": "Use resistant varieties. Space plants properly. Ventilate greenhouses well.",
        "description": "Leaf mold causes yellow spots on upper leaf surfaces with fuzzy gray mold underneath."
    },
    "Tomato___Septoria_leaf_spot": {
        "name": "Septoria Leaf Spot",
        "cure": "Remove infected leaves. Apply fungicides containing chlorothalonil or mancozeb.",
        "prevention": "Rotate crops. Avoid overhead watering. Remove plant debris after harvest.",
        "description": "Septoria leaf spot causes small, circular spots with dark borders on leaves."
    },
    "Tomato___Spider_mites": {
        "name": "Spider Mites",
        "cure": "Apply insecticidal soap or neem oil. Increase humidity. Remove heavily infested leaves.",
        "prevention": "Keep plants well-watered. Monitor regularly. Introduce beneficial insects.",
        "description": "Spider mites cause stippling, yellowing, and webbing on leaves."
    },
    "Tomato___Target_Spot": {
        "name": "Target Spot",
        "cure": "Apply fungicides containing azoxystrobin or chlorothalonil. Remove infected leaves.",
        "prevention": "Use resistant varieties. Ensure proper spacing. Avoid overhead watering.",
        "description": "Target spot causes circular lesions with concentric rings, resembling a target."
    },
    "Tomato___Tomato_mosaic_virus": {
        "name": "Tomato Mosaic Virus",
        "cure": "No cure. Remove and destroy infected plants. Disinfect tools and hands.",
        "prevention": "Use virus-free seeds. Control aphids. Practice good hygiene in the garden.",
        "description": "Mosaic virus causes mottled, distorted leaves and reduced fruit quality."
    },
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": {
        "name": "Yellow Leaf Curl Virus",
        "cure": "No cure. Remove infected plants. Control whiteflies with insecticides.",
        "prevention": "Use resistant varieties. Control whitefly populations. Use row covers.",
        "description": "Yellow leaf curl causes upward curling of leaves and yellowing."
    },
    # Potato Diseases
    "Potato___Early_blight": {
        "name": "Early Blight",
        "cure": "Apply fungicides containing chlorothalonil. Remove infected leaves.",
        "prevention": "Rotate crops. Use certified seed potatoes. Ensure proper spacing.",
        "description": "Early blight causes dark brown spots with target-like rings on leaves."
    },
    "Potato___Late_blight": {
        "name": "Late Blight",
        "cure": "Apply fungicides immediately. Remove and destroy infected plants.",
        "prevention": "Use certified disease-free seed. Plant resistant varieties. Avoid overhead watering.",
        "description": "Late blight causes rapid browning and death of foliage, affecting tubers."
    },
    # Pepper Diseases
    "Pepper___bell___Bacterial_spot": {
        "name": "Bacterial Spot",
        "cure": "Apply copper-based bactericides. Remove infected plant parts.",
        "prevention": "Use disease-free seeds. Rotate crops. Avoid overhead watering.",
        "description": "Bacterial spot causes dark, water-soaked lesions on leaves and fruits."
    },
    "Pepper___bell___Healthy": {
        "name": "Healthy",
        "cure": "N/A",
        "prevention": "Continue maintaining current care routine.",
        "description": "Your pepper plant appears healthy."
    },
    # Corn Diseases
    "Corn___Common_rust": {
        "name": "Common Rust",
        "cure": "Apply fungicides containing propiconazole or azoxystrobin.",
        "prevention": "Plant resistant varieties. Rotate crops. Ensure proper spacing.",
        "description": "Common rust causes reddish-brown pustules on both sides of leaves."
    },
    "Corn___Northern_Leaf_Blight": {
        "name": "Northern Leaf Blight",
        "cure": "Apply fungicides containing chlorothalonil or mancozeb.",
        "prevention": "Plant resistant varieties. Rotate crops. Remove crop debris.",
        "description": "Northern leaf blight causes long, elliptical lesions on leaves."
    },
    # Apple Diseases
    "Apple___Apple_scab": {
        "name": "Apple Scab",
        "cure": "Apply fungicides containing captan or myclobutanil. Remove infected leaves.",
        "prevention": "Plant resistant varieties. Prune for good air circulation. Remove fallen leaves.",
        "description": "Apple scab causes dark, scaly lesions on leaves and fruits."
    },
    "Apple___Black_rot": {
        "name": "Black Rot",
        "cure": "Apply fungicides containing captan. Remove and destroy infected fruits and cankers.",
        "prevention": "Prune to improve air circulation. Remove mummified fruits. Sanitize pruning tools.",
        "description": "Black rot causes dark, sunken lesions on fruits and cankers on branches."
    },
    "Apple___Cedar_apple_rust": {
        "name": "Cedar Apple Rust",
        "cure": "Apply fungicides containing myclobutanil or propiconazole during bloom.",
        "prevention": "Remove nearby cedar trees if possible. Plant resistant varieties.",
        "description": "Cedar apple rust causes yellow-orange spots on leaves and fruits."
    },
    # Cherry Diseases
    "Cherry___Powdery_mildew": {
        "name": "Powdery Mildew",
        "cure": "Apply fungicides containing sulfur or myclobutanil. Prune for air circulation.",
        "prevention": "Plant resistant varieties. Ensure good air circulation. Avoid overhead watering.",
        "description": "Powdery mildew causes white, powdery coating on leaves and shoots."
    },
    # Grape Diseases
    "Grape___Black_rot": {
        "name": "Black Rot",
        "cure": "Apply fungicides containing mancozeb or captan. Remove infected fruits and leaves.",
        "prevention": "Prune for good air circulation. Remove mummified fruits. Use resistant varieties.",
        "description": "Black rot causes dark, sunken lesions on fruits and brown spots on leaves."
    },
    "Grape___Esca": {
        "name": "Esca (Black Measles)",
        "cure": "No effective cure. Remove severely infected vines. Apply preventive fungicides.",
        "prevention": "Use disease-free planting material. Avoid wounding vines. Sanitize pruning tools.",
        "description": "Esca causes leaf discoloration, wood decay, and fruit rot."
    },
    "Grape___Leaf_blight": {
        "name": "Leaf Blight",
        "cure": "Apply fungicides containing copper or mancozeb. Remove infected leaves.",
        "prevention": "Prune for air circulation. Remove plant debris. Use resistant varieties.",
        "description": "Leaf blight causes brown spots and premature leaf drop."
    },
    # Strawberry Diseases
    "Strawberry___Leaf_scorch": {
        "name": "Leaf Scorch",
        "cure": "Apply fungicides containing captan or thiophanate-methyl.",
        "prevention": "Use disease-free plants. Ensure good air circulation. Remove old leaves.",
        "description": "Leaf scorch causes purple spots on leaves that may turn brown."
    },
    # Peach Diseases
    "Peach___Bacterial_spot": {
        "name": "Bacterial Spot",
        "cure": "Apply copper-based bactericides. Prune infected branches.",
        "prevention": "Use disease-free planting material. Prune for air circulation.",
        "description": "Bacterial spot causes dark lesions on leaves, fruits, and twigs."
    },
}

# Legacy support for old disease names
LEAF_DISEASES = [
    {
        "name": "Early Blight",
        "cure": "Apply copper-based fungicide and remove lower infected leaves.",
        "prevention": "Ensure proper spacing and use drip irrigation to keep foliage dry."
    },
    {
        "name": "Leaf Rust",
        "cure": "Spray sulfur-based organic fungicides immediately.",
        "prevention": "Plant resistant varieties and rotate crops every season."
    },
    {
        "name": "Healthy",
        "cure": "N/A",
        "prevention": "Continue maintaining current care routine."
    }
]


# --- UTILITY FUNCTIONS ---

def allowed_file(filename):
    """Security check for file extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]

def preprocess_image(path):
    """
    Prepare image for model prediction.
    Resize -> Normalize -> Expand Dims
    """
    try:
        img = Image.open(path)
        img = img.resize((224, 224))
        img_array = np.array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        return img_array
    except Exception as e:
        logger.error(f"Error processing image: {e}")
        return None

def load_model_lazy():
    """
    Lazy loading: Only load heavy TensorFlow models when needed.
    Prevents server timeout on startup.
    """
    # global leaf_model
    # if leaf_model is None:
    #     leaf_model = tf.keras.models.load_model("model/leaf_model.h5")
    pass


def _rebuild_plant_disease_model_from_weights(model_path):
    """Rebuild plant disease model and load weights by name."""
    import json
    import h5py
    import tensorflow as tf

    # Infer input shape from saved config
    input_shape = (224, 224, 3)
    num_classes = None
    
    try:
        with h5py.File(model_path, "r") as f:
            mc = f.attrs.get("model_config")
            if mc is not None:
                mc = mc.decode("utf-8") if hasattr(mc, "decode") else mc
                data = json.loads(mc)
                layers = (data.get("config") or {}).get("layers") or []
                if layers and layers[0].get("class_name") == "InputLayer":
                    bs = (layers[0].get("config") or {}).get("batch_shape")
                    if isinstance(bs, list) and len(bs) == 4:
                        h, w, c = bs[1], bs[2], bs[3]
                        if isinstance(h, int) and isinstance(w, int) and isinstance(c, int):
                            input_shape = (h, w, c)
                
                # Try to infer number of classes from last layer
                if layers:
                    last_layer = layers[-1]
                    if last_layer.get("class_name") == "Dense":
                        units = (last_layer.get("config") or {}).get("units")
                        if isinstance(units, int):
                            num_classes = units
    except Exception as e:
        logger.warning(f"Could not fully infer model structure: {e}")

    # Default to common architecture if we can't infer
    if num_classes is None:
        num_classes = 38  # Common number for plant disease models
    
    inputs = tf.keras.Input(shape=input_shape)
    base = tf.keras.applications.MobileNetV2(
        include_top=False,
        weights=None,
        input_tensor=inputs,
        input_shape=input_shape
    )
    x = base.output
    x = tf.keras.layers.GlobalAveragePooling2D()(x)
    outputs = tf.keras.layers.Dense(num_classes, activation="softmax")(x)
    model = tf.keras.Model(inputs=inputs, outputs=outputs)
    
    try:
        model.load_weights(model_path, by_name=True, skip_mismatch=True)
    except Exception as e:
        logger.warning(f"Could not load weights by name: {e}")
        raise
    
    return model


def _get_plant_disease_model():
    """Load and cache the plant disease model."""
    global _plant_disease_model, _plant_disease_target_size, _plant_disease_classes

    if _plant_disease_model is not None:
        return _plant_disease_model

    model_path = "plant_disease_model.h5"
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Plant disease model not found: {model_path}")

    import tensorflow as tf
    logger.info(f"Attempting to load disease model from: {model_path}")
    
    # Try direct load first
    try:
        model = tf.keras.models.load_model(
            model_path, 
            compile=False,
            custom_objects={'MobileNetV2': tf.keras.applications.MobileNetV2}
        )
        logger.info("✅ Disease model loaded successfully!")
    except Exception as e:
        error_str = str(e)
        logger.warning(f"Direct load failed with: {error_str[:200]}")
        
        if 'Unknown argument' in error_str or 'name' in error_str.lower():
            try:
                logger.info("Attempting alternative loading method...")
                model = tf.keras.models.load_model(model_path, compile=True)
                logger.info("✅ Disease model loaded with compile=True!")
            except Exception as e2:
                logger.info("Falling back to weight-based rebuild...")
                try:
                    model = _rebuild_plant_disease_model_from_weights(model_path)
                    logger.info("✅ Disease model rebuilt successfully from weights!")
                except Exception as rebuild_error:
                    logger.error(f"Rebuild also failed: {str(rebuild_error)[:200]}")
                    raise Exception(f"Failed to load disease model via all methods. Last error: {str(rebuild_error)[:200]}")
        else:
            logger.info("Falling back to weight-based rebuild...")
            try:
                model = _rebuild_plant_disease_model_from_weights(model_path)
                logger.info("✅ Disease model rebuilt successfully from weights!")
            except Exception as rebuild_error:
                logger.error(f"Rebuild also failed: {str(rebuild_error)[:200]}")
                raise Exception(f"Failed to load disease model via both methods. Direct: {error_str[:100]}, Rebuild: {str(rebuild_error)[:100]}")

    # Infer target size
    try:
        input_shape = model.input_shape
        if isinstance(input_shape, list):
            input_shape = input_shape[0]
        h, w = input_shape[1], input_shape[2]
        if isinstance(h, int) and isinstance(w, int) and h > 0 and w > 0:
            _plant_disease_target_size = (w, h)
            logger.info(f"✅ Inferred disease model target size: {_plant_disease_target_size}")
    except Exception as e:
        logger.warning(f"Could not infer target size: {e}. Using default (224, 224)")
        _plant_disease_target_size = (224, 224)

    # Try to get class names from model
    try:
        output_shape = model.output_shape
        if isinstance(output_shape, list):
            output_shape = output_shape[0]
        num_classes = output_shape[-1] if output_shape else None
        logger.info(f"✅ Disease model has {num_classes} output classes")
        
        # Try to extract class names from model metadata if available
        try:
            if hasattr(model, 'class_names'):
                _plant_disease_classes = model.class_names
                logger.info(f"✅ Found class names in model: {len(_plant_disease_classes)} classes")
            elif hasattr(model, 'config') and 'class_names' in model.config:
                _plant_disease_classes = model.config['class_names']
                logger.info(f"✅ Found class names in model config: {len(_plant_disease_classes)} classes")
        except Exception as e:
            logger.warning(f"Could not extract class names from model: {e}")
    except Exception as e:
        logger.warning(f"Could not infer number of classes: {e}")

    _plant_disease_model = model
    logger.info(f"✅ Plant disease model ready. Target size: {_plant_disease_target_size}")
    return _plant_disease_model



# --- ROUTES ---

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/detect")
def detect():
    return render_template("detect.html")

@app.route("/schemes")
def schemes():
    return render_template("schemes.html")

@app.route("/voice")
def voice():
    return render_template("voice.html")

@app.route("/chatbot")
def chatbot():
    return render_template("chatbot.html")

@app.route("/predict", methods=["POST"])
def predict():
    """
    API Endpoint: Receives image -> Returns JSON Result
    """
    try:
        # 1. Validation
        if 'image' not in request.files:
            return jsonify({"error": "No file part"}), 400
        
        file = request.files['image']
        # category = request.form.get('category', 'leaf') # Unused in simple binary mode but kept if needed

        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        if not allowed_file(file.filename):
            return jsonify({"error": "Invalid file type. Use JPG/PNG."}), 400

        # 2. Secure Save (Optional, good for debugging)
        filename = secure_filename(f"{datetime.now().strftime('%H%M%S')}_{file.filename}")
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        logger.info(f"File saved: {file_path}")

        # 3. Load Disease Model & Preprocess
        logger.info("Loading disease model...")
        model = _get_plant_disease_model()
        logger.info(f"Disease model loaded. Target size: {_plant_disease_target_size}")
        target_size = _plant_disease_target_size
        
        # Preprocess image from disk
        logger.info(f"Preprocessing image: {file_path}")
        try:
            pil_image = Image.open(file_path).convert("RGB")
            pil_image = pil_image.resize(target_size)
            img_array = np.asarray(pil_image, dtype=np.float32) / 255.0
            img_array = np.expand_dims(img_array, axis=0)
            logger.info(f"Image preprocessed. Shape: {img_array.shape}")
        except Exception as e:
            logger.error(f"Image preprocessing failed: {e}")
            return jsonify({"error": "Image processing failed", "details": str(e)}), 400

        # 4. Prediction
        logger.info("Running disease prediction...")
        try:
            pred = model.predict(img_array, verbose=0)
            logger.info(f"Prediction raw output shape: {pred.shape}")
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return jsonify({"error": "Prediction failed", "details": str(e)}), 500
        
        # Handle prediction output
        if isinstance(pred, list):
            pred = np.array(pred)
        
        pred = np.array(pred).flatten()
        
        # Check if it's a multi-class model (softmax) or binary (sigmoid)
        if len(pred) > 1:
            # Multi-class model - get the class with highest probability
            predicted_class_idx = int(np.argmax(pred))
            confidence = float(pred[predicted_class_idx])
            logger.info(f"Predicted class index: {predicted_class_idx}, Confidence: {confidence}")
            
            # Map class index to disease name
            # First, try to use class names from model if available
            if _plant_disease_classes is not None and predicted_class_idx < len(_plant_disease_classes):
                disease_key = _plant_disease_classes[predicted_class_idx]
                logger.info(f"Using class name from model: {disease_key}")
            else:
                # Fallback: Common plant disease models use class indices that map to disease names
                disease_class_names = [
                    "Apple___Apple_scab", "Apple___Black_rot", "Apple___Cedar_apple_rust", "Apple___Healthy",
                    "Cherry___Powdery_mildew", "Cherry___Healthy",
                    "Corn___Common_rust", "Corn___Northern_Leaf_Blight", "Corn___Healthy",
                    "Grape___Black_rot", "Grape___Esca", "Grape___Leaf_blight", "Grape___Healthy",
                    "Peach___Bacterial_spot", "Peach___Healthy",
                    "Pepper___bell___Bacterial_spot", "Pepper___bell___Healthy",
                    "Potato___Early_blight", "Potato___Late_blight", "Potato___Healthy",
                    "Strawberry___Leaf_scorch", "Strawberry___Healthy",
                    "Tomato___Bacterial_spot", "Tomato___Early_blight", "Tomato___Late_blight",
                    "Tomato___Leaf_Mold", "Tomato___Septoria_leaf_spot", "Tomato___Spider_mites",
                    "Tomato___Target_Spot", "Tomato___Tomato_mosaic_virus",
                    "Tomato___Tomato_Yellow_Leaf_Curl_Virus", "Tomato___Healthy"
                ]
                
                # Use the class index if available
                if predicted_class_idx < len(disease_class_names):
                    disease_key = disease_class_names[predicted_class_idx]
                else:
                    # Final fallback
                    disease_key = f"Class_{predicted_class_idx}"
                    logger.warning(f"Class index {predicted_class_idx} out of range, using fallback: {disease_key}")
            
            # Get disease information from database
            if disease_key in DISEASE_DATABASE:
                disease_info = DISEASE_DATABASE[disease_key]
                disease_name = disease_info.get("name", disease_key.replace("___", " ").replace("_", " "))
            else:
                # Format the key as a readable name
                disease_name = disease_key.replace("___", " ").replace("_", " ").title()
                disease_info = {
                    "cure": "Consult with a plant pathologist for specific treatment recommendations.",
                    "prevention": "Maintain good plant hygiene, proper spacing, and monitor regularly.",
                    "description": f"Detected: {disease_name}"
                }
            
            label = "Healthy" if "Healthy" in disease_name else "Diseased"
            
            extra_data = {
                "disease": disease_name,
                "cure": disease_info.get("cure", "N/A"),
                "prevention": disease_info.get("prevention", "N/A"),
                "description": disease_info.get("description", f"Detected disease: {disease_name}")
            }
            
        else:
            # Binary model (fallback to old logic)
            raw_score = float(pred[0])
            logger.info(f"Binary prediction score: {raw_score}")
            
            healthy_threshold = 0.7
            category = 'leaf'  # Seed defect category removed
            
            if raw_score >= healthy_threshold:
                label = "Healthy"
                confidence = raw_score
                disease_info = DISEASE_DATABASE.get("Healthy", LEAF_DISEASES[2])
                extra_data = {
                    "disease": disease_info.get("name", "Healthy"),
                    "cure": disease_info.get("cure", "N/A"),
                    "prevention": disease_info.get("prevention", "Continue maintaining current care routine."),
                    "description": disease_info.get("description", f"Your {category} appears healthy.")
                }
            else:
                label = "Diseased"
                confidence = 1.0 - raw_score
                disease_info = LEAF_DISEASES[0]  # Default to Early Blight
                
                extra_data = {
                    "disease": disease_info["name"],
                    "cure": disease_info["cure"],
                    "prevention": disease_info["prevention"],
                    "description": f"Your plant shows signs of disease. Immediate action is recommended."
                }

        # 5. Return JSON Response
        response = {
            "label": label,
            "confidence": round(confidence, 2),
            **extra_data,
            "image_url": f"/static/uploads/{filename}"
        }
        
        logger.info(f"Returning response: {response}")
        return jsonify(response)

    except Exception as e:
        logger.error(f"Prediction Error: {e}")
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500


@app.route("/validate-plant", methods=["POST"])
def validate_plant():
    """Validate whether an uploaded image is a plant image using disease model."""
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No file part"}), 400

        file = request.files['image']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        if not allowed_file(file.filename):
            return jsonify({"error": "Invalid file type. Use JPG/PNG."}), 400

        # Use disease model to validate
        model = _get_plant_disease_model()
        
        # Preprocess image
        img = Image.open(file.stream)
        img = img.convert("RGB")
        img = img.resize(_plant_disease_target_size)
        img_array = np.asarray(img, dtype=np.float32) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        pred = model.predict(img_array, verbose=0)
        pred = np.asarray(pred).flatten()

        # Check if prediction indicates a plant (not "Not a Plant" class)
        # If model has multiple classes, check if highest probability is a plant disease or healthy
        if len(pred) > 1:
            predicted_class_idx = int(np.argmax(pred))
            confidence = float(pred[predicted_class_idx])
            
            # Assume if we get a valid prediction, it's a plant
            # "Not a Plant" would typically be a separate class or very low confidence
            is_plant = confidence > 0.1  # Threshold for valid plant detection
            plant_prob = confidence if is_plant else (1.0 - confidence)
        else:
            # Binary output
            plant_prob = float(pred[0])
            is_plant = plant_prob >= 0.5
            confidence = plant_prob if is_plant else (1.0 - plant_prob)

        return jsonify({
            "success": True,
            "is_plant": bool(is_plant),
            "confidence": round(float(confidence) * 100.0, 2),
            "plant_probability": round(float(plant_prob) * 100.0, 2)
        })

    except FileNotFoundError as e:
        logger.error(str(e))
        return jsonify({"error": "Model not found", "details": str(e)}), 500
    except Exception as e:
        logger.error(f"Plant validation error: {e}")
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500


@app.route("/api/chat", methods=["POST"])
def chat():
    """Chatbot API endpoint that responds to agriculture-related queries."""
    try:
        data = request.get_json()
        user_message = data.get("message", "").strip()
        
        if not user_message:
            return jsonify({"error": "Message is required"}), 400
        
        # Agriculture-related keywords to filter queries
        agriculture_keywords = [
            'crop', 'plant', 'farming', 'farmer', 'agriculture', 'agricultural', 'harvest',
            'seed', 'fertilizer', 'pesticide', 'irrigation', 'soil', 'disease', 'pest',
            'yield', 'cultivation', 'sowing', 'weather', 'rainfall', 'drought', 'flood',
            'scheme', 'subsidy', 'loan', 'credit', 'insurance', 'market', 'price',
            'vegetable', 'fruit', 'grain', 'wheat', 'rice', 'corn', 'tomato', 'potato',
            'organic', 'compost', 'manure', 'weed', 'blight', 'rust', 'mildew',
            'livestock', 'cattle', 'dairy', 'poultry', 'fishery', 'aquaculture'
        ]
        
        # Check if query is agriculture-related
        user_message_lower = user_message.lower()
        is_agriculture_related = any(keyword in user_message_lower for keyword in agriculture_keywords)
        
        if not is_agriculture_related:
            return jsonify({
                "response": "I'm an agriculture-focused assistant. Please ask me questions related to farming, crops, plant diseases, government schemes, or agricultural practices. How can I help you with agriculture today?",
                "is_agriculture": False
            })
        
        # Use Google Generative AI (Gemini)
        import google.generativeai as genai
        
        # Configure API key
        api_key = "AIzaSyA_2sGPe5wJK-v5dSFSCkuI2GGRGIc6Lfw"
        genai.configure(api_key=api_key)
        
        # Create model instance
        try:
            model = genai.GenerativeModel('gemini-pro')
        except Exception as model_error:
            logger.error(f"Failed to initialize Gemini model: {model_error}")
            # Try alternative model name
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
            except:
                model = genai.GenerativeModel('models/gemini-pro')
        
        # Create agriculture-focused system prompt
        system_prompt = """You are an expert agriculture assistant for AgroVision, a platform helping farmers with plant disease detection and agricultural guidance. 

Your role is to:
- Provide accurate information about crops, farming practices, and agricultural techniques
- Help with plant disease identification and treatment
- Guide farmers on government schemes and subsidies
- Offer advice on soil health, irrigation, and crop management
- Answer questions about organic farming, pesticides, and fertilizers
- Provide information about market prices and agricultural economics

Keep responses:
- Clear, concise, and practical
- Focused on Indian agriculture context when relevant
- Helpful and supportive
- Based on scientific agricultural knowledge

If asked about non-agriculture topics, politely redirect to agriculture-related questions."""

        # Generate response
        full_prompt = f"{system_prompt}\n\nUser Question: {user_message}\n\nAssistant Response:"
        
        try:
            response = model.generate_content(full_prompt)
            # Handle response - sometimes it's a string, sometimes it has .text attribute
            if hasattr(response, 'text'):
                bot_response = response.text.strip()
            elif isinstance(response, str):
                bot_response = response.strip()
            else:
                bot_response = str(response).strip()
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            # Fallback response
            bot_response = "I apologize, but I'm having trouble processing your request right now. Please try again or rephrase your agriculture-related question."
        
        return jsonify({
            "response": bot_response,
            "is_agriculture": True
        })
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500

# --- ERROR HANDLERS ---

@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({"error": "File too large (Max 16MB)"}), 413

@app.errorhandler(404)
def page_not_found(error):
    return render_template("index.html"), 404

if __name__ == "__main__":
    # Enable debug for development, set to False in production
    print("=" * 50)
    print("🌾 AgroVision - Starting Server")
    print("=" * 50)
    print("📍 Server running at: http://127.0.0.1:5000")
    print("🔍 Disease Detection: http://127.0.0.1:5000/detect")
    print("🏛️  Government Schemes: http://127.0.0.1:5000/schemes")
    print("🤖 Chatbot: http://127.0.0.1:5000/chatbot")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)