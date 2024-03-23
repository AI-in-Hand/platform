from pydantic import BaseModel


class User(BaseModel):
    id: str
    username: str
    is_superuser: bool = False
