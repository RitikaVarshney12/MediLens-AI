import time
from threading import Lock

import httpx
from fastapi import Header, HTTPException, status
from jose import JWTError, jwt

from app.core.config import settings

# Supabase's new JWT Signing Keys are asymmetric (ES256/RS256) and published
# at this JWKS endpoint, rather than a single shared HS256 secret. Keys can
# rotate, so the cache is refreshed on a TTL and also force-refreshed once
# if a token's `kid` isn't found (covers rotation between cache refreshes).
_JWKS_CACHE: dict[str, object] = {"keys": [], "fetched_at": 0.0}
_JWKS_TTL_SECONDS = 3600
_jwks_lock = Lock()


def _jwks_url() -> str:
    return f"{settings.SUPABASE_URL}/auth/v1/.well-known/jwks.json"


def _fetch_jwks() -> list[dict]:
    response = httpx.get(_jwks_url(), timeout=10.0)
    response.raise_for_status()
    return response.json().get("keys", [])


def _get_jwks(force_refresh: bool = False) -> list[dict]:
    with _jwks_lock:
        is_stale = time.time() - _JWKS_CACHE["fetched_at"] > _JWKS_TTL_SECONDS
        if force_refresh or is_stale or not _JWKS_CACHE["keys"]:
            try:
                _JWKS_CACHE["keys"] = _fetch_jwks()
                _JWKS_CACHE["fetched_at"] = time.time()
            except httpx.HTTPError as exc:
                if not _JWKS_CACHE["keys"]:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Unable to fetch Supabase signing keys",
                    ) from exc
        return _JWKS_CACHE["keys"]  # type: ignore[return-value]


def _find_key(kid: str, force_refresh: bool = False) -> dict | None:
    for key in _get_jwks(force_refresh=force_refresh):
        if key.get("kid") == kid:
            return key
    return None


def get_current_user_id(authorization: str = Header(...)) -> str:
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token",
        )

    token = authorization.removeprefix("Bearer ").strip()

    try:
        unverified_header = jwt.get_unverified_header(token)
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token header",
        ) from exc

    kid = unverified_header.get("kid")
    alg = unverified_header.get("alg", "ES256")

    if kid:
        # New Supabase projects: asymmetric key (ES256/RS256), verified via JWKS.
        signing_key = _find_key(kid) or _find_key(kid, force_refresh=True)
        if signing_key is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unknown signing key",
            )
        try:
            payload = jwt.decode(
                token,
                signing_key,
                algorithms=[signing_key.get("alg", alg)],
                audience="authenticated",
            )
        except JWTError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            ) from exc
    else:
        # Legacy Supabase projects: shared HS256 secret, no `kid` in the header.
        if not settings.SUPABASE_JWT_SECRET:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Server is not configured to verify legacy HS256 tokens",
            )
        try:
            payload = jwt.decode(
                token,
                settings.SUPABASE_JWT_SECRET,
                algorithms=["HS256"],
                audience="authenticated",
            )
        except JWTError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            ) from exc

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing subject claim",
        )

    return user_id