# plugins/vscode_plugin.py
import subprocess # <--- تم التعديل

class Plugin:
    def get_keywords(self):
        return ["فيجوال", "افتح فيجوال", "فيجوال ستوديو كود"] # <--- تم التعديل لإضافة كلمات مفتاحية

    def execute(self, main_window, command, speak_func):
        speak_func("جاري فتح برنامج فيجوال ستوديو كود")
        try:
            # استخدام subprocess.Popen بدلاً من os.system
            subprocess.Popen("code", shell=True) # <--- تم التعديل
        except FileNotFoundError: # <--- تم الإضافة
            speak_func("عذراً، لا يبدو أن برنامج فيجوال ستوديو كود مثبت أو أنه ليس في مسار النظام.")
            main_window.logging.error("VS Code executable 'code' not found in PATH.")
        except Exception as e: # <--- تم الإضافة
            speak_func(f"عذراً، حدث خطأ أثناء محاولة فتح فيجوال ستوديو كود: {e}")
            main_window.logging.error(f"Error opening VS Code: {e}")