import os
import threading
from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO
from controller import TranscriptionController, FFmpegError
import logging

app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.config['UPLOAD_FOLDER'] = './uploads'
app.config['WAVE_FOLDER'] = './wave'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['WAVE_FOLDER'], exist_ok=True)

socketio = SocketIO(app, cors_allowed_origins="*")

controller = TranscriptionController()

@app.route('/')
def index():
    return render_template('index.html')  # Renderiza o template index.html

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files.get('file')
    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        wave_path = os.path.join(app.config['WAVE_FOLDER'], os.path.splitext(file.filename)[0] + ".wav")
        
        # Salva o arquivo de upload
        file.save(file_path)
        
        # Inicia o processamento do arquivo em uma thread separada
        threading.Thread(target=process_file, args=(file_path, wave_path, socketio)).start()
        
        return jsonify({"message": "Arquivo enviado e processamento iniciado"})
    
    return jsonify({"error": "Nenhum arquivo enviado"}), 400


def process_file(input_file, wave_file, socketio):
    try:
        # Etapa 1: Upload concluído
        socketio.emit('progress', {'step': 'upload', 'progress': 100, 'message': 'Upload concluído!'})

        # Etapa 2: Conversão
        socketio.emit('progress', {'step': 'conversion', 'progress': 0, 'message': 'Iniciando conversão...'})
        controller.convert_mp4_to_wave(input_file, wave_file)
        socketio.emit('progress', {'step': 'conversion', 'progress': 100, 'message': 'Conversão concluída!'})

        # Etapa 3: Transcrição
        socketio.emit('progress', {'step': 'transcription', 'progress': 0, 'message': 'Iniciando transcrição...'})
        transcript = controller.transcribe_audio_by_parts(wave_file, socketio)

        # Transcrição concluída, envia o resultado
        socketio.emit('progress', {'step': 'transcription', 'progress': 100, 'message': 'Transcrição concluída!'})
        socketio.emit('transcription_result', {'text': transcript})
    except FFmpegError as e:
        socketio.emit('progress', {'step': 'error', 'progress': 100, 'message': f'Erro na conversão: {str(e)}'})
    except Exception as e:
        logging.error(f"Erro durante o processamento: {e}")
        socketio.emit('progress', {'step': 'error', 'progress': 100, 'message': f'Erro: {str(e)}'})

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=1066, debug=True, allow_unsafe_werkzeug=True)
