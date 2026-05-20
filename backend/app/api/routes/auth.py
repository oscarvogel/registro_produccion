from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from app.api.deps import get_db
from app.models.personal import Personal
from app.models.personal_unidad_negocio import PersonalUnidadNegocio
from app.schemas.auth import LoginRequest, LoginResponse, SyncResponse, UserInfo
from app.core.security import create_access_token, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


def _personal_unidad_ids(user: Personal, db: Session) -> list[int]:
    try:
        rows = (
            db.query(PersonalUnidadNegocio.idUnidadNegocio)
            .filter(PersonalUnidadNegocio.idPersonal == user.idPersonal)
            .all()
        )
    except SQLAlchemyError:
        db.rollback()
        rows = []
    ids = [int(row[0]) for row in rows]
    if not ids and user.unidad_negocio:
        ids = [int(user.unidad_negocio)]
    return ids


@router.post("/login", response_model=LoginResponse)
async def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(Personal).filter(
        Personal.dni == credentials.dni,
        Personal.activo == 1,
    ).first()

    if not user or not verify_password(credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="DNI o contraseña incorrectos",
        )

    token = create_access_token(
        data={
            "sub": str(user.idPersonal),
            "dni": user.dni,
            "is_admin": int(user.is_admin or 0),
        }
    )

    return LoginResponse(
        access_token=token,
        user=UserInfo(
            idPersonal=user.idPersonal,
            nombre=user.Nombre,
            dni=user.dni,
            encargado=user.encargado,
            is_admin=user.is_admin,
            tipo_de_proceso_id=user.tipo_de_proceso_id,
            unidad_negocio=user.unidad_negocio,
            unidad_ids=_personal_unidad_ids(user, db),
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
