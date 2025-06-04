# word_recorder/main.py
import sys
from PySide6.QtWidgets import QApplication
from main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 在创建 MainWindow 之前，可以先加载一次样式，确保初始主题正确
    # (更完善的做法是在 SettingsManager 中提供一个应用初始主题的静态方法)
    # 或者在 MainWindow 的 __init__ 中尽早应用

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
