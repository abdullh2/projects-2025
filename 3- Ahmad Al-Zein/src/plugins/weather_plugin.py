# plugins/weather_plugin.py
import requests
import os
import logging # <--- تم الإضافة

class Plugin:
    def get_keywords(self):
        return ["طقس"]

    def execute(self, main_window, command, speak_func):
        city_from_command = None
        # نحاول استخراج المدينة من الأمر مباشرة
        if "في " in command:
            try:
                city_from_command = command.split("في ")[1].strip()
            except IndexError:
                city_from_command = None
        
        # إذا لم نجد مدينة في الأمر، نتحقق من المدينة الافتراضية
        if city_from_command:
            self.execute_follow_up(city_from_command, main_window, speak_func)
        elif main_window.user_city:
            self.execute_follow_up(main_window.user_city, main_window, speak_func)
        else:
            # إذا لم تكن هناك مدينة محددة ولم تكن هناك مدينة افتراضية، نطلبها من المستخدم
            main_window.follow_up_plugin = self # تعيين هذا المكون كمكون المتابعة
            speak_func("بالتأكيد، لأي مدينة؟")

    def process_follow_up(self, main_window, command, speak_func): # <--- دالة جديدة
        # هذه الدالة تستقبل أمر المستخدم بعد طلب المتابعة
        city_name = command.strip() # نفترض أن الأمر هو اسم المدينة
        if city_name:
            self.execute_follow_up(city_name, main_window, speak_func)
        else:
            speak_func("عذراً، لم أستطع فهم اسم المدينة. يرجى المحاولة مرة أخرى.")
        main_window.follow_up_plugin = None # مسح مكون المتابعة بعد المعالجة


    def execute_follow_up(self, city_name, main_window, speak_func):
        # لم تعد هناك حاجة لـ main_window.follow_up_plugin = None هنا، لأنها ستتم في process_follow_up
        # main_window.follow_up_plugin = None

        url = f"http://api.weatherapi.com/v1/current.json?key={os.getenv('WEATHER_API_KEY')}&q={city_name}&aqi=no"
        speak_func(f"حسنًا، جاري جلب حالة الطقس في {city_name}...")
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            report = f"الطقس في {data['location']['name']} حاليًا {data['current']['condition']['text']}، ودرجة الحرارة {int(data['current']['temp_c'])} درجة مئوية."
            speak_func(report)
        except requests.exceptions.HTTPError as http_err:
            error_message = f"عذرًا، لم أتمكن من جلب بيانات الطقس لـ {city_name}. خطأ في الخادم: {http_err}."
            if response.status_code == 401:
                error_message = "عذرًا، يبدو أن مفتاح WeatherAPI غير صالح. يرجى التحقق منه."
            elif response.status_code == 400:
                error_message = f"عذرًا، لم يتم العثور على بيانات الطقس لمدينة {city_name}. يرجى التحقق من اسم المدينة."
            elif response.status_code == 403:
                error_message = "عذراً، وصول WeatherAPI محظور. ربما انتهت صلاحية المفتاح أو هناك قيود."
            speak_func(error_message)
            main_window.logging.error("WeatherAPI HTTP Error for %s: %s - Response: %s", city_name, http_err, response.text)
        except requests.exceptions.ConnectionError as conn_err:
            speak_func("عذراً، لا أستطيع الاتصال بخدمة الطقس. يرجى التحقق من اتصالك بالإنترنت.")
            main_window.logging.error("WeatherAPI Connection Error: %s", conn_err)
        except requests.exceptions.Timeout as timeout_err:
            speak_func("عذراً، استغرق الاتصال بخدمة الطقس وقتاً طويلاً. يرجى المحاولة مرة أخرى.")
            main_window.logging.error("WeatherAPI Timeout Error: %s", timeout_err)
        except requests.exceptions.RequestException as req_err:
            speak_func(f"عذرًا، حدث خطأ عام أثناء جلب بيانات الطقس لمدينة {city_name}.")
            main_window.logging.error("WeatherAPI General Request Error: %s", req_err)