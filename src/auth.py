import os
import re
import httpx

from authlib.jose import jwt
from authlib.jose.errors import DecodeError
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from public_endpoints_config import PUBLIC_ENDPOINTS
from db import db_execute
from users import create_user

OPENID_CONFIG_URL = os.environ.get("OPENID_CONFIG_URL")

excluded_pattern = re.compile(r"^/docs/.*$")
cached_jwks = None


def add_cors_headers_to_response(response: Response, origin: str):
    response.headers["Access-Control-Allow-Origin"] = origin or "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        excluded_endpoints = [
            "/healthcheck",
            "/login",
            "/signup",
            "/docs",
            "/openapi.json",
        ]
        if (
            request.url.path in excluded_endpoints
            or request.url.path in PUBLIC_ENDPOINTS
            or excluded_pattern.match(request.url.path)
        ):
            return await call_next(request)

        # exclude OPTIONS requests
        if request.method == "OPTIONS":
            return await call_next(request)

        if "Authorization" not in request.headers:
            response = JSONResponse(
                status_code=401, content={"error": "Missing authorization header"}
            )
            return add_cors_headers_to_response(response, request.headers.get("origin"))

        access_token = request.headers["Authorization"].split(" ")[1]
        if not access_token:
            return JSONResponse(
                status_code=401, content={"error": "Missing bearer token"}
            )

        global cached_jwks
        if not cached_jwks:
            if not OPENID_CONFIG_URL:
                response = JSONResponse(
                    status_code=401, content={"error": "Missing openid config url"}
                )
                return add_cors_headers_to_response(
                    response, request.headers.get("origin")
                )

            try:
                openid_config_response = httpx.get(OPENID_CONFIG_URL)
                openid_config_response.raise_for_status()
            except httpx.RequestError:
                response = JSONResponse(
                    status_code=500, content={"error": "Unable to fetch openid config"}
                )
                return add_cors_headers_to_response(
                    response, request.headers.get("origin")
                )

            jwks_uri = openid_config_response.json().get("jwks_uri")
            if not jwks_uri:
                response = JSONResponse(
                    status_code=500,
                    content={"error": "Missing jwks_uri in openid config"},
                )
                return add_cors_headers_to_response(
                    response, request.headers.get("origin")
                )

            try:
                jwks_response = httpx.get(jwks_uri)
                jwks_response.raise_for_status()
            except httpx.RequestError:
                response = JSONResponse(
                    status_code=500, content={"error": "Unable to fetch JWKS data"}
                )
                return add_cors_headers_to_response(
                    response, request.headers.get("origin")
                )

            cached_jwks = jwks_response.json()

        try:
            claims = jwt.decode(
                access_token, key=cached_jwks, claims_options={"alg": "RS256"}
            )

            request.state.current_user_jwt_claims = claims
        except DecodeError:
            response = JSONResponse(status_code=401, content={"error": "Invalid token"})
            return add_cors_headers_to_response(response, request.headers.get("origin"))

        user = db_execute(
            "SELECT * FROM users WHERE sub = :sub",
            {"sub": claims["sub"]},
        ).rows

        if not user:
            create_user(claims)

        return await call_next(request)
