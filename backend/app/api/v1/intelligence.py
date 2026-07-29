import json
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from app.core.dependencies import get_current_user, get_database_session
from sqlalchemy.orm import Session
from app.models.fraud import FraudAnalysis
from app.models.digital_wealth_twin import DigitalWealthTwin
from app.models.recommendation import Recommendation
from app.models.agent_memory import AgentMemory
from app.schemas.common import APIResponse
from app.services.intelligence_service import IntelligenceService
from app.services.runtime_state_service import RuntimeStateService
from app.utils.request_context import get_request_id
from app.utils.responses import build_api_response

router = APIRouter(tags=["intelligence"], dependencies=[Depends(get_current_user)])
service = IntelligenceService()


def _response(message: str, data: object) -> dict[str, object]:
    return build_api_response(status="success", message=message, data=data, request_id=get_request_id())


def _required(data: object, label: str) -> object:
    if data is None:
        raise HTTPException(status_code=404, detail=f"No {label} was found for this customer.")
    return data


@router.get("/customers/{customer_id}/profile", response_model=APIResponse)
def customer_profile(customer_id: str):
    return _response("Customer intelligence profile retrieved successfully.", _required(service.customer_intelligence(customer_id), "intelligence profile"))


@router.get("/customers/{customer_id}/intelligence", response_model=APIResponse)
def customer_intelligence(customer_id: str):
    return _response("Customer intelligence retrieved successfully.", _required(service.customer_intelligence(customer_id), "intelligence profile"))


@router.get("/behavior/{customer_id}", response_model=APIResponse)
def behavior(customer_id: str):
    return _response("Customer behavior retrieved successfully.", _required(service.customer_behavior(customer_id), "behavior profile"))


@router.get("/behavioral-intelligence/{customer_id}", response_model=APIResponse)
def behavioral_intelligence(customer_id: str):
    return _response("Behavioral intelligence retrieved successfully.", _required(service.behavioral_intelligence(customer_id), "behavioral intelligence"))


@router.get("/fraud/score/{transaction_id}", response_model=APIResponse)
@router.get("/fraud/explanation/{transaction_id}", response_model=APIResponse)
def fraud_score(transaction_id: str, session: Session = Depends(get_database_session)):
    runtime = session.query(FraudAnalysis).filter(FraudAnalysis.transaction_id == transaction_id).order_by(FraudAnalysis.updated_at.desc()).first()
    if runtime is not None and runtime.fraud_score_placeholder is not None:
        return _response("Fraud analysis retrieved successfully.", {
            "transaction_id": transaction_id,
            "fraud_score": runtime.fraud_score_placeholder,
            "risk_level": runtime.anomaly_reason_placeholder,
            "explanation": runtime.explanation_placeholder,
            "evidence": runtime.evidence_json or {},
        })
    raise HTTPException(status_code=404, detail="No persisted fraud analysis was found for this transaction.")


@router.get("/fraud/history/{customer_id}", response_model=APIResponse)
def fraud_history(customer_id: str, session: Session = Depends(get_database_session)):
    analyses = session.query(FraudAnalysis).filter(FraudAnalysis.customer_id == customer_id).order_by(FraudAnalysis.updated_at.desc()).all()
    return _response("Fraud history retrieved successfully.", [{"transaction_id": item.transaction_id, "fraud_score": item.fraud_score_placeholder, "risk_level": item.anomaly_reason_placeholder, "explanation": item.explanation_placeholder, "evidence": item.evidence_json or {}} for item in analyses])


@router.get("/fraud/analytics", response_model=APIResponse)
@router.get("/fraud/risk-summary/{customer_id}", response_model=APIResponse)
def fraud_analytics(customer_id: Optional[str] = None, session: Session = Depends(get_database_session)):
    return _response("Fraud analytics retrieved successfully.", RuntimeStateService(session).fraud_analytics(customer_id))


@router.get("/wealth/{customer_id}", response_model=APIResponse)
@router.get("/wealth/twin/{customer_id}", response_model=APIResponse)
def wealth_twin(customer_id: str, session: Session = Depends(get_database_session)):
    runtime = session.get(DigitalWealthTwin, customer_id)
    if runtime is not None and runtime.financial_dna_json:
        return _response("Digital Wealth Twin retrieved successfully.", {**runtime.financial_dna_json, "financial_health_score": runtime.health_score_placeholder, "financial_personality": runtime.wealth_summary})
    return _response("Digital Wealth Twin retrieved successfully.", _required(RuntimeStateService(session).wealth_analytics(customer_id), "Digital Wealth Twin"))


