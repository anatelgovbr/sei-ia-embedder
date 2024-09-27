FROM python:3.10-slim

LABEL MAINTAINER="MATHEUS GYSI"

WORKDIR /app

ARG GIT_TOKEN
ENV GIT_TOKEN=$GIT_TOKEN
# Criação do script askpass.sh no diretório raiz para que todas as autorizacoes do git sejam feitas com o token
RUN echo "#!/bin/sh" > /askpass.sh && \
    echo "echo \$GIT_TOKEN" >> /askpass.sh && \
    chmod +x /askpass.sh
ENV GIT_ASKPASS="/askpass.sh"

RUN mkdir -p /app/logs
RUN apt-get update \
    && apt-get install -y \
        uvicorn g++ build-essential libpoppler-cpp-dev pkg-config git curl gnupg lsb-release \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg
RUN curl https://packages.microsoft.com/config/debian/12/prod.list | tee /etc/apt/sources.list.d/mssql-release.list

# Atualizando PATH
ENV PATH="$PATH:/opt/mssql-tools18/bin"

# Optional: for unixODBC development headers
RUN apt-get update && apt-get install -y unixodbc-dev && ACCEPT_EULA=Y apt-get install -y msodbcsql18

RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

COPY ./pyproject.toml /app/pyproject.toml
RUN pip install . --no-cache-dir
RUN pip install pyodbc 
COPY . /app

EXPOSE 8088

CMD ["sleep", "infinity"]