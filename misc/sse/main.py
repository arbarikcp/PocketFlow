from fastapi import FastAPI
from sse_starlette.sse import EventSourceResponse
import asyncio
import time

app = FastAPI()

@app.get("/stream")
async def stream():
    async def event_generator():
        for i in range(10):  # send 10 messages then close
            await asyncio.sleep(3)  # simulate delay
            yield {
                "event": "message",
                "data": f"Server time: {time.strftime('%X')}"
            }
        yield {"event": "end", "data": "Stream closed."}

    return EventSourceResponse(event_generator())
