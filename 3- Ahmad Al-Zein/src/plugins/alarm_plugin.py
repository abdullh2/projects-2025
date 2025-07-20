# plugins/alarm_plugin.py
import subprocess # <--- تم التعديل

class Plugin:
    def get_keywords(self):
        return ["منبه", "افتح المنبه", "الساعة"]

    def execute(self, main_window, command, speak_func):
        speak_func("بالتأكيد، سأفتح لك تطبيق المنبهات والساعة.")
        try:
            # استخدام subprocess.Popen بدلاً من os.system
            if main_window.sys.platform.startswith('win'): # <--- التحقق من نظام التشغيل
                subprocess.Popen("start ms-clock:", shell=True) # <--- تم التعديل
            elif main_window.sys.platform.startswith('darwin'): # macOS
                subprocess.Popen("open -a Clock", shell=True) # <--- تم الإضافة
            elif main_window.sys.platform.startswith('linux'): # Linux
                # قد تحتاج إلى تحديد تطبيق معين للمنبه في Linux، مثلاً gnome-clocks
                # هذا يعتمد على التوزيعة وما هو مثبت
                subprocess.Popen("gnome-clocks", shell=True) # مثال: <--- تم الإضافة
            else:
                speak_func("عذراً، لا أعرف كيف أفتح المنبه على نظام التشغيل هذا.")
        except Exception as e:
            speak_func(f"عذراً، حدث خطأ أثناء محاولة فتح المنبه: {e}")
            main_window.logging.error(f"Error opening alarm app: {e}") # <--- تم الإضافة