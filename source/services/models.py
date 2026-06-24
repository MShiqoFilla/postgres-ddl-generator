from pydantic import BaseModel
from typing import List

class Columns(BaseModel):
    name : str
    data_type : str
    udt_name : str
    character_maximum_length : int | None
    is_nullable : str
    column_default : str | None
    numeric_precision : int | None
    numeric_scale : int | None
    is_identity : str
    identity_generation : str | None

class Constraints(BaseModel):
    name : str
    type : str
    definition : str

class TableMetadata(BaseModel):
    schema_name : str
    table_name : str
    columns : List[Columns]
    constraints : List[Constraints]
    has_fk : bool