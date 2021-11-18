import orjson

# Используем pydantic для упрощения работы при перегонке данных из json в объекты
from pydantic import BaseModel as PydanticBaseModel

def orjson_dumps(v, *, default):
    # orjson.dumps возвращает bytes, а pydantic требует unicode, поэтому декодируем
    return orjson.dumps(v, default=default).decode()

class BaseModel(PydanticBaseModel):
    class Config:
        # Заменяем стандартную работу с json на более быструю
        json_loads = orjson.loads
        json_dumps = orjson_dumps
        allow_population_by_field_name = True