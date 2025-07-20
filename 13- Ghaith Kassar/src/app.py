import re
import arabic_reshaper
from bidi.algorithm import get_display
from PyQt6.QtWidgets import (
     QWidget, QTextEdit, QListWidget, QListWidgetItem,
    QVBoxLayout, QLabel, QPushButton, QHBoxLayout
)
from PyQt6.QtCore import Qt, QEvent

from model import load_models, predict_next_words, generate_sentences

class AutoCompleteApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("نظام الإكمال التلقائي")
        self.resize(900, 600)

        self.trigram_model, self.bigram_model = load_models()
        self.sentence_mode = False
        self.used_suggestions = set()

        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.title_label = QLabel("الإكمال التلقائي للنصوص")
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.layout.addWidget(self.title_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.text_edit = QTextEdit()
        self.text_edit.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.text_edit.setStyleSheet("font-size: 18px;")
        self.text_edit.textChanged.connect(self.on_text_changed)
        self.text_edit.installEventFilter(self) 
        self.layout.addWidget(self.text_edit)

        self.suggestions_list = QListWidget()
        self.suggestions_list.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.suggestions_list.hide()
        self.suggestions_list.itemClicked.connect(self.on_suggestion_clicked)
        self.layout.addWidget(self.suggestions_list)

        btn_layout = QHBoxLayout()

        self.toggle_mode_btn = QPushButton("تغيير النمط: كلمة")
        self.toggle_mode_btn.clicked.connect(self.toggle_mode)
        btn_layout.addWidget(self.toggle_mode_btn)

        self.clear_btn = QPushButton("مسح")
        self.clear_btn.clicked.connect(self.clear_text)
        btn_layout.addWidget(self.clear_btn)

        self.quit_btn = QPushButton("خروج")
        self.quit_btn.clicked.connect(self.close)
        btn_layout.addWidget(self.quit_btn)

        self.layout.addLayout(btn_layout)
        self.setLayout(self.layout)

    def toggle_mode(self):
        self.sentence_mode = not self.sentence_mode
        mode_text = "جملة" if self.sentence_mode else "كلمة"
        self.toggle_mode_btn.setText(f"تغيير النمط: {mode_text}")
        self.update_suggestions()

    def tokenize_text(self, text):
        words = re.findall(r'[\w\u0600-\u06FF\u0750-\u077F]+', text)
        return [w for w in words if w]

    def is_arabic(self, text):
        return bool(re.search(r'[\u0600-\u06FF]', text))

    def reshape_arabic(self, text):
        reshaped_text = arabic_reshaper.reshape(text)
        bidi_text = get_display(reshaped_text)
        return bidi_text

    def on_text_changed(self):
        self.update_suggestions()

    def update_suggestions(self):
        text = self.text_edit.toPlainText().strip()
        words = self.tokenize_text(text)

        if not words:
            self.suggestions_list.hide()
            self.suggestions_list.clear()
            self.used_suggestions.clear()
            return

        suggestions = []
        if self.sentence_mode and len(words) >= 2:
            suggestions = generate_sentences(words[-2:], self.trigram_model, self.bigram_model)
        else:
            context = words[-2:] if len(words) >= 2 else words
            suggestions = predict_next_words(
                context[0] if len(context) > 0 else "",
                context[1] if len(context) > 1 else "",
                self.trigram_model,
                self.bigram_model
            )

      
        seen = set()
        unique_suggestions = []
        for s in suggestions:
            if s not in seen and s not in self.used_suggestions:
                seen.add(s)
                unique_suggestions.append(s)

        self.suggestions_list.clear()

        if unique_suggestions:
            for s in unique_suggestions:
                display_text = self.reshape_arabic(s) if self.is_arabic(s) else s
                item = QListWidgetItem(display_text)
                item.setData(1000, s)
                alignment = Qt.AlignmentFlag.AlignRight if self.is_arabic(s) else Qt.AlignmentFlag.AlignLeft
                item.setTextAlignment(alignment | Qt.AlignmentFlag.AlignVCenter)
                self.suggestions_list.addItem(item)

            self.suggestions_list.setCurrentRow(0)
            self.suggestions_list.show()
        else:
            self.suggestions_list.hide()

    def on_suggestion_clicked(self, item):
        self.insert_suggestion(item)

    def insert_suggestion(self, item):
        original_text = item.data(1000) or item.text()
        cursor = self.text_edit.textCursor()
        cursor.insertText(" " + original_text + " ")
        self.text_edit.setTextCursor(cursor)
        self.suggestions_list.hide()
        self.used_suggestions.add(original_text)

    def clear_text(self):
        self.text_edit.clear()
        self.suggestions_list.hide()
        self.used_suggestions.clear()

    def eventFilter(self, source, event):
        if source == self.text_edit and self.suggestions_list.isVisible():
            if event.type() == QEvent.Type.KeyPress:
                key = event.key()
                current_row = self.suggestions_list.currentRow()
                count = self.suggestions_list.count()

                if key == Qt.Key.Key_Down:
                    if current_row < count - 1:
                        self.suggestions_list.setCurrentRow(current_row + 1)
                    return True
                elif key == Qt.Key.Key_Up:
                    if current_row > 0:
                        self.suggestions_list.setCurrentRow(current_row - 1)
                    return True
                elif key in (Qt.Key.Key_Enter, Qt.Key.Key_Return):
                    item = self.suggestions_list.currentItem()
                    if item:
                        self.insert_suggestion(item)
                        return True
                elif key == Qt.Key.Key_Escape:
                    self.suggestions_list.hide()
                    return True
        return super().eventFilter(source, event)

