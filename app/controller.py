import os
import subprocess
import logging
from pydub import AudioSegment
import speech_recognition as sr
import json


class FFmpegError(Exception):
    """Exception raised for errors in the FFmpeg command."""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class TranscriptionController:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def convert_mp4_to_wave(self, input_file: str, output_file: str):
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

    # No controller.py
    def transcribe_audio_by_parts(self, wave_file: str, socketio):
        """
        Transcreve um arquivo WAV para texto, enviando o progresso para o front-end.
        """
        recognizer = sr.Recognizer()
        audio = AudioSegment.from_wav(wave_file)
        passo = 10 * 1000  # Intervalos de 10 segundos
        sobreposicao = 2 * 1000  # Sobreposição de 1 segundo
        transcript = ""
        
        total_segments = (len(audio) + passo - 1) // passo  # Calcula quantas partes existem no áudio

        for i in range(0, len(audio), passo):
            segmento = audio[i:i + passo + sobreposicao]
            segmento.export(wave_file, format="wav")
            
            with sr.AudioFile(wave_file) as source:
                audio_data = recognizer.record(source)
                try:
                    transcricao = recognizer.recognize_google(audio_data, language='pt-BR')
                    transcript += f"{transcricao}\n"
                except sr.UnknownValueError:
                    continue

            # Calcula o progresso e envia para o Socket.IO
            progress = (i // passo) * 100 // total_segments
            socketio.emit('progress', {'step': 'transcription', 'progress': progress, 'message': f'Transcrevendo {progress} %'})

        # Retorna o texto completo
        return transcript
