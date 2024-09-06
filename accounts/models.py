from uuid import UUID

from pydantic import BaseModel

from db.models import UserRole


class UserDTO(BaseModel):
    uuid: UUID
    full_name: str
    email: str
    role: UserRole
