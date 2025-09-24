# 한국 디스코드 봇 리스트 API 로 서버수 업데이트 하는 코드인데 일단 주석처리
# @Task.create(IntervalTrigger(hours=1))
# async def updatekoreandiscordbot():
#     url = "https://koreanbots.dev/api/v2/bots/1181513333002739772/stats"
#     json = {"servers": len(bot.guilds), "shards": 1, }
#     header = {"Authorization": var.koreanbottoken, "Content-Type": "application/json"}
#     async with aiohttp.ClientSession() as session:
#         async with session.post(url, headers=header, json=json) as response:
#             response = await response.json()
#     logger.info("koreanbots:" + response['message'])
