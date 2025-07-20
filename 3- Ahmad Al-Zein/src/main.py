# main.py
import sys
from PySide6.QtWidgets import QApplication
from dotenv import load_dotenv
import os
import logging

# تأكد من تحميل متغيرات البيئة في بداية التطبيق
load_dotenv()

# إعداد نظام التسجيل (Logging)
# تم تحديث المسار ليشير إلى app.log في الدليل الجذر للمشروع
log_file_path = os.path.join(os.path.dirname(__file__), '..', 'app.log')
logging.basicConfig(
    level=logging.INFO, # ابدأ بتسجيل رسائل INFO وما فوقها
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file_path), # تسجيل الأخطاء في ملف
        logging.StreamHandler(sys.stdout)    # تسجيل الأخطاء في الطرفية أيضاً
    ]
)
# لضمان تسجيل أخطاء Pygame وغيرها، يمكن رفع المستوى قليلاً لتشمل أخطاء المكتبات
logging.getLogger('PySide6').setLevel(logging.WARNING)
logging.getLogger('pyaudio').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('requests').setLevel(logging.WARNING)
logging.getLogger('speech_recognition').setLevel(logging.WARNING)


from gui import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())