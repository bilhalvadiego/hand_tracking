import cv2
import mediapipe as mp
import numpy as np

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

hands = mp_hands.Hands()

cam = cv2.VideoCapture(2)

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
                    
            print(hand_side.classification[0].label)
            
            all_hands.append(hand_info)
            mp_drawing.draw_landmarks(frame, hand_marks, mp_hands.HAND_CONNECTIONS)
            
    return frame, all_hands

while True:
    success, frame = cam.read()
    frame = cv2.flip(frame, 1)
    # frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    frame, all_hands = find_hands_coord(frame)
    
    if len(all_hands) > 0:
        print(all_hands)
    if success:        
        cv2.imshow('Imagem', frame)
    
    key = cv2.waitKey(1)
    
    if key == 27:
        break;