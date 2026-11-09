"""Flask adapter for the renderer-neutral Jiu-Jitsu application model."""
from __future__ import annotations
from typing import Callable
from ..jiu_jitsu import AccessDenied, JiuJitsuApp, JiuJitsuError

def create_blueprint(app_for_principal: Callable[[str], JiuJitsuApp], principal_resolver: Callable[[], str | None], *, name: str = "sambu", url_prefix: str = "/sambu"):
    """Create a Flask Blueprint using host authentication and user-scoped state."""
    if not callable(app_for_principal) or not callable(principal_resolver):
        raise TypeError("app_for_principal and principal_resolver must be callable")
    try:
        from flask import Blueprint, jsonify, request
    except ImportError as exc:
        raise ImportError("Flask integration requires the Flask optional dependency") from exc
    blueprint = Blueprint(name, __name__, url_prefix=url_prefix)

    def context():
        principal = principal_resolver()
        if not isinstance(principal, str) or not principal.strip():
            return None, (jsonify({"error": "authentication_required"}), 401)
        try:
            return app_for_principal(principal), None
        except AccessDenied as exc:
            return None, (jsonify({"error": str(exc)}), 403)
        except JiuJitsuError as exc:
            return None, (jsonify({"error": str(exc)}), 400)

    def payload():
        value = request.get_json(silent=True)
        if value is None: return {}
        if not isinstance(value, dict): raise ValueError("request body must be a JSON object")
        return value

    def failure(exc):
        status = 403 if isinstance(exc, AccessDenied) else 400
        return jsonify({"error": str(exc)}), status

    @blueprint.get("/snapshot")
    def snapshot():
        app, error = context()
        if error: return error
        return jsonify(app.snapshot().to_dict())

    @blueprint.post("/navigate")
    def navigate():
        app, error = context()
        if error: return error
        try:
            route = payload().get("route")
            if not isinstance(route, str) or not route: raise ValueError("route must be a non-empty string")
            app.navigate(route)
            return jsonify(app.snapshot().to_dict())
        except (JiuJitsuError, ValueError, TypeError) as exc:
            return failure(exc)

    @blueprint.post("/actions/<action_name>")
    def dispatch(action_name: str):
        app, error = context()
        if error: return error
        try:
            app.dispatch(action_name, payload())
            return jsonify(app.snapshot().to_dict())
        except (JiuJitsuError, ValueError, TypeError) as exc:
            return failure(exc)

    @blueprint.post("/modals/<modal_id>")
    def open_modal(modal_id: str):
        app, error = context()
        if error: return error
        try:
            app.open_modal(modal_id, payload=payload())
            return jsonify(app.snapshot().to_dict())
        except (JiuJitsuError, ValueError, TypeError) as exc:
            return failure(exc)

    @blueprint.delete("/modals/current")
    def close_modal():
        app, error = context()
        if error: return error
        try:
            app.modals.close()
            return jsonify(app.snapshot().to_dict())
        except (JiuJitsuError, ValueError, TypeError) as exc:
            return failure(exc)
    return blueprint

__all__ = ["create_blueprint"]
