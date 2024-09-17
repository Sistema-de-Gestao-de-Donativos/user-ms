from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/", status_code=200)
def health() -> dict[str, str]:
    return {"status": "ok"}
