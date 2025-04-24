from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

class TestRequest(BaseModel):
    message: str

@app.get("/")
async def root():
    return {"status": "ok", "message": "API está funcionando!"}

@app.post("/test/")
async def test_endpoint(request: TestRequest):
    return {
        "status": "success",
        "received_message": request.message,
        "response": "Mensagem recebida com sucesso!"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000) 