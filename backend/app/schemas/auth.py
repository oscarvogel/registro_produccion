from pydantic import BaseModel


class LoginRequest(BaseModel):
    dni: str
    password: str


class SyncRequest(BaseModel):
    dni: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserInfo"


class UserInfo(BaseModel):
    idPersonal: int
    nombre: str
    dni: str
    encargado: int = 0
    tipo_de_proceso_id: int | None = None

    class Config:
        from_attributes = True


class SyncResponse(BaseModel):
    synced: bool = True
    user: UserInfo


# Rebuild model to resolve forward ref
LoginResponse.model_rebuild()
