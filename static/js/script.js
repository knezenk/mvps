document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('uploadForm');
    const submitBtn = document.getElementById('submitBtn');
    const fileInput = document.getElementById('fileInput');
    const progressSection = document.getElementById('progressSection');
    const resultSection = document.getElementById('resultSection');
    const resetBtn = document.getElementById('resetBtn');

    const uploadProgressBar = document.getElementById('uploadProgressBar');
    const uploadProgressMessage = document.getElementById('uploadProgressMessage');
    const conversionProgressBar = document.getElementById('conversionProgressBar');
    const conversionProgressMessage = document.getElementById('conversionProgressMessage');
    const transcriptionProgressBar = document.getElementById('transcriptionProgressBar');
    const transcriptionProgressMessage = document.getElementById('transcriptionProgressMessage');
    const transcriptionResult = document.getElementById('transcriptionResult');

    const socket = io.connect('http://' + document.domain + ':' + location.port);

    form.onsubmit = function (e) {
        e.preventDefault();

        // Desabilitar o botão durante o processo
        submitBtn.disabled = true;

        // Limpar os campos de progresso e transcrição
        progressSection.style.display = 'block';
        resultSection.style.display = 'none';
        resetFields();

        const formData = new FormData(form);  // Garantindo que estamos enviando o arquivo
        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                console.log(data.message);
            } else if (data.error) {
                console.error(data.error);
                submitBtn.disabled = false; // Habilitar botão novamente
            }
        })
        .catch(error => {
            console.error('Erro ao enviar arquivo:', error);
            submitBtn.disabled = false; // Habilitar botão novamente
        });
    };

    // Atualizar o progresso
    socket.on('progress', function (data) {
        if (data.step === 'upload') {
            uploadProgressBar.value = data.progress;
            uploadProgressMessage.textContent = data.message;
        } else if (data.step === 'conversion') {
            conversionProgressBar.value = data.progress;
            conversionProgressMessage.textContent = data.message;
        } else if (data.step === 'transcription') {
            transcriptionProgressBar.value = data.progress;
            transcriptionProgressMessage.textContent = data.message;
        } else if (data.step === 'error') {
            alert('Erro: ' + data.message);
            submitBtn.disabled = false; // Habilitar botão novamente em caso de erro
        }
    });

    // Exibir transcrição
    socket.on('transcription_result', function (data) {
        transcriptionResult.value = data.text;
        resultSection.style.display = 'block';
        submitBtn.disabled = false; // Habilitar botão após o processamento
    });

    // Resetar campos
    resetBtn.addEventListener('click', function () {
        fileInput.value = '';
        transcriptionResult.value = '';
        progressSection.style.display = 'none';
        resultSection.style.display = 'none';
    });

    function resetFields() {
        uploadProgressBar.value = 0;
        uploadProgressMessage.textContent = '';
        conversionProgressBar.value = 0;
        conversionProgressMessage.textContent = '';
        transcriptionProgressBar.value = 0;
        transcriptionProgressMessage.textContent = '';
    }
});
