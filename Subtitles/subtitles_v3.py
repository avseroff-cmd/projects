import moviepy.editor as mp
import assemblyai as aai
from PIL import Image, ImageDraw, ImageFont
import numpy as np

class SubtitleGenerator:
    def __init__(self, video_file):
        self.video_file = video_file
        self.audio_file = "audio.wav"
        self.output_file = "output.mp4"
        self.video = mp.VideoFileClip(self.video_file)

    def extract_audio(self):
        audio_clip = self.video.audio
        audio_clip.write_audiofile(self.audio_file)

    def transcribe_audio(self):
        aai.settings.api_key = "236120c131074659bb0e2dd636a4142c"
        transcriber = aai.Transcriber()
        config = aai.TranscriptionConfig(language_code="ru")
        transcript = transcriber.transcribe(self.audio_file, config)
        subtitles = transcript.export_subtitles_srt(chars_per_caption=20)
        return subtitles

    def draw_text(self, text, font_size=70):
        img = Image.new('RGBA', (int(self.video.w * 0.8), int(self.video.h * 0.1)), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype("arial.ttf", font_size)
        draw.text((10, 0), text, font=font, fill=(255, 255, 255), stroke_width=4, stroke_fill=(0, 0, 0))
        img = np.array(img)
        return img

    def add_subtitles_to_video(self, subtitles):
        clips = [self.video]
        for subtitle in subtitles.split("\n\n"):
            parts = subtitle.split("\n")
            if len(parts) < 2:
                print(f"Skipping subtitle: {subtitle}")
                continue
            start_time, end_time = parts[1].split(" --> ")
            start_time = self.parse_time(start_time)
            end_time = self.parse_time(end_time)
            text = "\n".join(parts[2:])
            img = self.draw_text(text)
            txt_clip = mp.ImageClip(img).set_position('center').set_duration(end_time - start_time).set_start(start_time)
            clips.append(txt_clip)
        final_video = mp.CompositeVideoClip(clips)
        final_video.write_videofile(self.output_file)

    def parse_time(self, time_str):
        h, m, s = time_str.split(":")
        s, ms = s.split(",")
        return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000

    def generate_subtitled_video(self):
        self.extract_audio()
        subtitles = self.transcribe_audio()
        self.add_subtitles_to_video(subtitles)

if __name__ == "__main__":
    video_file = 'input.mp4'
    generator = SubtitleGenerator(video_file)
    generator.generate_subtitled_video()
