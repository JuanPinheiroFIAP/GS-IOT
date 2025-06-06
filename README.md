
---

# Sistema de Segurança com Detecção de Movimento em Ambiente Escuro

## Descrição do problema

Em ambientes com baixa luminosidade, a segurança é um desafio maior, pois a detecção visual fica prejudicada. Sistemas tradicionais de monitoramento podem não identificar situações de risco em tempo real, especialmente quando o ambiente está escuro. O objetivo deste projeto é desenvolver um sistema que, mesmo com pouca luz, consiga identificar movimentos suspeitos, como uma pessoa levantando as duas mãos — uma possível indicação de situação de perigo — e enviar alertas visuais e digitais.

---

## Visão geral da solução

Desenvolvemos uma aplicação web utilizando Flask para interface e OpenCV + MediaPipe para captura e análise do vídeo da webcam em tempo real. O sistema detecta a pose da pessoa e identifica quando as duas mãos estão levantadas. Neste caso, dispara um alerta:

* Uma imagem do momento é capturada e salva.
* Um alerta aparece em tempo real na interface web.
* Um JSON com os dados do alerta é enviado para um endpoint configurado para comunicação (simulando um sistema de monitoramento).

### Fluxo de funcionamento

1. O usuário acessa a página web.
2. A webcam é ativada e o vídeo ao vivo é exibido.
3. O sistema monitora o vídeo para detectar mãos levantadas via MediaPipe Pose.
4. Quando o movimento suspeito é detectado:

   * Captura a imagem do vídeo no instante.
   * Exibe um alerta visual na interface.
   * Armazena a captura na pasta `static/capturas`.
   * Envia um JSON com dados do alerta para um endpoint `/receber_alerta`.
5. O usuário pode visualizar as imagens capturadas na galeria integrada.
6. Log em tempo real mostra o histórico dos alertas detectados.

### Ilustração do sistema

```plaintext
Usuário acessa http://localhost:5000
         ↓
Webcam ativa e vídeo exibido
         ↓
Sistema detecta mãos levantadas (MediaPipe Pose)
         ↓
Alerta disparado:
  - Imagem salva e exibida
  - Notificação visual no navegador
  - JSON enviado para endpoint de alerta
```

---

## Link do vídeo demonstrativo

[Vídeo demonstrativo do Sistema de Segurança](hhttps://www.youtube.com/watch?v=0tOxd54NOgQ)

---

## Código Fonte

O código principal da aplicação está no arquivo `app.py`. Abaixo está um resumo da estrutura e partes principais do código:

```python
from flask import Flask, render_template, Response, jsonify, request
import cv2
import mediapipe as mp
import os
from datetime import datetime

app = Flask(__name__)

mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

camera = cv2.VideoCapture(0)

capturas_dir = 'static/capturas'
os.makedirs(capturas_dir, exist_ok=True)

alertas = []

def detectar_maos_levantadas(frame):
    # Função que usa MediaPipe Pose para detectar se as duas mãos estão levantadas
    # Retorna True se condição atendida
    pass  # Implementação real do detector

def gera_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break

        if detectar_maos_levantadas(frame):
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            nome_arquivo = f'{capturas_dir}/alerta_{timestamp}.jpg'
            cv2.imwrite(nome_arquivo, frame)
            alertas.append({'timestamp': timestamp, 'imagem': nome_arquivo})
            # Envia JSON para endpoint etc.

        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html', alertas=alertas)

@app.route('/video_feed')
def video_feed():
    return Response(gera_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/alertas_recebidos')
def alertas_recebidos():
    return jsonify(alertas)

@app.route('/receber_alerta', methods=['POST'])
def receber_alerta():
    data = request.json
    # Processa alerta recebido
    return jsonify({'status': 'Alerta recebido'})

if __name__ == "__main__":
    app.run(debug=True)
```

---

## Instruções para rodar o projeto

1. Clone o repositório:

```bash
git clone https://github.com/JuanPinheiroFIAP/GS-IOT.git
cd GS-IOT
```

2. Crie e ative um ambiente virtual (recomendado):

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. Instale as dependências:

```bash
pip install -r requirements.txt
```

4. Execute a aplicação:

```bash
python app.py
```

5. Acesse `http://localhost:5000` no navegador para usar o sistema.

---

## Estrutura do projeto

```
/
├── app.py                   # Código principal Flask e OpenCV
├── requirements.txt         # Dependências
├── static/
│   └── capturas/            # Capturas de imagens salvas após alertas
├── templates/
│   ├── base.html            # Template base
│   ├── index.html           # Página principal
│   └── gallery.html         # Galeria de imagens capturadas
└── README.md                # Documentação do projeto
```

---

## Observações finais

* O sistema depende da webcam do computador para captar vídeo.
* Requer Python 3.12+ e bibliotecas atualizadas.
* As imagens capturadas ficam armazenadas para consulta posterior.
* A comunicação JSON pode ser expandida para integração com sistemas externos.

---

## Integrantes do Projeto

| Nome                     | RM        |
| ------------------------ | --------- |
| Juan Pinheiro de França  | RM 552202 |
| Lucas Rodrigues da Silva | RM 98344  |
| Kaiky Alvaro Miranda     | RM 98118  |
