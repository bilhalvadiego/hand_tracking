import cv2
import mediapipe as mp
import numpy as np
import asyncio
import concurrent.futures
from .ifttt.ifttt import IFTTT_General, Livingroom, Livestock
import aiohttp

class HandGestureController:
    def __init__(self, ifttt_token_id, show_hands_drawing=True, b_show_image=True):
        """
        Inicializa a classe HandGestureController.

        Parâmetros:
        - ifttt_token_id (str): Token de autenticação para o IFTTT.
        - show_hands_drawing (bool): Se True, desenha as linhas das mãos na imagem.
        - b_show_image (bool): Se True, exibe a imagem capturada pela câmera usando cv2.imshow.

        """
        # Configuração da variável que controla se as linhas da mão serão desenhadas
        self.bShowHandsDrawing = show_hands_drawing
        self.bShowImage = b_show_image

        self.IFTTT_TOKEN_ID = ifttt_token_id

        self.livingroom = Livingroom(token_id=self.IFTTT_TOKEN_ID)
        self.livestock = Livestock(token_id=self.IFTTT_TOKEN_ID)
        self.iftttGeneral = IFTTT_General(token_id=self.IFTTT_TOKEN_ID)

        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils

        self.hands = self.mp_hands.Hands()

        self.cam = cv2.VideoCapture(0)

        self.resolution_x = 1280
        self.resolution_y = 720

        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution_x)
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution_y)

    async def run(self):
        """
        Executa o loop principal do reconhecimento de gestos de mão.

        Este método deve ser chamado para iniciar o reconhecimento de gestos.
        """
        dStatus = {}
        dStatus['livingroomMainLight'] = [False, "livingroomMainLightOff"]
        dStatus['ifttt-startMusic'] = False
        dStatus['ifttt-pauseMusic'] = False
        dStatus['livingroomGloboLight'] = [False, "livingroomGloboLightOff"]

        async with aiohttp.ClientSession() as session:
            bNoHands = True
            bHands = True
            texto = "Show at least one hand to order something"
            while True:
                success, frame = self.cam.read()
                frame = cv2.flip(frame, 1)
                cv2.putText(frame, texto, (self.resolution_x - 800, self.resolution_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

                frame, all_hands = self.find_hands_coord(frame)

                if len(all_hands) == 1:
                    if bHands:
                        bHands = False
                        bNoHands = True
                        texto = "I'm ready for your orders!"
                        print("I'm ready for your orders!")
                        
                    finger_info_hand1 = self.fingers_raised(all_hands[0])
                    if finger_info_hand1 == [True, False, False, False]:  #1000
                        if dStatus['livingroomMainLight'][0] == False:
                            
                            if dStatus['livingroomMainLight'][1] == "livingroomMainLightOff":
                                print("liga sala")
                                asyncio.create_task(self.livingroom.MainLightOn(session))
                                dStatus['livingroomMainLight'] = [True, "livingroomMainLightOn"]
                            else:
                                print("desliga sala")
                                asyncio.create_task(self.livingroom.MainLightOff(session))
                                dStatus['livingroomMainLight'] = [True, "livingroomMainLightOff"]
                    else:
                        dStatus['livingroomMainLight'][0] = False

                    if finger_info_hand1 == [False, False, False, True]:  #1100
                        if dStatus['livingroomGloboLight'][0] == False:
                            if dStatus['livingroomGloboLight'][1] == "livingroomGloboLightOff":
                                print('liga globo')
                                asyncio.create_task(self.livingroom.globoOn(session))
                                dStatus['livingroomGloboLight'] = [True, "livingroomGloboLightOn"]
                            else:
                                print('desliga globo')
                                asyncio.create_task(self.livingroom.globoOff(session))
                                dStatus['livingroomGloboLight'] = [True, "livingroomGloboLightOff"]
                    else:
                        dStatus['livingroomGloboLight'][0] = False

                else:
                    if bNoHands:
                        bNoHands = False
                        bHands = True
                        texto = "Show at least one hand to order something"
                        print("Show at least one hand to order something")

                if self.bShowImage and success:
                    cv2.imshow('Imagem', frame)

                key = cv2.waitKey(1)

                if key == 27:
                    break

                await asyncio.sleep(0.01)

    def find_hands_coord(self, frame: np.ndarray, side_inv: bool = False) -> (np.ndarray, list):
        """
        Localiza as coordenadas das mãos na imagem.

        Parâmetros:
        - frame (np.ndarray): Imagem de entrada.
        - side_inv (bool): Se True, inverte os lados direito e esquerdo.

        Retorna:
        - frame (np.ndarray): Imagem com as marcações das mãos.
        - all_hands (list): Lista contendo informações sobre as mãos detectadas.
        """
        result = self.hands.process(frame)

        all_hands = []
        if result.multi_hand_landmarks:
            for hand_side, hand_marks in zip(result.multi_handedness, result.multi_hand_landmarks):
                hand_info = {}
                coords = []
                for marks in hand_marks.landmark:
                    coord_x, coord_y, coord_z = int(marks.x * self.resolution_x), int(marks.y * self.resolution_y), int(marks.z * self.resolution_x)
                    coords.append((coord_x, coord_y, coord_z))

                hand_info['coords'] = coords

                if side_inv:
                    if hand_side.classification[0].label == 'Left':
                        hand_info['hand'] = 'Right'
                    else:
                        hand_info['hand'] = 'Left'
                else:
                    hand_info['hand'] = hand_side.classification[0].label

                all_hands.append(hand_info)
                if self.bShowHandsDrawing:
                    self.mp_drawing.draw_landmarks(frame, hand_marks, self.mp_hands.HAND_CONNECTIONS)

        return frame, all_hands

    def fingers_raised(self, hands: list) -> list:
        """
        Verifica quais dedos estão levantados com base nas coordenadas das mãos.

        Parâmetros:
        - hands (list): Lista contendo informações sobre as mãos.

        Retorna:
        - fingers (list): Lista indicando quais dedos estão levantados.
        """
        fingers = []

        for fingertip in [8, 12, 16, 20]:
            k1 = hands['coords'][fingertip][1] < hands['coords'][fingertip - 2][1]
            k2 = hands['coords'][4][1] < hands['coords'][fingertip][1]
            k3 = hands['coords'][4][1] > hands['coords'][0][1]
            if k1 & (~k2) & (~k3):
                fingers.append(True)
            else:
                fingers.append(False)

        return fingers