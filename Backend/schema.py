from pydantic import BaseModel, Field
from typing import Literal, List

class Category(BaseModel):
    category: Literal[
        "SELECT", "INSERT", "UPDATE", "DELETE", "DDL", "SCHEMA", "OTHER"
    ] = Field(description="Best-matching SQL operation for the request.")

class Query(BaseModel):
    query:str = Field(..., description="A valid SQL statement in proper SQL syntax that fulfills the user's request.")
    category:Literal[
        "SELECT",
        "INSERT",
        "UPDATE",
        "DELETE",
        "DDL",
        "SCHEMA",
        "OTHER"
        ] = Field(...,
            description=(
            "The SQL operation type inferred from the user's request:\n"
            "- SELECT: read/query data; counts/aggregations also fall here\n"
            "- INSERT: add new rows\n"
            "- UPDATE: modify existing rows\n"
            "- DELETE: remove rows\n"
            "- DDL: create/alter/drop tables, indexes, constraints, etc.\n"
            "- SCHEMA: describe/explain schema or columns (no data change)\n"
            "- OTHER: anything that doesn't fit above")
        )

class Decomposition(BaseModel):
    subqueries: List[str] = Field(
        ..., description="Ordered list of atomic natural language sub-queries."
    )