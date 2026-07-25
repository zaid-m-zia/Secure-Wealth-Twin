from sqlalchemy.orm import Session

from app.models.fraud import FraudAnalysis
from app.repositories.base_repository import BaseRepository


class FraudAnalysisRepository(BaseRepository[FraudAnalysis]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, FraudAnalysis)
