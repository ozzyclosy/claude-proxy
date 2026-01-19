# proxy_app.py
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import httpx

app = FastAPI()
TARGET_URL = "https://api.apiyi.com"

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy(request: Request, path: str):
    async with httpx.AsyncClient() as client:
        url = f"{TARGET_URL}/{path}"
        headers = dict(request.headers)
        headers["host"] = "api.apiyi.com"
        headers["authorization"] = "Bearer sk-QLvcMgEb9p1qbzfwD5E9C138185b474eB27dFc46FaE16fE9"
        if request.query_params:
            url += "?" + str(request.query_params)

        req = client.build_request(
            method=request.method,
            url=url,
            headers=headers,
            content=await request.body()
        )
        resp = await client.send(req, stream=True)

        return StreamingResponse(
            resp.aiter_raw(),
            status_code=resp.status_code,
            headers=dict(resp.headers),
        )
