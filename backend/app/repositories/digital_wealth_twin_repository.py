from sqlalchemy.orm import Session

from app.models.digital_wealth_twin import DigitalWealthTwin
from app.repositories.base_repository import BaseRepository


class DigitalWealthTwinRepository(BaseRepository[DigitalWealthTwin]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, DigitalWealthTwin)
