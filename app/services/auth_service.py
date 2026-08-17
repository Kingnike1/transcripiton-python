"""Authentication and authorization service."""

from __future__ import annotations

import hashlib
import hmac
import secrets
from datetime import timedelta

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.core.time import utc_now
from app.models.auth_session import AuthSession
from app.models.meeting import Meeting
from app.models.user import User

SESSION_COOKIE_NAME = "amip_session"
SESSION_DAYS = 7
_SCRYPT_N = 2**14
_SCRYPT_R = 8
_SCRYPT_P = 1


class AuthService:
    """Manage accounts, passwords, sessions and legacy ownership migration."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def authentication_enabled(self) -> bool:
        return bool(self.session.scalar(select(func.count(User.id))))

    def register(self, email: str, password: str) -> tuple[User, str]:
        normalized = self._normalize_email(email)
        if len(password) < 10:
            raise ValueError("Password must be at least 10 characters")
        if self.session.scalar(select(User).where(User.email == normalized)) is not None:
            raise ValueError("Email already registered")

        first_user = not self.authentication_enabled()
        user = User(email=normalized, password_hash=self.hash_password(password))
        self.session.add(user)
        self.session.flush()
        if first_user:
            self.session.execute(
                update(Meeting).where(Meeting.owner_id.is_(None)).values(owner_id=user.id)
            )
        token = self._create_session(user.id)
        self.session.commit()
        self.session.refresh(user)
        return user, token

    def login(self, email: str, password: str) -> tuple[User, str] | None:
        normalized = self._normalize_email(email)
        user = self.session.scalar(select(User).where(User.email == normalized))
        if user is None or not user.is_active or not self.verify_password(password, user.password_hash):
            return None
        token = self._create_session(user.id)
        self.session.commit()
        return user, token

    def logout(self, token: str | None) -> None:
        if not token:
            return
        row = self.session.scalar(
            select(AuthSession).where(AuthSession.token_hash == self._token_hash(token))
        )
        if row is not None:
            self.session.delete(row)
            self.session.commit()

    def user_from_token(self, token: str | None) -> User | None:
        if not token:
            return None
        now = utc_now()
        row = self.session.scalar(
            select(AuthSession).where(
                AuthSession.token_hash == self._token_hash(token),
                AuthSession.expires_at > now,
            )
        )
        if row is None or not row.user.is_active:
            return None
        return row.user

    def can_access_meeting(self, user: User | None, meeting: Meeting | None) -> bool:
        if meeting is None:
            return False
        if not self.authentication_enabled():
            return True
        return user is not None and meeting.owner_id == user.id

    @staticmethod
    def hash_password(password: str) -> str:
        salt = secrets.token_bytes(16)
        digest = hashlib.scrypt(
            password.encode("utf-8"), salt=salt, n=_SCRYPT_N, r=_SCRYPT_R, p=_SCRYPT_P, dklen=64
        )
        return f"scrypt${_SCRYPT_N}${_SCRYPT_R}${_SCRYPT_P}${salt.hex()}${digest.hex()}"

    @staticmethod
    def verify_password(password: str, encoded: str) -> bool:
        try:
            algorithm, n, r, p, salt_hex, digest_hex = encoded.split("$", 5)
            if algorithm != "scrypt":
                return False
            candidate = hashlib.scrypt(
                password.encode("utf-8"),
                salt=bytes.fromhex(salt_hex),
                n=int(n),
                r=int(r),
                p=int(p),
                dklen=len(bytes.fromhex(digest_hex)),
            )
            return hmac.compare_digest(candidate, bytes.fromhex(digest_hex))
        except (ValueError, TypeError):
            return False

    def _create_session(self, user_id: int) -> str:
        token = secrets.token_urlsafe(32)
        self.session.add(
            AuthSession(
                user_id=user_id,
                token_hash=self._token_hash(token),
                expires_at=utc_now() + timedelta(days=SESSION_DAYS),
            )
        )
        self.session.flush()
        return token

    @staticmethod
    def _token_hash(token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    @staticmethod
    def _normalize_email(email: str) -> str:
        normalized = email.strip().lower()
        if "@" not in normalized or normalized.startswith("@") or normalized.endswith("@"):
            raise ValueError("Invalid email")
        return normalized
