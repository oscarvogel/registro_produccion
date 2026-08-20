from pydantic import BaseModel, ConfigDict, Field, field_validator


class MotivoNoOperativoBase(BaseModel):
    nombre: str = Field(min_length=1, max_length=80)
    codigo: str | None = Field(default=None, max_length=40)
    activo: bool = True
    unidad_ids: list[int] = Field(default_factory=list)

    @field_validator("nombre", "codigo", mode="before")
    @classmethod
    def strip_text(cls, value):
        if value is None:
            return value
        return str(value).strip()

    @field_validator("unidad_ids", mode="before")
    @classmethod
    def normalize_unidades(cls, value):
        if value is None:
            return []
        result: list[int] = []
        for item in value:
            try:
                parsed = int(item)
            except (TypeError, ValueError):
                continue
            if parsed > 0 and parsed not in result:
                result.append(parsed)
        return result


class MotivoNoOperativoCreate(MotivoNoOperativoBase):
    pass


class MotivoNoOperativoUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=80)
    codigo: str | None = Field(default=None, max_length=40)
    activo: bool | None = None
    unidad_ids: list[int] | None = None

    @field_validator("nombre", "codigo", mode="before")
    @classmethod
    def strip_text(cls, value):
        if value is None:
            return value
        return str(value).strip()


class MotivoNoOperativoResponse(BaseModel):
    id: int
    codigo: str
    nombre: str
    activo: bool
    unidad_ids: list[int] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class MotivoNoOperativoCatalogoItem(BaseModel):
    id: int
    codigo: str
    nombre: str

    model_config = ConfigDict(from_attributes=True)
