# plugins/time_plugin.py
import datetime

class Plugin:
    def get_keywords(self):
        return ["الوقت", "كم الساعة", "الساعه كم"]

    # The 'main_window' argument is now included
    def execute(self, main_window, command, speak_func):
        time_str = datetime.datetime.now().strftime("الساعة الآن %I:%M %p")
        speak_func(time_str)