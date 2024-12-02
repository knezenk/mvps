from flask import Flask, request, jsonify
import os
import logging
from werkzeug.utils import secure_filename
from app.controller import TranscriptionController, FFmpegError

# Configuração do Flask
app = Flask(__name__)
UPLOAD_FOLDER = "./uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Configuração do logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Instância do Controller
controller = TranscriptionController()


@app.route('/transcribe', methods=['POST'])
def transcribe():
    """
    Rota para processar e transcrever um arquivo enviado.
    """
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado.'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Nome de arquivo vazio.'}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    try:
        # Convertendo para WAV
        wav_filepath = filepath.rsplit('.', 1)[0] + '.wav'
        controller.convert_mp4_to_wave(filepath, wav_filepath)

        # Transcrevendo o áudio
        transcript = controller.transcribe_audio(wav_filepath)
        os.remove(wav_filepath)

        # Retornando o texto transcrito
        return jsonify({'text': transcript}), 200
    except FFmpegError as e:
        logger.error(f"Erro no FFmpeg: {e}")
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        logger.error(f"Erro ao processar o arquivo: {e}")
        return jsonify({'error': 'Erro ao processar o arquivo.'}), 500
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5151, debug=True)
