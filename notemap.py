import itertools
import streamlit as st
import pandas as pd

class Guitar:
    # 定义音阶，编号从 0 到 11
    NOTES = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]
    # 音符到编号的映射（编号从 0 开始）
    NOTE_TO_NUM = {note: i for i, note in enumerate(NOTES)}
    NUM_TO_NOTE = {i: note for i, note in enumerate(NOTES)}

    # 标准调音：E B G D A E
    STRING_TUNINGS = ["E", "B", "G", "D", "A", "E"]

    def __init__(self, max_fret=14):
        self.max_fret = max_fret
        self.strings = self._initialize_strings()

    def _initialize_strings(self):
        strings = {}
        for i, note in enumerate(self.STRING_TUNINGS, start=1):
            start_idx = self.NOTES.index(note)
            # 每根弦上从0品到max_fret的音符依次加1（模12循环）
            frets = [self.NOTES[(start_idx + f) % 12] for f in range(self.max_fret + 1)]
            strings[i] = frets
        return strings

    def get_note(self, string: int, fret: int) -> str:
        """返回指定弦号和品号的音符"""
        return self.strings[string][fret]

    def get_scale(self, note: str):
        """返回指定音符在吉他上的所有位置（弦号, 品号）"""
        positions = []
        for string, frets in self.strings.items():
            for fret, fret_note in enumerate(frets):
                if fret_note == note:
                    positions.append((string, fret))
        return positions

    def get_chord(self, chord_name: str):
        """
        返回指定和弦在吉他上的所有位置（弦号, 品号）。
        和弦名称格式为：根音后跟一个标识，
        'M' 表示大调（三和弦），'m' 表示小调，
        '+' 表示增和弦，'-' 表示减和弦。
        """
        # 假设和弦名称至少两位，前面的部分为根音，最后一位为和弦类型
        note, chord_type = chord_name[:-1], chord_name[-1]
        if chord_type == 'M':  # 大调三和弦（根音、纯四度、纯五度即0,4,7半音）
            intervals = [0, 4, 7]
        elif chord_type == 'm':  # 小调三和弦（根音、降三度、纯五度即0,3,7半音）
            intervals = [0, 3, 7]
        elif chord_type == '+':  # 增和弦（根音、纯四度、增五度即0,4,8半音）
            intervals = [0, 4, 8]
        elif chord_type == '-':  # 减和弦（根音、降三度、降五度即0,3,6半音）
            intervals = [0, 3, 6]
        else:
            return []

        root_idx = self.NOTES.index(note)
        chord_notes = [self.NOTES[(root_idx + interval) % 12] for interval in intervals]

        positions = []
        for string, frets in self.strings.items():
            for fret, fret_note in enumerate(frets):
                if fret_note in chord_notes:
                    positions.append((string, fret))
        return positions

    def get_fretboard(self):
        """返回所有弦上的音符信息，键为弦号，值为该弦上的音符列表"""
        return self.strings

# ---- Streamlit UI ----
guitar = Guitar()

# st.title("Guitar Fretboard Visualizer")

# 设置页面宽度
st.set_page_config(page_title="Guitar Fretboard Visualizer", layout="wide")

# 选择显示模式：音符或数字（对应音符编号0-11）
view_mode = st.radio("显示模式：", ["音符", "数字"], horizontal=True)
fretboard = guitar.get_fretboard()

# 下拉选择用于高亮的音符（音符名称）以及和弦（格式如 C M, D m, ...）
highlight_note = st.selectbox("选择音符高亮：", [None] + Guitar.NOTES)
highlight_chord = st.selectbox("选择和弦高亮（例如 C M, D m, E+, F-）：", [None] + [n + t for n, t in itertools.product(Guitar.NOTES, ['M', 'm', '+', '-'])])

highlight_positions = set()
if highlight_note:
    highlight_positions.update(guitar.get_scale(highlight_note))
elif highlight_chord:
    highlight_positions.update(guitar.get_chord(highlight_chord))

# 将指板数据构造成DataFrame，行表示弦（1到6），列表示品位(0到max_fret)
fretboard_df = pd.DataFrame.from_dict(fretboard, orient='index')
if view_mode == "数字":
    fretboard_df = fretboard_df.applymap(lambda note: Guitar.NOTE_TO_NUM[note])

st.markdown("### 吉他指板：")
def highlight_func(val, row, col):
    """高亮显示选定的音符或和弦位置"""
    return 'background-color: yellow' if (row, col) in highlight_positions else ''

styled_df = fretboard_df.style.apply(lambda row: [highlight_func(val, row.name, col) for col, val in enumerate(row)], axis=1)
st.dataframe(styled_df, use_container_width=True)
