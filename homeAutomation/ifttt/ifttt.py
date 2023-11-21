import requests

class IFTTT_General:
    def __init__(self, token_id: str):
        print("IFTTT")
        self.token_id = token_id
    
    async def pauseMusic(self, session):
        url = f"https://maker.ifttt.com/trigger/pauseMusic/json/with/key/{self.token_id}"

        # Faça uma solicitação GET para o webhook usando a sessão do aiohttp
        async with session.get(url) as response:
            return response.status
        
    async def startMusic(self, session):
        url = f"https://maker.ifttt.com/trigger/startMusic/json/with/key/{self.token_id}"

        # Faça uma solicitação GET para o webhook usando a sessão do aiohttp
        async with session.get(url) as response:
            return response.status
        
class Livingroom:
    def __init__(self, token_id: str):
        print("LIVINGROOM")
        self.token_id = token_id
        
    async def globoOn(self, session):
        url = f"https://maker.ifttt.com/trigger/globoOn/json/with/key/{self.token_id}"

        # Faça uma solicitação GET para o webhook usando a sessão do aiohttp
        async with session.get(url) as response:
            return response.status
        
    async def globoOff(self, session):
        url = f"https://maker.ifttt.com/trigger/globoOff/json/with/key/{self.token_id}"

        # Faça uma solicitação GET para o webhook usando a sessão do aiohttp
        async with session.get(url) as response:
            return response.status
        
    async def MainLightOn(self, session):
        url = f"https://maker.ifttt.com/trigger/livingroomMainLightOn/json/with/key/{self.token_id}"

        # Faça uma solicitação GET para o webhook usando a sessão do aiohttp
        async with session.get(url) as response:
            return response.status
        
    async def MainLightOff(self, session):
        url = f"https://maker.ifttt.com/trigger/livingroomMainLightOff/json/with/key/{self.token_id}"

        # Faça uma solicitação GET para o webhook usando a sessão do aiohttp
        async with session.get(url) as response:
            return response.status
        
class Livestock:
    def __init__(self, token_id: str):
        print("LIVINGROOM")
        self.token_id = token_id
        
    async def globoOn(self, session):
        url = f"https://maker.ifttt.com/trigger/globoOn/json/with/key/{self.token_id}"

        # Faça uma solicitação GET para o webhook usando a sessão do aiohttp
        async with session.get(url) as response:
            return response.status
        
    async def globoOff(self, session):
        url = f"https://maker.ifttt.com/trigger/globoOff/json/with/key/{self.token_id}"

        # Faça uma solicitação GET para o webhook usando a sessão do aiohttp
        async with session.get(url) as response:
            return response.status
        
    async def MainLightOn(self, session):
        url = f"https://maker.ifttt.com/trigger/livingRoomMainLightOn/json/with/key/{self.token_id}"

        # Faça uma solicitação GET para o webhook usando a sessão do aiohttp
        async with session.get(url) as response:
            return response.status
        
    async def MainLightOff(self, session):
        url = f"https://maker.ifttt.com/trigger/livingRoomMainLightOff/json/with/key/{self.token_id}"

        # Faça uma solicitação GET para o webhook usando a sessão do aiohttp
        async with session.get(url) as response:
            return response.status