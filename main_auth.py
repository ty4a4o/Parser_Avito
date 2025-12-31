import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from auth import AvitoAuthService

app = FastAPI()
# Теперь создаем объект без аргументов
avito_service = AvitoAuthService()

class LoginSchema(BaseModel):
    login: str
    password: str

@app.post("/auth/avito/check")
async def check_avito_auth(data: LoginSchema):
    result = await avito_service.login_and_get_cookies(data.login, data.password)
    
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    
    # Сохраняем куки для дальнейшего использования
    with open('avito_cookies.json', 'w') as file:
        json.dump(result["cookies"], file)
        
    return {"message": "Авторизация успешна, куки сохранены"}

if __name__ == "__main_auth__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)