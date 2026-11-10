"""Jiu-Jitsu: visual views, MVC controllers, modal flows and inherited RBAC roles.

The framework is renderer-neutral: it exports a safe serializable view tree for
web, desktop or mobile renderers. It does not execute arbitrary UI code.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Mapping


class JiuJitsuError(RuntimeError):
    """Base error for view, controller, modal and authorization failures."""


class AccessDenied(JiuJitsuError):
    """Raised when a principal lacks a required permission."""


@dataclass(frozen=True, slots=True)
class Role:
    name: str
    grants: frozenset[str] = frozenset()
    denies: frozenset[str] = frozenset()
    inherits: tuple[str, ...] = ()


class RoleManager:
    """RBAC registry with role inheritance and explicit-deny precedence."""

    def __init__(self) -> None:
        self._roles: dict[str, Role] = {}
        self._assignments: dict[str, set[str]] = {}

    @property
    def roles(self) -> Mapping[str, Role]:
        return dict(self._roles)

    def add_role(self, role: Role) -> "RoleManager":
        if not role.name.strip():
            raise ValueError("role name cannot be empty")
        if role.name in self._roles:
            raise ValueError(f"role {role.name!r} is already registered")
        self._roles[role.name] = role
        try:
            self._expanded_roles((role.name,))
        except Exception:
            del self._roles[role.name]
            raise
        return self

    def assign(self, principal: str, role_name: str) -> "RoleManager":
        if not principal.strip():
            raise ValueError("principal cannot be empty")
        if role_name not in self._roles:
            raise KeyError(f"unknown role {role_name!r}")
        self._assignments.setdefault(principal, set()).add(role_name)
        return self

    def revoke(self, principal: str, role_name: str) -> None:
        self._assignments.get(principal, set()).discard(role_name)

    def assigned_roles(self, principal: str) -> tuple[str, ...]:
        return tuple(sorted(self._assignments.get(principal, set())))

    def _expanded_roles(self, names: tuple[str, ...]) -> tuple[Role, ...]:
        found: list[Role] = []
        visited: set[str] = set()
        active: set[str] = set()

        def visit(name: str) -> None:
            if name in active:
                raise ValueError(f"role inheritance cycle detected at {name!r}")
            if name in visited:
                return
            role = self._roles.get(name)
            if role is None:
                raise ValueError(f"role {name!r} inherits an unknown role")
            active.add(name)
            for parent in role.inherits:
                visit(parent)
            active.remove(name)
            visited.add(name)
            found.append(role)

        for name in names:
            visit(name)
        return tuple(found)

    @staticmethod
    def _matches(pattern: str, permission: str) -> bool:
        if pattern == "*":
            return True
        if pattern.endswith(":*"):
            return permission.startswith(pattern[:-1])
        return pattern == permission

    def authorize(self, principal: str, permission: str) -> bool:
        roles = self._expanded_roles(tuple(sorted(self._assignments.get(principal, set()))))
        grants = {item for role in roles for item in role.grants}
        denies = {item for role in roles for item in role.denies}
        if any(self._matches(rule, permission) for rule in denies):
            return False
        return any(self._matches(rule, permission) for rule in grants)

    def require(self, principal: str, permission: str) -> None:
        if not self.authorize(principal, permission):
            raise AccessDenied(
                f"principal {principal!r} is not authorized for {permission!r}"
            )


def _serializable(value: object) -> object:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Mapping):
        return {str(key): _serializable(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_serializable(item) for item in value]
    raise TypeError(f"view properties must be serializable, got {type(value).__name__}")


@dataclass(frozen=True, slots=True)
class ViewNode:
    identifier: str
    kind: str
    props: Mapping[str, object] = field(default_factory=dict)
    children: tuple["ViewNode", ...] = ()

    def __post_init__(self) -> None:
        if not self.identifier.strip() or not self.kind.strip():
            raise ValueError("view node identifier and kind are required")
        if len({child.identifier for child in self.children}) != len(self.children):
            raise ValueError("sibling view node identifiers must be unique")
        _serializable(self.props)

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.identifier,
            "type": self.kind,
            "props": _serializable(self.props),
            "children": [child.to_dict() for child in self.children],
        }


@dataclass(frozen=True, slots=True)
class DualActionButton:
    """Renderer-neutral button exposing two explicitly named action paths."""

    identifier: str
    label: str
    primary_action: str
    secondary_action: str
    default_intent: str = "primary"
    primary_label: str | None = None
    secondary_label: str | None = None

    def __post_init__(self) -> None:
        if not all(value.strip() for value in (
            self.identifier, self.label, self.primary_action, self.secondary_action,
        )):
            raise ValueError("dual-action button identifiers, labels, and actions are required")
        if self.primary_action == self.secondary_action:
            raise ValueError("dual-action button actions must be distinct")
        if self.default_intent not in {"primary", "secondary"}:
            raise ValueError("default_intent must be 'primary' or 'secondary'")

    def to_node(self) -> ViewNode:
        return ViewNode(
            self.identifier, "dual_action_button",
            {
                "label": self.label,
                "default_intent": self.default_intent,
                "actions": {
                    "primary": {"name": self.primary_action, "label": self.primary_label or self.primary_action},
                    "secondary": {"name": self.secondary_action, "label": self.secondary_label or self.secondary_action},
                },
            },
        )


@dataclass(frozen=True, slots=True)
class ViewDefinition:
    route: str
    title: str
    root: ViewNode
    permission: str | None = None


@dataclass(frozen=True, slots=True)
class ModalDefinition:
    identifier: str
    root: ViewNode
    permission: str | None = None
    dismissible: bool = True


@dataclass(frozen=True, slots=True)
class ModalFrame:
    modal_id: str
    payload: Mapping[str, object]
    return_route: str | None


@dataclass(frozen=True, slots=True)
class ViewSnapshot:
    route: str | None
    view: Mapping[str, object] | None
    modals: tuple[Mapping[str, object], ...]
    state: Mapping[str, object]

    def to_dict(self) -> dict[str, object]:
        return {
            "route": self.route,
            "view": self.view,
            "modals": list(self.modals),
            "state": _serializable(self.state),
        }


ActionHandler = Callable[["ControllerContext", Mapping[str, object]], object]


@dataclass(slots=True)
class ControllerContext:
    principal: str
    roles: RoleManager
    state: dict[str, object]
    route: str | None

    def require(self, permission: str) -> None:
        self.roles.require(self.principal, permission)


class ViewController:
    """Explicit action-to-handler controller; unknown actions are rejected."""

    def __init__(self, name: str) -> None:
        if not name.strip():
            raise ValueError("controller name cannot be empty")
        self.name = name
        self._actions: dict[str, tuple[ActionHandler, str | None]] = {}
        self._dual_actions: dict[str, dict[str, tuple[ActionHandler, str | None]]] = {}

    def action(
        self,
        name: str,
        handler: ActionHandler,
        *,
        permission: str | None = None,
    ) -> "ViewController":
        if not name.strip():
            raise ValueError("action name cannot be empty")
        if name in self._actions or name in self._dual_actions:
            raise ValueError(f"action {name!r} is already registered")
        self._actions[name] = (handler, permission)
        return self

    def dual_action(
        self,
        name: str,
        primary: ActionHandler,
        secondary: ActionHandler,
        *,
        primary_permission: str | None = None,
        secondary_permission: str | None = None,
    ) -> "ViewController":
        """Register two separately authorized branches under one UI action ID."""
        if not name.strip():
            raise ValueError("dual action name cannot be empty")
        if name in self._actions or name in self._dual_actions:
            raise ValueError(f"action {name!r} is already registered")
        self._dual_actions[name] = {
            "primary": (primary, primary_permission),
            "secondary": (secondary, secondary_permission),
        }
        return self

    def dispatch(
        self,
        action_name: str,
        context: ControllerContext,
        payload: Mapping[str, object] | None = None,
    ) -> object:
        body = payload or {}
        if action_name in self._dual_actions:
            intent = body.get("intent")
            if intent not in {"primary", "secondary"}:
                raise JiuJitsuError(
                    f"dual action {action_name!r} requires intent 'primary' or 'secondary'"
                )
            handler, permission = self._dual_actions[action_name][intent]
            action_payload = {key: value for key, value in body.items() if key != "intent"}
        else:
            try:
                handler, permission = self._actions[action_name]
            except KeyError as exc:
                raise JiuJitsuError(
                    f"controller {self.name!r} has no action {action_name!r}"
                ) from exc
            action_payload = body
        if permission:
            context.require(permission)
        return handler(context, action_payload)


class ModalManager:
    """Stack-based modal workflow with access checks and deterministic dismissal."""

    def __init__(self, roles: RoleManager) -> None:
        self.roles = roles
        self._definitions: dict[str, ModalDefinition] = {}
        self._stack: list[ModalFrame] = []

    @property
    def stack(self) -> tuple[ModalFrame, ...]:
        return tuple(self._stack)

    def register(self, definition: ModalDefinition) -> "ModalManager":
        if definition.identifier in self._definitions:
            raise ValueError(f"modal {definition.identifier!r} is already registered")
        self._definitions[definition.identifier] = definition
        return self

    def open(
        self,
        modal_id: str,
        principal: str,
        *,
        payload: Mapping[str, object] | None = None,
        return_route: str | None = None,
    ) -> ModalFrame:
        try:
            definition = self._definitions[modal_id]
        except KeyError as exc:
            raise JiuJitsuError(f"unknown modal {modal_id!r}") from exc
        if definition.permission:
            self.roles.require(principal, definition.permission)
        safe_payload = _serializable(payload or {})
        frame = ModalFrame(modal_id, safe_payload, return_route)  # type: ignore[arg-type]
        self._stack.append(frame)
        return frame

    def close(self, *, force: bool = False) -> ModalFrame:
        if not self._stack:
            raise JiuJitsuError("modal stack is empty")
        frame = self._stack[-1]
        definition = self._definitions[frame.modal_id]
        if not definition.dismissible and not force:
            raise JiuJitsuError(f"modal {frame.modal_id!r} cannot be dismissed by the user")
        return self._stack.pop()

    def current(self) -> ModalDefinition | None:
        return self._definitions[self._stack[-1].modal_id] if self._stack else None

    def render_stack(self) -> tuple[Mapping[str, object], ...]:
        return tuple({
            "id": frame.modal_id,
            "view": self._definitions[frame.modal_id].root.to_dict(),
            "payload": _serializable(frame.payload),
            "return_route": frame.return_route,
            "dismissible": self._definitions[frame.modal_id].dismissible,
        } for frame in self._stack)


class JiuJitsuApp:
    """Small MVC composition root: routes, controllers, state, RBAC and modals."""

    def __init__(self, principal: str, roles: RoleManager | None = None) -> None:
        if not principal.strip():
            raise ValueError("principal cannot be empty")
        self.principal = principal
        self.roles = roles or RoleManager()
        self._views: dict[str, ViewDefinition] = {}
        self._controllers: dict[str, ViewController] = {}
        self.state: dict[str, object] = {}
        self.current_route: str | None = None
        self.modals = ModalManager(self.roles)

    def register_view(self, view: ViewDefinition) -> "JiuJitsuApp":
        if not view.route.startswith("/"):
            raise ValueError("view route must start with '/'")
        if view.route in self._views:
            raise ValueError(f"view route {view.route!r} is already registered")
        self._views[view.route] = view
        return self

    def register_controller(self, route: str, controller: ViewController) -> "JiuJitsuApp":
        if route not in self._views:
            raise KeyError(f"register the view for route {route!r} before its controller")
        if route in self._controllers:
            raise ValueError(f"controller for route {route!r} is already registered")
        self._controllers[route] = controller
        return self

    def navigate(self, route: str) -> ViewSnapshot:
        try:
            view = self._views[route]
        except KeyError as exc:
            raise JiuJitsuError(f"unknown route {route!r}") from exc
        if view.permission:
            self.roles.require(self.principal, view.permission)
        self.current_route = route
        return self.snapshot()

    def dispatch(self, action: str, payload: Mapping[str, object] | None = None) -> object:
        if self.current_route is None:
            raise JiuJitsuError("navigate to a view before dispatching controller actions")
        controller = self._controllers.get(self.current_route)
        if controller is None:
            raise JiuJitsuError(f"no controller registered for {self.current_route!r}")
        context = ControllerContext(
            principal=self.principal,
            roles=self.roles,
            state=self.state,
            route=self.current_route,
        )
        return controller.dispatch(action, context, payload)

    def open_modal(
        self,
        modal_id: str,
        *,
        payload: Mapping[str, object] | None = None,
    ) -> ModalFrame:
        return self.modals.open(
            modal_id, self.principal, payload=payload, return_route=self.current_route,
        )

    def snapshot(self) -> ViewSnapshot:
        view = self._views.get(self.current_route) if self.current_route else None
        return ViewSnapshot(
            route=self.current_route,
            view=view.root.to_dict() if view else None,
            modals=self.modals.render_stack(),
            state=_serializable(self.state),  # type: ignore[arg-type]
        )


class JiuJitsu:
    """Namespace-style factory for a UI/MVC application."""

    @staticmethod
    def app(principal: str, roles: RoleManager | None = None) -> JiuJitsuApp:
        return JiuJitsuApp(principal, roles)


__all__ = [
    "JiuJitsuError", "AccessDenied", "Role", "RoleManager", "ViewNode",
    "DualActionButton", "ViewDefinition", "ModalDefinition", "ModalFrame", "ViewSnapshot",
    "ControllerContext", "ViewController", "ModalManager", "JiuJitsuApp", "JiuJitsu",
]

# Canonical MCL terminology; the historical symbol remains supported.
AccessControlledApplication = JiuJitsuApp

# Canonical MCL terminology; the historical symbol remains supported.
AccessComposition = JiuJitsu
