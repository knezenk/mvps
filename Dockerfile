# Use uma imagem base oficial do Python
FROM python:3.10-slim

# Defina o diretório de trabalho dentro do container
WORKDIR /app

# Instale as dependências do sistema, incluindo o ffmpeg
RUN apt-get update && apt-get install -y \
    ffmpeg \
    tzdata \
	locales \
    && rm -rf /var/lib/apt/lists/*

RUN locale-gen pt_BR.UTF-8 && locale-gen en_US.UTF-8 && update-locale

# Define o fuso horário para São Paulo (Horário de Brasília)
ENV TZ=America/Sao_Paulo

# Reconfigura o fuso horário sem interação
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Copie o arquivo requirements.txt para o diretório de trabalho
COPY requirements.txt .

# Instale as dependências necessárias
RUN pip install --no-cache-dir -r requirements.txt

# Copie todos os arquivos do projeto para o diretório de trabalho do container
COPY . .

# Exponha a porta na qual a aplicação irá rodar (opcional, ajuste conforme necessário)
# EXPOSE 5151

# Comando para rodar sua aplicação (ajuste conforme necessário)
CMD ["python", "app/app.py"]
