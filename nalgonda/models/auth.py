from pydantic import BaseModel


class User(BaseModel):
    id: str
    username: str
    disabled: bool = False
    is_superuser: bool = False
