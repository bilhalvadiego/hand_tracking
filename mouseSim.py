import cv2
import mediapipe as mp
import pyautogui
from pynput import keyboard

mp_hands = mp.solutions.hands

cap = cv2.VideoCapture(0)

prev_index_tip_y = 0

exit_program = False

def on_key_release(key):
    global exit_program
    try:
        if key.char == 'q' or key.char == 'esc':
            exit_program = True
    except AttributeError:
        pass

listener = keyboard.Listener(on_release=on_key_release)
listener.start()

with mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
    while not exit_program:
        ret, frame = cap.read()
        if not ret:
            break

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        results = hands.process(frame_rgb)

        if results.multi_hand_landmarks:
            for landmarks in results.multi_hand_landmarks:
                index_tip = landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                thumb_tip = landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]

                # Obter a resolução da tela
                screen_width, screen_height = pyautogui.size()

                # Mapear as coordenadas do MediaPipe para as coordenadas da tela
                x = int((1 - index_tip.x) * screen_width)
                y = int(index_tip.y * screen_height)

                # Simular o movimento do mouse em toda a tela
                pyautogui.moveTo(x, y)

                # Verificar se o indicador está se movendo para frente (simulando um toque)
                if index_tip.y < prev_index_tip_y:
                    # Movimento para frente detectado, simular um clique
                    pyautogui.click()

                # Atualizar a posição anterior do indicador
                prev_index_tip_y = index_tip.y

        
cap.release()
cv2.destroyAllWindows()
listener.stop()
listener.join()