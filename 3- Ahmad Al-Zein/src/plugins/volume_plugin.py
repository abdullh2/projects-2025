# plugins/volume_plugin.py
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import logging # تم الإضافة: استيراد مكتبة التسجيل

class Plugin:
    def __init__(self):
        """Initializes the audio volume interface."""
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            self.volume = cast(interface, POINTER(IAudioEndpointVolume))
            self.error = None
        except Exception as e:
            self.volume = None
            self.error = e
            # تم التعديل: استخدام logging.error لتسجيل الخطأ في ملف app.log
            logging.error(f"Volume Control Error: Could not initialize audio device. {e}")

    def get_keywords(self):
        return ["صوت"]

    def execute(self, main_window, command, speak_func):
        if not self.volume:
            speak_func(f"عذرًا، لا يمكن التحكم بالصوت. {self.error}")
            return

        if "ارفع" in command:
            current_volume = self.volume.GetMasterVolumeLevelScalar()
            new_volume = min(1.0, current_volume + 0.1) # Increase by 10%
            self.volume.SetMasterVolumeLevelScalar(new_volume, None)
            speak_func("تم رفع الصوت")
        
        elif "اخفض" in command:
            current_volume = self.volume.GetMasterVolumeLevelScalar()
            new_volume = max(0.0, current_volume - 0.1) # Decrease by 10%
            self.volume.SetMasterVolumeLevelScalar(new_volume, None)
            speak_func("تم خفض الصوت")

        elif "كتم" in command:
            self.volume.SetMute(1, None)
            speak_func("تم كتم الصوت")
            
        elif "إلغاء كتم" in command or "شغل الصوت" in command:
            self.volume.SetMute(0, None)
            speak_func("تم تشغيل الصوت")

        elif "اضبط" in command or "خلي" in command:
            try:
                level_str = [s for s in command.split() if s.isdigit()][0]
                level = int(level_str)
                if 0 <= level <= 100:
                    self.volume.SetMasterVolumeLevelScalar(level / 100.0, None)
                    speak_func(f"تم ضبط الصوت على {level} بالمئة")
                else:
                    speak_func("يرجى اختيار مستوى صوت بين 0 و 100.")
            except (IndexError, ValueError):
                speak_func("عذرًا، لم أفهم مستوى الصوت المطلوب.")
        else:
            # Default action if only "صوت" is said
            current_level = int(self.volume.GetMasterVolumeLevelScalar() * 100)
            speak_func(f"مستوى الصوت الحالي هو {current_level} بالمئة.")