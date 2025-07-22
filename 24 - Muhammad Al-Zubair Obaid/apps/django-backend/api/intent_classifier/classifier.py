# services/intent_classifier/classifier.py
import os
import re
import json
import logging
import unicodedata
from datetime import datetime
from os.path import exists
from typing import Dict, List, Any, Optional, Tuple

import numpy as np
import tensorflow as tf
from transformers import TFAutoModelForSequenceClassification, AutoTokenizer
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split

# --- Logging Configuration ---
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'./logs/classifier_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('IntentClassifierService')


# --- Singleton Metaclass for Model Loading ---
class SingletonMeta(type):
    """
    A metaclass to ensure that a class has only one instance, used here to
    prevent reloading the heavyweight ML model and tokenizer on every call.
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


# --- Core AI Classifier Class ---
class MultilingualIntentClassifier(metaclass=SingletonMeta):
    """
    Manages the lifecycle of the multilingual BERT intent classifier,
    including data loading, preprocessing, training, and inference.
    """

    def __init__(self, model_name: str = 'bert-base-multilingual-cased', model_dir: str = './models/intent_classifier',
                 config_dir: str = './config/ai'):
        logger.info(f"Initializing classifier with model '{model_name}'...")
        self.model_name = model_name
        self.model_dir = model_dir
        self.config_dir = config_dir
        self.tokenizer = None
        self.model = None
        self.label_encoder = LabelEncoder()
        self.max_length = 128
        self.num_labels = 0
        self.is_ready = exists('../../models/intent_classifier')
        logger.info(f"Is ready to load model: '{self.is_ready}'")

        # Lazy-loaded properties
        self._intents_config = None
        self._apps_config = None
        self._envs_config = None

        # Ensure directories exist
        os.makedirs(self.model_dir, exist_ok=True)
        os.makedirs('./logs', exist_ok=True)

        self.load_model_and_tokenizer()
        if self.is_ready:
            logger.info("Classifier initialized successfully and is ready for inference.")
        else:
            logger.warning("Classifier initialized, but model is not loaded. Training is required.")

    def _load_json_config(self, file_name: str) -> Dict:
        """Loads a JSON configuration file."""
        path = os.path.join(self.config_dir, file_name)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {path}")
            raise
        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON from file: {path}")
            raise

    @property
    def intents_config(self) -> Dict:
        if self._intents_config is None:
            self._intents_config = self._load_json_config('intents.json')
        return self._intents_config

    @property
    def apps_config(self) -> Dict:
        if self._apps_config is None:
            self._apps_config = self._load_json_config('apps.json')
        return self._apps_config

    @property
    def envs_config(self) -> Dict:
        if self._envs_config is None:
            self._envs_config = self._load_json_config('environments.json')
        return self._envs_config

    def detect_language(self, text: str) -> str:
        """Simple language detection based on Arabic character ratio."""
        if not text:
            return 'en'
        arabic_chars = len(re.findall(r'[\u0600-\u06FF]', text))
        total_chars = len(re.findall(r'\w', text))
        return 'ar' if total_chars > 0 and (arabic_chars / total_chars) > 0.3 else 'en'

    def preprocess_text(self, text: str) -> str:
        """Cleans and normalizes text for both English and Arabic."""
        text = text.lower()
        text = unicodedata.normalize('NFKC', text)

        # Arabic-specific normalization
        if self.detect_language(text) == 'ar':
            text = re.sub(r'[\u064B-\u0652\u0670\u0640]', '', text)  # Remove diacritics
            text = text.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا')
            text = text.replace('ى', 'ي').replace('ة', 'ه')

        text = re.sub(r'http[s]?://\S+', '', text)
        text = re.sub(r'\S+@\S+', '', text)
        text = re.sub(r'[^\w\s\u0600-\u06FF-]', ' ', text)  # Keep alphanumeric, space, arabic, hyphen
        text = ' '.join(text.split())
        return text.strip()

    def _extract_entities(self, text: str) -> Dict[str, Any]:
        """Extracts applications and environments from text using config files."""
        entities = {'apps': [], 'environment': None}
        text_lower = self.preprocess_text(text)

        # Extract apps
        for app_info in self.apps_config.get('applications', []):
            for alias in app_info.get('aliases', []):
                if re.search(r'\b' + re.escape(alias) + r'\b', text_lower):
                    if app_info['id'] not in entities['apps']:
                        entities['apps'].append(app_info['id'])

        # Extract environment (simple keyword matching)
        for env_info in self.envs_config.get('environments', []):
            if env_info['id'].replace('_', ' ') in text_lower:
                entities['environment'] = env_info['id']
                for app_id in env_info.get('apps', []):
                    if app_id not in entities['apps']:
                        entities['apps'].append(app_id)
                break
        return entities

    def load_training_data(self) -> Tuple[List[str], List[str]]:
        """Loads and preprocesses training data from intents.json."""
        logger.info("Loading training data...")
        texts, labels = [], []
        for intent_data in self.intents_config.get('intents', []):
            intent = intent_data['intent']
            for pattern in intent_data['patterns']:
                processed_text = self.preprocess_text(pattern)
                if processed_text:
                    texts.append(processed_text)
                    labels.append(intent)
        logger.info(f"Loaded {len(texts)} patterns for {len(set(labels))} intents.")
        return texts, labels

    def train(self, epochs: int = 10, batch_size: int = 16):
        """Trains and saves the intent classification model."""
        logger.info("--- Starting Model Training ---")
        texts, labels = self.load_training_data()

        if not texts:
            logger.error("No training data loaded. Aborting training.")
            return

        # Encode labels
        encoded_labels = self.label_encoder.fit_transform(labels)
        self.num_labels = len(self.label_encoder.classes_)

        # Build and compile model
        self.model = TFAutoModelForSequenceClassification.from_pretrained(self.model_name, num_labels=self.num_labels)
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)

        optimizer = tf.keras.optimizers.Adam(learning_rate=3e-5)
        # FIX: Use a standard Keras loss function for compilation.
        loss = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True)
        self.model.compile(optimizer=optimizer, loss=loss, metrics=['accuracy'])

        # Prepare datasets
        X_train, X_val, y_train, y_val = train_test_split(texts, encoded_labels, test_size=0.2, random_state=42,
                                                          stratify=encoded_labels)

        train_encodings = self.tokenizer(X_train, truncation=True, padding=True, max_length=self.max_length)
        val_encodings = self.tokenizer(X_val, truncation=True, padding=True, max_length=self.max_length)

        train_dataset = tf.data.Dataset.from_tensor_slices((dict(train_encodings), y_train)).shuffle(1000).batch(
            batch_size)
        val_dataset = tf.data.Dataset.from_tensor_slices((dict(val_encodings), y_val)).batch(batch_size)

        # Setup callbacks
        callbacks = [
            tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)
        ]

        # Train the model
        logger.info("Fitting the model...")
        logger.debug("Parameters: ", train_dataset, val_dataset, train_encodings, callbacks)
        self.model.fit(train_dataset, validation_data=val_dataset, epochs=epochs, callbacks=callbacks)

        # Save the fine-tuned model and set the ready flag
        self.save_model()
        self.is_ready = True
        logger.info("--- Model Training Complete ---")

    def save_model(self):
        """Saves the model, tokenizer, and label encoder."""
        logger.info(f"Saving model to {self.model_dir}...")
        self.model.save_pretrained(self.model_dir)
        self.tokenizer.save_pretrained(self.model_dir)
        with open(os.path.join(self.model_dir, 'label_encoder.json'), 'w') as f:
            json.dump({'classes': self.label_encoder.classes_.tolist()}, f)
        logger.info("Model saved successfully.")

    def load_model_and_tokenizer(self):

        config_path = os.path.join(self.model_dir, 'config.json')
        logger.info(f"Loading model from {config_path}...")
        logger.info(f"Exists: " + str(os.path.exists(config_path)))
        if not os.path.exists(config_path):
            logger.warning(f"No trained model config found in {self.model_dir}. Please train the model first.")
            self.is_ready = False
            return

        logger.info(f"Loading model from {self.model_dir}...")
        try:
            self.model = TFAutoModelForSequenceClassification.from_pretrained(self.model_dir)
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_dir)

            with open(os.path.join(self.model_dir, 'label_encoder.json'), 'r') as f:
                le_data = json.load(f)
                self.label_encoder.classes_ = np.array(le_data['classes'])
            self.num_labels = len(self.label_encoder.classes_)
            self.is_ready = True
            logger.info("Model, tokenizer, and label encoder loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load model from {self.model_dir}: {e}")
            self.is_ready = False


    async def classify(self, text: str) -> Dict[str, Any]:
        """
        Performs intent classification on the input text.
        Returns a dictionary with intent, confidence, and extracted entities.
        """
        if not self.is_ready:
            logger.error("Model is not ready. Cannot perform classification.")
            return {
                "error": "Model not loaded or ready",
                "intent": "unknown",
                "confidence": 0.0,
                "language": "en",
                "entities": {}
            }

        start_time = datetime.now()

        # 1. Preprocess and Language Detection
        processed_text = self.preprocess_text(text)
        language = self.detect_language(text)

        # 2. Tokenize
        inputs = self.tokenizer(processed_text, return_tensors="tf", truncation=True, padding=True,
                                max_length=self.max_length)

        # 3. Predict
        logits = self.model(inputs).logits
        probabilities = tf.nn.softmax(logits, axis=-1).numpy()[0]

        # 4. Get top prediction
        top_index = np.argmax(probabilities)
        confidence = float(probabilities[top_index])
        intent = self.label_encoder.inverse_transform([top_index])[0]

        # 5. Extract entities
        entities = self._extract_entities(text)

        # 6. Confidence Threshold Check
        if confidence < 0.80:
            logger.warning(f"Low confidence ({confidence:.2f}) for intent '{intent}'. Original text: '{text}'")

        inference_time = (datetime.now() - start_time).total_seconds() * 1000
        logger.info(f"Classified '{text}' as '{intent}' with confidence {confidence:.2f} in {inference_time:.2f}ms")

        return {
            "intent": intent,
            "confidence": confidence,
            "language": language,
            "entities": entities
        }


class ResponseFormatter:
    """
    Generates user-friendly chat responses based on classification results
    and predefined templates.
    """
    def __init__(self, config_path: str = './config/ai/responses.json'):
        logger.info(f"Initializing ResponseFormatter with config: {config_path}")
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.responses = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load response templates: {e}")
            self.responses = {}

    def generate_response(self, classification_result: dict) -> str:
        """
        Formats a response string using templates.
        """
        intent = classification_result.get('intent', 'unknown')
        lang = classification_result.get('language', 'en')
        entities = classification_result.get('entities', {})

        lang_responses = self.responses.get(lang, self.responses.get('en', {}))
        intent_responses = lang_responses.get(intent)

        if not intent_responses:
            return lang_responses.get('unknown', {}).get('not_found', "I'm not sure how to help with that.")

        # Correctly check if an automated solution exists for the detected intent.
        is_automated = intent in ["app_installation", "environment_setup", "hardware_info"]
        response_key = 'found' if is_automated else 'not_found'
        
        template = intent_responses.get(response_key, "Processing your request.")

        try:
            app_names = ", ".join(entities.get('apps', []))
            env_name = (entities.get('environment') or '').replace('_', ' ').title()
            return template.format(apps=app_names, environment=env_name)
        except KeyError:
            return template.replace("{apps}", "").replace("{environment}", "")