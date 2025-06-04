# word_recorder/main_window.py
import sys
import os

# PySide6 imports
from PySide6.QtCore import Qt, Slot, QSize
from PySide6.QtGui import (QAction, QIcon, QKeySequence, QCloseEvent, QGuiApplication, QFont,
                           QActionGroup) # <-- QActionGroup 被添加到这里
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QTabWidget,
                               QFileDialog, QMessageBox, QLabel, QToolBar, QApplication)

# Local application imports
from core.settings_manager import SettingsManager
from core.data_manager import DataManager
from models.word_list_model import WordListModel
from tabs.add_word_tab import AddWordTab
from tabs.preview_tab import PreviewTab

# --- Icon Path Helper ---
ICON_PATH = os.path.join(os.path.dirname(__file__), "resources", "icons")

def get_icon(name: str) -> QIcon:
    path = os.path.join(ICON_PATH, name)
    if os.path.exists(path):
        return QIcon(path)
    # Fallback to theme icons if custom icon not found
    if name == "new_file.png": return QIcon.fromTheme("document-new", QIcon(
        ":/qt-project.org/styles/commonstyle/images/standardbutton-new-32.png"))
    if name == "open_file.png": return QIcon.fromTheme("document-open", QIcon(
        ":/qt-project.org/styles/commonstyle/images/standardbutton-open-32.png"))
    if name == "save_file.png": return QIcon.fromTheme("document-save", QIcon(
        ":/qt-project.org/styles/commonstyle/images/standardbutton-save-32.png"))
    if name == "toggle_theme.png": return QIcon.fromTheme("preferences-desktop-theme", QIcon(
        ":/qt-project.org/styles/commonstyle/images/standardbutton-িক্যালেন্ডრი-32.png"))  # Placeholder
    return QIcon()  # Empty icon


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("单词记录本")
        self.setGeometry(100, 100, 800, 600)  # x, y, width, height

        self.settings_manager = SettingsManager()
        self.data_manager = DataManager()
        self.word_model = WordListModel(self.data_manager.get_data())

        self._init_ui()
        self._load_settings()  # 加载并应用字体和主题

        self._auto_load_last_file()  # <--- 新增调用

        self._update_status_bar()  # 确保在自动加载后更新状态栏
        self._update_word_count_display()

        if not self.data_manager.filepath:  # 如果没有自动加载文件
            self.add_tab.stop_random_word_timer()
            self.add_tab.display_random_word(None, None)

    def _auto_load_last_file(self):
        """尝试自动加载上次打开的文件"""
        last_file = self.settings_manager.load_last_opened_file()
        if last_file and os.path.exists(last_file):
            # print(f"Attempting to auto-load: {last_file}") # Debugging
            success, message = self.data_manager.load_csv(last_file)
            if success:
                self.word_model.set_data(self.data_manager.get_data())
                # _update_all_displays() 会在 __init__ 的后续部分被间接调用
                if self.data_manager.get_word_count() > 0:
                    self.add_tab.start_random_word_timer()
                    self._display_random_word_on_tab()
                # QMessageBox.information(self, "自动加载", f"已自动加载词表: {os.path.basename(last_file)}") # 可选提示
            else:
                QMessageBox.warning(self, "自动加载失败",
                                    f"无法自动加载上次的词表 '{os.path.basename(last_file)}':\n{message}\n\n将清空此记录。")
                self.settings_manager.save_last_opened_file(None)  # 清除无效路径
        # else:
        # print("No last file to load or file does not exist.") # Debugging

