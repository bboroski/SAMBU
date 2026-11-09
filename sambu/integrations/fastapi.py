"""FastAPI router adapter for the renderer-neutral Jiu-Jitsu application model."""
import inspect
import json
from typing import Callable
from ..jiu_jitsu import AccessDenied, JiuJitsuApp, JiuJitsuError

def create_router(app_for_principal: Callable[[str], JiuJitsuApp], principal_resolver: Callable[[object], str | None], *, prefix: str = "/sambu", tags: list[str] | None = None):
    """Create a FastAPI router with host-supplied authentication and per-user state."""
    if not callable(app_for_principal) or not callable(principal_resolver):
        raise TypeError("app_for_principal and principal_resolver must be callable")
    try:
        from fastapi import APIRouter, HTTPException, Request
    except ImportError as exc:
        raise ImportError("FastAPI integration requires the FastAPI optional dependency") from exc
    router = APIRouter(prefix=prefix, tags=tags or ["SAMBU"])

    async def resolve_app(request: Request) -> JiuJitsuApp:
        try:
            principal = principal_resolver(request)
            if inspect.isawaitable(principal): principal = await principal
            if not isinstance(principal, str) or not principal.strip():
                raise HTTPException(status_code=401, detail="authentication_required")
            app = app_for_principal(principal)
            if inspect.isawaitable(app): app = await app
            return app
        except AccessDenied as exc:
            raise HTTPException(status_code=403, detail=str(exc)) from exc
        except JiuJitsuError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    async def read_body(request: Request) -> dict[str, object]:
        try: raw = await request.body()
        except Exception as exc:
            raise HTTPException(status_code=400, detail="unable to read request body") from exc
        if len(raw) > 1_000_000:
            raise HTTPException(status_code=413, detail="request body exceeds 1 MB")
        if not raw: return {}
        try: value = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise HTTPException(status_code=400, detail="request body must be valid UTF-8 JSON") from exc
        if not isinstance(value, dict):
            raise HTTPException(status_code=400, detail="request body must be a JSON object")
        return value

    @router.get("/snapshot")
    async def snapshot(request: Request):
        app = await resolve_app(request)
        return app.snapshot().to_dict()

    @router.post("/navigate")
    async def navigate(request: Request):
        app = await resolve_app(request)
        route = (await read_body(request)).get("route")
        if not isinstance(route, str) or not route:
            raise HTTPException(status_code=400, detail="route must be a non-empty string")
        try:
            app.navigate(route)
            return app.snapshot().to_dict()
        except AccessDenied as exc:
            raise HTTPException(status_code=403, detail=str(exc)) from exc
        except (JiuJitsuError, ValueError, TypeError) as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @router.post("/actions/{action_name}")
    async def dispatch(action_name: str, request: Request):
        app = await resolve_app(request)
        try:
            app.dispatch(action_name, await read_body(request))
            return app.snapshot().to_dict()
        except AccessDenied as exc:
            raise HTTPException(status_code=403, detail=str(exc)) from exc
        except (JiuJitsuError, ValueError, TypeError) as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @router.post("/modals/close")
    async def close_modal(request: Request):
        app = await resolve_app(request)
        try:
            app.modals.close()
            return app.snapshot().to_dict()
        except (JiuJitsuError, ValueError, TypeError) as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @router.post("/modals/{modal_id}")
    async def open_modal(modal_id: str, request: Request):
        app = await resolve_app(request)
        try:
            app.open_modal(modal_id, payload=await read_body(request))
            return app.snapshot().to_dict()
        except AccessDenied as exc:
            raise HTTPException(status_code=403, detail=str(exc)) from exc
        except (JiuJitsuError, ValueError, TypeError) as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    return router

__all__ = ["create_router"]
