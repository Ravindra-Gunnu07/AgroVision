# Model Placeholder Directory

This directory will contain your trained AI models:
- leaf_model.h5 (for leaf disease detection)
- seed_model.h5 (for seed defect detection)

## For Demo/Hackathon Mode:
The app.py is currently configured to work WITHOUT models for demonstration purposes.

## When you have trained models:
1. Place your .h5 model files in this directory
2. Uncomment the model loading lines in app.py:
   - `leaf_model = tf.keras.models.load_model("model/leaf_model.h5")`
   - `seed_model = tf.keras.models.load_model("model/seed_model.h5")`
3. Uncomment the prediction lines in the predict() function

## Model Training Resources:
- Use TensorFlow/Keras for training
- Recommended input size: 224x224 pixels
- Dataset sources: PlantVillage, Kaggle agriculture datasets
