# word_recorder/models/word_list_model.py
from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex
from PySide6.QtGui import QColor
import pandas as pd
from typing import Any, Optional


class WordListModel(QAbstractTableModel):
    def __init__(self, data: Optional[pd.DataFrame] = None, parent=None):
        super().__init__(parent)
        self._data = data if data is not None else pd.DataFrame(columns=["单词", "释义"])
        self._display_column_name = "词条"  # 单列显示的表头

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid() or self._data is None:
            return 0
        return len(self._data)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid() or self._data is None:
            return 0
        return 1  # 我们只显示一列："单词：释义"

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if not index.isValid() or self._data is None:
            return None

        row = index.row()
        # col = index.column() # col is always 0

        if role == Qt.ItemDataRole.DisplayRole:
            try:
                word = str(self._data.iloc[row, 0])  # "单词"列
                definition = str(self._data.iloc[row, 1])  # "释义"列
                return f"{word}：{definition}"
            except IndexError:
                return None  # 数据可能不完整

        # Pandas-like alternating row colors (optional, can also be done via QSS on QTableView)
        # if role == Qt.ItemDataRole.BackgroundRole:
        #     return QColor(Qt.GlobalColor.lightGray) if row % 2 == 0 else QColor(Qt.GlobalColor.white)

        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                if section == 0:
                    return self._display_column_name
            # Можно добавить и вертикальные заголовки (номера строк), если нужно
            # if orientation == Qt.Orientation.Vertical:
            #     return str(section + 1)
        return None

    def set_data(self, data: Optional[pd.DataFrame]):
        """更新模型数据并刷新视图"""
        self.beginResetModel()
        self._data = data if data is not None else pd.DataFrame(columns=["单词", "释义"])
        self.endResetModel()

    def get_underlying_data(self) -> Optional[pd.DataFrame]:
        """获取内部的DataFrame对象"""
        return self._data
