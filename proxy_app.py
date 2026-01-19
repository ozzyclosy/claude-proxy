from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import httpx

app = FastAPI()
TARGET_URL = "https://api.anthropic.com"

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy(request: Request, path: str):
    async with httpx.AsyncClient(timeout=120.0) as client:
        url = f"{TARGET_URL}/{path}"
        
        # Копируем заголовки, исключая те что могут вызвать проблемы
        headers = {}
        for key, value in request.headers.items():
            if key.lower() not in ["host", "content-length", "transfer-encoding"]:
                headers[key] = value
        
        # Устанавливаем правильный host
        headers["host"] = "api.anthropic.com"
        
        # Добавляем query параметры если есть
        if request.query_params:
            url += "?" + str(request.query_params)

        req = client.build_request(
            method=request.method,
            url=url,
            headers=headers,
            content=await request.body()
        )
        resp = await client.send(req, stream=True)

        # Фильтруем заголовки ответа
        response_headers = {}
        for key, value in resp.headers.items():
            if key.lower() not in ["content-encoding", "transfer-encoding", "content-length"]:
                response_headers[key] = value

        return StreamingResponse(
            resp.aiter_raw(),
            status_code=resp.status_code,
            headers=response_headers,
        )
