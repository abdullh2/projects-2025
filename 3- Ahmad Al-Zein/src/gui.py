# gui.py
import sys
import os
import subprocess
import difflib
import json
import spacy
import importlib.util
import webbrowser
from gtts import gTTS
import uuid
import datetime
import requests
import io
import urllib.parse
import google.generativeai as genai
import threading
import logging
import google.api_core.exceptions
import tempfile

# استيراد PySide6
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, QTextEdit,
                               QVBoxLayout, QWidget, QLabel, QListWidget,
                               QListWidgetItem, QHBoxLayout, QGraphicsOpacityEffect,
                               QDialog, QLineEdit, QDialogButtonBox, QComboBox)
from PySide6.QtCore import Qt, QThread, Signal, QPropertyAnimation, QEasingCurve, QTimer, QSize, QPoint, QSequentialAnimationGroup, QParallelAnimationGroup, QPauseAnimation
from PySide6.QtGui import QPixmap, QMovie

# استيراد مكونات إدارة الصوت من الملف الجديد
from audio_manager import AudioPlaybackThread, WakeWordThread, ConversationThread


import pygame
import speech_recognition as sr


class ChatMessageWidget(QWidget):
    def __init__(self, text, is_user, source=None):
        super().__init__()

        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(10)

        avatar_label = QLabel()
        # تم تحديث المسار ليشير إلى صور الأفاتار في الدليل الجذر للمشروع
        avatar_pixmap = QPixmap(os.path.join(os.path.dirname(__file__), '..', 'user.png') if is_user else os.path.join(os.path.dirname(__file__), '..', 'assistant.png'))
        avatar_label.setPixmap(avatar_pixmap.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        bubble_widget = QWidget()
        bubble_layout = QVBoxLayout(bubble_widget)
        bubble_layout.setContentsMargins(10, 10, 10, 10)
        is_code = text.strip().startswith("```") and text.strip().endswith("```")

        if is_code:
            self.setup_code_view(bubble_layout, text)
        else:
            self.setup_normal_message(bubble_layout, text)
        
        if source and source != "user":
            source_label = QLabel(f"<p style='font-size: 10px; color: #b2bec3; margin-top: 5px;'>المصدر: {source}</p>")
            source_label.setAlignment(Qt.AlignRight)
            bubble_layout.addWidget(source_label)


        bubble_widget.setObjectName("assistant_message" if not is_user else "user_message")
        bubble_widget.setMaximumWidth(450)

        if is_user:
            self.main_layout.addStretch()
            self.main_layout.addWidget(bubble_widget)
            self.main_layout.addWidget(avatar_label)
        else:
            self.main_layout.addWidget(avatar_label)
            self.main_layout.addWidget(bubble_widget)
            self.main_layout.addStretch()

    def setup_normal_message(self, layout, text):
        display_widget = QLabel(text)
        display_widget.setWordWrap(True)
        display_widget.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(display_widget)

    def setup_code_view(self, layout, text):
        self.code_text = text.strip().strip("```").strip()

        copy_button = QPushButton("نسخ")
        copy_button.setFixedSize(60, 25)
        copy_button.setStyleSheet("background-color: #528bff; color: white; border-radius: 5px;")
        copy_button.clicked.connect(self._copy_code_to_clipboard)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(copy_button)

        code_view = QTextEdit(self.code_text)
        code_view.setReadOnly(True)
        code_view.setFixedHeight(150)
        code_view.setStyleSheet("background-color: #1e1e1e; color: #d4d4d4; font-family: 'Consolas', 'Courier New', monospace;')")

        layout.addLayout(button_layout)
        layout.addWidget(code_view)

    def _copy_code_to_clipboard(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.code_text)
        sender_button = self.sender()
        if sender_button:
            original_text = sender_button.text()
            sender_button.setText("تم النسخ!")
            QTimer.singleShot(1500, lambda: sender_button.setText(original_text))

class TypingIndicatorWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(10, 5, 10, 5)
        self.dots = []
        self.animations = []
        for i in range(3):
            dot = QLabel("●")
            dot.setStyleSheet("color: #dcdde1; font-size: 20px;")
            self.main_layout.addWidget(dot)
            self.dots.append(dot)
            anim = QPropertyAnimation(dot, b"pos")
            anim.setStartValue(dot.pos())
            anim.setEndValue(dot.pos() - QPoint(0, 10))
            anim.setDuration(300)
            anim.setEasingCurve(QEasingCurve.OutCubic)
            anim_return = QPropertyAnimation(dot, b"pos")
            anim_return.setStartValue(dot.pos() - QPoint(0, 10))
            anim_return.setEndValue(dot.pos())
            anim_return.setDuration(300)
            anim_return.setEasingCurve(QEasingCurve.InCubic)
            seq_group = QSequentialAnimationGroup()
            seq_group.addAnimation(anim)
            seq_group.addAnimation(anim_return)
            self.animations.append(seq_group)
        self.main_animation_group = QParallelAnimationGroup()
        for i, anim_seq in enumerate(self.animations):
            pause = QPauseAnimation(i * 150)
            staggered_anim = QSequentialAnimationGroup()
            staggered_anim.addAnimation(pause)
            staggered_anim.addAnimation(anim_seq)
            self.main_animation_group.addAnimation(staggered_anim)
        self.main_animation_group.setLoopCount(-1)
    def start_animation(self): self.show(); self.main_animation_group.start()
    def stop_animation(self): self.main_animation_group.stop(); self.hide()

class SettingsDialog(QDialog):
    def __init__(self, current_name, current_city, current_mic_index, parent=None):
        super().__init__(parent)
        self.setWindowTitle("الإعدادات")
        layout = QVBoxLayout(self)

        name_label = QLabel("الاسم:")
        self.name_input = QLineEdit(current_name if current_name else "")
        layout.addWidget(name_label)
        layout.addWidget(self.name_input)

        city_label = QLabel("المدينة الافتراضية للطقس:")
        self.city_input = QLineEdit(current_city if current_city else "")
        layout.addWidget(city_label)
        layout.addWidget(self.city_input)

        mic_label = QLabel("اختيار الميكروفون:")
        self.mic_combo = QComboBox()
        self.populate_microphones()
        if current_mic_index is not None:
            idx = self.mic_combo.findData(current_mic_index)
            if idx != -1:
                self.mic_combo.setCurrentIndex(idx)
        layout.addWidget(mic_label)
        layout.addWidget(self.mic_combo)


        layout.addStretch()
        button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def populate_microphones(self):
        import pyaudio
        p = pyaudio.PyAudio()
        info = p.get_host_api_info_by_index(0)
        num_devices = info.get('deviceCount')
        for i in range(0, num_devices):
            if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                name = p.get_device_info_by_host_api_device_index(0, i).get('name')
                self.mic_combo.addItem(name, i)
        p.terminate()

    def get_data(self):
        return {
            "name": self.name_input.text(),
            "city": self.city_input.text(),
            "microphone_index": self.mic_combo.currentData()
        }


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # تم تحديث المسار ليشير إلى user_data.json في مجلد data
        self.user_data_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'user_data.json')
        self.user_name = None
        self.user_city = None
        self.microphone_index = None
        self.last_known_subject = None

        self.commands = {}
        self.conversation_thread = None 
        self.audio_playback_thread = AudioPlaybackThread()

        self.load_plugins()

        self.setWindowTitle("المساعد الصوتي | Hands-Free"); self.setGeometry(100, 100, 600, 800)
        self.setStyleSheet("""
            #main_widget { background-color: #282c34; }
            QListWidget { background-color: #282c34; border: none; }
            #user_message {
                background-color: #528bff;
                color: white;
                padding: 12px;
                border-radius: 18px;
                font: 14px 'Segoe UI';
            }
            #assistant_message {
                background-color: #353b48;
                color: #dcdde1;
                padding: 12px;
                border-radius: 18px;
                font: 14px 'Segoe UI';
            }
            #bottom_bar { background-color: #21252b; border-top: 1px solid #353b48; }
            #status_label { font-size: 13px; color: #dcdde1; padding-left: 10px; }
            #status_icon { font-size: 20px; padding-left: 10px;}
        """)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.setSpacing(0)

        self.conversation_list = QListWidget()
        self.conversation_list.setSpacing(10)

        bottom_widget = QWidget()
        bottom_widget.setObjectName("bottom_bar")
        bottom_layout = QHBoxLayout(bottom_widget)

        self.settings_button = QPushButton("⚙️")
        self.settings_button.setFixedSize(30, 30)
        self.settings_button.setStyleSheet("font-size: 18px; border: none;")

        self.status_icon = QLabel("⚫")
        self.status_label = QLabel("جاري بدء المحرك...")
        self.typing_indicator = TypingIndicatorWidget()
        self.typing_indicator.hide()


        bottom_layout.addWidget(self.settings_button)
        bottom_layout.addWidget(self.status_icon)
        bottom_layout.addWidget(self.status_label)
        bottom_layout.addWidget(self.typing_indicator)
        bottom_layout.addStretch()

        main_layout.addWidget(self.conversation_list)
        main_layout.addWidget(bottom_widget)

        central_widget = QWidget()
        central_widget.setObjectName("main_widget")
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.settings_button.clicked.connect(self.open_settings_dialog)

        pygame.mixer.init()

        self.gemini_chat_session = None

        self.nlu_model = None
        self.preferred_browser_path = None
        self._set_preferred_browser()
        try:
            # تم تحديث المسار ليشير إلى nlu_model_ar في مجلد data
            self.nlu_model = spacy.load(os.path.join(os.path.dirname(__file__), '..', 'data', 'nlu_model_ar'))
            logging.info("NLU model loaded successfully.")
        except IOError:
            logging.warning("NLU model not found. Assistant will run in normal mode.")

        self.follow_up_plugin = None

        QTimer.singleShot(500, self.check_for_first_run)


    def _set_preferred_browser(self):
        chrome_paths_win = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
        ]
        chrome_paths_mac_linux = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable"
        ]

        if sys.platform.startswith('win'):
            for path in chrome_paths_win:
                if os.path.exists(path):
                    self.preferred_browser_path = path
                    logging.info(f"Preferred browser (Chrome) found at: {path}")
                    break
        elif sys.platform.startswith('darwin') or sys.platform.startswith('linux'):
            for path in chrome_paths_mac_linux:
                if os.path.exists(path):
                    self.preferred_browser_path = path
                    logging.info(f"Preferred browser (Chrome) found at: {path}")
                    break

        if self.preferred_browser_path:
            try:
                webbrowser.register('chrome', None, webbrowser.BackgroundBrowser(self.preferred_browser_path))
                logging.info("Google Chrome registered as preferred browser.")
            except webbrowser.Error as e:
                logging.warning(f"Could not register Google Chrome with webbrowser: {e}")
                self.preferred_browser_path = None

        if not self.preferred_browser_path:
            logging.warning("Google Chrome executable not found at common paths. Will use system default browser.")
    
    def open_url_in_thread(self, url):
        def _open():
            try:
                if self.preferred_browser_path:
                    controller = webbrowser.get('chrome')
                    controller.open_new_tab(url)
                    logging.info(f"Opened URL with preferred browser (Chrome): {url}")
                else:
                    webbrowser.open(url)
                    logging.info(f"Opened URL with system default browser: {url}")
            except Exception as e:
                logging.error("Error opening URL: %s", e)
                self.speak(f"عذراً، واجهت مشكلة في فتح الرابط.", "خطأ محلي")

        thread = threading.Thread(target=_open)
        thread.daemon = True
        thread.start()

    def _open_application(self, app_name):
        app_commands = {
            "الرسام": {
                "win": "mspaint",
                "mac": "open -a 'Microsoft Paint'"
            },
            "الآلة الحاسبة": {
                "win": "calc",
                "mac": "open -a Calculator"
            },
            "المفكرة": {
                "win": "notepad",
                "mac": "open -a TextEdit"
            },
            "جوجل كروم": {
                "win": "start chrome.exe",
                "mac": "open -a 'Google Chrome'"
            },
            "يوتيوب": {
                "win": "start https://www.youtube.com/",
                "mac": "open https://www.youtube.com/"
            },
            "الإعدادات": {
                "win": "start ms-settings:",
                "mac": "open -a 'System Settings'"
            },
            "فيجوال ستوديو كود": {
                "win": "code",
                "mac": "code"
            },
            "المنبه": {
                "win": "start ms-clock:",
                "mac": "open -a Clock"
            },
            "المتصفح": {
                "win": "start https://www.google.com/",
                "mac": "open https://www.google.com/"
            }
        }

        known_apps = list(app_commands.keys())
        matches = difflib.get_close_matches(app_name, known_apps, n=1, cutoff=0.7)

        if matches:
            matched_app_name = matches[0]
            current_os = 'win' if sys.platform.startswith('win') else 'mac'
            command_info = app_commands[matched_app_name][current_os]

            self.speak(f"حاضر، جاري فتح {matched_app_name}.", "تطبيق محلي")
            
            if matched_app_name in ["يوتيوب", "المتصفح"]:
                self.open_url_in_thread(command_info.replace("start ", "").replace("open ", "")) 
            elif matched_app_name == "جوجل كروم" and current_os == 'win':
                try:
                    subprocess.Popen(command_info, shell=True)
                except Exception as e:
                    logging.error("Error opening application %s: %s", matched_app_name, e)
                    self.speak(f"عذراً، واجهت مشكلة في فتح {matched_app_name}.", "خطأ محلي")
            else:
                try:
                    subprocess.Popen(command_info, shell=True)
                except Exception as e:
                    logging.error("Error opening application %s: %s", matched_app_name, e)
                    self.speak(f"عذراً، واجهت مشكلة في فتح {matched_app_name}.", "خطأ محلي")
        else:
            self.speak(f"عذراً، لا أعرف كيف أفتح برنامجاً اسمه '{app_name}'.", "تطبيق محلي")

    def open_settings_dialog(self):
        dialog = SettingsDialog(self.user_name, self.user_city, self.microphone_index, self)
        if dialog.exec():
            new_data = dialog.get_data()
            self.user_name = new_data["name"]
            self.user_city = new_data["city"]
            self.microphone_index = new_data["microphone_index"]
            
            with open(self.user_data_file, 'w', encoding='utf-8') as f:
                json.dump(new_data, f, ensure_ascii=False, indent=4)
            self.speak("تم تحديث الإعدادات بنجاح.", "إعدادات")
            
            self.restart_audio_engines()
    
    def restart_audio_engines(self):
        logging.info("Restarting audio engines to apply new settings...")
        if hasattr(self, 'wake_word_thread') and self.wake_word_thread and self.wake_word_thread.isRunning():
            self.wake_word_thread.stop()
            self.wake_word_thread.wait()

        if hasattr(self, 'conversation_thread') and self.conversation_thread and self.conversation_thread.isRunning():
            self.conversation_thread.stop()
            self.conversation_thread.wait()
        
        if self.microphone_index is None:
            try:
                import pyaudio
                p = pyaudio.PyAudio()
                info = p.get_default_input_device_info()
                self.microphone_index = info['index']
                logging.info(f"Using default microphone from check_for_first_run: {info['name']} (Index: {self.microphone_index})")
                p.terminate()
            except Exception as e:
                logging.warning(f"Could not find default microphone, continuing without specific index. Error: {e}")
                self.microphone_index = -1

        self.start_wake_word_engine()
        self.speak("تم تطبيق إعدادات الميكروفون الجديدة.", "إعدادات")


    def listen_for_single_response(self, timeout=10):
        recognizer = sr.Recognizer()
        with sr.Microphone(device_index=self.microphone_index) as source:
            self.update_status("أستمع...")
            QApplication.processEvents()
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            try:
                audio = recognizer.listen(source, timeout=timeout)
                self.update_status("جاري التحليل...")
                QApplication.processEvents()
                command = recognizer.recognize_google(audio, language="ar-AR")
                self.add_message_to_conversation("أنت", command, "user")
                return command
            except sr.WaitTimeoutError:
                self.speak("لم أستطع سماع أي شيء. يرجى المحاولة مرة أخرى.", "إعدادات")
                logging.warning("Timeout while listening for single response.")
                return None
            except sr.UnknownValueError:
                self.speak("لم أفهم ما قلته. يرجى المحاولة مرة أخرى.", "إعدادات")
                logging.warning("UnknownValueError while listening for single response.")
                return None
            except sr.RequestError as e:
                self.speak(f"عذراً، حدث خطأ في خدمة التعرف على الكلام: {e}", "إعدادات")
                logging.error("RequestError during single response listen: %s", e)
                return None
            except Exception as e:
                self.speak(f"حدث خطأ غير متوقع أثناء الاستماع: {e}", "إعدادات")
                logging.error("General error during single response listen: %s", e)
                return None

    def run_first_time_setup(self):
        self.speak("مرحبًا بك في مساعدك الشخصي. لإعداد التجربة، أحتاج لبعض المعلومات.", "إعدادات")
        self.speak("ما هو اسمك؟", "إعدادات")
        name = self.listen_for_single_response()
        if name:
            self.user_name = name
            self.speak(f"أهلاً بك يا {name}. الآن، في أي مدينة تقيم؟", "إعدادات")
            city = self.listen_for_single_response()
            if city:
                self.user_city = city
                
                self.speak("وأخيراً، يرجى اختيار الميكروفون الذي تود استخدامه من القائمة الظاهرة.", "إعدادات")

                dialog = SettingsDialog(self.user_name, self.user_city, self.microphone_index, self)
                if dialog.exec():
                    new_data = dialog.get_data()
                    self.user_name = new_data["name"]
                    self.user_city = new_data["city"]
                    self.microphone_index = new_data["microphone_index"]

                    user_data = {"name": self.user_name,
                                 "city": self.user_city,
                                 "microphone_index": self.microphone_index}
                    with open(self.user_data_file, 'w', encoding='utf-8') as f:
                        json.dump(user_data, f, ensure_ascii=False, indent=4)
                    self.speak("رائع. تم حفظ إعداداتك. أصبح المساعد جاهزًا الآن.", "إعدادات")
                    self.start_wake_word_engine()
                else:
                    self.speak("تم إلغاء الإعدادات الأولية. قد لا يعمل المساعد بشكل كامل.", "إعدادات")
                    self.start_wake_word_engine()
            else:
                self.speak("لم أتمكن من سماع المدينة. سنحاول لاحقًا.", "إعدادات")
                self.start_wake_word_engine()
        else:
            self.speak("لم أتمكن من سماع الاسم. سنحاول لاحقًا.", "إعدادات")
            self.start_wake_word_engine()

    def check_for_first_run(self):
        if os.path.exists(self.user_data_file):
            with open(self.user_data_file, 'r', encoding='utf-8') as f:
                user_data = json.load(f)
                self.user_name = user_data.get("name")
                self.user_city = user_data.get("city")
                self.microphone_index = user_data.get("microphone_index")
                if self.microphone_index is None:
                    try:
                        import pyaudio
                        p = pyaudio.PyAudio()
                        info = p.get_default_input_device_info()
                        self.microphone_index = info['index']
                        logging.info(f"Using default microphone from check_for_first_run: {info['name']} (Index: {self.microphone_index})")
                        p.terminate()
                    except Exception as e:
                        logging.warning(f"Could not find default microphone, continuing without specific index. Error: {e}")
                        self.microphone_index = -1
            self.speak(f"مرحبًا بعودتك يا {self.user_name}!", "إعدادات")
            self.start_wake_word_engine()
        else:
            self.run_first_time_setup()

    def load_plugins(self):
        plugins_dir = os.path.join(os.path.dirname(__file__), 'plugins')
        if not os.path.exists(plugins_dir):
            logging.warning(f"تنبيه: مجلد الإضافات '{plugins_dir}' غير موجود.")
            return

        logging.info("--- Loading Plugins ---")
        for filename in os.listdir(plugins_dir):
            if filename.endswith(".py") and not filename.startswith("__"):
                try:
                    module_name = filename[:-3]
                    file_path = os.path.join(plugins_dir, filename)

                    spec = importlib.util.spec_from_file_location(module_name, file_path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    if hasattr(module, 'Plugin'):
                        plugin_instance = module.Plugin()
                        for keyword in plugin_instance.get_keywords():
                            self.commands[keyword] = plugin_instance
                        logging.info("[Success] Loaded plugin: %s", module_name)
                except Exception as e:
                    logging.error("[Failed] Failed to load plugin %s: %s", filename, e)
        logging.info("-----------------------")


    def stop_current_speech(self):
        self.audio_playback_thread.stop_playback()

    def execute_command(self, command):
        # 1. أوامر التحكم الأساسية (الأولوية القصوى)
        if command == "stop_conversation":
            self.speak("على الرحب والسعة. في انتظار كلمة التفعيل مجددًا.", "تحكم")
            self.last_known_subject = None
            return
        
        # 2. التحقق من وجود عملية متابعة نشطة (أولوية عالية قبل NLU)
        if self.follow_up_plugin: # <--- إضافة هذا الجزء
            logging.info(f"Processing follow-up command for plugin: {type(self.follow_up_plugin).__name__}")
            try:
                # استدعاء دالة process_follow_up في المكون النشط
                self.follow_up_plugin.process_follow_up(self, command, self.speak)
            except AttributeError:
                logging.error(f"Follow-up plugin {type(self.follow_up_plugin).__name__} does not have 'process_follow_up' method.")
                self.speak("عذراً، حدث خطأ في معالجة طلب المتابعة.", "خطأ داخلي")
                self.follow_up_plugin = None # مسح المكون لمنع الأخطاء المستقبلية
            except Exception as e:
                logging.error(f"Error in follow-up plugin {type(self.follow_up_plugin).__name__}: {e}")
                self.speak("عذراً، حدث خطأ أثناء معالجة طلب المتابعة الخاص بك.", "خطأ داخلي")
                self.follow_up_plugin = None
            self.last_known_subject = None # مسح السياق لأن المكون قام بمعالجة الأمر
            return # إيقاف المعالجة في execute_command


        # 3. معالجة أوامر النظام باستخدام NLU (مع عتبة ثقة عالية)
        intent = None
        entities = {}
        top_confidence = 0.0
    
        if self.nlu_model:
            doc = self.nlu_model(command)
            intents_scored = sorted(doc.cats.items(), key=lambda item: item[1], reverse=True)
    
            if intents_scored:
                top_intent = intents_scored[0][0]
                top_confidence = intents_scored[0][1]
                if top_confidence > 0.75:
                    intent = top_intent
                    entities = {ent.label_: ent.text for ent in doc.ents}
    
            logging.info("NLU Analysis -> Top Intent: %s (Confidence: %.2f), Entities: %s",
                         intent, top_confidence, entities)
    
        if intent:
            if intent == "VOLUME_CONTROL":
                volume_plugin = self.commands.get("صوت")
                if volume_plugin: volume_plugin.execute(self, command, self.speak)
                else: self.speak("عذراً، لا أستطيع التحكم بالصوت حالياً.", "خطأ محلي")
                self.last_known_subject = None
                return
            elif intent == "OPEN_APPLICATION":
                app_name = entities.get("APP_NAME")
                if app_name and "يوتيوب" in app_name:
                    self.add_message_to_conversation("المساعد", "بالتأكيد، جاري فتح يوتيوب.", "تطبيق محلي")
                    self.open_url_in_thread("https://www.youtube.com/")
                elif app_name: 
                    self._open_application(app_name)
                else: self.speak(f"عذراً، لم أفهم اسم التطبيق الذي تريد فتحه: {command}", "خطأ محلي")
                self.last_known_subject = None
                return
            elif intent == "GET_TIME":
                time_plugin = self.commands.get("الوقت")
                if time_plugin: time_plugin.execute(self, command, self.speak)
                else: self.speak("عذراً، لا أستطيع معرفة الوقت حالياً.", "خطأ محلي")
                self.last_known_subject = None
                return
            elif intent == "GET_WEATHER":
                weather_plugin = self.commands.get("طقس")
                city = entities.get("LOCATION")
                if weather_plugin:
                    if city: weather_plugin.execute_follow_up(city, self, self.speak)
                    else: weather_plugin.execute(self, command, self.speak)
                else: self.speak("عذراً، لا أستطيع جلب معلومات الطقس حالياً.", "خطأ محلي")
                self.last_known_subject = None
                return
            elif intent == "GREETING":
                if self.user_name: self.speak(f"أهلاً بك يا {self.user_name}، كيف يمكنني مساعدتك اليوم؟", "تحية")
                else: self.speak("أهلاً بك، كيف يمكنني مساعدتك؟", "تحية")
                self.last_known_subject = None
                return
            elif intent == "SEARCH_YOUTUBE":
                youtube_query = entities.get("QUERY")
                if youtube_query:
                    encoded_query = urllib.parse.quote_plus(youtube_query)
                    search_url = f"https://www.youtube.com/results?search_query={encoded_query}"
                    self.speak(f"حاضر، جاري البحث عن {youtube_query} على يوتيوب.", "يوتيوب")
                    self.open_url_in_thread(search_url)
                else:
                    self.speak("عذراً، لم أفهم ماذا تريد أن تبحث في يوتيوب.", "يوتيوب")
                self.last_known_subject = None
                return
            elif intent == "SEARCH_BROWSER":
                search_query = entities.get("QUERY")
                if search_query:
                    encoded_query = urllib.parse.quote_plus(search_query)
                    search_url = f"https://www.google.com/search?q={encoded_query}"
                    self.speak(f"حاضر، جاري البحث عن {search_query} على المتصفح.", "متصفح")
                    self.open_url_in_thread(search_url)
                else:
                    self.speak("عذراً، لم أفهم ماذا تريد أن تبحث في المتصفح.", "متصفح")
                self.last_known_subject = None
                return
    
        # 4. السقوط إلى Gemini (للاستعلامات العامة التي لم يتم معالجتها بالأعلى)
        self.handle_gemini_chat(command)
        self.last_known_subject = None

    def start_wake_word_engine(self):
        if hasattr(self, 'wake_word_thread') and self.wake_word_thread and self.wake_word_thread.isRunning():
            self.wake_word_thread.stop()
            self.wake_word_thread.wait()

        self.update_status("في انتظار كلمة التفعيل (أليكسا)...", "#A3BE8C")
        self.wake_word_thread = WakeWordThread(access_key=os.getenv("PICOVOICE_ACCESS_KEY"))
        self.wake_word_thread.wake_word_detected.connect(self.start_conversation_mode)
        self.wake_word_thread.stop_speaking_signal.connect(self.stop_current_speech)
        self.wake_word_thread.wake_word_error_signal.connect(self.handle_wake_word_error)
        self.wake_word_thread.start()

    def handle_wake_word_error(self, error_message):
        logging.error(f"Handled Wake Word Error: {error_message}")
        self.update_status("خطأ في تفعيل كلمة التفعيل. يرجى التحقق من الميكروفون أو مفتاح Picovoice.", "#E06C75")
        self.speak("عذراً، واجهت مشكلة في الاستماع لكلمة التفعيل. يرجى التأكد من توصيل الميكروفون أو مراجعة إعداداتي.", "خطأ")
        if hasattr(self, 'wake_word_thread') and self.wake_word_thread and self.wake_word_thread.isRunning():
            self.wake_word_thread.stop()
            self.wake_word_thread.wait()


    def start_conversation_mode(self):
        if self.conversation_thread is not None and self.conversation_thread.isRunning(): 
            return
        
        welcome_message = f"أهلاً {self.user_name}, تفضل بأمرك..." if self.user_name else "تفضل بأمرك..."
        self.update_status(welcome_message)
        self.gemini_chat_session = genai.GenerativeModel('gemini-1.5-flash').start_chat(history=[])
        self.conversation_thread = ConversationThread()
        self.conversation_thread.status_signal.connect(self.update_status)
        self.conversation_thread.conversation_signal.connect(self.add_message_to_conversation)
        self.conversation_thread.command_to_execute_signal.connect(self.execute_command)
        self.conversation_thread.conversation_finished_signal.connect(lambda: self.update_status("في انتظار كلمة التفعيل (أليكسا)...", "#A3BE8C"))
        self.conversation_thread.stop_speaking_signal.connect(self.stop_current_speech)
        self.conversation_thread.microphone_index = self.microphone_index
        self.conversation_thread.start()

    def add_message_to_conversation(self, speaker, text, source=None):
        list_item = QListWidgetItem(self.conversation_list)
        message_widget = ChatMessageWidget(text, speaker == "أنت", source)
        list_item.setSizeHint(message_widget.sizeHint())
        self.conversation_list.addItem(list_item)
        self.conversation_list.setItemWidget(list_item, message_widget)
        self.conversation_list.scrollToBottom()

    def update_status(self, text, color_hex="#EBCB8B"):
        self.status_icon.setStyleSheet(f"color: {color_hex};")
        if text in ["جاري التحليل...", "أفكر..."]:
            self.status_label.hide()
            self.typing_indicator.start_animation()
        else:
            self.typing_indicator.stop_animation()
            self.status_label.setText(text)
            self.status_label.show()

    def closeEvent(self, event):
        logging.info("Closing application and stopping threads...")
        self.audio_playback_thread.stop_playback()
        self.audio_playback_thread.wait()

        if hasattr(self, 'conversation_thread') and self.conversation_thread and self.conversation_thread.isRunning():
            self.conversation_thread.stop()
            self.conversation_thread.wait()
            logging.info("Conversation thread stopped.")
        
        if hasattr(self, 'wake_word_thread') and self.wake_word_thread:
            self.wake_word_thread.stop()
            self.wake_word_thread.wait()
            logging.info("Wake word thread stopped.")
        
        event.accept()

    def speak(self, text, source="المساعد"):
        self.update_status("يتحدث...")
        self.add_message_to_conversation("المساعد", text, source)

        temp_file_path = None
        try:
            tts = gTTS(text=text, lang='ar')
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_audio:
                tts.write_to_fp(tmp_audio)
                temp_file_path = tmp_audio.name

            self.audio_playback_thread.play_audio(temp_file_path)

        except Exception as e:
            logging.error("gTTS error: %s", e)
            self.add_message_to_conversation("المساعد", f"عذراً، لا أستطيع التحدث الآن: {e}", "خطأ صوتي")
            if temp_file_path and os.path.exists(temp_file_path):
                logging.warning("Failed to delete temp audio file: %s - it might be in use.", temp_file_path)


    def handle_gemini_chat(self, command, keep_subject=False):
        self.update_status("أفكر...")
        try:
            response = self.gemini_chat_session.send_message(command)
            self.speak(response.text, "Gemini")
            if not keep_subject:
                if len(response.text.split()) > 2:
                    potential_subject = response.text.split()[0:3]
                    if not any(k in potential_subject for k in ["الطقس", "الساعة", "الوقت", "تطبيق", "برنامج", "المتصفح", "يوتيوب"]):
                        self.last_known_subject = " ".join(potential_subject)
                    else:
                        self.last_known_subject = None
                else:
                    self.last_known_subject = None
            
        except google.api_core.exceptions.InvalidArgument as e: 
            self.speak("عذراً، لا يمكنني معالجة هذا الطلب. قد يكون هناك مشكلة في صياغة السؤال أو نوع المدخلات.", "خطأ Gemini")
            logging.error("Gemini InvalidArgument Error: %s", e)
            self.last_known_subject = None
        except google.api_core.exceptions.ResourceExhausted as e:
            self.speak("عذراً، لقد تجاوزتُ حد الاستخدام اليومي للذكاء الاصطناعي (الكوتا). يرجى المحاولة لاحقاً أو التحقق من استخدامك.", "خطأ Gemini")
            logging.error("Gemini ResourceExhausted Error: %s", e)
            self.last_known_subject = None
        except requests.exceptions.ConnectionError as e:
            self.speak("عذراً، لا أستطيع الاتصال بخدمة الذكاء الاصطناعي. يرجى التحقق من اتصالك بالإنترنت.", "خطأ شبكة")
            logging.error("Gemini Connection Error: %s", e)
            self.last_known_subject = None
        except Exception as e:
            logging.exception("Gemini General Error: %s", e)
            self.speak("عذرًا، حدث خطأ عام أثناء التواصل مع الذكاء الاصطناعي. يرجى مراجعة سجل الأخطاء.", "خطأ Gemini")
            self.last_known_subject = None
