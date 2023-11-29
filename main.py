import asyncio
from homeAutomation.handsGestureController import HandGestureController as HGC

from dotenv import load_dotenv

# Carregue as variáveis de ambiente do arquivo .env
load_dotenv('.env')

import os

async def main():
    IFTTT_TOKEN_ID = os.getenv('IFTTT_TOKEN_ID')
    hgc = HGC(ifttt_token_id=IFTTT_TOKEN_ID, show_hands_drawing=False, b_show_image=False, bPutIcon=True)
    await hgc.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass