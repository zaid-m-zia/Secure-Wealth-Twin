from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from app.core.dependencies import get_current_user
from app.schemas.common import APIResponse
from app.services.intelligence_service import IntelligenceService
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
def fraud_score(transaction_id: str):
    return _response("Fraud analysis retrieved successfully.", _required(service.fraud_score(transaction_id), "fraud analysis"))


@router.get("/fraud/history/{customer_id}", response_model=APIResponse)
def fraud_history(customer_id: str):
    return _response("Fraud history retrieved successfully.", service.fraud_history(customer_id))


@router.get("/fraud/analytics", response_model=APIResponse)
@router.get("/fraud/risk-summary/{customer_id}", response_model=APIResponse)
def fraud_analytics(customer_id: Optional[str] = None):
    return _response("Fraud analytics retrieved successfully.", service.fraud_analytics(customer_id))


@router.get("/wealth/{customer_id}", response_model=APIResponse)
@router.get("/wealth/twin/{customer_id}", response_model=APIResponse)
def wealth_twin(customer_id: str):
    return _response("Digital Wealth Twin retrieved successfully.", _required(service.wealth_twin(customer_id), "Digital Wealth Twin"))


@router.get("/wealth/{customer_id}/health", response_model=APIResponse)
@router.get("/wealth/{customer_id}/lifestyle", response_model=APIResponse)
@router.get("/wealth/{customer_id}/personality", response_model=APIResponse)
@router.get("/wealth/{customer_id}/metrics", response_model=APIResponse)
def wealth_metrics(customer_id: str):
    return _response("Digital Wealth Twin metrics retrieved successfully.", _required(service.wealth_twin(customer_id), "Digital Wealth Twin"))


@router.get("/recommendations/{customer_id}", response_model=APIResponse)
@router.get("/recommendations/{customer_id}/ranking", response_model=APIResponse)
@router.get("/recommendations/{customer_id}/explanations", response_model=APIResponse)
def recommendations(customer_id: str):
    return _response("Financial recommendations retrieved successfully.", service.recommendations(customer_id))


@router.get("/agentic-ai/{customer_id}", response_model=APIResponse)
@router.get("/agentic-ai/{customer_id}/decision", response_model=APIResponse)
@router.get("/agentic-ai/{customer_id}/reasoning", response_model=APIResponse)
@router.get("/agentic-ai/{customer_id}/confidence", response_model=APIResponse)
@router.get("/agentic-ai/{customer_id}/evidence", response_model=APIResponse)
@router.get("/agentic-ai/{customer_id}/risk", response_model=APIResponse)
def agentic_decision(customer_id: str):
    return _response("Agentic AI decision retrieved successfully.", _required(service.decision(customer_id), "agentic decision"))


@router.get("/dashboard/{customer_id}", response_model=APIResponse)
@router.get("/dashboard/{customer_id}/overview", response_model=APIResponse)
def dashboard(customer_id: str):
    return _response("Dashboard overview retrieved successfully.", _required(service.dashboard(customer_id), "dashboard data"))


@router.get("/analytics/behavior", response_model=APIResponse)
def behavior_analytics():
    return _response("Behavior analytics retrieved successfully.", service.behavior_analytics())


@router.get("/analytics/fraud", response_model=APIResponse)
def analytics_fraud():
    return _response("Fraud analytics retrieved successfully.", service.fraud_analytics())


@router.get("/analytics/wealth", response_model=APIResponse)
def analytics_wealth():
    return _response("Wealth analytics retrieved successfully.", service.wealth_analytics())


@router.get("/analytics/transactions", response_model=APIResponse)
def analytics_transactions():
    return _response("Transaction analytics retrieved successfully.", service.transaction_analytics())


@router.get("/analytics/recommendations", response_model=APIResponse)
def analytics_recommendations():
    return _response("Recommendation analytics retrieved successfully.", service.recommendation_analytics())


@router.get("/reports/{customer_id}", response_model=APIResponse)
def report(customer_id: str):
    return _response("Structured report retrieved successfully.", _required(service.report(customer_id), "report"))
