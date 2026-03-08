from __future__ import annotations

import json
from datetime import timedelta
from pathlib import Path

import pytest

fastapi = pytest.importorskip("fastapi")
Response = fastapi.Response
b = pytest.importorskip("backend_api")


def _write_json(path: Path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_redeemed_invite_reenters_same_user(monkeypatch, tmp_path):
    web = tmp_path / "web"
    invites_path = tmp_path / "invites.json"

    monkeypatch.setattr(b, "WEB", web)
    monkeypatch.setattr(b, "INVITES_PATH", invites_path)

    _write_json(web / "users.json", [])
    _write_json(invites_path, [{
        "token": "tok1",
        "created_at": b._utc_now().isoformat(),
        "expires_at": (b._utc_now() + timedelta(hours=1)).isoformat(),
        "used_at": None,
        "redeemed_user_id": None,
        "revoked_at": None,
    }])

    first = b.join(b.JoinIn(token="tok1", display_name="Alice"), Response())
    assert first["ok"] is True
    first_user_id = first["user_id"]

    users_after_first = b._read_json(web / "users.json", [])
    assert len(users_after_first) == 1

    second = b.join(b.JoinIn(token="tok1", display_name="Different Name Ignored"), Response())
    assert second["ok"] is True
    assert second["user_id"] == first_user_id
    assert second["reentry"] is True

    users_after_second = b._read_json(web / "users.json", [])
    assert len(users_after_second) == 1


def test_redeemed_token_does_not_fail_as_used(monkeypatch, tmp_path):
    web = tmp_path / "web"
    invites_path = tmp_path / "invites.json"

    monkeypatch.setattr(b, "WEB", web)
    monkeypatch.setattr(b, "INVITES_PATH", invites_path)

    _write_json(web / "users.json", [{"id": "u_123", "displayName": "Alice", "isAdmin": False, "avatar": "A"}])
    _write_json(invites_path, [{
        "token": "tok2",
        "created_at": b._utc_now().isoformat(),
        "expires_at": (b._utc_now() - timedelta(hours=1)).isoformat(),
        "used_at": b._utc_now().isoformat(),
        "redeemed_user_id": "u_123",
        "revoked_at": None,
    }])

    out = b.join(b.JoinIn(token="tok2", display_name="Alice"), Response())
    assert out["ok"] is True
    assert out["user_id"] == "u_123"
    assert out["reentry"] is True
