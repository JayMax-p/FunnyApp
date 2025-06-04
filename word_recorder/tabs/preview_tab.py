# word_recorder/tabs/preview_tab.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableView, QHeaderView, QAbstractItemView
from models.word_list_model import WordListModel # 确保路径正确

class PreviewTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10,10,10,10)

        self.table_view = QTableView(self)
        layout.addWidget(self.table_view)

        # 设置表格属性
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows) # 整行选择
        self.table_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers) # 不可编辑
        self.table_view.horizontalHeader().setStretchLastSection(True) # 最后一列自动拉伸填充
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive) #列宽可拖动
        self.table_view.setAlternatingRowColors(True) # 奇偶行不同背景色，QSS可以覆盖

        # 应用 "pandas-like" 风格（主要通过QSS实现，这里是基本设置）
        # 具体的QSS规则将在主窗口加载时应用到整个应用程序

    def set_model(self, model: WordListModel):
        self.table_view.setModel(model)
        # 可以根据模型内容调整列宽，但通常QSS或默认行为已经足够
        # self.table_view.resizeColumnsToContents()
        # self.table_view.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)

    def refresh_view(self):
        """如果模型内部数据变化但结构不变，可以尝试layoutChanged"""
        if self.table_view.model():
            self.table_view.model().layoutChanged.emit()
