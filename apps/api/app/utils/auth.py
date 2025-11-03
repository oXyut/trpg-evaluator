from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional


try:
    import firebase_admin  # type: ignore
    from firebase_admin import auth as firebase_auth  # type: ignore
    from firebase_admin import credentials  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    firebase_admin = None  # type: ignore
    firebase_auth = None  # type: ignore
    credentials = None  # type: ignore


class FirebaseAuthError(Exception):
    pass


@dataclass
class FirebaseUser:
    uid: str
    email: Optional[str] = None
    email_verified: bool = False


_firebase_initialized = False


def is_auth_disabled() -> bool:
    value = os.getenv("FIREBASE_AUTH_DISABLED", "1").lower()
    return value in {"1", "true", "yes"}


def _ensure_firebase_initialized() -> None:
    global _firebase_initialized
    if _firebase_initialized:
        return
    if firebase_admin is None or firebase_auth is None or credentials is None:
        raise FirebaseAuthError("firebase-admin package is not installed.")
    if firebase_admin._apps:  # type: ignore[attr-defined]
        _firebase_initialized = True
        return

    project_id = os.getenv("FIREBASE_PROJECT_ID")
    credentials_path = os.getenv("FIREBASE_CREDENTIALS_PATH")

    options = {"projectId": project_id} if project_id else None

    if credentials_path:
        cred = credentials.Certificate(credentials_path)
        firebase_admin.initialize_app(cred, options)  # type: ignore[arg-type]
    else:
        firebase_admin.initialize_app(options=options)  # type: ignore[arg-type]
    _firebase_initialized = True


def verify_firebase_token(token: str) -> FirebaseUser:
    if not token:
        raise FirebaseAuthError("Empty token.")
    _ensure_firebase_initialized()
    assert firebase_auth is not None  # for mypy
    try:
        decoded = firebase_auth.verify_id_token(token, check_revoked=True)
    except Exception as exc:  # pragma: no cover - firebase specific errors
        raise FirebaseAuthError(f"Invalid Firebase token: {exc}") from exc

    return FirebaseUser(
        uid=decoded.get("uid") or "",
        email=decoded.get("email"),
        email_verified=decoded.get("email_verified", False),
    )

