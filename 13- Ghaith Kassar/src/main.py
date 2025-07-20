from PyQt6.QtWidgets import QApplication
from app import AutoCompleteApp  
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AutoCompleteApp()
    window.show()
    sys.exit(app.exec())

