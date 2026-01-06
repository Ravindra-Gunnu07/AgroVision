import tensorflow as tf
import os

model_path = "plant_validity_model.h5"

print(f"Model file exists: {os.path.exists(model_path)}")
print(f"Model file size: {os.path.getsize(model_path)} bytes")

try:
    print("\nAttempting to load model directly...")
    model = tf.keras.models.load_model(model_path, compile=False)
    print("✅ Model loaded successfully!")
    print(f"Model input shape: {model.input_shape}")
    print(f"Model output shape: {model.output_shape}")
except Exception as e:
    print(f"❌ Direct load failed: {e}")
    print(f"Error type: {type(e).__name__}")
