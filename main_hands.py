import cv2
import mediapipe as mp
import numpy as np

import asyncio
import concurrent.futures

from homeAutomation.ifttt.ifttt import IFTTT_General, Livingroom, Livestock

from dotenv import load_dotenv

# Carregue as variáveis de ambiente do arquivo .env
load_dotenv('.env')

import os

EWELINK_livingroom_TOKEN_ID = os.getenv('EWELINK_livingroom_TOKEN_ID')
IFTTT_TOKEN_ID = os.getenv('IFTTT_TOKEN_ID')

livingroom = Livingroom(token_id=IFTTT_TOKEN_ID)
livestock = Livestock(token_id=IFTTT_TOKEN_ID)
iftttGeneral = IFTTT_General(token_id=IFTTT_TOKEN_ID)

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

hands = mp_hands.Hands()

cam = cv2.VideoCapture(0)

resolution_x = 1280
resolution_y = 720

cam.set(cv2.CAP_PROP_FRAME_WIDTH, resolution_x)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution_y)

def find_hands_coord(frame:np.ndarray, side_inv:bool = False)->(np.ndarray, list):
    result = hands.process(frame)
    
    all_hands = []
    if result.multi_hand_landmarks:
        for hand_side, hand_marks in zip(result.multi_handedness,result.multi_hand_landmarks):
            hand_info = {}
            coords = []
            for marks in hand_marks.landmark:
                coord_x, coord_y, coord_z = int(marks.x*resolution_x), int(marks.y*resolution_y), int(marks.z*resolution_x)
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
            mp_drawing.draw_landmarks(frame, hand_marks, mp_hands.HAND_CONNECTIONS)
            
    return frame, all_hands

def fingers_raised(hands:list) -> list:
    fingers = []
    
    for fingertip in [8,12,16,20]:
        k1 = hands['coords'][fingertip][1] < hands['coords'][fingertip-2][1]
        k2 = hands['coords'][4][1] < hands['coords'][fingertip][1]
        k3 = hands['coords'][4][1] > hands['coords'][0][1]
        if k1 & (~k2) & (~k3):
            fingers.append(True)
        else:
            fingers.append(False)
    
    return fingers

import aiohttp

async def main():
    dStatus = {}
    dStatus['livingroomMainLight'] = [False, "livingroomMainLightOff"]
    dStatus['ifttt-startMusic'] = False
    dStatus['ifttt-pauseMusic'] = False
    dStatus['livingroomGloboLight'] = [False, "livingroomGloboLightOff"]
    async with aiohttp.ClientSession() as session:
        while True:
            success, frame = cam.read()
            frame = cv2.flip(frame, 1)

            frame, all_hands = find_hands_coord(frame)

            if len(all_hands) == 1:
                finger_info_hand1 = fingers_raised(all_hands[0])

                if finger_info_hand1 == [True, False, False, False]:  #1000
                    if dStatus['livingroomMainLight'][0] == False:
                        print("liga/desliga sala")
                        if dStatus['livingroomMainLight'][1] == "livingroomMainLightOff":
                            asyncio.create_task(livingroom.MainLightOn(session))
                            dStatus['livingroomMainLight'] = [True, "livingroomMainLightOn"]
                        else:
                            asyncio.create_task(livingroom.MainLightOff(session))
                            dStatus['livingroomMainLight'] = [True, "livingroomMainLightOff"]
                else:
                    dStatus['livingroomMainLight'][0] = False

                if finger_info_hand1 == [False, False, False, True]:  #1100
                    if dStatus['livingroomGloboLight'][0] == False:
                        if dStatus['livingroomGloboLight'][1] == "livingroomGloboLightOff":
                            print('liga globo')
                            asyncio.create_task(livingroom.globoOn(session))
                            dStatus['livingroomGloboLight'] = [True, "livingroomGloboLightOn"]
                        else:
                            print('desliga globo')
                            asyncio.create_task(livingroom.globoOff(session))
                            dStatus['livingroomGloboLight'] = [True, "livingroomGloboLightOff"]
                else:
                    dStatus['livingroomGloboLight'][0] = False
                    
                
                
                # if finger_info_hand1 == [False, True, False, False]:  #0100
                #     if dStatus['ifttt-pauseMusic'] == False:
                #         print("pausa a música")
                #         asyncio.create_task(iftttGeneral.pauseMusic(session))
                #         dStatus['ifttt-pauseMusic'] = True
                # else:
                #     dStatus['ifttt-pauseMusic'] = False
                    
                # if finger_info_hand1 == [True, True, False, False]:  #1100
                #     if dStatus['ifttt-startMusic'] == False:
                #         print("Inicia a música")
                #         asyncio.create_task(iftttGeneral.startMusic(session))
                #         dStatus['ifttt-startMusic'] = True
                # else:
                #     dStatus['ifttt-startMusic'] = False 
                       
                # if finger_info_hand1 == [False, False, True, False]:  #0010
                #     if dStatus['ifttt-globoOn'] == False:
                #         print('Start globoOn')
                #         asyncio.create_task(iftttGeneral.globoOn(session))
                #         dStatus['ifttt-globoOn'] = True
                # else:
                #     dStatus['ifttt-globoOn'] = False
                       
                # if finger_info_hand1 == [True, False, True, False]:  #1010
                #     if dStatus['ifttt-globoOff'] == False:
                #         print('Start globoOff')
                #         asyncio.create_task(iftttGeneral.globoOff(session))
                #         dStatus['ifttt-globoOff'] = True
                # else:
                #     dStatus['ifttt-globoOff'] = False

            if success:
                cv2.imshow('Imagem', frame)

            key = cv2.waitKey(1)

            if key == 27:
                break

            # Aguarde por um pequeno intervalo para não sobrecarregar o loop
            await asyncio.sleep(0.01)

if __name__ == "__main__":
    try:
        # Execute o loop principal de eventos assíncronos
        asyncio.run(main())
    except KeyboardInterrupt:
        pass