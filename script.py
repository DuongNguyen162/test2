import asyncio
import datetime
from urllib import request
import aiohttp
import time

async def sendrq(session, data):
    async with session.post("http://127.0.0.1:5000/Applicant", json=data) as resp:
        return await resp.json()

async def main():
    async with aiohttp.ClientSession() as session:
        khoiluongviec = []
        applicant = applicant(
        name=request.json.get('name'),
        email=request.json.get('email'),
        dob=datetime.strptime(
            request.json.get('dob'),
            '%m-%d-%Y').date(),
        country=request.json.get('country'),
        status=request.json.get('status'),
        created_dttm=datetime.strptime(
            request.json.get('created_dttm'),
            '%m-%d-%Y').date())
        for i in range(1000):
            data = {{applicant}}
            task = asyncio.ensure_future(sendrq(session, data))
            khoiluongviec.append(task)

        rp = await asyncio.gather(*khoiluongviec)
        print(f"done {len(rp)} req")

if __name__ == "__main__":
    timebatdau = time.perf_counter()
    asyncio.run(main())
    timekethucrq = time.perf_counter()
    print(f"tong time: {timekethucrq - timebatdau:.2f} s")
