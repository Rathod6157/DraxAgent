from email.mime import text
import sys
from core import understand
from executor import execute
from PySide6.QtWidgets import QTextEdit
from terminal import set_output_callback

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
)


class DraxWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("DraxAgent")
        self.resize(700, 420)

        layout = QVBoxLayout()

        title = QLabel("🤖 DraxAgent")
        title.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
        """)

        subtitle = QLabel("Your Personal Desktop Companion")

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        
        self.input_box = QLineEdit()
        self.input_box.setPlaceholderText("Ask Drax anything...")

        self.button = QPushButton("Send")
        
        self.button.clicked.connect(self.process_command)
        self.input_box.returnPressed.connect(self.process_command)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(20)
        layout.addWidget(self.output)
        layout.addWidget(self.input_box)
        layout.addWidget(self.button)

        self.setLayout(layout)
        
        set_output_callback(self.append_output)

    def process_command(self):

        command = self.input_box.text().strip()

        if not command:
            return

        # Show what the user typed
        self.append_output(f"> {command}")

        task = understand(command)
        execute(task)

        self.input_box.clear()
        
    def append_output(self, text):
        self.output.append(text)

from skills.skill_loader import load_skills

load_skills()

app = QApplication(sys.argv)

window = DraxWindow()
window.show()

sys.exit(app.exec())