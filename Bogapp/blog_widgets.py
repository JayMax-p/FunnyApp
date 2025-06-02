# blog_widgets.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QDateEdit, QTextEdit,
    QPushButton, QFormLayout, QSizePolicy, QTableWidget, QTableWidgetItem,
    QHeaderView
)
from PySide6.QtCore import QDate, Qt


# from PySide6.QtGui import QFontMetrics # Not strictly needed if using a good fixed width

class InputFormWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        main_v_layout = QVBoxLayout(self)
        main_v_layout.setContentsMargins(15, 15, 15, 15)
        main_v_layout.setSpacing(15)

        # --- Date QHBoxLayout ---
        date_h_layout = QHBoxLayout()
        date_h_layout.setSpacing(10)

        start_date_label = QLabel("起始日期*:")
        self.start_date_edit = QDateEdit(calendarPopup=True)
        self.start_date_edit.setDate(QDate(2025, 6, 2))
        self.start_date_edit.setDisplayFormat("yyyy/M/d")
        # Set a fixed width to ensure enough space for text and make components same size
        self.start_date_edit.setFixedWidth(135)  # Adjusted width

        end_date_label = QLabel("结束日期*:")
        self.end_date_edit = QDateEdit(calendarPopup=True)
        self.end_date_edit.setDate(QDate(2025, 6, 3))  # Default end date
        self.end_date_edit.setDisplayFormat("yyyy/M/d")
        # Set a fixed width to ensure enough space for text and make components same size
        self.end_date_edit.setFixedWidth(135)  # Adjusted width

        date_h_layout.addWidget(start_date_label)
        date_h_layout.addWidget(self.start_date_edit)
        date_h_layout.addSpacing(25)
        date_h_layout.addWidget(end_date_label)
        date_h_layout.addWidget(self.end_date_edit)
        date_h_layout.addStretch(1)  # Keeps date components aligned to the left
        main_v_layout.addLayout(date_h_layout)

        # --- Task/Notes QFormLayout ---
        task_notes_form_layout = QFormLayout()
        task_notes_form_layout.setSpacing(10)
        task_notes_form_layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)

        self.task_edit = QTextEdit()
        self.task_edit.setPlaceholderText("请输入详细的任务内容 (必填)")
        self.task_edit.setMinimumHeight(120)
        self.task_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        task_notes_form_layout.addRow("任务*:", self.task_edit)

        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("请输入备注信息 (可选)")
        self.notes_edit.setMinimumHeight(80)
        self.notes_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        task_notes_form_layout.addRow("备注:", self.notes_edit)
        main_v_layout.addLayout(task_notes_form_layout)

        # --- Submit Button ---
        self.submit_button = QPushButton("提交日志")
        self.submit_button.setStyleSheet("padding: 10px; font-size: 16px; margin-top: 10px;")
        self.submit_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        button_h_layout = QHBoxLayout()
        button_h_layout.addStretch()
        button_h_layout.addWidget(self.submit_button)
        button_h_layout.addStretch()
        main_v_layout.addLayout(button_h_layout)

        main_v_layout.setStretchFactor(date_h_layout, 0)
        main_v_layout.setStretchFactor(task_notes_form_layout, 1)
        main_v_layout.setStretchFactor(button_h_layout, 0)

    def get_form_data(self):
        return {
            "start_date": self.start_date_edit.date(),
            "end_date": self.end_date_edit.date(),
            "task": self.task_edit.toPlainText().strip(),
            "notes": self.notes_edit.toPlainText().strip()
        }

    def clear_fields(self):
        # self.start_date_edit.setDate(QDate(2025, 6, 2)) # Optionally reset dates
        # self.end_date_edit.setDate(QDate(2025, 6, 3))
        self.task_edit.clear()
        self.notes_edit.clear()


class TableViewWidget(QWidget):
    def __init__(self, headers, parent=None):
        super().__init__(parent)
        self.headers = headers
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(len(self.headers))
        self.table_widget.setHorizontalHeaderLabels(self.headers)
        self.table_widget.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table_widget.setAlternatingRowColors(True)
        self.table_widget.verticalHeader().setVisible(False)
        self.table_widget.setShowGrid(True)
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table_widget)

    def load_data_rows(self, data_rows):
        self.table_widget.setRowCount(0)
        for row_idx, row_data in enumerate(data_rows):
            self.table_widget.insertRow(row_idx)
            for col_idx, cell_data in enumerate(row_data):
                self.table_widget.setItem(row_idx, col_idx, QTableWidgetItem(str(cell_data)))

        self.table_widget.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table_widget.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table_widget.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)

    def set_headers(self, headers):
        self.headers = headers
        self.table_widget.setColumnCount(len(self.headers))
        self.table_widget.setHorizontalHeaderLabels(self.headers)