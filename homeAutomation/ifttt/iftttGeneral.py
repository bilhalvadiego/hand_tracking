import requests

class IFTTT:
    def __init__(self):
        print("IFTTT")
    
    async def pauseMusic(self, session, token_id: str):
        url = f"https://maker.ifttt.com/trigger/pauseMusic/json/with/key/{token_id}"

        # Faça uma solicitação GET para o webhook usando a sessão do aiohttp
        async with session.get(url) as response:
            return response.status
        
    async def startMusic(self, session, token_id: str):
        url = f"https://maker.ifttt.com/trigger/startMusic/json/with/key/{token_id}"

        # Faça uma solicitação GET para o webhook usando a sessão do aiohttp
        async with session.get(url) as response:
            return response.status