"""Sustain the encounter's build until the dragon takes over.

The original opening plays once, then this developed minor section holds
the momentum through variable-length dialogue. No return to the sparse
desert intro, and no quiet cadence just before the boss cue.
"""
from data.music import desert_trio as theme
from src.audio.sequencer import Note, Track

TEMPO_BPM = theme.TEMPO_BPM
BEATS_PER_BAR = theme.BEATS_PER_BAR
TOTAL_BARS = 16
TOTAL_BEATS = TOTAL_BARS * BEATS_PER_BAR
MASTER_HEADROOM = theme.MASTER_HEADROOM


def build_tracks():
    offset = 16 * BEATS_PER_BAR
    tracks = []
    for track in theme.build_tracks():
        notes = [note._replace(beat=note.beat - offset)
                 for note in track.notes if note.beat >= offset]
        if track.name == "brass":
            # Carry the hook through the final four bars instead of yielding
            # to the reed's descending, quieter answer.
            notes.extend(note._replace(beat=note.beat + 16)
                         for note in list(notes) if 32 <= note.beat < 48)
        if track.name == "timp":
            for bar in range(TOTAL_BARS):
                if bar % 2:
                    root = theme._ROOTS[bar + 16]
                    notes.append(Note(bar * 4, .7, root, .50))
        if track.name == "snare":
            for bar in (7, 15):
                notes.extend(Note(bar * 4 + beat, .10, "C3", velocity)
                             for beat, velocity in ((3.5, .60), (3.75, .72)))
        tracks.append(Track(track.name, track.instrument, track.level, notes))
    return tracks
