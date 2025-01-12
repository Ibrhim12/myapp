import os
import tensorflow as tf
import numpy as np
from urllib.parse import urlparse
import joblib
from utils.helpers import preprocess_text, detect_language

# Load assets
ASSETS_PATH = os.path.join(os.getcwd(), "assets")

scaler = joblib.load(os.path.join(ASSETS_PATH, "standard_scaler.pkl"))

# Load TFLite models
url_tflite_path = os.path.join(ASSETS_PATH, "url.tflite")
url_interpreter = tf.lite.Interpreter(model_path= 'assets/url.tflite')
url_interpreter.allocate_tensors()
url_input_details = url_interpreter.get_input_details()
url_output_details = url_interpreter.get_output_details()

eng_tflite_path = os.path.join(ASSETS_PATH, "eng.tflite")
eng_interpreter = tf.lite.Interpreter(model_path='assets/eng.tflite')
eng_interpreter.allocate_tensors()
eng_input_details = eng_interpreter.get_input_details()
eng_output_details = eng_interpreter.get_output_details()

urdu_tflite_path = os.path.join(ASSETS_PATH, "urdu.tflite")
urdu_interpreter = tf.lite.Interpreter(model_path= 'assets/urdu.tflite')
urdu_interpreter.allocate_tensors()
urdu_input_details = urdu_interpreter.get_input_details()
urdu_output_details = urdu_interpreter.get_output_details()

eng_vectorizer = joblib.load(os.path.join(ASSETS_PATH, "tfidf_vectorizer.pkl"))
urdu_vectorizer = joblib.load(os.path.join(ASSETS_PATH, "tfidf_vectorizer_urdu.pkl"))

# Extract features from URL
def extract_features(url):
    parsed_url = urlparse(url)
    url_length = len(url)
    domain_length = len(parsed_url.netloc)
    uses_https = 1 if parsed_url.scheme == "https" else 0
    suspicious_keywords = 0  # Placeholder for suspicious keywords logic
    return [url_length, domain_length, uses_https, suspicious_keywords]

# Predict phishing URL
def predict_phishing_url(url):
    features = np.array([extract_features(url)])
    features_scaled = scaler.transform(features)

    # Set input tensor
    url_interpreter.set_tensor(url_input_details[0]['index'], features_scaled.astype(np.float32))
    
    # Run inference
    url_interpreter.invoke()
    
    # Get prediction
    prediction = url_interpreter.get_tensor(url_output_details[0]['index'])
    return "Phishing URL" if prediction[0][0] > 0.5 else "Safe URL"

# Predict phishing for English text
def predict_phishing_text_eng(text):
    preprocessed = preprocess_text(text)
    vector = eng_vectorizer.transform([preprocessed]).toarray()

    # Set input tensor
    eng_interpreter.set_tensor(eng_input_details[0]['index'], vector.astype(np.float32))
    
    # Run inference
    eng_interpreter.invoke()
    
    # Get prediction
    prediction = eng_interpreter.get_tensor(eng_output_details[0]['index'])
    return "Phishing Text" if prediction[0][0] > 0.5 else "Safe Text"

# Predict phishing for Urdu text
def predict_phishing_text_urdu(text):
    preprocessed = preprocess_text(text)
    vector = urdu_vectorizer.transform([preprocessed]).toarray()

    # Set input tensor
    urdu_interpreter.set_tensor(urdu_input_details[0]['index'], vector.astype(np.float32))
    
    # Run inference
    urdu_interpreter.invoke()
    
    # Get prediction
    prediction = urdu_interpreter.get_tensor(urdu_output_details[0]['index'])
    return "Phishing Text" if prediction[0][0] > 0.5 else "Safe Text"

# Detect phishing text based on language
def predict_phishing_text(text):
    language = detect_language(text)
    if language == "english":
        return predict_phishing_text_eng(text)
    elif language == "urdu":
        return predict_phishing_text_urdu(text)
    return "Unsupported language"
