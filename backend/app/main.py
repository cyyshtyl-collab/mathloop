from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

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


@app.get("/{frontend_path:path}", include_in_schema=False)
def redirect_frontend_paths(frontend_path: str):
    frontend_routes = ("dashboard", "login", "register", "upload", "mistakes", "review", "me")
    if settings.frontend_base_url and (frontend_path == "" or frontend_path.split("/", 1)[0] in frontend_routes):
        target = f"{settings.frontend_base_url.rstrip('/')}/{frontend_path}"
        return RedirectResponse(target)
    return {"detail": "Not Found"}
