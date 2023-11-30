import asyncio
from homeAutomation.handsGestureController import HandGestureController as HGC
from dotenv import load_dotenv
import os
import argparse

# Carregue as variáveis de ambiente do arquivo .env
load_dotenv('.env')

async def main():
    parser = argparse.ArgumentParser(description='HandGestureController Configuration')

    # Opções dinâmicas para os argumentos
    parser.add_argument('-hd', '--show_hands_drawing', action='store_true', help='Show hands drawing')
    parser.add_argument('-s', '--show_image', action='store_true', help='Show image')
    parser.add_argument('-i', '--put_icon', action='store_true', help='Put an icon')
    parser.add_argument('-c', '--camera_option', type=str, default='best', help='Camera option (e.g., best, min_index or max_index (beta))')

    # Argumento para mostrar tudo
    parser.add_argument('-all', '--show_all', action='store_true', help='Show all (image, hands drawing, icon)')

    # Argumento para desativar tudo
    parser.add_argument('-off', '--disable_all', action='store_true', help='Disable all (image, hands drawing, icon)')

    args = parser.parse_args()

    if args.disable_all:
        show_hands_drawing = False
        show_image = False
        put_icon = False
    elif args.show_hands_drawing:
        show_hands_drawing = True
        show_image = True
        put_icon = False
    elif args.show_image:
        show_hands_drawing = False
        show_image = True
        put_icon = False
    elif args.put_icon:
        show_hands_drawing = False
        show_image = True
        put_icon = True
    else:
        show_hands_drawing = True
        show_image = True
        put_icon = True

    IFTTT_TOKEN_ID = os.getenv('IFTTT_TOKEN_ID')
    hgc = HGC(
        ifttt_token_id=IFTTT_TOKEN_ID,
        show_hands_drawing=show_hands_drawing,
        b_show_image=show_image,
        bPutIcon=put_icon,
        camera_option=args.camera_option
    )
    await hgc.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass