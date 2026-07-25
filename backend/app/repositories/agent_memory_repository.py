from sqlalchemy.orm import Session

from app.models.agent_memory import AgentMemory
from app.repositories.base_repository import BaseRepository


class AgentMemoryRepository(BaseRepository[AgentMemory]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, AgentMemory)
