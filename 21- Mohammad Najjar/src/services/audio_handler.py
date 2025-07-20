
import speech_recognition as sr
import pyttsx3
import pygame
import tempfile
import os
import time
from gtts import gTTS
from utils.logger import logger

class AudioHandler:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.mic = sr.Microphone()

    def record_voice(self):
        try:
            with self.mic as source:
                self.recognizer.adjust_for_ambient_noise(source)
                audio = self.recognizer.listen(source, timeout=5)
                voice_query = self.recognizer.recognize_google(audio, language="ar-EG")
                return voice_query
        except sr.UnknownValueError:
            logger.error("لم يتم التعرف على الصوت.")
        except sr.RequestError as e:
            logger.error(f"خطأ في الاتصال بخدمة Google Speech: {e}")
        return None

    def speak(self, text):
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', 150)
            engine.setProperty('volume', 1.0)
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            logger.error(f"حدث خطأ أثناء تشغيل الصوت: {e}")

    def speak_naturally(self, text, lang="ar"): 
        try:
            tts = gTTS(text=text, lang=lang)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                tts.save(fp.name)
                audio_path = fp.name
            pygame.init()
            pygame.mixer.init()
            pygame.mixer.music.load(audio_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.5)
            pygame.mixer.music.stop()
            pygame.quit()
            os.remove(audio_path)
        except Exception as e:
            logger.error(f"حدث خطأ أثناء تشغيل الصوت الطبيعي باستخدام pygame: {e}")
