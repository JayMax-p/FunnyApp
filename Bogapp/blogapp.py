# blogapp.py
import sys
import csv
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton,
    QMessageBox, QStackedWidget, QStatusBar
)
from PySide6.QtCore import QDate, Qt, Slot
from PySide6.QtGui import QIcon

# Import custom widgets from blog_widgets.py
from blog_widgets import InputFormWidget, TableViewWidget


class BlogApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Jay的日志记录器")
        self.setGeometry(100, 100, 850, 700)  # Adjusted size for overall comfort

        self.csv_file = "blogs.csv"
        self.csv_headers = ["期日", "任务", "备注"]
        self._init_csv()

        # --- Main Central Widget and Layout ---
        self.central_area_widget = QWidget()  # A container for layout
        self.setCentralWidget(self.central_area_widget)
        self.main_layout = QVBoxLayout(self.central_area_widget)
        self.main_layout.setContentsMargins(10, 10, 10, 10)  # Overall margins
        self.main_layout.setSpacing(10)  # Spacing between toggle button and stacked_widget

        # --- Toggle Button ---
        self.toggle_button = QPushButton("查看日志数据")
        self.toggle_button.setMinimumHeight(35)  # Make button a bit taller
        self.toggle_button.setStyleSheet("font-size: 14px; padding: 5px;")
        self.toggle_button.clicked.connect(self._toggle_view)
        self.main_layout.addWidget(self.toggle_button)

        # --- Stacked Widget for Input Form and Table View ---
        self.stacked_widget = QStackedWidget()

        self.input_form_page = InputFormWidget()
        # Apply QDateEdit stylesheet after InputFormWidget is created
        self._apply_dateedit_styles(self.input_form_page)
        self.input_form_page.submit_button.clicked.connect(self._handle_submit)  # Connect here

        self.table_view_page = TableViewWidget(headers=self.csv_headers)

        self.stacked_widget.addWidget(self.input_form_page)
        self.stacked_widget.addWidget(self.table_view_page)
        self.main_layout.addWidget(self.stacked_widget)  # Stacked widget takes most space

        # --- Status Bar ---
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪", 3000)

        # Set initial view
        self.stacked_widget.setCurrentWidget(self.input_form_page)

    def _apply_dateedit_styles(self, input_form):
        date_edit_stylesheet = """
            QDateEdit {
                background-color: #FFFFFF; 
                color: #222222;            
                border: 1px solid #B0B0B0; 
                padding: 4px;              
                border-radius: 4px;        
                min-height: 22px;          
            }
            QDateEdit:focus {
                border: 1px solid #0078D7; 
                background-color: #FBFEFF; 
            }
            QDateEdit::down-button {
                background-color: #E0EAF5; 
                border: none;              
                border-left: 1px solid #B0B0B0; 
                border-top-right-radius: 3px; 
                border-bottom-right-radius: 3px;
                border-top-left-radius: 0px;    
                border-bottom-left-radius: 0px; 
                min-width: 30px;           
                padding: 0px 2px 0px 2px;  
            }
            QDateEdit::down-button:hover {
                background-color: #D0DDEC; 
            }
            QDateEdit::down-button:pressed {
                background-color: #C0D0E2; 
            }
        """
        input_form.start_date_edit.setStyleSheet(date_edit_stylesheet)
        input_form.end_date_edit.setStyleSheet(date_edit_stylesheet)

    def _init_csv(self):
        if not os.path.exists(self.csv_file):
            try:
                with open(self.csv_file, mode='w', newline='', encoding='utf-8-sig') as file:
                    writer = csv.writer(file)
                    writer.writerow(self.csv_headers)
            except IOError as e:
                QMessageBox.critical(self, "文件错误", f"无法创建CSV文件: {self.csv_file}\n{e}")

    @Slot()
    def _handle_submit(self):
        form_data = self.input_form_page.get_form_data()
        start_date = form_data["start_date"]
        end_date = form_data["end_date"]
        task = form_data["task"]
        notes = form_data["notes"]

        if not task:
            QMessageBox.warning(self, "输入错误", "任务内容为必填项，不能为空！")
            self.input_form_page.task_edit.setFocus()
            return

        if start_date > end_date:
            QMessageBox.warning(self, "日期错误", "起始日期不能晚于结束日期！")
            return

        date_str = f"{start_date.toString('yyyy/M/d')}至{end_date.toString('yyyy/M/d')}"

        try:
            with open(self.csv_file, mode='a', newline='', encoding='utf-8-sig') as file:
                writer = csv.writer(file)
                writer.writerow([date_str, task, notes])

            self.status_bar.showMessage("日志写入完成！", 3000)  # Use status bar
            QMessageBox.information(self, "成功", "日志写入完成！")  # Keep popup for explicit confirmation
            self.input_form_page.clear_fields()  # Clear fields after successful submission

        except IOError as e:
            QMessageBox.critical(self, "写入错误", f"无法写入到CSV文件: {self.csv_file}\n{e}")
        except Exception as e:
            QMessageBox.critical(self, "未知错误", f"发生意外错误: {e}")

    @Slot()
    def _load_csv_data_to_table(self):
        if not os.path.exists(self.csv_file):
            self.status_bar.showMessage(f"日志文件 {self.csv_file} 不存在或为空。", 3000)
            self.table_view_page.load_data_rows([])  # Pass empty list
            return

        data_rows = []
        try:
            with open(self.csv_file, mode='r', newline='', encoding='utf-8-sig') as file:
                reader = csv.reader(file)
                header_from_file = next(reader, None)

                if header_from_file != self.csv_headers and header_from_file is not None:
                    QMessageBox.warning(self, "文件警告", "CSV文件头与预期不符。可能无法正确显示。")
                    # self.table_view_page.set_headers(header_from_file if header_from_file else self.csv_headers)

                for row_data in reader:
                    if any(field.strip() for field in row_data):  # Skip truly empty rows
                        data_rows.append(row_data)

            self.table_view_page.load_data_rows(data_rows)
            self.status_bar.showMessage(f"已加载 {len(data_rows)} 条日志。", 3000)

        except FileNotFoundError:
            QMessageBox.warning(self, "文件错误", f"找不到文件: {self.csv_file}")
        except Exception as e:
            QMessageBox.critical(self, "读取错误", f"无法读取CSV文件: {self.csv_file}\n{e}")
            self.table_view_page.load_data_rows([])

    @Slot()
    def _toggle_view(self):
        current_index = self.stacked_widget.currentIndex()
        if current_index == 0:  # Currently on input form, switch to table view
            self._load_csv_data_to_table()
            self.stacked_widget.setCurrentIndex(1)
            self.toggle_button.setText("返回日志输入")
            self.status_bar.showMessage("切换到日志预览模式", 3000)
        else:  # Currently on table view, switch to input form
            self.stacked_widget.setCurrentIndex(0)
            self.toggle_button.setText("查看日志数据")
            self.status_bar.showMessage("切换到日志输入模式", 3000)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Optional: Set an application icon (create a 'icon.png' or similar in the same directory)
    # icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app_icon.png')
    # if os.path.exists(icon_path):
    # app.setWindowIcon(QIcon(icon_path))

    # You can try different styles: "Windows", "Fusion", "macOS" (if on macOS)
    # app.setStyle("Fusion")

    window = BlogApp()
    window.show()
    sys.exit(app.exec())