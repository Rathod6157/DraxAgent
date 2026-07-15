import sys
from skills.skill_loader import load_skills
from core import understand
from executor import execute
from terminal import set_output_callback

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
)

from PySide6.QtCore import (
    QObject,
    QThread,
    Signal,
)

from widgets.chat_area import ChatArea
from widgets.status_bar import StatusBar
from widgets.input_bar import InputBar

import widgets.theme as theme

class Worker(QObject):

    finished = Signal()

    def __init__(self, command):
        super().__init__()
        self.command = command

    def run(self):

        task = understand(self.command)

        execute(task)

        self.finished.emit()
        
class DraxWindow(QWidget):

    output_signal = Signal(object)

    def __init__(self):
        super().__init__()

        self.setWindowTitle("🤖 DraxAgent")

        self.resize(900, 650)

        self.build_ui()

        self.connect_signals()
        
    def build_ui(self):

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            theme.WINDOW_PADDING,
            theme.WINDOW_PADDING,
            theme.WINDOW_PADDING,
            theme.WINDOW_PADDING,
        )

        layout.setSpacing(
            theme.SECTION_SPACING
        )
        
        header = QWidget()

        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 10)
        header_layout.setSpacing(14)

        icon = QLabel("🤖")
        icon.setStyleSheet("""
        font-size:40px;
        """)

        titles = QVBoxLayout()

        self.title = QLabel("DraxAgent")
        self.subtitle = QLabel("Your Personal Desktop Companion")

        self.title.setStyleSheet(f"""
        font-size:{theme.TITLE_SIZE}px;
        font-weight:700;
        color:{theme.TEXT};
        """)

        self.subtitle.setStyleSheet(f"""
        font-size:{theme.SUBTITLE_SIZE}px;
        color:{theme.TEXT_SECONDARY};
        """)

        titles.addWidget(self.title)
        titles.addWidget(self.subtitle)

        header_layout.addWidget(icon)
        header_layout.addLayout(titles)
        header_layout.addStretch()

        self.online = QLabel("● Online")

        self.online.setStyleSheet("""
        color:#49D17D;
        font-size:13px;
        font-weight:600;
        """)

        header_layout.addWidget(self.online)

        self.subtitle.setStyleSheet(f"""
            color:{theme.TEXT_SECONDARY};
            font-size:{theme.SUBTITLE_SIZE}px;
        """)
        
        self.status_bar = StatusBar()

        self.chat = ChatArea()

        self.input = InputBar()

        

        layout.addWidget(header)

        layout.addWidget(self.status_bar)

        layout.addWidget(
            self.chat,
            1
        )

        layout.addWidget(self.input)
        
        self.setStyleSheet(f"""
        QWidget{{
            background:{theme.WINDOW_BACKGROUND};
            color:{theme.TEXT};
        }}
        """)

    def connect_signals(self):

        self.input.send_clicked.connect(
            self.process_command
        )

        self.output_signal.connect(
            self.handle_output
        )

        set_output_callback(
            lambda text, kind:
            self.output_signal.emit(
                (text, kind)
            )
        )
        
    
    
    def process_command(self, command):

        command = command.strip()

        if not command:
            return

        self.chat.add_user_message(command)

        self.chat.show_typing()

        self.thread = QThread()

        self.worker = Worker(command)

        self.worker.moveToThread(self.thread)

        self.thread.started.connect(
            self.worker.run
        )

        self.worker.finished.connect(
            self.thread.quit
        )

        self.worker.finished.connect(
            self.worker.deleteLater
        )

        self.thread.finished.connect(
            self.thread.deleteLater
        )

        self.thread.finished.connect(
            self.chat.hide_typing
        )

        self.thread.start()
        
    def handle_output(
        self,
        data
    ):

        text, kind = data

        if kind == "status":

            self.status_bar.show_message(text)

            return

        self.status_bar.hide_message()

        if kind == "assistant":

            self.chat.add_drax_message(text)

            return

        if kind == "success":

            self.chat.add_drax_message(
                "✅ " + text
            )

            return

        if kind == "error":

            self.chat.add_drax_message(
                "❌ " + text
            )

            return

        self.chat.add_drax_message(text)



def main():

    load_skills()

    app = QApplication(sys.argv)

    window = DraxWindow()

    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()