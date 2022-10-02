from collections import defaultdict
from mido import MidiFile
from pydub import AudioSegment
from pydub.generators import Sine


def note_to_freq(note, concert_A=440.0):
    return (2.0 ** ((note - 69) / 12.0)) * concert_A


mid = MidiFile("./mel5.mid")
output = AudioSegment.silent(mid.length * 1000.0)

tempo = 100  # bpm


def ticks_to_ms(ticks):
    tick_ms = (60000.0 / tempo) / mid.ticks_per_beat
    return ticks * tick_ms


for track in mid.tracks:
    # position of rendering in ms
    current_pos = 0.0

    current_notes = defaultdict(dict)
    # current_notes = {
    #   channel: {
    #     note: (start_time, message)
    #   }
    # }

    for msg in track:
        current_pos += ticks_to_ms(msg.time)

        if msg.type == 'note_on':
            current_notes[msg.channel][msg.note] = (current_pos, msg)

        if msg.type == 'note_off':
            start_pos, start_msg = current_notes[msg.channel].pop(msg.note)

            duration = current_pos - start_pos

            signal_generator = Sine(note_to_freq(msg.note))
            rendered = signal_generator.to_audio_segment(duration=duration - 50, volume=-20).fade_out(100).fade_in(30)

            output = output.overlay(rendered, start_pos)

output.export("mid_wav5.wav", format="wav")