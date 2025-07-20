
import customtkinter as ctk
from PIL import Image, ImageTk
from io import BytesIO
from services.visual_assistant import VisualAssistant
from services.audio_handler import AudioHandler
import tkinter.filedialog as filedialog

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("مساعد الذكي")
        self.geometry("800x700")
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self.assistant = VisualAssistant()
        self.audio = AudioHandler()
        self.voice_query = None

        self.upload_button = ctk.CTkButton(self, text="تحميل صورة", command=self.upload_image)
        self.upload_button.grid(row=0, column=0, padx=20, pady=20, sticky="ew")

        self.record_button = ctk.CTkButton(self, text="تسجيل صوتي", command=self.start_voice_recording)
        self.record_button.grid(row=0, column=1, padx=10, pady=20, sticky="ew")

        self.image_frame = ctk.CTkFrame(self)
        self.image_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=10, sticky="nsew")
        self.image_label = ctk.CTkLabel(self.image_frame, text="")
        self.image_label.grid(row=0, column=0, sticky="nsew")

        self.description_label = ctk.CTkLabel(self, text="الوصف:", font=ctk.CTkFont(size=16, weight="bold"))
        self.description_label.grid(row=2, column=0, columnspan=2, padx=20, pady=(10, 0), sticky="w")

        self.description_text = ctk.CTkTextbox(self, wrap="word", width=600, height=200, font=ctk.CTkFont(size=14))
        self.description_text.grid(row=3, column=0, columnspan=2, padx=20, pady=(0, 20), sticky="nsew")

        self.status_label = ctk.CTkLabel(self, text="اضغط على 'تسجيل صوتي' ثم 'تحميل صورة' لتحليل الصورة.", text_color="grey")
        self.status_label.grid(row=4, column=0, columnspan=2, padx=20, pady=10, sticky="w")

        self.replay_button = ctk.CTkButton(self, text="🔁 تشغيل الصوت مجددًا", command=self.replay_description)
        self.replay_button.grid(row=5, column=0, columnspan=2, padx=20, pady=(0, 10), sticky="ew")

    def upload_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.tiff")])
        if not file_path:
            self.status_label.configure(text="لم يتم تحديد صورة.", text_color="grey")
            return
        self.status_label.configure(text="جاري تحليل الصورة، الرجاء الانتظار...", text_color="orange")
        self.update()
        self.description_text.delete("1.0", "end")

        img = Image.open(file_path)
        img.thumbnail((400, 300))
        img_ctk = ctk.CTkImage(light_image=img, size=(400, 300))
        self.image_label.configure(image=img_ctk, text="")
        self.image_label.image = img_ctk

        img_bytes = BytesIO()
        Image.open(file_path).save(img_bytes, format='PNG')
        img_bytes.seek(0)

        result = self.assistant.analyze_image(img_bytes, voice_query=self.voice_query)
        if result:
            self.description_text.insert("1.0", result)
            self.audio.speak_naturally(result) 
            self.status_label.configure(text="تم تحليل الصورة بنجاح!", text_color="green")
        else:
            self.description_text.insert("1.0", "عذرًا، لم أتمكن من تحليل الصورة.")
            self.status_label.configure(text="فشل التحليل.", text_color="red")

    def start_voice_recording(self):
        self.status_label.configure(text="جاري تسجيل الصوت، الرجاء التحدث...", text_color="orange")
        self.update()
        query = self.audio.record_voice()
        if query:
            self.voice_query = query
            self.status_label.configure(text=f"تم التعرف على الصوت: {query}", text_color="green")
        else:
            self.status_label.configure(text="لم أفهم الصوت. حاول مرة أخرى.", text_color="red")

    def replay_description(self):
        self.audio.speak_naturally(self.description_text.get("1.0", "end").strip())

def run_app():
    app = App()
    app.mainloop()
