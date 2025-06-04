# word_recorder/core/settings_manager.py
from PySide6.QtCore import QSettings, QDir
from PySide6.QtGui import QFont, QGuiApplication
from typing import Optional
class SettingsManager:
    def __init__(self, organization_name="MyCompany", application_name="WordRecorder"):
        self.settings = QSettings(organization_name, application_name)

    # --- Theme Settings ---
    def save_theme(self, theme_name: str):
        """保存主题名称 ('light' 或 'dark')"""
        self.settings.setValue("appearance/theme", theme_name)

    def load_theme(self) -> str:
        """加载主题名称，默认为 'light'"""
        return self.settings.value("appearance/theme", "light")

    # --- Font Size Settings ---
    def save_font_size(self, size_str: str):
        """保存字体大小 ('small', 'medium', 'large')"""
        self.settings.setValue("appearance/font_size", size_str)

    def load_font_size(self) -> str:
        """加载字体大小，默认为 'medium'"""
        return self.settings.value("appearance/font_size", "medium")

    def get_font(self, size_str: str = None) -> QFont:
        """根据大小字符串获取QFont对象"""
        if size_str is None:
            size_str = self.load_font_size()

        font = QGuiApplication.font() # 获取应用程序默认字体作为基础
        if size_str == "small":
            font.setPointSize(10)
        elif size_str == "large":
            font.setPointSize(14)
        else: # medium or default
            font.setPointSize(12) # 或者使用 QGuiApplication.font().pointSize()
        return font

    # --- Last Opened File Settings ---
    def save_last_opened_file(self, file_path: Optional[str]):
        """保存上次打开的文件路径"""
        if file_path:
            self.settings.setValue("general/last_opened_file", file_path)
        else:
            self.settings.remove("general/last_opened_file") # 如果路径为空，则移除记录

    def load_last_opened_file(self) -> Optional[str]:
        """加载上次打开的文件路径"""
        return self.settings.value("general/last_opened_file", None) # 默认为 None

    # --- Style Sheet Loading ---
    def load_stylesheet(self, theme_name: str) -> str:
        """根据主题名称加载对应的 QSS 文件内容"""
        qss_file_path = f":/styles/{theme_name}.qss" # 使用Qt资源系统路径
        # 如果不使用Qt资源系统，则需要构建绝对路径
        # import os
        # base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # 项目根目录
        # qss_file_path = os.path.join(base_path, "resources", "styles", f"{theme_name}.qss")

        # 为了简化，我们先假设QSS文件会被编译到资源文件中
        # 如果直接读取文件，需要确保路径正确
        # For direct file reading (if not using Qt resources):
        import os
        try:
            # Assuming this file is in core/, resources/ is ../resources/
            current_dir = os.path.dirname(os.path.abspath(__file__))
            style_path = os.path.join(current_dir, '..', 'resources', 'styles', f'{theme_name}.qss')

            if os.path.exists(style_path):
                with open(style_path, "r", encoding="utf-8") as f:
                    return f.read()
            else:
                print(f"Warning: Stylesheet file not found: {style_path}")
                return ""
        except Exception as e:
            print(f"Error loading stylesheet {theme_name}.qss: {e}")
            return ""