import os
import uuid

from fastapi import APIRouter, HTTPException
from fusionauth.fusionauth_client import FusionAuthClient
from models.signup import SignupRequest

router = APIRouter()


@router.post("/signup", status_code=204)
def signup(signup_request: SignupRequest) -> None:
    client = FusionAuthClient(
        os.environ.get("FUSIONAUTH_TENANT_API_KEY"), os.environ.get("FUSIONAUTH_URL")
    )
    try:
        user_uuid = str(uuid.uuid4())
        client.register(
            {
                "registration": {
                    "applicationId": os.environ.get("FUSIONAUTH_APPLICATION_ID"),
                },
                "user": {
                    "email": signup_request.email,
                    "password": signup_request.password,
                },
            },
            user_id=user_uuid,
        )
        return None
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=400,
            detail="Unable to initiate signup process. Please try again later.",
        )
