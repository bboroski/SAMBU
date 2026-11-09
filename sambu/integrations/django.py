"""Django URL adapter for the renderer-neutral Jiu-Jitsu application model."""
from __future__ import annotations
import json
from typing import Callable
from ..jiu_jitsu import AccessDenied, JiuJitsuApp, JiuJitsuError

def create_urlpatterns(app_for_principal: Callable[[str], JiuJitsuApp], principal_resolver: Callable[[object], str | None]):
    """Return Django URL patterns; the host supplies authentication and persistence."""
    if not callable(app_for_principal) or not callable(principal_resolver):
        raise TypeError("app_for_principal and principal_resolver must be callable")
    try:
        from django.http import JsonResponse
        from django.urls import path
        from django.views.decorators.http import require_GET, require_POST
    except ImportError as exc:
        raise ImportError("Django integration requires the Django optional dependency") from exc

    def parse_body(request):
        raw = request.body
        if len(raw) > 1_000_000: raise ValueError("request body exceeds 1 MB")
        if not raw: return {}
        try: value = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError("request body must be valid UTF-8 JSON") from exc
        if not isinstance(value, dict): raise ValueError("request body must be a JSON object")
        return value

    def execute(request, operation, *, needs_body):
        try:
            principal = principal_resolver(request)
            if not isinstance(principal, str) or not principal.strip():
                return JsonResponse({"error": "authentication_required"}, status=401)
            app = app_for_principal(principal)
            operation(app, parse_body(request) if needs_body else {})
            return JsonResponse(app.snapshot().to_dict())
        except AccessDenied as exc:
            return JsonResponse({"error": str(exc)}, status=403)
        except (JiuJitsuError, ValueError, TypeError, KeyError) as exc:
            return JsonResponse({"error": str(exc)}, status=400)

    @require_GET
    def snapshot(request):
        return execute(request, lambda app, body: None, needs_body=False)

    @require_POST
    def navigate(request):
        def operation(app, body):
            route = body.get("route")
            if not isinstance(route, str) or not route: raise ValueError("route must be a non-empty string")
            app.navigate(route)
        return execute(request, operation, needs_body=True)

    @require_POST
    def dispatch(request, action_name):
        return execute(request, lambda app, body: app.dispatch(action_name, body), needs_body=True)

    @require_POST
    def open_modal(request, modal_id):
        return execute(request, lambda app, body: app.open_modal(modal_id, payload=body), needs_body=True)

    @require_POST
    def close_modal(request):
        return execute(request, lambda app, body: app.modals.close(), needs_body=False)

    return [
        path("snapshot/", snapshot, name="sambu-snapshot"),
        path("navigate/", navigate, name="sambu-navigate"),
        path("actions/<str:action_name>/", dispatch, name="sambu-action"),
        path("modals/close/", close_modal, name="sambu-close-modal"),
        path("modals/<str:modal_id>/", open_modal, name="sambu-open-modal"),
    ]

__all__ = ["create_urlpatterns"]
