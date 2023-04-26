import asyncio
from concurrent.futures import ThreadPoolExecutor
import time
from server.utils import calc_time
import base64

def sync_calc_fib(n):
    if n in [1, 2]:
        return 1
    return sync_calc_fib(n - 1) + sync_calc_fib(n - 2)


def calc_fib(n):
    result = sync_calc_fib(n)
    print(f'第 {n} 项计算完成，结果是：{result}')
    return result

async def request(i):
    asyncio.sleep(i)
    print(f'第 {i} 项请求')
    return i

async def main():
    start = time.perf_counter()
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor(max_workers=4) as executor:
        tasks_list = [
            loop.run_in_executor(executor, calc_fib, 20),
            loop.run_in_executor(executor, calc_fib, 20),
            asyncio.create_task(request(5))
        ]
        lis = await asyncio.gather(*tasks_list)
        for i in lis:
            print(i)

        end = time.perf_counter()
        print(f'总计耗时：{end - start}')


# asyncio.run(main())


def readwav2base64(wav_file):
    """
    read wave file and covert to base64 string
    """
    with open(wav_file, 'rb') as f:
        base64_bytes = base64.b64encode(f.read())
        base64_string = base64_bytes.decode('utf-8')
    return base64_string

def save(data):
    with open("a.text", "w+") as f:
        f.write(data)
    

save(readwav2base64("./zh.wav"))