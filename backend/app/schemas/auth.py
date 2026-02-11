from pydantic import BaseModel


class LoginRequest(BaseModel):
    dni: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserInfo"


class UserInfo(BaseModel):
    idPersonal: int
    nombre: str
    dni: str

    class Config:
        from_attributes = True


# Rebuild model to resolve forward ref
LoginResponse.model_rebuild()
