# AgroVision Android App (Offline AI)

This is a native Android application written in Kotlin that uses **TensorFlow Lite** to perform offline plant disease detection directly on the device.

## 🚀 Setup Instructions

### 1. Get the TFLite Model
The app requires a `plant_validity_model.tflite` file in the assets folder.

1.  Open the root `AgroVision` folder in a terminal.
2.  Run the conversion script:
    ```bash
    python convert_to_tflite.py
    ```
    *(Ensure you have `tensorflow` installed given your requirements.txt)*
3.  This generates `plant_validity_model.tflite`.
4.  **Move** this file to:
    `AgroVision\android-app\app\src\main\assets\`

### 2. Open in Android Studio
1.  Open **Android Studio**.
2.  Select **Open** and choose `AgroVision\android-app`.
3.  Sync Gradle.
4.  Run on an Emulator or Device.

## 📱 Features
- **Offline Inference**: No internet connection required for detection.
- **Photo Picker**: Modern Android photo picker support.
- **Real-time Results**: Instant feedback using the local neural network.
