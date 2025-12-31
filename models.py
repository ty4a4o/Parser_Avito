from pydantic import BaseModel
from typing import Optional, List

# Данные для создания заказа
class OrderCreate(BaseModel):
    user_id: int
    title: str
    target_url: str

# Данные для ответа по задаче
class TaskResponse(BaseModel):
    order_id: int
    title: str
    target_url: str
    reward: int = 5

# Данные для завершения задачи
class TaskComplete(BaseModel):
    user_id: int
    order_id: int

# Для регистрации/создания юзера
class UserCreate(BaseModel):
    username: str

class UserResponse(BaseModel):
    id: int
    username: str
    balance: int