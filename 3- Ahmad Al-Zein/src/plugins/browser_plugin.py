# plugins/browser_plugin.py
import webbrowser
import urllib.parse
import logging

class Plugin:
    def get_keywords(self):
        return ["متصفح", "افتح المتصفح", "ابحث"]

    def execute(self, main_window, command, speak_func, query_text=None):
        search_query = query_text
        
        if search_query is None:
            if "ابحث عن" in command:
                search_query = command.split("ابحث عن", 1)[1].strip()
            elif "عن" in command and len(command.split("عن")) > 1:
                search_query = command.split("عن", 1)[1].strip()
            
        if search_query:
            encoded_query = urllib.parse.quote_plus(search_query)
            search_url = f"https://www.google.com/search?q={encoded_query}"
            speak_func(f"حاضر، جاري البحث عن {search_query} على المتصفح.")
            main_window.open_url_in_thread(search_url)
        else:
            speak_func("جاري فتح المتصفح.")
            main_window.open_url_in_thread("https://www.google.com/")