from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str


class User(BaseModel):
    username: str  # used as DB ID, FIXME
    disabled: bool = False
    is_superuser: bool = False


class UserInDB(User):
    id: str
    hashed_password: str
