from pydantic import BaseModel, EmailStr, Field


class UserSchema(BaseModel):
    """Схема пользователя"""

    name: str = Field(..., min_length=2)
    email: EmailStr = Field(..., description="Электронная почта")
    password: str = Field(..., min_length=6)
