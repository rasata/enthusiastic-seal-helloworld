import os

from fastapi import APIRouter, HTTPException
from fusionauth.fusionauth_client import FusionAuthClient
from models.login import LoginRequest, LoginResponse

router = APIRouter()


@router.post("/login")
def login(login_request: LoginRequest) -> LoginResponse:
    client = FusionAuthClient(
        os.environ.get("FUSIONAUTH_TENANT_API_KEY"), os.environ.get("FUSIONAUTH_URL")
    )
    try:
        response = client.login(
            {
                "loginId": login_request.email,
                "password": login_request.password,
                "applicationId": os.environ.get("FUSIONAUTH_APPLICATION_ID"),
            }
        )
        response_json = response.response.json()
        return {"accessToken": response_json["token"]}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=401, detail="Invalid credentials")
