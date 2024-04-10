from pydantic import BaseModel


class User(BaseModel):
    id: str
    email: str
    is_superuser: bool = False  # TODO: Implement superuser functionality
