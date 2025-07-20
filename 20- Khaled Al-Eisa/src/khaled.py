# from tqdm import tqdm
import os
import cv2
import torch
import torchaudio
import numpy as np
from gtts import gTTS
from pydub import AudioSegment
from pydub.utils import mediainfo
from transformers import MarianMTModel, MarianTokenizer, Wav2Vec2Processor, Wav2Vec2Model
import whisper
import face_alignment
from moviepy.editor import VideoFileClip, AudioFileClip

class VideoDubbingSystem:
    def __init__(self):
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.face_aligner = face_alignment.FaceAlignment(
            face_alignment.LandmarksType.TWO_D, device=self.device
        )
        self.speech_model = whisper.load_model("medium", device=self.device)
        self.audio_processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base-960h")
        self.audio_model = Wav2Vec2Model.from_pretrained("facebook/wav2vec2-base-960h").to(self.device)

    def extract_audio(self, video_path, audio_output="temp_audio.wav"):
        video = VideoFileClip(video_path)
        video.audio.write_audiofile(audio_output)
        return audio_output

    def speech_to_text(self, audio_path):
        result = self.speech_model.transcribe(audio_path)
        return result["text"], result["segments"]

    def translate_text(self, text, source_lang="en", target_lang="ar"):
        model_name = f'Helsinki-NLP/opus-mt-{source_lang}-{target_lang}'
        tokenizer = MarianTokenizer.from_pretrained(model_name)
        model = MarianMTModel.from_pretrained(model_name)

        sentences = text.split('.')
        translated_sentences = []
        for sent in sentences:
            if sent.strip():
                inputs = tokenizer(sent, return_tensors="pt", truncation=True)
                outputs = model.generate(**inputs)
                translated = tokenizer.decode(outputs[0], skip_special_tokens=True)
                translated_sentences.append(translated)
        return ' '.join(translated_sentences)

    def text_to_speech(self, text, output_file="translated_audio.wav", lang="ar"):
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save("temp.mp3")
        audio = AudioSegment.from_mp3("temp.mp3")
        audio.export(output_file, format="wav")
        os.remove("temp.mp3")
        return output_file

    def extract_face_frames(self, video_path):
        cap = cv2.VideoCapture(video_path)
        frames = []

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        print(f"frames in the video: {total_frames}")
        i=0
        while cap.isOpened():
            i=i+1
            print("The frame",i)
            ret, frame = cap.read()
            if not ret:
                break

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            preds = self.face_aligner.get_landmarks(rgb)
            if preds is not None:
                landmarks = preds[0]
                lip_points = landmarks[48:68]
                frames.append((frame, lip_points))

        cap.release()
        return frames

    def audio_to_lip_movement(self, audio_path):
        waveform, sample_rate = torchaudio.load(audio_path)
        if waveform.shape[0] > 1:
            waveform = waveform.mean(dim=0, keepdim=True)
        if sample_rate != 16000:
            resampler = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=16000)
            waveform = resampler(waveform)
        waveform = waveform.squeeze(0)
        inputs = self.audio_processor(waveform, return_tensors="pt", sampling_rate=16000)
        input_values = inputs["input_values"].to(self.device)

        with torch.no_grad():
            outputs = self.audio_model(input_values=input_values)
        return outputs.last_hidden_state

    def downsample_features(self, features, target_len):
        features = features.squeeze(0)
        seq_len = features.shape[0]
        if target_len >= seq_len:
            indices = np.linspace(0, seq_len - 1, target_len).astype(int)
        else:
            step = seq_len // target_len
            indices = np.arange(0, step * target_len, step)
        return features[indices].cpu().numpy()

    def apply_lip_sync(self, frames, lip_movements, audio_duration, output_path="output_video.mp4"):
        if len(frames) == 0:
            raise ValueError("No frames found")

       
        new_fps = len(frames) / audio_duration
        print(f"new frames: {new_fps:.2f} fps")

        h, w = frames[0][0].shape[:2]
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, new_fps, (w, h))

        for i, (frame, lip_points) in enumerate(frames):
            if i >= lip_movements.shape[0]:
                break

            lip_points = np.array(lip_points)
            if lip_movements.shape[1] >= 40:
                movement = lip_movements[i, :40].reshape(-1, 2)
            else:
                raise ValueError(f"lip_movements does not have enough features: {lip_movements.shape[1]} < 40")

            new_lip_points = lip_points + movement * 0.5
            for point in new_lip_points:
                cv2.circle(frame, tuple(point.astype(int)), 2, (0, 255, 0), -1)

            out.write(frame)

        out.release()
        return output_path

    def dub_video(self, video_path, source_lang="en", target_lang="ar"):
        #رح احفظ الصوت الاصلي بملف بالمشروع للاستخدامات اللاحقة
        audio_path = self.extract_audio(video_path)
        print("Extract text from video ============================================")
        original_text, _ = self.speech_to_text(audio_path)
        print("Original text:", original_text)

        print("translation=================================")
        translated_text = self.translate_text(original_text, source_lang, target_lang)
        print("translation text :", translated_text)

        print("new text to sound ====================================")
        print("Saved in translated_audio.wav")
        translated_audio = self.text_to_speech(translated_text, lang=target_lang)

        info = mediainfo(translated_audio)
        audio_duration = float(info['duration'])
        raw_movements = self.audio_to_lip_movement(translated_audio)
        frames = self.extract_face_frames(video_path)
        lip_movements = self.downsample_features(raw_movements, len(frames))
        output_video = self.apply_lip_sync(frames, lip_movements, audio_duration)
        final_output = "final_output.mp4"
        video_clip = VideoFileClip(output_video)
        audio_clip = AudioFileClip(translated_audio)
        final_clip = video_clip.set_audio(audio_clip)
        final_clip.write_videofile(final_output, codec="libx264")

        print(f"The video has been saved in: {final_output}")
        return final_clip


if __name__ == "__main__":
    dubbing_system = VideoDubbingSystem()
    #البارمتر الاول اسم الفيديو بحيث يكون بنفس المجلد
    #بارمتر الثاني اللغة الحالية 
    #بارمتر الثالث اللغة الهدف في هذا المشروع تم تجربة اللغة الفرنسية والعربية
    dubbing_system.dub_video("input_video.mp4", "en", "fr")
