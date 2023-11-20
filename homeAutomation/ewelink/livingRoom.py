import requests

class LivingRoom:
    def __init__(self):
        print("Ewelink - LivingRoom")
    
    async def mainLight(self, session, token_id: str):
        url = f"https://us-apia.coolkit.cc/v2/smartscene2/webhooks/execute?id={token_id}"

        # Faça uma solicitação GET para o webhook usando a sessão do aiohttp
        async with session.get(url) as response:
            return response.status