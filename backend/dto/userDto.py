from pydantic import BaseModel

class UserDTO(BaseModel):
    id: int
    name: str