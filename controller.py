import os
import subprocess
import logging
from pydub import AudioSegment
import speech_recognition as sr


class FFmpegError(Exception):
    """Exception raised for errors in the FFmpeg command."""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class TranscriptionController:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def convert_mp4_to_wave(self, input_file: str, output_file: str):
        """
        Converte um arquivo MP4 para WAV usando FFmpeg.
        """
        if os.path.exists(output_file):
            os.remove(output_file)

        command = [
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-i", input_file, "-acodec", "pcm_s16le", "-ac", "1", "-ar", "16000", output_file
        ]

        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        _, stderr = process.communicate()

        if process.returncode != 0:
            raise FFmpegError(f"FFmpeg Error occurred: {stderr.decode('utf-8')}")
        return True

    def transcribe_audio(self, wave_file: str):
        """
        Transcreve um arquivo WAV para texto usando Google Speech Recognition.
        """
        recognizer = sr.Recognizer()
        audio = AudioSegment.from_wav(wave_file)
        passo = 10 * 1000  # Intervalos de 10 segundos
        sobreposicao = 1 * 1000  # Sobreposição de 1 segundo
        transcript = ""

        for i in range(0, len(audio), passo):
            segmento = audio[i:i+passo+sobreposicao]
            segmento.export(wave_file, format="wav")
            with sr.AudioFile(wave_file) as source:
                audio_data = recognizer.record(source)
                try:
                    transcricao = recognizer.recognize_google(audio_data, language='pt-BR')
                    transcript += f"{transcricao}\n"
                except sr.UnknownValueError:
                    continue

        return transcript
