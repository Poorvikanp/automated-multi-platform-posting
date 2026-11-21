import logging

from fastapi import Depends, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.platforms import default_platforms
from app.schemas import PostingRequest, PostingResponse
from app.services.posting_service import post_to_all

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("posting")

app = FastAPI(
    title="Automated Multi-Platform Posting System",
    description="POST one short message with one CTA link; it is published to several platforms via their APIs.",
    version="1.0.0",
)


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    errors = [
        {
            "field": ".".join(str(p) for p in err["loc"][1:]) or "body",
            "message": err["msg"].removeprefix("Value error, "),
        }
        for err in exc.errors()
    ]
    return JSONResponse(status_code=422, content={"success": False, "errors": errors})


@app.post("/posting", response_model=PostingResponse)
async def posting(payload: PostingRequest, platforms=Depends(default_platforms)):
    results = await post_to_all(payload.message, platforms)
    for r in results:
        logger.info("%s -> %s %s", r.platform, r.status, r.posted_url or r.error)
    return PostingResponse(success=any(r.status == "success" for r in results), results=results)


@app.get("/health", include_in_schema=False)
async def health():
    return {"status": "ok"}
