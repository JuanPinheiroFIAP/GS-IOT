from flask import Flask, render_template, Response, send_from_directory, jsonify, request
import cv2
import os
from datetime import datetime
import mediapipe as mp
import queue
import threading
import requests

app = Flask(__name__)

CAMERA = cv2.VideoCapture(0)
SAVE_DIR = 'static/capturas'

if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

mp_pose = mp.solutions.pose
pose = mp_pose.Pose(
    static_image_mode=False,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

alert_queue = queue.Queue()

def hands_raised(pose_landmarks):
    if not pose_landmarks:
        return False

    left_wrist = pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST]
    right_wrist = pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST]
    left_shoulder = pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER]
    right_shoulder = pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER]

    left_raised = left_wrist.y < left_shoulder.y
    right_raised = right_wrist.y < right_shoulder.y

    return left_raised and right_raised

def enviar_alerta_json(data):
    try:
        requests.post('http://localhost:5000/receber_alerta', json=data)
    except Exception as e:
        print("Erro ao enviar alerta JSON:", e)

def gen_frames():
    alerta_ativo = False
    alerta_tempo_inicio = None

    while True:
        success, frame = CAMERA.read()
        if not success:
            break
        else:
            frame = cv2.flip(frame, 1)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            results = pose.process(frame_rgb)
            pose_landmarks = results.pose_landmarks

            if hands_raised(pose_landmarks):
                if alerta_tempo_inicio is None:
                    alerta_tempo_inicio = datetime.now()
                else:
                    elapsed = (datetime.now() - alerta_tempo_inicio).total_seconds()
                    if elapsed >= 2 and not alerta_ativo:
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S%f')
                        filename = f"alerta_maos_{timestamp}.jpg"
                        filepath = os.path.join(SAVE_DIR, filename)
                        cv2.imwrite(filepath, frame)

                        alerta_ativo = True
                        alerta_tempo_inicio = None

                        alert_queue.put('alerta_maos')

                        # Envio assíncrono do alerta JSON
                        threading.Thread(target=enviar_alerta_json, args=([{
                            'tipo_alerta': 'movimento_suspeito',
                            'timestamp': timestamp,
                            'arquivo': filename
                        }],)).start()

                cv2.putText(frame, "Movimento suspeito", (50, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3, cv2.LINE_AA)
            else:
                alerta_tempo_inicio = None
                alerta_ativo = False

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/gallery')
def gallery():
    imagens = sorted(os.listdir(SAVE_DIR), reverse=True)
    return render_template('gallery.html', imagens=imagens)

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/alert_stream')
def alert_stream():
    def event_stream():
        while True:
            msg = alert_queue.get()
            yield f"data: {msg}\n\n"
    return Response(event_stream(), mimetype='text/event-stream')

@app.route('/imagens_atualizadas')
def imagens_atualizadas():
    imagens = sorted(os.listdir(SAVE_DIR), reverse=True)
    return jsonify(imagens)

@app.route('/static/capturas/<filename>')
def get_image(filename):
    return send_from_directory(SAVE_DIR, filename)

alertas_recebidos = []

@app.route('/receber_alerta', methods=['POST'])
def receber_alerta():
    data = request.get_json()
    print("Alerta JSON recebido:", data)
    alertas_recebidos.append(data)
    return jsonify({"status": "recebido"}), 200

@app.route('/alertas_recebidos')
def ver_alertas_recebidos():
    return jsonify(alertas_recebidos)

if __name__ == '__main__':
    app.run(debug=True, threaded=True)
