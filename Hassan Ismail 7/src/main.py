import os
import logging
from datetime import datetime
from dotenv import load_dotenv
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from PIL import Image, ImageTk
from ocr_utils import GPUAcceleratedOCR
from nlp_utils import MedicationNER
from drug_interaction import DrugInteractionChecker

load_dotenv()


if not os.path.exists('logs'):
    os.makedirs('logs')


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class PrescriptionAnalysisSystem:
    def __init__(self):
        self.api_key = os.getenv('OPENFDA_API_KEY') or "demo-key"
        self.ocr = GPUAcceleratedOCR(lang='en') 
        self.ner = MedicationNER(self.api_key)
        self.interaction_checker = DrugInteractionChecker(self.api_key)

    def process_prescription(self, image_path):
        try:
            logger.info(f"Processing prescription image: {image_path}")

            ocr_text, confidence = self.ocr.image_to_text(image_path)
            if not ocr_text:
                raise ValueError("No text extracted from image")

            meds = self.ner.extract_medications_from_text(ocr_text)
            interactions = {
                med: self.interaction_checker.get_drug_events(med)
                for med in meds
            }

            self._save_results(image_path, ocr_text, confidence, meds, interactions)

            return {
                'ocr': {'text': ocr_text, 'confidence': confidence},
                'ner': meds,
                'interactions': interactions
            }
        except Exception as e:
            logger.error(f"Error processing prescription: {str(e)}")
            raise

    def _save_results(self, image_path, ocr_text, confidence, meds, interactions):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs("prescriptions_output", exist_ok=True)
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        output_path = os.path.join("prescriptions_output", f"{base_name}_{timestamp}_analysis.txt")

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\nPRESCRIPTION ANALYSIS REPORT\n" + "="*80 + "\n\n")
            f.write("OCR RESULTS:\n" + "-"*50 + "\n")
            f.write(f"Extracted Text:\n{ocr_text}\n")
            f.write(f"Confidence: {confidence}%\n\n")
            f.write("RECOGNIZED MEDICATIONS:\n" + "-"*50 + "\n")
            f.write(f"{', '.join(meds)}\n")
            f.write("DRUG INTERACTIONS:\n" + "-"*50 + "\n")
            for med, data in interactions.items():
                f.write(f"\nMedication: {med}\n")
                if 'error' in data:
                    f.write(f"Error: {data['error']}\n")
                else:
                    f.write(f"Total Reports: {data.get('total_reports', 0)}\n")
                    if 'reactions' in data:
                        f.write("Top Reactions:\n")
                        for reaction, count in list(data['reactions'].items())[:5]:
                            f.write(f"- {reaction}: {count} reports\n")

        logger.info(f"Analysis results saved to: {output_path}")

class PrescriptionApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Prescription OCR Analysis")
        self.geometry("800x800")

        self.system = PrescriptionAnalysisSystem()
        self.image_path = None
        self.img_display = None  # للاحتفاظ بصورة Tkinter

        self.create_widgets()

    def create_widgets(self):
        self.btn_select = tk.Button(self, text="اختر صورة الوصفة", command=self.select_image)
        self.btn_select.pack(pady=10)

        self.lbl_path = tk.Label(self, text="لم يتم اختيار صورة بعد")
        self.lbl_path.pack(pady=5)

        self.lbl_image = tk.Label(self)
        self.lbl_image.pack(pady=10)

        self.btn_process = tk.Button(self, text="حلل الوصفة", command=self.process_image, state=tk.DISABLED)
        self.btn_process.pack(pady=10)

        self.txt_result = scrolledtext.ScrolledText(self, wrap=tk.WORD, width=90, height=20)
        self.txt_result.pack(padx=10, pady=10)

    def select_image(self):
        path = filedialog.askopenfilename(
            title="اختر صورة الوصفة الطبية",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp")]
        )
        if path:
            self.image_path = path
            self.lbl_path.config(text=f"الصورة المختارة: {path}")
            self.btn_process.config(state=tk.NORMAL)
            self.txt_result.delete(1.0, tk.END)

            img = Image.open(path)
            img.thumbnail((400, 400))
            self.img_display = ImageTk.PhotoImage(img)
            self.lbl_image.config(image=self.img_display)
        else:
            self.image_path = None
            self.lbl_path.config(text="لم يتم اختيار صورة بعد")
            self.btn_process.config(state=tk.DISABLED)
            self.txt_result.delete(1.0, tk.END)
            self.lbl_image.config(image='')

    def process_image(self):
        if not self.image_path:
            messagebox.showwarning("تحذير", "يرجى اختيار صورة أولاً!")
            return
        try:
            self.txt_result.delete(1.0, tk.END)
            self.txt_result.insert(tk.END, "جارٍ تحليل الوصفة، يرجى الانتظار...\n")
            self.update()

            result = self.system.process_prescription(self.image_path)


            ocr = result['ocr']
            ner = result['ner']
            interactions = result['interactions']

            output_text = f"--- نتائج التعرف الضوئي على النص (OCR) ---\n\n"
            output_text += f"النص المستخرج:\n{ocr['text']}\n\n"
            output_text += f"الثقة: {ocr['confidence']}%\n\n"

            output_text += "--- الأدوية المعترف بها (NER) ---\n\n"
            if ner:
                output_text += ", ".join(ner) + "\n\n"
            else:
                output_text += "لم يتم التعرف على أدوية.\n\n"

            output_text += "--- التفاعلات الدوائية ---\n\n"
            for med, data in interactions.items():
                output_text += f"دواء: {med}\n"
                if 'error' in data:
                    output_text += f"خطأ: {data['error']}\n"
                else:
                    output_text += f"عدد التقارير: {data.get('total_reports', 0)}\n"
                    if 'reactions' in data:
                        output_text += "أهم التفاعلات:\n"
                        for reaction, count in list(data['reactions'].items())[:5]:
                            output_text += f"- {reaction}: {count} تقرير\n"
                output_text += "\n"

            self.txt_result.delete(1.0, tk.END)
            self.txt_result.insert(tk.END, output_text)

        except Exception as e:
            logger.error(f"Error processing image: {e}")
            messagebox.showerror("خطأ", f"حدث خطأ أثناء تحليل الوصفة:\n{e}")

if __name__ == "__main__":
    app = PrescriptionApp()
    app.mainloop()
