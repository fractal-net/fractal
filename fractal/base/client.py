import aiohttp
import json
import asyncio

class HttpClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = None

    async def open_session(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()

    async def close_session(self):
        if self.session and not self.session.closed:
            await self.session.close()

    async def generate(self, text, seed, **kwargs):
        await self.open_session()  # Ensure session is open and ready to use
        url = f"{self.base_url}/generate"
        data = {"text": text, "seed": seed}
        data.update(kwargs)  # Allows for additional parameters if needed
        headers = {"Content-Type": "application/json"}

        try:
            async with self.session.post(url, data=json.dumps(data), headers=headers) as response:
                if response.status == 200:
                    response_json = await response.json()
                    completion_text = response_json.get('completion', '')  
                    return completion_text
                elif response.status == 500:
                    # Handle server error
                    return 'Server error occurred'
                else:
                    # Handle other non-successful statuses
                    return f'Error: received status code {response.status}'
        except aiohttp.ClientError as e:
            # Handle client-side errors (e.g., connection issues)
            return f'Client error occurred: {str(e)}'
        except asyncio.TimeoutError:
            # Handle timeout error
            return 'Request timed out'
        # Additional specific exceptions can be caught and handled as needed

    # Ensure you call close_session() when your application is shutting down