# ...

    def _init_ui(self):
        # --- Central Widget and Layout ---
        self.central_widget = QWidget()
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)  # 让infobar和tabwidget紧贴边缘
        self.main_layout.setSpacing(0)
        self.setCentralWidget(self.central_widget)

        # --- Info Bar (Status Label) ---
        self.info_bar_label = QLabel("当前无列表打开")
        self.info_bar_label.setObjectName("infoBarLabel")  # For QSS styling
        self.info_bar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_bar_label.setFixedHeight(30)  # 固定高度
        self.main_layout.addWidget(self.info_bar_label)

        # --- Tab Widget ---
        self.tab_widget = QTabWidget()
        self.add_tab = AddWordTab()
        self.preview_tab = PreviewTab()
        self.preview_tab.set_model(self.word_model)

        self.tab_widget.addTab(self.add_tab, "新增单词")
        self.tab_widget.addTab(self.preview_tab, "词表预览")
        self.main_layout.addWidget(self.tab_widget)

        # --- Connect Signals from Tabs ---
        self.add_tab.add_word_requested.connect(self._handle_add_word)
        self.add_tab.random_word_requested.connect(self._display_random_word_on_tab)

        # --- Actions, Menus, Toolbars ---
        self._create_actions()
        self._create_menus()
        self._create_toolbars()

    def _load_settings(self):
        # Load and apply theme
        current_theme = self.settings_manager.load_theme()
        self._apply_theme(current_theme)
        # Update theme toggle button state
        self.toggle_theme_action.setChecked(current_theme == "dark")

        # Load and apply font size
        font_size_str = self.settings_manager.load_font_size()
        self._apply_font_size(font_size_str)
        # Update font menu check state
        if font_size_str == "small":
            self.small_font_action.setChecked(True)
        elif font_size_str == "medium":
            self.medium_font_action.setChecked(True)
        elif font_size_str == "large":
            self.large_font_action.setChecked(True)

    def _create_actions(self):
        # File Actions
        self.new_action = QAction(get_icon("new_file.png"), "创建单词表 (&N)", self,
                                  shortcut=QKeySequence.StandardKey.New, statusTip="创建一个新的单词表",
                                  triggered=self.new_list)
        self.open_action = QAction(get_icon("open_file.png"), "打开单词表 (&O)", self,
                                   shortcut=QKeySequence.StandardKey.Open, statusTip="打开一个已存在的单词表",
                                   triggered=self.open_list)
        self.save_action = QAction(get_icon("save_file.png"), "保存 (&S)", self,
                                   shortcut=QKeySequence.StandardKey.Save, statusTip="保存当前单词表",
                                   triggered=self.save_list)
        self.save_as_action = QAction("另存为 (&A)...", self,
                                      shortcut=QKeySequence.StandardKey.SaveAs, triggered=self.save_as_list)
        self.exit_action = QAction("退出 (&X)", self, shortcut="Ctrl+Q", triggered=self.close)

        # Settings Actions - Font
        self.small_font_action = QAction("小", self, checkable=True, triggered=lambda: self.update_font_size("small"))
        self.medium_font_action = QAction("中", self, checkable=True, triggered=lambda: self.update_font_size("medium"))
        self.large_font_action = QAction("大", self, checkable=True, triggered=lambda: self.update_font_size("large"))

        # Settings Actions - Theme (Toolbar will have a toggle button)
        self.light_theme_action = QAction("明亮主题", self, checkable=True, triggered=lambda: self._set_theme("light"))
        self.dark_theme_action = QAction("黑暗主题", self, checkable=True, triggered=lambda: self._set_theme("dark"))

        self.toggle_theme_action = QAction(get_icon("toggle_theme.png"), "切换主题", self,
                                           checkable=True, statusTip="切换明亮/黑暗主题",
                                           triggered=self.toggle_theme)

    def _create_menus(self):
        menu_bar = self.menuBar()

        # File Menu
        file_menu = menu_bar.addMenu("开始 (&F)")
        file_menu.addAction(self.new_action)
        file_menu.addAction(self.open_action)
        file_menu.addAction(self.save_action)
        file_menu.addAction(self.save_as_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)

        # Settings Menu
        settings_menu = menu_bar.addMenu("设置 (&S)")
        font_menu = settings_menu.addMenu("字体大小")
        font_menu.addAction(self.small_font_action)
        font_menu.addAction(self.medium_font_action)
        font_menu.addAction(self.large_font_action)

        self.font_size_group = QActionGroup(self)  # 不传递父对象
        self.font_size_group.addAction(self.small_font_action)
        self.font_size_group.addAction(self.medium_font_action)
        self.font_size_group.addAction(self.large_font_action)
        # self.medium_font_action.setChecked(True) # Default, will be overridden by load_settings

        theme_menu = settings_menu.addMenu("程序背景")
        theme_menu.addAction(self.light_theme_action)
        theme_menu.addAction(self.dark_theme_action)

        self.theme_group = QActionGroup(self)  # 不传递父对象
        self.theme_group.addAction(self.light_theme_action)
        self.theme_group.addAction(self.dark_theme_action)
        # self.light_theme_action.setChecked(True) # Default, will be overridden by load_settings

    def _create_toolbars(self):
        file_toolbar = self.addToolBar("File")
        file_toolbar.setIconSize(QSize(24, 24))  # Set icon size
        file_toolbar.addAction(self.new_action)
        file_toolbar.addAction(self.open_action)
        file_toolbar.addAction(self.save_action)

        settings_toolbar = self.addToolBar("Settings")
        settings_toolbar.setIconSize(QSize(24, 24))
        settings_toolbar.addAction(self.toggle_theme_action)

    # --- Action Handlers / Slots ---
    def _prompt_save_if_dirty(self) -> bool:
        """如果数据已更改，提示用户保存。返回 True 表示可以继续操作，False 表示用户取消。"""
        if not self.data_manager.is_dirty:
            return True  # No changes, proceed

        reply = QMessageBox.warning(
            self, "未保存的更改",
            f"词表 '{self.data_manager.get_current_filename()}' 有未保存的更改。是否保存？",
            QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel
        )
        if reply == QMessageBox.StandardButton.Save:
            return self.save_list()  # save_list returns True on success, False on failure/cancel
        elif reply == QMessageBox.StandardButton.Cancel:
            return False  # User cancelled
        return True  # User chose Discard

    def new_list(self):
        if not self._prompt_save_if_dirty():
            return

        # 立即弹出保存对话框让用户命名新词表
        file_path, _ = QFileDialog.getSaveFileName(
            self, "创建并保存新单词表", # 对话框标题
            self.data_manager.filepath or "untitled.csv", # 默认文件名或路径
            "CSV 文件 (*.csv);;所有文件 (*)"
        )

        if file_path:
            # 确保文件有 .csv 后缀
            if not file_path.lower().endswith(".csv"):
                file_path += ".csv"

            self.data_manager.create_new_list()  # 初始化一个空的DataFrame
            self.data_manager.filepath = file_path   # 设置文件路径

            # 将这个空的DataFrame（带表头）保存到磁盘，以创建文件
            # data_manager.save_csv() 会将 is_dirty 设置为 False
            success, message = self.data_manager.save_csv(file_path)

            if success:
                self.word_model.set_data(self.data_manager.get_data()) # 更新模型
                self._update_all_displays() # 更新UI（状态栏会显示新文件名）
                self.add_tab.clear_inputs()
                self.add_tab.stop_random_word_timer()
                self.add_tab.display_random_word(None, None)
                QMessageBox.information(self, "创建成功", f"词表 '{os.path.basename(file_path)}' 已创建并连接。")
                # 新创建并保存后，这也是最后操作的文件
                self.settings_manager.save_last_opened_file(file_path)
            else:
                QMessageBox.critical(self, "创建失败", f"无法创建词表文件：{message}")
                # 创建失败，重置状态，避免程序处于不一致状态
                self.data_manager.create_new_list() # 回到完全未命名状态
                self.data_manager.filepath = None
                self.word_model.set_data(self.data_manager.get_data())
                self._update_all_displays()
        # else: 用户取消了文件对话框，不执行任何操作

    def open_list(self):
        if not self._prompt_save_if_dirty():
            return

        file_path, _ = QFileDialog.getOpenFileName(
            self, "打开单词表", "", "CSV 文件 (*.csv);;所有文件 (*)"
        )
        if file_path:
            success, message = self.data_manager.load_csv(file_path)
            if success:
                self.word_model.set_data(self.data_manager.get_data())
                QMessageBox.information(self, "打开成功", message)
                self.settings_manager.save_last_opened_file(file_path)
                if self.data_manager.get_word_count() > 0:
                    self.add_tab.start_random_word_timer()
                    self._display_random_word_on_tab()  # Display one immediately
                else:
                    self.add_tab.stop_random_word_timer()
                    self.add_tab.display_random_word(None, None)

            else:
                QMessageBox.critical(self, "打开失败", message)
                if self.data_manager.dataframe is None:
                    self.data_manager.create_new_list()
                    self.word_model.set_data(self.data_manager.get_data())
            self._update_all_displays()

    def save_list(self) -> bool:
        if not self.data_manager.is_dirty and self.data_manager.filepath:
            return True

        if not self.data_manager.filepath:
            return self.save_as_list()
        else:
            success, message = self.data_manager.save_csv()
            if success:
                QMessageBox.information(self, "保存成功", message)
                self._update_status_bar()
                self.settings_manager.save_last_opened_file(self.data_manager.filepath)
                return True
            else:
                QMessageBox.critical(self, "保存失败", message)
                return False

    def save_as_list(self) -> bool:
        if self.data_manager.dataframe is None:
            QMessageBox.warning(self, "另存为", "没有可保存的数据。")
            return False

        file_path, _ = QFileDialog.getSaveFileName(
            self, "单词表另存为", self.data_manager.filepath or "untitled.csv",
            "CSV 文件 (*.csv);;所有文件 (*)"
        )
        if file_path:
            success, message = self.data_manager.save_csv(file_path)
            if success:
                QMessageBox.information(self, "保存成功", message)
                self._update_status_bar()
                self.settings_manager.save_last_opened_file(file_path)
                return True
            else:
                QMessageBox.critical(self, "保存失败", message)
                return False
        return False

    @Slot(str, str)
    def _handle_add_word(self, word: str, definition: str):
        if self.data_manager.add_word(word, definition):
            self.word_model.set_data(self.data_manager.get_data())
            self._update_word_count_display()
            self.add_tab.clear_inputs()
            self._update_status_bar()
            if self.data_manager.get_word_count() == 1:
                self.add_tab.start_random_word_timer()
                self._display_random_word_on_tab()
        else:
            QMessageBox.warning(self, "添加失败", "无法添加单词（可能是单词为空）。")

    @Slot()
    def _display_random_word_on_tab(self):
        random_entry = self.data_manager.get_random_word()
        if random_entry:
            self.add_tab.display_random_word(random_entry[0], random_entry[1])
        else:
            self.add_tab.display_random_word(None, None)

    def _update_status_bar(self):
        filename = self.data_manager.get_current_filename()
        dirty_indicator = "*" if self.data_manager.is_dirty else ""
        if filename == "未命名" and not self.data_manager.is_dirty and self.data_manager.get_word_count() == 0:
            self.info_bar_label.setText("当前无列表打开")
            self.setWindowTitle("单词记录本")
        else:
            self.info_bar_label.setText(f"当前词表：{filename}{dirty_indicator}")
            self.setWindowTitle(f"{filename}{dirty_indicator} - 单词记录本")

    def _update_word_count_display(self):
        count = self.data_manager.get_word_count()
        self.add_tab.update_word_count(count)

    def _update_all_displays(self):
        self._update_status_bar()
        self._update_word_count_display()
        if self.preview_tab.table_view.model(): # Check if model exists before calling layoutChanged
             self.preview_tab.table_view.model().layoutChanged.emit()


    # --- Theme and Font Management ---
    def _apply_theme(self, theme_name: str):
        stylesheet = self.settings_manager.load_stylesheet(theme_name)
        QApplication.instance().setStyleSheet(stylesheet)
        self.settings_manager.save_theme(theme_name)
        # Update menu check state
        self.light_theme_action.setChecked(theme_name == "light")
        self.dark_theme_action.setChecked(theme_name == "dark")
        self.toggle_theme_action.setChecked(theme_name == "dark")

    def _set_theme(self, theme_name: str):
        self._apply_theme(theme_name)

    def toggle_theme(self):
        current_theme = self.settings_manager.load_theme()
        new_theme = "dark" if current_theme == "light" else "light"
        self._apply_theme(new_theme)

    def _apply_font_size(self, size_str: str):
        font = self.settings_manager.get_font(size_str)
        QApplication.instance().setFont(font) # 设置应用全局字体

        # 尝试强制刷新样式以应用字体更改
        # 有时，仅仅 QApplication.setFont() 可能不足以更新所有通过QSS设置过字体的控件
        # 重新应用当前样式表可以帮助解决这个问题
        current_stylesheet = QApplication.instance().styleSheet()
        QApplication.instance().setStyleSheet("") # 临时清除
        QApplication.instance().setStyleSheet(current_stylesheet) # 重新应用

        self.settings_manager.save_font_size(size_str)
        # Update menu check state
        self.small_font_action.setChecked(size_str == "small")
        self.medium_font_action.setChecked(size_str == "medium")
        self.large_font_action.setChecked(size_str == "large")

    def update_font_size(self, size_str: str):
        self._apply_font_size(size_str)

    def closeEvent(self, event: QCloseEvent):
        if self._prompt_save_if_dirty():
            self.add_tab.stop_random_word_timer()
            event.accept()
        else:
            event.ignore()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())