
import os
# المكاتب المستخدمة
import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
# مكتبة هاي اشتغلت اسهل لاتعامل مع نصوص استاذ
# مكتبة مدمجةهاي 
import re  
# مكاتب تعلم الة اخدت منها نماذج ال naive bayes , svm ,بعض دوال المستخدمة لبناء النموذج 
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC
from sklearn.metrics import accuracy_score, confusion_matrix
# مكاتب التمثيل البياني للنموذج
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns


def clean_text(text):
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.lower().strip()

class SentimentModel:
    def __init__(self, model_type):
        df = pd.read_csv("../Data/twitter_training.csv", header=None)
        df.columns = ['id', 'entity', 'sentiment', 'text']
        print(df)
        df = df[['text', 'sentiment']]
        df = df[df['sentiment'].isin(['Positive', 'Negative', 'Neutral'])]
        df['text'] = df['text'].astype(str).apply(clean_text)
        label_map = {'Positive': 1, 'Negative': -1, 'Neutral': 0}
        df['sentiment'] = df['sentiment'].map(label_map)
        X_train, X_test, y_train, y_test = train_test_split(df["text"], df["sentiment"], test_size=0.2, random_state=42)
        self.vectorizer = TfidfVectorizer(max_features=5000)
        X_train_vec = self.vectorizer.fit_transform(X_train)
        X_test_vec = self.vectorizer.transform(X_test)
        if model_type == "Naive Bayes":
            self.model = MultinomialNB()
        else:
            self.model = LinearSVC()
        self.model.fit(X_train_vec, y_train)
        self.X_test_vec = X_test_vec
        self.y_test = y_test
        self.y_pred = self.model.predict(X_test_vec)
        self.accuracy = accuracy_score(y_test, self.y_pred)
        self.df = df
    def predict(self, text):
        text_clean = clean_text(text)
        text_vec = self.vectorizer.transform([text_clean])
        return self.model.predict(text_vec)[0]

class SentimentApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Customer Sentiment Analysis")
        self.root.geometry("500x420")
        self.root.configure(bg="#f5f6fa")
        # Set window icon if available
        icon_path = os.path.join(os.path.dirname(__file__), "book_and_pen.ico")
        print(icon_path)
        if os.path.exists(icon_path):
            try:
                self.root.iconbitmap(icon_path)
            except Exception:
                pass
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TLabel', font=('Cairo', 12), background="#f5f6fa")
        style.configure('TButton', font=('Cairo', 12, 'bold'), foreground="#fff", background="#273c75")
        style.map('TButton', background=[('active', '#40739e')])
        style.configure('TCombobox', font=('Cairo', 12))

        self.model_type = tk.StringVar(value="Naive Bayes")
        self.model = SentimentModel(self.model_type.get())

        title = ttk.Label(root, text="Customer Sentiment Analysis", font=("Cairo", 18, "bold"), foreground="#192a56")
        title.pack(pady=10)

        frame = tk.Frame(root, bg="#f5f6fa")
        frame.pack(pady=5)

        ttk.Label(frame, text="Select Model:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        model_menu = ttk.Combobox(frame, textvariable=self.model_type, values=["Naive Bayes", "SVM"], state="readonly", width=15)
        model_menu.grid(row=0, column=1, padx=5, pady=5)
        model_menu.bind("<<ComboboxSelected>>", self.change_model)

        self.accuracy_label = ttk.Label(frame, text=f"Accuracy: {self.model.accuracy*100:.2f}%", foreground="#0097e6", font=("Cairo", 12, "bold"))
        self.accuracy_label.grid(row=0, column=2, padx=10, pady=5)

        ttk.Label(root, text="Enter a tweet to classify:").pack(pady=5)
        self.text_entry = tk.Text(root, height=4, width=55, font=("Cairo", 12))
        self.text_entry.pack(pady=5)

        self.result_label = ttk.Label(root, text="", font=("Cairo", 14, "bold"))
        self.result_label.pack(pady=10)

        btn_frame = tk.Frame(root, bg="#f5f6fa")
        btn_frame.pack(pady=5)

        predict_btn = ttk.Button(btn_frame, text="Predict Sentiment", command=self.predict_sentiment)
        predict_btn.grid(row=0, column=0, padx=10)

        plot_btn = ttk.Button(btn_frame, text="Show Plots", command=self.show_plots)
        plot_btn.grid(row=0, column=1, padx=10)

        # Footer
        footer = ttk.Label(root, text="by AI | sentiment analysis", font=("Cairo", 10), foreground="#718093")
        footer.pack(side="bottom", pady=8)

    def change_model(self, event=None):
        self.model = SentimentModel(self.model_type.get())
        self.accuracy_label.config(text=f"Accuracy: {self.model.accuracy*100:.2f}%")
        self.result_label.config(text="Model changed.")

    def predict_sentiment(self):
        user_text = self.text_entry.get("1.0", tk.END).strip()
        if not user_text:
            messagebox.showwarning("Warning", "Please enter a tweet.")
            return
        user_pred = self.model.predict(user_text)
        if user_pred == 1:
            result = "Sentiment: Positive"
            color = "#44bd32"
        elif user_pred == -1:
            result = "Sentiment: Negative"
            color = "#e84118"
        else:
            result = "Sentiment: Neutral"
            color = "#273c75"
        self.result_label.config(text=result, foreground=color)

    def show_plots(self):
        plot_win = tk.Toplevel(self.root)
        plot_win.title("Evaluation Plots")
        plot_win.geometry("900x400")
        plot_win.configure(bg="#f5f6fa")
        
        icon_path = os.path.join(os.path.dirname(__file__), "book_and_pen.png")
        if os.path.exists(icon_path):
            try:
                plot_win.iconbitmap(icon_path)
            except Exception:
                pass

        # انا هون شغلت المصفوفة الادراك ووصلتها مع واجه تعطي مخطط heatmap
        conf_matrix = confusion_matrix(self.model.y_test, self.model.y_pred, labels=[-1, 0, 1])
        fig1, ax1 = plt.subplots(figsize=(4, 3))
        sns.heatmap(conf_matrix, annot=True, fmt="d", cmap="Blues",
                    xticklabels=['Negative', 'Neutral', 'Positive'],
                    yticklabels=['Negative', 'Neutral', 'Positive'], ax=ax1)
        ax1.set_xlabel("Predicted Label", fontname="Cairo")
        ax1.set_ylabel("True Label", fontname="Cairo")
        ax1.set_title("Confusion Matrix", fontname="Cairo")
        fig1.tight_layout()

        canvas1 = FigureCanvasTkAgg(fig1, master=plot_win)
        canvas1.get_tk_widget().grid(row=0, column=0, padx=20, pady=10)
        canvas1.draw()

        
        fig2 , ax2 = plt.subplots(figsize=(4, 3))
        sentiment_counts = self.model.df['sentiment'].value_counts().sort_index()
        labels = ['Negative', 'Neutral', 'Positive']
        ax2.bar(labels, [sentiment_counts.get(-1,0), sentiment_counts.get(0,0), sentiment_counts.get(1,0)], color=["#e84118", "#273c75", "#44bd32"])
        ax2.set_title("Sentiment Distribution in Data", fontname="Cairo")
        fig2.tight_layout()

        canvas2 = FigureCanvasTkAgg(fig2, master=plot_win)
        canvas2.get_tk_widget().grid(row=0, column=1, padx=20, pady=10)
        canvas2.draw()


# من اجل بداية البرنامج 
if __name__ == "__main__":
    root = tk.Tk()
    app = SentimentApp(root)
    root.mainloop() 


