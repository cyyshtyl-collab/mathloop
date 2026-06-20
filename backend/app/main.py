from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, mistakes
from app.core.config import get_settings

settings = get_settings()

if settings.environment == "production" and settings.jwt_secret_key == "change_me_to_a_long_random_secret":
    raise RuntimeError("生产环境必须设置 JWT_SECRET_KEY")

app = FastAPI(title="MathLoop Junior API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(mistakes.router)


@app.get("/health")
def health():
    return {"ok": True, "version": "1.0.0"}
