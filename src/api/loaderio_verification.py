from fastapi import APIRouter, Response

router = APIRouter()

@router.get("/loaderio-bffbe3f257bed1bcc16ed5e1257bac75.txt")
def loaderio_verification() -> Response:
    content = "loaderio-bffbe3f257bed1bcc16ed5e1257bac75"
    return Response(content=content, media_type="text/plain")