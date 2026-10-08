from __future__ import annotations

from pydantic import BaseModel


class LoginRequest(BaseModel):
    tenant_id: str
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    tenant_id: str
    user_id: int
    role: str
    username: str


class MeResponse(BaseModel):
    tenant_id: str
    user_id: int
    role: str
    username: str


class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    text: str
    citations: list[dict[str, object]]
    refused: bool
    reason: str | None
    usage: dict[str, object]
    evidence: list[dict[str, object]]


class AcknowledgeRequest(BaseModel):
    step_ids: list[int]


class ApprovalRequest(BaseModel):
    decision: str  # "approve" | "reject" | "edit"
    comment: str | None = None
    edited_content: dict[str, object] | None = None


class RunStartRequest(BaseModel):
    symptoms: str
    installed_revision: str | None = None


class RunStatusResponse(BaseModel):
    id: str
    status: str
    question: str
    total_tokens: int
    estimated_tokens: bool
    steps: list[dict[str, object]]
