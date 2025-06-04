# word_recorder/tabs/add_word_tab.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QLineEdit, QPushButton, QFrame, QLCDNumber, QTextEdit)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont
from typing import Optional # <--- 添加这一行


class AddWordTab(QWidget):
    # 信号：当用户点击“添加到词表”按钮时发出，参数为 (单词, 释义)
    add_word_requested = Signal(str, str)
    # 信号：当需要随机单词时发出 (由内部定时器触发)
    random_word_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

        self.random_word_timer = QTimer(self)
        self.random_word_timer.timeout.connect(self.request_random_word_display)
        # 每分钟 (60000 ms) 刷新一次
        # self.random_word_timer.start(60000) # 由MainWindow控制何时启动

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)  # 增加一些边距
        main_layout.setSpacing(10)  # 增加控件间距

        # --- 上半部分：单词数和随机单词 ---
        top_section_layout = QVBoxLayout()

        # 水平布局1: 单词数目表盘 和 随机单词显示区
        h_layout1 = QHBoxLayout()

        # 单词数目
        self.word_count_lcd = QLCDNumber(self)
        self.word_count_lcd.setSegmentStyle(QLCDNumber.SegmentStyle.Flat)  # 扁平风格
        self.word_count_lcd.setDigitCount(5)  # 最多显示5位数
        self.word_count_lcd.setToolTip("当前词表中的单词总数")

        # 为了让LCD不占据太多空间，可以把它放在一个小布局里
        lcd_container = QVBoxLayout()
        lcd_label = QLabel("当前单词数:")
        lcd_container.addWidget(lcd_label)
        lcd_container.addWidget(self.word_count_lcd)
        lcd_container.addStretch()  # 将LCD推到顶部

        h_layout1.addLayout(lcd_container, 1)  # 比例为1

        # 随机单词显示区
        random_word_group = QFrame(self)
        random_word_group.setFrameShape(QFrame.Shape.StyledPanel)
        random_word_layout = QVBoxLayout(random_word_group)

        random_word_title_label = QLabel("随机词条：")
        font_title = QFont()
        font_title.setBold(True)
        random_word_title_label.setFont(font_title)

        self.random_word_label = QLabel("单词： N/A")
        self.random_definition_label = QTextEdit("释义： N/A")  # 使用QTextEdit以便换行和滚动
        self.random_definition_label.setReadOnly(True)
        self.random_definition_label.setFixedHeight(80)  # 限制释义区高度

        random_word_layout.addWidget(random_word_title_label)
        random_word_layout.addWidget(self.random_word_label)
        random_word_layout.addWidget(self.random_definition_label)

        h_layout1.addWidget(random_word_group, 2)  # 比例为2，占据更多空间

        top_section_layout.addLayout(h_layout1)
        main_layout.addLayout(top_section_layout)

        # --- 分隔线 ---
        separator = QFrame(self)
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(separator)

        # --- 下半部分：输入和提交 ---
        bottom_section_layout = QVBoxLayout()
        bottom_section_layout.setSpacing(10)

        input_layout = QHBoxLayout()
        self.word_input = QLineEdit(self)
        self.word_input.setPlaceholderText("输入单词...")
        self.word_input.setClearButtonEnabled(True)
        input_layout.addWidget(self.word_input, 1)  # 参数1代表拉伸因子

        self.definition_input = QLineEdit(self)  # 或者 QTextEdit 如果释义很长
        self.definition_input.setPlaceholderText("输入释义...")
        self.definition_input.setClearButtonEnabled(True)
        input_layout.addWidget(self.definition_input, 2)  # 参数2代表拉伸因子

        bottom_section_layout.addLayout(input_layout)

        self.submit_button = QPushButton("添加到词表", self)
        self.submit_button.clicked.connect(self._on_submit)
        # 可以给按钮加个icon
        # from PySide6.QtGui import QIcon
        # self.submit_button.setIcon(QIcon.fromTheme("list-add"))

        bottom_section_layout.addWidget(self.submit_button, 0, Qt.AlignmentFlag.AlignRight)  # 按钮靠右

        main_layout.addLayout(bottom_section_layout)
        main_layout.addStretch()  # 添加伸缩，使得内容更紧凑

    def _on_submit(self):
        word = self.word_input.text().strip()
        definition = self.definition_input.text().strip()
        if word:  # 确保单词不为空
            self.add_word_requested.emit(word, definition)
        else:
            # 可以弹出一个小提示，或者让主窗口处理
            print("单词不能为空")  # 简单打印，实际应用中应有更友好的提示

    def update_word_count(self, count: int):
        self.word_count_lcd.display(count)

    def display_random_word(self, word: Optional[str], definition: Optional[str]):
        if word is not None and definition is not None:  # 更安全的检查
            self.random_word_label.setText(f"<b>单词：</b>{word}")
            self.random_definition_label.setPlainText(f"{definition}")  # QTextEdit用setPlainText
        else:
            self.random_word_label.setText("<b>单词：</b> N/A")
            self.random_definition_label.setPlainText("释义： 词表为空或无法获取。")

    def clear_inputs(self):
        self.word_input.clear()
        self.definition_input.clear()
        self.word_input.setFocus()  # 将焦点设置回单词输入框

    def request_random_word_display(self):
        """由定时器调用，发出请求信号"""
        self.random_word_requested.emit()

    def start_random_word_timer(self):
        self.random_word_timer.start(60000)  # 1 minute

    def stop_random_word_timer(self):
        self.random_word_timer.stop()
