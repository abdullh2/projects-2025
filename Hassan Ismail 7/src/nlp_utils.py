class MedicationNER:
    def __init__(self, api_key=None):
        self.api_key = api_key

    def process_and_format(self, text):
        return f"[NER] Extracted entities from text."

    def extract_medications_from_text(self, text):
        keywords = ["paracetamol", "ibuprofen", "amoxicillin", "aspirin"]
        found = [word for word in keywords if word.lower() in text.lower()]
        return found
