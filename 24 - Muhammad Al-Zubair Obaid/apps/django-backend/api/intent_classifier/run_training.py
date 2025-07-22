# services/intent_classifier/run_training.py
import argparse
from classifier import MultilingualIntentClassifier

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train the intent classification model.")
    parser.add_argument("--epochs", type=int, default=50, help="Number of training epochs.")
    parser.add_argument("--batch-size", type=int, default=32, help="Training batch size.")
    args = parser.parse_args()

    # Initialize the classifier
    # This will download the base BERT model on the first run
    intent_classifier = MultilingualIntentClassifier()

    # Start training
    intent_classifier.train(epochs=args.epochs, batch_size=args.batch_size)
