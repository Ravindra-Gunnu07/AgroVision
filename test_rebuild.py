import tensorflow as tf
import h5py
import json
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

model_path = "plant_validity_model.h5"

def _rebuild_plant_validity_model_from_weights(model_path):
    """Rebuild MobileNetV2-based binary classifier and load weights by name."""
    
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
        print(f"Could not infer shape: {e}")

    print(f"Using input shape: {input_shape}")
    
    inputs = tf.keras.Input(shape=input_shape)
    base = tf.keras.applications.MobileNetV2(
        include_top=False,
        weights=None,
        input_tensor=inputs
    )
    x = base.output
    x = tf.keras.layers.GlobalAveragePooling2D()(x)
    outputs = tf.keras.layers.Dense(1, activation="sigmoid")(x)
    model = tf.keras.Model(inputs=inputs, outputs=outputs)
    
    print("Attempting to load weights by name...")
    try:
        model.load_weights(model_path, by_name=True, skip_mismatch=True)
        print("✅ Weights loaded successfully!")
    except Exception as e:
        print(f"Weights loading failed: {e}")
        raise
    
    return model

print("Testing rebuild function...")
try:
    model = _rebuild_plant_validity_model_from_weights(model_path)
    print("✅ Model rebuilt successfully!")
    print(f"Model input shape: {model.input_shape}")
    print(f"Model output shape: {model.output_shape}")
except Exception as e:
    print(f"❌ Rebuild failed: {e}")
    import traceback
    traceback.print_exc()
