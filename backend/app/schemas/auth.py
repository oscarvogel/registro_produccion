from pydantic import BaseModel, Field


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
    encargado: int = 0
    is_admin: int = 0
    tipo_de_proceso_id: int | None = None
    unidad_negocio: int = 1
    unidad_ids: list[int] = Field(default_factory=list)

    class Config:
        from_attributes = True


class SyncResponse(BaseModel):
    synced: bool = True
    message: str
    total_activos: int


# Rebuild model to resolve forward ref
LoginResponse.model_rebuild()
