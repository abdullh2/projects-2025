
import google.generativeai as genai
from PIL import Image
from utils.logger import logger
import os

class VisualAssistant:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            logger.error("GOOGLE_API_KEY not found in environment.")
            raise ValueError("Missing API key")

        genai.configure(api_key=self.api_key)
        logger.info("Gemini API configured.")
        self.model = genai.GenerativeModel('gemini-1.5-flash-latest')
        logger.debug("Gemini model initialized.")

        self.base_prompt = """
أنت مساعد افتراضي ذكي.

مهمتك هي: 
- تحليل الصورة فقط من أجل البحث عن كائن معين يُحدده المستخدم.
- لا تصف محتوى الصورة بشكل عام.

إذا طلب المستخدم العثور على كائن (مثل \"الهاتف\"، \"المفاتيح\"، إلخ):
- تحقق أولاً مما إذا كان الكائن موجودًا في الصورة.
- إذا وُجد، قدم إجابة مباشرة على الشكل التالي:
  - \"تم العثور على {الكائن}.\"
  - موقعه: (مثلاً: في الزاوية اليمنى العليا، أو في المنتصف، أو أسفل الصورة...).
  - بجانبه: (أي كائنات مرئية بالقرب منه).
  - شكله أو لونه إن أمكن.

إذا لم يتم العثور على الكائن، قل بوضوح: \"لم يتم العثور على {الكائن} في الصورة.\"

المستخدم يسأل عن الكائن التالي:
"""


    def analyze_image(self, image_file_object, voice_query=None):
        try:
            img = Image.open(image_file_object)
        except Exception as e:
            logger.error(f"خطأ في فتح الصورة: {e}")
            return None

        prompt = self.base_prompt
        if voice_query:
            prompt += f"\nيرجى التركيز على البحث عن: '{voice_query}' إن وُجد في الصورة."

        try:
            response = self.model.generate_content([prompt, img])
            return response.text
        except Exception as e:
            logger.error(f"فشل تحليل الصورة: {e}")
            return None
