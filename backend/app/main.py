from fastapi import Depends, FastAPI, HTTPException, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from .ai_service import generate_triage_recommendation
from .config import settings
from .models import TokenResponse, TriageRequest, TriageResponse, UserAuthRequest
from .security import authenticate_user, create_access_token

app = FastAPI(title=settings.app_name, version=settings.api_version)
security_scheme = HTTPBearer()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security_scheme),
) -> dict:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        username: str | None = payload.get("sub")
        role: str | None = payload.get("role")
        if username is None or role is None:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
        return {"username": username, "role": role}
    except JWTError as exc:
        raise HTTPException(status_code=401, detail="Token verification failed") from exc


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": settings.app_name}


@app.post("/auth/token", response_model=TokenResponse)
def login(payload: UserAuthRequest) -> TokenResponse:
    user = authenticate_user(payload.username, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(subject=user["username"], role=user["role"])
    return TokenResponse(access_token=token)


@app.post("/api/triage", response_model=TriageResponse)
def triage(
    request: TriageRequest,
    _: dict = Depends(get_current_user),
) -> TriageResponse:
    return generate_triage_recommendation(request)
