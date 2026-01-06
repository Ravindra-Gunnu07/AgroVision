import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' # Suppress TF Info/Warnings
import tensorflow as tf
import json
import h5py
import numpy as np

print("Starting checks...")

def _rebuild_plant_validity_model_from_weights(model_path):
    """Rebuild MobileNetV2-based binary classifier and load weights by name."""
    print("Attempting to rebuild model structure...")
    
    # Infer input shape from saved config
    input_shape = (224, 224, 3)
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
                            print(f"Inferred input shape: {input_shape}")
    except Exception as e:
        print(f"Warning: Could not infer shape from h5 attributes ({e}). Using default (224, 224, 3)")
        pass

    inputs = tf.keras.Input(shape=input_shape)
    # Re-create the MobileNetV2 structure
    base = tf.keras.applications.MobileNetV2(
        include_top=False,
        weights=None,
        input_tensor=inputs
    )
    x = base.output
    x = tf.keras.layers.GlobalAveragePooling2D()(x)
    outputs = tf.keras.layers.Dense(1, activation="sigmoid")(x)
    model = tf.keras.Model(inputs=inputs, outputs=outputs)
    
    # Load weights
    print("Loading weights...")
    model.load_weights(model_path, by_name=True, skip_mismatch=True)
    return model

def convert_h5_to_tflite(h5_path, tflite_path):
    model = None
    
    # 1. Try Loading Directly
    try:
        print(f"Loading model from: {h5_path}")
        model = tf.keras.models.load_model(h5_path, compile=False)
        print("Model loaded successfully (direct load).")
    except Exception as e:
        print(f"Direct load failed: {e}")
        
        # 2. Try Rebuilding
        try:
            model = _rebuild_plant_validity_model_from_weights(h5_path)
            print("Model rebuilt successfully.")
        except Exception as rebuild_error:
            print(f"Rebuild failed: {rebuild_error}")
            return

    if model is None:
        print("Failed to obtain model.")
        return

    # 3. Convert to TFLite
    print("Converting to TFLite (No optimizations)...")
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    
    # Disable optimizations to ensure maximum compatibility first
    # converter.optimizations = [tf.lite.Optimize.DEFAULT] 
    
    try:
        tflite_model = converter.convert()
        
        # 4. Save
        with open(tflite_path, "wb") as f:
            f.write(tflite_model)
        
        print(f"✅ Success! TFLite model saved to: {tflite_path}")
        
        # 5. Verify the model
        print("Verifying model validity...")
        interpreter = tf.lite.Interpreter(model_path=tflite_path)
        interpreter.allocate_tensors()
        print("Model verification successful (Interpreter allocated).")
        
        # Print details
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()
        print(f"Input Shape: {input_details[0]['shape']}")
        print(f"Output Shape: {output_details[0]['shape']}")
        
    except Exception as e:
        print(f"Conversion or Verification failed: {e}")

if __name__ == "__main__":
    # Adjust paths as needed based on where you run the script from
    # Assuming run from project root: python android-app/app/src/main/assets/convert_to_tflite.py
    
    # Possible locations for the H5 file
    possible_h5_paths = [
        "plant_validity_model.h5", 
        "c:/Users/ASUS/Desktop/AgroVision/plant_validity_model.h5"
    ]
    
    h5_path = None
    for p in possible_h5_paths:
        if os.path.exists(p):
            h5_path = p
            break
            
    if not h5_path:
        print("❌ Could not find 'plant_validity_model.h5'. Please run this from the project root.")
        exit(1)
        
    # Standard location for TFLite file (in this same folder)
    tflite_path = os.path.join(os.path.dirname(__file__), "plant_validity_model.tflite")
    
    convert_h5_to_tflite(h5_path, tflite_path)
