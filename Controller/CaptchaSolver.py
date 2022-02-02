import asyncio
import concurrent.futures
from twocaptcha import TwoCaptcha

config = {
    'apiKey': '04b58e5335ac7041a33e9cf1b3c5a03e',
    'defaultTimeout': 60
}

class CaptchaSolver:
    def __init__(self):
        self.solver = TwoCaptcha('04b58e5335ac7041a33e9cf1b3c5a03e')

    async def solve(self, path):
        # noinspection PyUnresolvedReferences,PyProtectedMember
        loop = asyncio._get_running_loop()
        with concurrent.futures.ThreadPoolExecutor() as pool:
            result = await loop.run_in_executor(pool, lambda: self.solver.normal(path, numeric=1, minLength=5, maxLength=5))
            return result
