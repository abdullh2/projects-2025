# plugins/youtube_plugin.py
import webbrowser
import urllib.parse
import logging

class Plugin:
    def get_keywords(self):
        return ["يوتيوب", "افتح يوتيوب", "شغل على يوتيوب", "ابحث في يوتيوب"]

    def execute(self, main_window, command, speak_func, query_text=None):
        search_query = query_text
        
        if search_query is None:
            if "ابحث عن" in command:
                search_query = command.split("ابحث عن", 1)[1].strip()
            elif "شغل" in command:
                potential_query = command.split("شغل", 1)[1].strip()
                if not any(app in potential_query for app in ["المنبه", "الرسام", "الآلة الحاسبة", "المفكرة", "جوجل كروم"]):
                    search_query = potential_query

        if search_query:
            encoded_query = urllib.parse.quote_plus(search_query)
            # الرابط الصحيح للبحث في يوتيوب
            search_url = f"https://www.youtube.com/results?search_query={encoded_query}" # <--- تم التصحيح هنا
            speak_func(f"حاضر، جاري البحث عن {search_query} على يوتيوب.")
            main_window.open_url_in_thread(search_url)
        else:
            speak_func("بالتأكيد، جاري فتح يوتيوب.")
            # استخدام رابط يوتيوب الأساسي الصحيح والقياسي
            main_window.open_url_in_thread("https://www.youtube.com/") # <--- تم التصحيح هنا