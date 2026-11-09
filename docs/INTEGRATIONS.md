# Django, Flask and FastAPI integration

SAMBU's Jiu-Jitsu framework describes renderer-neutral views, controller actions, modals and RBAC permissions. Optional adapters expose those objects through common Python web frameworks.

Install only the adapter you use:

~~~bash
python -m pip install -e ".[flask]"
python -m pip install -e ".[django]"
python -m pip install -e ".[fastapi]"
~~~

## Flask

~~~python
from flask import Flask
from sambu.integrations.flask import create_blueprint

app = Flask(__name__)
blueprint = create_blueprint(
    app_for_principal=load_or_create_ui_for_user,
    principal_resolver=lambda: current_authenticated_user_id(),
)
app.register_blueprint(blueprint)
~~~

Routes: GET /sambu/snapshot, POST /sambu/navigate, POST /sambu/actions/<action>, POST /sambu/modals/<id>, and DELETE /sambu/modals/current.

## Django

~~~python
from django.urls import include, path
from sambu.integrations.django import create_urlpatterns

sambu_patterns = create_urlpatterns(
    app_for_principal=load_or_create_ui_for_user,
    principal_resolver=lambda request: request.user.get_username()
        if request.user.is_authenticated else None,
)
urlpatterns = [path("sambu/", include(sambu_patterns))]
~~~

The host project must retain Django authentication and CSRF middleware. Mutating UI routes use POST.

## FastAPI

~~~python
from fastapi import FastAPI, Request
from sambu.integrations.fastapi import create_router

async def principal_from_request(request: Request) -> str | None:
    return authenticated_user_id(request)  # implement with your auth layer

router = create_router(load_or_create_ui_for_user, principal_from_request)
app = FastAPI()
app.include_router(router)
~~~

Routes mirror the Flask adapter under /sambu.

## Shared security contract

- The principal resolver is the sole identity source; clients cannot nominate another user in JSON.
- The host supplies a per-principal JiuJitsuApp and persistence strategy. Adapters do not create a database, session store or authentication system.
- Jiu-Jitsu checks permissions on route navigation, controller dispatch and modal opening. Host APIs must also enforce authorization at every protected data boundary.
- Add CSRF protection where cookie authentication is used, rate limits where appropriate, and HTTPS in deployment.
- Request bodies are JSON objects; Django and FastAPI adapters cap parsed body size at 1 MB.
- Adapters return serialized view snapshots. They do not ship a browser renderer, execute arbitrary JavaScript, run user-supplied SAMBU source, or perform background jobs.

For a UI control with two named actions, use DualActionButton and register two handlers with ViewController.dual_action(). The caller must specify intent as primary or secondary; ambiguous requests fail closed.
