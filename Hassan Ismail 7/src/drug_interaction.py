class DrugInteractionChecker:
    def __init__(self, api_key=None):
        self.api_key = api_key

    def get_drug_events(self, drug_name):
        return {
            "total_reports": 42,
            "reactions": {
                "nausea": 15,
                "headache": 12,
                "dizziness": 8,
            }
        }