@router.get("/wealth/{customer_id}/health", response_model=APIResponse)
@router.get("/wealth/{customer_id}/lifestyle", response_model=APIResponse)
@router.get("/wealth/{customer_id}/personality", response_model=APIResponse)
@router.get("/wealth/{customer_id}/metrics", response_model=APIResponse)
def wealth_metrics(customer_id: str, session: Session = Depends(get_database_session)):
    return _response("Digital Wealth Twin metrics retrieved successfully.", _required(RuntimeStateService(session).wealth_analytics(customer_id), "Digital Wealth Twin"))


@router.get("/recommendations/{customer_id}", response_model=APIResponse)
@router.get("/recommendations/{customer_id}/ranking", response_model=APIResponse)
@router.get("/recommendations/{customer_id}/explanations", response_model=APIResponse)
def recommendations(customer_id: str, session: Session = Depends(get_database_session)):
    runtime = session.query(Recommendation).filter(Recommendation.customer_id == customer_id).order_by(Recommendation.updated_at.desc()).all()
    if runtime:
        return _response("Financial recommendations retrieved successfully.", [{"recommendation": item.recommendation_text, "priority": item.priority, "status": item.status} for item in runtime])
    return _response("Financial recommendations retrieved successfully.", [])


@router.get("/agentic-ai/{customer_id}", response_model=APIResponse)
@router.get("/agentic-ai/{customer_id}/decision", response_model=APIResponse)
@router.get("/agentic-ai/{customer_id}/reasoning", response_model=APIResponse)
@router.get("/agentic-ai/{customer_id}/confidence", response_model=APIResponse)
@router.get("/agentic-ai/{customer_id}/evidence", response_model=APIResponse)
@router.get("/agentic-ai/{customer_id}/risk", response_model=APIResponse)
def agentic_decision(customer_id: str, session: Session = Depends(get_database_session)):
    runtime = session.query(AgentMemory).filter(AgentMemory.customer_id == customer_id).first()
    if runtime is not None and runtime.conversation_memory:
        return _response("Agentic AI decision retrieved successfully.", json.loads(runtime.conversation_memory))
    raise HTTPException(status_code=404, detail="No persisted agent decision was found for this account.")


@router.get("/dashboard/{customer_id}", response_model=APIResponse)
@router.get("/dashboard/{customer_id}/overview", response_model=APIResponse)
def dashboard(customer_id: str, session: Session = Depends(get_database_session)):
    return _response("Dashboard overview retrieved successfully.", _required(RuntimeStateService(session).dashboard(customer_id), "dashboard data"))


@router.get("/analytics/behavior", response_model=APIResponse)
def behavior_analytics(customer_id: Optional[str] = None, session: Session = Depends(get_database_session)):
    return _response("Behavior analytics retrieved successfully.", RuntimeStateService(session).behavior_analytics(customer_id))


@router.get("/analytics/fraud", response_model=APIResponse)
def analytics_fraud(customer_id: Optional[str] = None, session: Session = Depends(get_database_session)):
    return _response("Fraud analytics retrieved successfully.", RuntimeStateService(session).fraud_analytics(customer_id))


@router.get("/analytics/wealth", response_model=APIResponse)
def analytics_wealth(customer_id: Optional[str] = None, session: Session = Depends(get_database_session)):
    return _response("Wealth analytics retrieved successfully.", RuntimeStateService(session).wealth_analytics(customer_id))


@router.get("/analytics/transactions", response_model=APIResponse)
def analytics_transactions(customer_id: Optional[str] = None, session: Session = Depends(get_database_session)):
    return _response("Transaction analytics retrieved successfully.", RuntimeStateService(session).transaction_analytics(customer_id))


@router.get("/analytics/recommendations", response_model=APIResponse)
def analytics_recommendations(customer_id: Optional[str] = None, session: Session = Depends(get_database_session)):
    return _response("Recommendation analytics retrieved successfully.", RuntimeStateService(session).recommendation_analytics(customer_id))


@router.get("/reports/{customer_id}", response_model=APIResponse)
def report(customer_id: str):
    return _response("Structured report retrieved successfully.", _required(service.report(customer_id), "report"))
