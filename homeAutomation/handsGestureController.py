import cv2
import mediapipe as mp
import numpy as np
import asyncio
# import concurrent.futures
from .ifttt.ifttt import IFTTT_General, Livingroom, Livestock
import aiohttp

import cv2
import mediapipe as mp

class HandGestureController:
    def __init__(self, ifttt_token_id, show_hands_drawing=True, b_show_image=True, bPutIcon=True, camera_option="best"):
        """
        Inicializa a classe HandGestureController.

        Parâmetros:
        - ifttt_token_id (str): Token de autenticação para o IFTTT.
        - show_hands_drawing (bool): Se True, desenha as linhas das mãos na imagem.
        - b_show_image (bool): Se True, exibe a imagem capturada pela câmera usando cv2.imshow.
        - bPutIcon (bool): Se True, coloca um ícone na tela.
        - camera_option (str): Opção para escolher a câmera a ser aberta. Pode ser "best", "min_index", "max_index" ou um índice específico.

        """
        # Configuração da variável que controla se as linhas da mão serão desenhadas
        self.bShowHandsDrawing = show_hands_drawing
        self.bShowImage = b_show_image
        self.bPutIcon = bPutIcon

        self.IFTTT_TOKEN_ID = ifttt_token_id

        self.livingroom = Livingroom(token_id=self.IFTTT_TOKEN_ID)
        self.livestock = Livestock(token_id=self.IFTTT_TOKEN_ID)
        self.iftttGeneral = IFTTT_General(token_id=self.IFTTT_TOKEN_ID)

        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils

        # Obtém o índice da câmera de acordo com a opção escolhida
        if camera_option == "min_index":
            best_camera_index = 0
        elif camera_option == "max_index":
            best_camera_index = self.get_max_camera_index()
        elif camera_option.isdigit():
            best_camera_index = int(camera_option)
        else:
            best_camera_index = self.get_best_resolution_camera()

        # Abre a câmera de acordo com o índice escolhido
        if best_camera_index != -1:
            self.cam = cv2.VideoCapture(best_camera_index)
            self.resolution_x = int(self.cam.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.resolution_y = int(self.cam.get(cv2.CAP_PROP_FRAME_HEIGHT))
        else:
            print("Nenhuma câmera encontrada.")
            # Defina resoluções padrão caso não seja possível encontrar uma câmera
            self.resolution_x = 1280
            self.resolution_y = 720

        # Configuração da resolução da câmera
        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution_x)
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution_y)

        # Inicialização do modelo de mãos
        self.hands = self.mp_hands.Hands()

    def get_best_resolution_camera(self):
        # Obtém o número de câmeras disponíveis diretamente do sistema
        max_camera_index = self.get_max_camera_index()

        # Tenta abrir as câmeras em ordem decrescente de índice
        for camera_index in range(max_camera_index, -1, -1):
            try:
                cap = cv2.VideoCapture(camera_index)
                if cap.isOpened():
                    # Se a câmera foi aberta com sucesso, retorna o índice dela
                    cap.release()
                    return camera_index
                else:
                    print(f"Não foi possível abrir a câmera {camera_index}.")
            except Exception as e:
                print(f"Erro ao tentar abrir câmera {camera_index}: {e}")

        # Se todas as tentativas falharam, retorna -1
        return -1

    def get_max_camera_index(self):
        # Encontra o índice máximo das câmeras disponíveis
        max_camera_index = 0
        while cv2.VideoCapture(max_camera_index).isOpened():
            max_camera_index += 1

        return max_camera_index
    
    
# hand_controller = HandGestureController(ifttt_token_id='seu_token_aqui')

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
                
                if self.bPutIcon:
                    frame = self.putIcon(frame)
                
                if len(all_hands) == 1:
                    if bHands:
                        bHands = False
                        bNoHands = True
                        texto = "I'm ready for your orders!"
                        print("I'm ready for your orders!")
                        
                    finger_info_hand1 = self.fingers_raised(all_hands[0])
                    
                    if self.bPutIcon:
                        if all_hands[0]:
                            x = all_hands[0]['coords'][8][0]
                            y = all_hands[0]['coords'][8][1]
                            
                            if (50 <= x <= 100) & (50 <= y <= 100):
                                print('passou pela tecla')
                                frame = self.putIcon(frame, color = (0,0,255))
                    
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
    
    def putIcon(self, frame: np.ndarray, color:str = (0,255,0)) -> np.ndarray:
        frame = frame
        
        frame = cv2.rectangle(frame, (50,50), (100,100), color)
        frame = cv2.putText(frame, 'Q', (65,85), cv2.FONT_HERSHEY_COMPLEX, 1, color, 2)
        
        return frame