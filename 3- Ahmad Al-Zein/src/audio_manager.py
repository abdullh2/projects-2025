# audio_manager.py
import os
import struct
import pyaudio
import pvporcupine
import speech_recognition as sr
import pygame
import google.generativeai as genai
import logging

from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import QApplication

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
gemini_model = genai.GenerativeModel('gemini-1.5-flash')


class AudioPlaybackThread(QThread):
    finished = Signal()
    def __init__(self):
        super().__init__()
        self._is_playing = False
        self._stop_requested = False
        self.current_audio_file = None

    def run(self):
        self._is_playing = True
        self._stop_requested = False
        
        try: # <--- إضافة هنا
            while pygame.mixer.music.get_busy() and not self._stop_requested:
                QApplication.processEvents()
                self.msleep(50)
            
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
            
            pygame.mixer.music.unload()
            
        finally: # <--- إضافة هنا
            # نضمن أن يتم حذف الملف المؤقت دائمًا، حتى لو حدث خطأ أثناء التشغيل
            if self.current_audio_file and os.path.exists(self.current_audio_file):
                try:
                    os.remove(self.current_audio_file)
                    logging.info(f"Successfully removed temporary audio file: {self.current_audio_file}") # <--- تم الإضافة
                except Exception as e:
                    logging.error("Error removing temporary audio file in AudioPlaybackThread finally block: %s", e) # <--- تم التعديل
                finally: # <--- إضافة هنا
                    self.current_audio_file = None # <--- تم الإضافة
            self._is_playing = False
            self.finished.emit()

    def play_audio(self, file_path):
        # قبل تشغيل ملف جديد، تأكد من إزالة أي ملف قديم متبقي
        if self.current_audio_file and os.path.exists(self.current_audio_file): # <--- تم الإضافة
            try: # <--- تم الإضافة
                os.remove(self.current_audio_file) # <--- تم الإضافة
                logging.info(f"Cleaned up previous temporary audio file before playing new one: {self.current_audio_file}") # <--- تم الإضافة
            except Exception as e: # <--- تم الإضافة
                logging.warning(f"Could not remove old temporary audio file: {e}") # <--- تم الإضافة

        self.stop_playback()
        self.current_audio_file = file_path
        try:
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            if not self.isRunning():
                self.start()
        except pygame.error as e:
            logging.error("Error playing audio: %s", e)
            self.current_audio_file = None

    def stop_playback(self):
        if self._is_playing:
            self._stop_requested = True
            self.wait(100)
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()


class WakeWordThread(QThread):
    wake_word_detected = Signal()
    stop_speaking_signal = Signal()
    wake_word_error_signal = Signal(str)

    def __init__(self, access_key):
        super().__init__()
        self.access_key = access_key
        self._is_running = True
        self.porcupine = None # <--- تم الإضافة
        self.pa = None # <--- تم الإضافة
        self.audio_stream = None # <--- تم الإضافة

    def run(self):
        try:
            self.porcupine = pvporcupine.create(access_key=self.access_key, keyword_paths=[pvporcupine.KEYWORD_PATHS['alexa']])
            self.pa = pyaudio.PyAudio()
            self.audio_stream = self.pa.open(rate=self.porcupine.sample_rate, channels=1, format=pyaudio.paInt16, input=True, frames_per_buffer=self.porcupine.frame_length)
            logging.info("Wake word engine started successfully.")
            while self._is_running:
                pcm = self.audio_stream.read(self.porcupine.frame_length, exception_on_overflow=False)
                pcm = struct.unpack_from("h" * self.porcupine.frame_length, pcm)
                if self.porcupine.process(pcm) >= 0:
                    if self._is_running: 
                        self.stop_speaking_signal.emit()
                        self.wake_word_detected.emit()
        except Exception as e:
            logging.error("Wake word engine error: %s", e)
            self.stop_speaking_signal.emit()
            self.wake_word_error_signal.emit(str(e))

    def stop(self):
        self._is_running = False
        if self.porcupine:
            self.porcupine.delete()
            self.porcupine = None
        if self.audio_stream:
            self.audio_stream.close()
            self.audio_stream = None
        if self.pa:
            self.pa.terminate()
            self.pa = None


class ConversationThread(QThread):
    conversation_signal = Signal(str, str, str)
    status_signal = Signal(str)
    conversation_finished_signal = Signal()
    command_to_execute_signal = Signal(str)
    stop_speaking_signal = Signal() 

    def __init__(self):
        super().__init__()
        self._is_in_conversation = True
        self.microphone_index = None

    def run(self):
        self.status_signal.emit("تفضل بأمرك...")
        try:
            pygame.mixer.music.load("start.mp3")
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                QApplication.processEvents()
                self.msleep(50)
        except pygame.error:
            logging.warning("Could not find 'start.mp3' file.")
            self.conversation_signal.emit("المساعد", "تفضل بأمرك...", "صوت")
            
        recognizer = sr.Recognizer()
        
        while self._is_in_conversation:
            try:
                with sr.Microphone(device_index=self.microphone_index) as source:
                    recognizer.energy_threshold = 500
                    recognizer.dynamic_energy_threshold = False
                    recognizer.pause_threshold = 1.0
                    audio = recognizer.listen(source, timeout=10, phrase_time_limit=25)

                self.status_signal.emit("جاري التحليل...")
                command = recognizer.recognize_google(audio, language="ar-AR").lower()
                self.conversation_signal.emit("أنت", command, "user")
                if any(word in command for word in ["توقف", "شكرا لك", "إيقاف"]):
                    self.command_to_execute_signal.emit("stop_conversation")
                    self._is_in_conversation = False
                else:
                    self.stop_speaking_signal.emit() 
                    self.command_to_execute_signal.emit(command)
                if self._is_in_conversation: self.status_signal.emit("في انتظار أمرك التالي...")
            except sr.WaitTimeoutError:
                self.status_signal.emit("لم أسمع شيئًا. في انتظار أمرك التالي...")
                continue
            except sr.UnknownValueError:
                self.status_signal.emit("لم أفهم الأمر. هل يمكنك المحاولة مرة أخرى؟")
                continue
            except sr.RequestError as e:
                logging.error("Speech Recognition Request Error: %s", e)
                self.status_signal.emit("عذراً، حدث خطأ في خدمة التعرف على الكلام. يرجى التحقق من اتصالك بالإنترنت.")
                self._is_in_conversation = False
                continue
            except Exception as e:
                logging.error("Conversation Thread General Error: %s", e)
                self.status_signal.emit("حدث خطأ غير متوقع في وضع المحادثة.")
                self._is_in_conversation = False
                continue

    def stop(self):
        self._is_in_conversation = False