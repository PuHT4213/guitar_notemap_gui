import itertools
import streamlit as st
import pandas as pd

class Guitar:
    NOTES = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]
    NOTE_TO_NUM = {note: + 1 for i, note in enumerate(NOTES)}
    NUM_TO_NOTE = {i: note for i, note in enumerate(NOTES)}

    # Standard tuning: E4 B3 G3 D3 A2 E2
    STRING_TUNINGS = ["E", "B", "G", "D", "A", "E"]

    def __init__(self, max_fret=14):
        self.max_fret = max_fret
        self.strings = self._initialize_strings()

    def _initialize_strings(self):
        strings = {}
        for i, note in enumerate(self.STRING_TUNINGS, start=1):
            start_idx = self.NOTES.index(note)
            frets = [(self.NOTES[(start_idx + f) % 12]) for f in range(self.max_fret + 1)]
            strings[i] = frets
        return strings

    def get_note(self, string: int, fret: int) -> str:
        return self.strings[string][fret]

    def get_scale(self, note: str):
        positions = []
        for string, frets in self.strings.items():
            for fret, fret_note in enumerate(frets):
                if fret_note == note:
                    positions.append((string, fret))
        return positions

    def get_chord(self, chord_name: str):
        note, chord_type = chord_name[:-1], chord_name[-1]
        if chord_type == 'M':  # major triad
            intervals = [0, 4, 7]
        elif chord_type == 'm':  # minor triad
            intervals = [0, 3, 7]
        elif chord_type == '+':  # augmented
            intervals = [0, 4, 8]
        elif chord_type == '-':  # diminished
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
        return self.strings

# ---- Streamlit UI ----
guitar = Guitar()

st.title("Guitar Fretboard Visualizer")

view_mode = st.radio("显示模式：", ["音符", "数字"], horizontal=True)
fretboard = guitar.get_fretboard()

highlight_note = st.selectbox("选择音符高亮：", [None] + Guitar.NOTES)
highlight_chord = st.selectbox("选择和弦高亮（C, D, E... + M/m/+/-）:", [None] + [n + t for n, t in itertools.product(Guitar.NOTES, ['M', 'm', '+', '-'])])

highlight_positions = set()
if highlight_note:
    highlight_positions.update(guitar.get_scale(highlight_note))
elif highlight_chord:
    highlight_positions.update(guitar.get_chord(highlight_chord))

fretboard_df = pd.DataFrame.from_dict(fretboard, orient='index')
if view_mode == "数字":
    fretboard_df = fretboard_df.applymap(lambda note: Guitar.NOTE_TO_NUM[note])

st.markdown("### 吉他指板：")
def highlight_func(val, row, col):
    return 'background-color: yellow' if (row + 1, col) in highlight_positions else ''

styled_df = fretboard_df.style.apply(lambda row: [highlight_func(val, row.name, col) for col, val in enumerate(row)], axis=1)
st.dataframe(styled_df, use_container_width=True)