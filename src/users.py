from fastapi import Request
from authlib.jose import JWTClaims
from db import db_execute, format_result_set


def create_user(claims: JWTClaims):
    sub = claims["sub"]
    db_execute(
        "INSERT INTO users (sub) VALUES (:sub)",
        {"sub": sub},
    )


def get_user_id_from_request(request: Request):
    user_sub = request.state.current_user_jwt_claims["sub"]
    user = db_execute(
        "SELECT id FROM users WHERE sub = :sub",
        {"sub": user_sub},
    )
    user_rows = format_result_set(user)
    return user_rows[0]["id"] if user_rows else None
