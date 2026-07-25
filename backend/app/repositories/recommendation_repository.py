from sqlalchemy.orm import Session

from app.models.recommendation import Recommendation
from app.repositories.base_repository import BaseRepository


class RecommendationRepository(BaseRepository[Recommendation]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Recommendation)
