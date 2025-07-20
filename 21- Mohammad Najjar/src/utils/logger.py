class MockLogger:
    def info(self, message): print(f"[INFO] {message}")
    def debug(self, message): print(f"[DEBUG] {message}")
    def error(self, message): print(f"[ERROR] {message}")
    def success(self, message): print(f"[SUCCESS] {message}")

logger = MockLogger()
