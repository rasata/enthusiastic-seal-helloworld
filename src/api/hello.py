from fastapi import APIRouter

router = APIRouter()

@router.get("/hello/{first_name}")
def say_hello(first_name: str) -> dict:
    return {"message": f"Hello {first_name} user"}