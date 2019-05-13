
from subtitles import Subtitles
from subtitle import Subtitle
import speech_recognition

class SpeechToText:

    def __init__(self):
        pass


recognizer = speech_recognition.Recognizer()
audio_file = speech_recognition.AudioFile("asset/audio.wav")

fragments = []

duration = 1.
offset = 25 * 60 + 10

with audio_file as source:
    for i in range(50):
        fragments.append(recognizer.record(
            source,
            offset=offset,
            duration=duration)
        )
        offset = 0

cursor = (25 * 60 + 10)

subs = Subtitles()
sub_id = 1
for fragment in fragments:
    try:
        text = recognizer.recognize_google(fragment)
        sub = Subtitle()
        sub.id = sub_id
        sub_id += 1
        sub.start += 1000 * cursor
        sub.stop += 1000 * (cursor + duration)
        sub.text = text
        subs.add(sub)
    except speech_recognition.UnknownValueError:
        pass
    cursor += duration
subs.save("out.srt")
