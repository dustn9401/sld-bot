import asyncio
import concurrent.futures
from twocaptcha import TwoCaptcha, ValidationException, NetworkException, ApiException, TimeoutException


class CaptchaSolver:
    def __init__(self):
        self.solver = TwoCaptcha('04b58e5335ac7041a33e9cf1b3c5a03e')

    async def solve(self, path):
        loop = asyncio.get_running_loop()
        with concurrent.futures.ThreadPoolExecutor() as pool:
            return await loop.run_in_executor(pool, lambda: self.solver.normal(path, numeric=1, minLength=5, maxLength=5))

    def report(self, captcha_id, result):
        try:
            self.solver.report(captcha_id, result)
        except ValidationException as e:
            print(e)
        except NetworkException as e:
            print(e)
        except ApiException as e:
            print(e)
        except TimeoutException as e:
            print(e)