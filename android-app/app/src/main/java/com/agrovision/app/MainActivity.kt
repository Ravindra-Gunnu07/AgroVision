package com.agrovision.app

import java.io.FileInputStream // Keep if needed or remove if not. Wait, I should remove it.
// Checking imports: 
// import java.io.FileInputStream
// import java.nio.ByteBuffer
// import java.nio.channels.FileChannel
// These are no longer used.

import android.graphics.Bitmap
import android.net.Uri
import android.os.Bundle
import android.provider.MediaStore
import android.view.View
import android.widget.Button
import android.widget.ImageView
import android.widget.ProgressBar
import android.widget.TextView
import android.widget.Toast
import androidx.activity.result.PickVisualMediaRequest
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.tensorflow.lite.Interpreter
import org.tensorflow.lite.support.common.ops.NormalizeOp
import org.tensorflow.lite.support.image.ImageProcessor
import org.tensorflow.lite.support.image.TensorImage
import org.tensorflow.lite.support.image.ops.ResizeOp

class MainActivity : AppCompatActivity() {

    private lateinit var btnSelect: Button
    private lateinit var btnAnalyze: Button
    private lateinit var imageView: ImageView
    private lateinit var tvResult: TextView
    private lateinit var progressBar: ProgressBar

    private var selectedImageUri: Uri? = null
    private var interpreter: Interpreter? = null
    
    // Model configuration
    private val MODEL_FILE = "plant_validity_model.tflite"
    private val INPUT_SIZE = 224
    
    private var isModelLoaded = false

    // Register Photo Picker
    private val pickMedia = registerForActivityResult(ActivityResultContracts.PickVisualMedia()) { uri ->
        if (uri != null) {
            selectedImageUri = uri
            imageView.setImageURI(uri)
            
            if (isModelLoaded) {
                btnAnalyze.isEnabled = true
                tvResult.text = "Image ready for Offline Analysis."
            } else {
                Toast.makeText(this, "Image selected, but model failed to load.", Toast.LENGTH_LONG).show()
                // Do NOT overwrite the error message in tvResult
            }
        } else {
            Toast.makeText(this, "No media selected", Toast.LENGTH_SHORT).show()
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        btnSelect = findViewById(R.id.btnSelectImage)
        btnAnalyze = findViewById(R.id.btnAnalyze)
        imageView = findViewById(R.id.imageViewPreview)
        tvResult = findViewById(R.id.tvResult)
        progressBar = findViewById(R.id.progressBar)

        // Initialize TFLite Model
        initializeModel()

        btnSelect.setOnClickListener {
            pickMedia.launch(PickVisualMediaRequest(ActivityResultContracts.PickVisualMedia.ImageOnly))
        }

        btnAnalyze.setOnClickListener {
            selectedImageUri?.let { uri ->
                if (isModelLoaded) {
                    analyzeImageLocally(uri)
                } else {
                    showError("Model is not loaded. Cannot analyze.")
                }
            }
        }
    }

    private fun initializeModel() {
        try {
            // Debug: Check if file exists in assets
            val assetList = assets.list("")
            if (assetList == null || !assetList.contains(MODEL_FILE)) {
                throw Exception("File '$MODEL_FILE' not found in assets. Available: ${assetList?.joinToString()}")
            }

            // Load model using FileUtil (requires 'noCompress' in build.gradle)
            val modelBuffer = org.tensorflow.lite.support.common.FileUtil.loadMappedFile(this, MODEL_FILE)
            
            // Debug: Check size
            val size = modelBuffer.capacity()
            
            interpreter = Interpreter(modelBuffer)
            
            isModelLoaded = true
            Toast.makeText(this, "AI Model Loaded", Toast.LENGTH_SHORT).show()
            tvResult.text = "Model loaded successfully. Size: ${size / 1024} KB"
        } catch (e: Exception) {
            isModelLoaded = false
            val errorMsg = "Error loading model: ${e.message}"
            android.util.Log.e("AgroVision", errorMsg, e)
            tvResult.text = errorMsg
            tvResult.setTextColor(android.graphics.Color.RED)
            btnAnalyze.isEnabled = false
        }
    }

    private fun analyzeImageLocally(uri: Uri) {
        if (interpreter == null) {
            showError("Model not initialized.")
            return
        }

        progressBar.visibility = View.VISIBLE
        btnAnalyze.isEnabled = false
        tvResult.text = "Analyzing on device..."
        tvResult.setTextColor(android.graphics.Color.DKGRAY)

        CoroutineScope(Dispatchers.IO).launch {
            try {
                // 1. Get Bitmap
                val bitmap = MediaStore.Images.Media.getBitmap(contentResolver, uri)
                
                // 2. Preprocess (Resize -> Normalize)
                val imageProcessor = ImageProcessor.Builder()
                    .add(ResizeOp(INPUT_SIZE, INPUT_SIZE, ResizeOp.ResizeMethod.BILINEAR))
                    .add(NormalizeOp(0.0f, 255.0f)) // Output range 0.0 - 1.0 (assuming float32 input)
                    .build()

                var tensorImage = TensorImage(org.tensorflow.lite.DataType.FLOAT32)
                tensorImage.load(bitmap)
                tensorImage = imageProcessor.process(tensorImage)

                // 3. Run Inference
                // Output shape: [1, 1] for binary classification
                val outputBuffer = Array(1) { FloatArray(1) }
                interpreter?.run(tensorImage.buffer, outputBuffer)

                // 4. Interpret Results
                val rawScore = outputBuffer[0][0] // Probability
                
                withContext(Dispatchers.Main) {
                    displayResult(rawScore)
                }

            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    showError("Analysis Failed: ${e.message}")
                    android.util.Log.e("AgroVision", "Inference error", e)
                }
            } finally {
                withContext(Dispatchers.Main) {
                    progressBar.visibility = View.GONE
                    btnAnalyze.isEnabled = true
                }
            }
        }
    }

    private fun displayResult(score: Float) {
        // MATCHING PYTHON SCRIPT LOGIC:
        // prediction = model.predict(img)[0][0]
        // if prediction > 0.5: Plant
        // else: Not a Plant
        
        val threshold = 0.5f
        val isPlant = score > threshold
        
        // If it's a plant, the score IS the confidence of being a plant (Sigmoid output)
        // If not, confidence is 1 - score
        val confidence = if (isPlant) score else (1.0f - score)
        
        val label = if (isPlant) "Plant Detected" else "Not a Plant"
        val color = if (isPlant) "#2E7D32" else "#C62828"
        
        val description = if (isPlant) {
             "Valid plant detected. You can proceed with disease analysis if needed."
        } else {
             "This does not appear to be a plant. Please upload a clear photo of a plant leaf."
        }

        val resultText = """
            RESULT: $label
            Confidence: ${(confidence * 100).toInt()}%
            Raw Score: $score
            
            $description
        """.trimIndent()

        tvResult.text = resultText
        tvResult.setTextColor(android.graphics.Color.parseColor(color))
    }

    private fun showError(msg: String) {
        tvResult.text = msg
        Toast.makeText(this, msg, Toast.LENGTH_SHORT).show()
    }

    override fun onDestroy() {
        super.onDestroy()
        interpreter?.close()
    }
}
