from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.api.deps import get_db
from app.models.personal import Personal
from app.schemas.auth import LoginRequest, LoginResponse, SyncResponse, UserInfo
from app.core.security import create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
async def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(Personal).filter(
        Personal.dni == credentials.dni,
        Personal.activo == 1,
    ).first()

    if not user or user.password != credentials.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="DNI o contraseña incorrectos",
        )

    token = create_access_token(data={"sub": str(user.idPersonal), "dni": user.dni})

    return LoginResponse(
        access_token=token,
        user=UserInfo(
            idPersonal=user.idPersonal,
            nombre=user.Nombre,
            dni=user.dni,
            encargado=user.encargado,
            tipo_de_proceso_id=user.tipo_de_proceso_id,
        ),
    )


@router.post("/sincronizar", response_model=SyncResponse)
async def sincronizar(db: Session = Depends(get_db)):
    total_activos = (
        db.query(func.count(Personal.idPersonal))
        .filter(Personal.activo == 1)
        .scalar()
        or 0
    )

    return SyncResponse(
        message="Sincronización completada",
        total_activos=total_activos,
    )
