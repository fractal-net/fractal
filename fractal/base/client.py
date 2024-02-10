import aiohttp
import json

class HttpClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = aiohttp.ClientSession()

    async def generate(self, text, seed, **kwargs):
        url = f"{self.base_url}/generate"
        data = {"text": text, "seed": seed}
        data.update(kwargs)  # Allows for additional parameters if needed
        headers = {"Content-Type": "application/json"}

        async with self.session.post(url, data=json.dumps(data), headers=headers) as response:
            if response.status == 200:
                response_json = await response.json()
                completion_text = response_json.get('completion', '')  
                return completion_text
            else:
                return ''  # Return an empty string in case of non-200 responses

    async def close(self):
        await self.session.close()

