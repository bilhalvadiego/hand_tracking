import cv2
import mediapipe as mp
import numpy as np

import asyncio
import concurrent.futures

from homeAutomation.ewelink.livingRoom import LivingRoom
from homeAutomation.ifttt.iftttGeneral import IFTTT

from dotenv import load_dotenv

# Carregue as variáveis de ambiente do arquivo .env
load_dotenv('.env')

import os

EWELINK_LIVINGROOM_TOKEN_ID = os.getenv('EWELINK_LIVINGROOM_TOKEN_ID')
IFTTT_TOKEN_ID = os.getenv('IFTTT_TOKEN_ID')

livingRoom = LivingRoom()
iftttGeneral = IFTTT()

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
    dStatus['ewelink-livingRoom-mainLight'] = False
    dStatus['ifttt-startMusic'] = False
    dStatus['ifttt-pauseMusic'] = False

    async with aiohttp.ClientSession() as session:
        while True:
            success, frame = cam.read()
            frame = cv2.flip(frame, 1)

            frame, all_hands = find_hands_coord(frame)

            if len(all_hands) == 1:
                finger_info_hand1 = fingers_raised(all_hands[0])

                if finger_info_hand1 == [True, False, False, False]:  # Indicador
                    if dStatus['ewelink-livingRoom-mainLight'] == False:
                        asyncio.create_task(livingRoom.mainLight(session, EWELINK_LIVINGROOM_TOKEN_ID))
                        dStatus['ewelink-livingRoom-mainLight'] = True
                else:
                    dStatus['ewelink-livingRoom-mainLight'] = False
                    
                if finger_info_hand1 == [True, True, False, False]:  # Indicador + Médio
                    if dStatus['ifttt-pauseMusic'] == False:
                        
                        asyncio.create_task(iftttGeneral.pauseMusic(session, IFTTT_TOKEN_ID))
                        dStatus['ifttt-pauseMusic'] = True
                else:
                    dStatus['ifttt-pauseMusic'] = False
                    
                if finger_info_hand1 == [False, False, False, True]:  # Indicador + Médio + Mindinho
                    if dStatus['ifttt-startMusic'] == False:
                        print('Start')
                        asyncio.create_task(iftttGeneral.startMusic(session, IFTTT_TOKEN_ID))
                        dStatus['ifttt-startMusic'] = True
                else:
                    dStatus['ifttt-startMusic'] = False

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