# word_recorder/core/data_manager.py
import pandas as pd
import os
from typing import Tuple, Optional

class DataManager:
    def __init__(self):
        self.dataframe: Optional[pd.DataFrame] = None
        self.filepath: Optional[str] = None
        self.is_dirty: bool = False # 标记是否有未保存的更改
        self._columns = ["单词", "释义"]

    def create_new_list(self):
        """创建一个新的空词表"""
        self.dataframe = pd.DataFrame(columns=self._columns)
        self.filepath = None # 新列表尚未保存，没有路径
        self.is_dirty = False # 新创建的空列表是干净的，但一旦命名或添加内容就变脏
        return True

    def load_csv(self, file_path: str) -> Tuple[bool, str]:
        """
        从CSV文件加载词表。
        返回: (是否成功, 消息)
        """
        try:
            if not os.path.exists(file_path):
                return False, "文件不存在。"

            # 尝试读取CSV，不指定header，稍后检查
            try:
                df = pd.read_csv(file_path, dtype=str, header=None, keep_default_na=False, skip_blank_lines=True)
            except pd.errors.EmptyDataError: # CSV文件为空
                df = pd.DataFrame(columns=self._columns) # 创建一个空的带列名的DataFrame
                # 这种情况可以认为是成功的加载了一个空表，然后保存时会写入列名
                self.dataframe = df
                self.filepath = file_path
                self.is_dirty = False #刚加载，认为是干净的，但如果后续自动添加了列名并打算保存，则应标记为dirty
                # 如果文件是空的，我们创建一个带列名的空表，并标记为dirty，以便首次保存时写入列名
                if df.empty:
                    self.is_dirty = True # 空文件加载后，我们希望保存时能写入列名
                return True, "成功加载空的词表。首次保存时将添加列名。"
            except Exception as e:
                return False, f"读取CSV文件失败: {e}"


            message = "词表加载成功。"
            # 检查列数
            if df.shape[1] != len(self._columns):
                return False, f"文件格式错误：应包含 {len(self._columns)} 列数据。"

            # 检查表头
            if list(df.iloc[0]) == self._columns:
                df = pd.read_csv(file_path, dtype=str, keep_default_na=False, skip_blank_lines=True) # 用第一行做表头重新读取
            else:
                # 没有表头，或者表头不匹配，将当前数据视为内容，并指定列名
                df.columns = self._columns
                message = "词表加载成功。文件缺少标准表头，已按默认格式加载。保存时将添加标准表头。"
                self.is_dirty = True # 因为我们修改了数据的表示（添加了列名）

            self.dataframe = df.fillna('') #确保没有NaN，而是空字符串
            self.filepath = file_path
            if not self.is_dirty: #如果上面没有因为表头问题标记为dirty
                 self.is_dirty = False
            return True, message

        except Exception as e:
            self.dataframe = None
            self.filepath = None
            return False, f"加载词表时发生错误: {e}"

    def save_csv(self, file_path: Optional[str] = None) -> Tuple[bool, str]:
        """
        保存当前词表到CSV文件。
        如果提供了 file_path，则“另存为”到该路径。
        否则，保存到 self.filepath。
        返回: (是否成功, 消息)
        """
        if self.dataframe is None:
            return False, "没有可保存的词表数据。"

        save_path = file_path if file_path else self.filepath

        if not save_path:
            return False, "未指定保存路径。"

        try:
            # 确保 DataFrame 有正确的列名
            if list(self.dataframe.columns) != self._columns:
                 self.dataframe.columns = self._columns # 以防万一
            self.dataframe.to_csv(save_path, index=False, encoding='utf-8')
            self.filepath = save_path # 更新当前文件路径
            self.is_dirty = False
            return True, f"词表已成功保存到: {os.path.basename(save_path)}"
        except Exception as e:
            return False, f"保存词表失败: {e}"

    def add_word(self, word: str, definition: str) -> bool:
        """向词表中添加单词和释义"""
        if self.dataframe is None:
            # 如果还没有DataFrame（例如，程序刚启动，用户还没新建或打开）
            # 理论上UI层应该先确保有一个活动的DataFrame
            self.create_new_list() # 或者返回错误，由UI处理

        if not word: # 单词不能为空
            return False

        new_row = pd.DataFrame([{self._columns[0]: word, self._columns[1]: definition}])
        self.dataframe = pd.concat([self.dataframe, new_row], ignore_index=True)
        self.is_dirty = True
        return True

    def get_random_word(self) -> Optional[Tuple[str, str]]:
        """从词表中随机获取一个单词及其释义"""
        if self.dataframe is not None and not self.dataframe.empty:
            sample = self.dataframe.sample(1)
            return sample.iloc[0][self._columns[0]], sample.iloc[0][self._columns[1]]
        return None

    def get_word_count(self) -> int:
        """获取当前词表中的单词数量"""
        if self.dataframe is not None:
            return len(self.dataframe)
        return 0

    def get_data(self) -> Optional[pd.DataFrame]:
        """获取整个DataFrame"""
        return self.dataframe

    def get_current_filename(self) -> str:
        if self.filepath:
            return os.path.basename(self.filepath)
        return "未命名"
