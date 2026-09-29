"""Regressões P0.2: sem credenciais, e-mail real ou acesso ao banco."""
from types import SimpleNamespace as NS
from unittest.mock import Mock

import pytest

from core import auth, database


@pytest.fixture
def state(monkeypatch):
    state = {}
    monkeypatch.setattr(database.st, "session_state", state)
    monkeypatch.setattr(database.st, "secrets", {"supabase": {"url": "https://example.supabase.co", "key": "test-key"}})
    return state


def signed_in(state, user_id="user-a"):
    client = Mock()
    user = NS(id=user_id, email=f"{user_id}@example.com", user_metadata={})
    session = NS(user=user, access_token="test-token")
    client.auth.get_session.return_value = session
    client.auth.get_user.return_value = NS(user=user)
    client.auth.sign_in_with_password.return_value = NS(user=user, session=session)
    state.update(logged_in=True, user_data={"id": user_id}, _supabase_client=client,
                 projeto_ativo={"id": "private-project"}, report="private-report")
    return client


def test_clients_are_reused_only_within_the_same_session(state, monkeypatch):
    factory = Mock(side_effect=[Mock(), Mock()])
    monkeypatch.setattr(database, "create_client", factory)
    first = database.get_supabase()
    assert database.get_supabase() is first
    second_state = {}
    monkeypatch.setattr(database.st, "session_state", second_state)
    second = database.get_supabase()
    assert first is not second
    assert factory.call_args.kwargs["options"].auto_refresh_token is False
    monkeypatch.setattr(database.st, "session_state", state)
    database.clear_supabase_client()
    assert second_state["_supabase_client"] is second


def test_anonymous_rerun_keeps_form_input(state):
    state["email_input"] = "a@example.com"
    assert auth.check_login() is False
    assert state["email_input"] == "a@example.com"


@pytest.mark.parametrize("missing", ["logged_in", "user_data"])
def test_partial_login_clears_private_state(state, missing):
    signed_in(state)
    del state[missing]
    assert auth.check_login() is False
    assert state == {}


def test_valid_login_requires_server_validation(state):
    client = signed_in(state)
    assert auth.check_login() is True
    client.auth.get_user.assert_called_once_with("test-token")


@pytest.mark.parametrize("failure", ["missing_session", "local_identity", "remote_identity", "remote_missing", "network", "refresh"])
def test_invalid_sessions_fail_closed_and_clear_all_state(state, failure):
    client = signed_in(state)
    if failure == "missing_session":
        client.auth.get_session.return_value = None
    elif failure == "local_identity":
        client.auth.get_session.return_value.user = NS(id="user-b")
    elif failure == "remote_identity":
        client.auth.get_user.return_value = NS(user=NS(id="user-b"))
    elif failure == "remote_missing":
        client.auth.get_user.return_value = None
    elif failure == "network":
        client.auth.get_user.side_effect = RuntimeError("offline")
    else:
        client.auth.get_session.side_effect = RuntimeError("refresh rejected")
    assert auth.check_login() is False
    assert state == {}


@pytest.mark.parametrize("offline", [False, True])
def test_logout_is_local_and_cleans_even_when_remote_fails(state, monkeypatch, offline):
    client = signed_in(state)
    if offline:
        client.auth.sign_out.side_effect = RuntimeError("offline")
    rerun = Mock()
    monkeypatch.setattr(auth.st, "rerun", rerun)
    auth.logout()
    client.auth.sign_out.assert_called_once_with({"scope": "local"})
    assert state == {}
    rerun.assert_called_once()


def test_login_replaces_old_client_and_private_state(state, monkeypatch):
    old = signed_in(state)
    fresh_state = {}
    fresh = signed_in(fresh_state, "user-b")
    monkeypatch.setattr(database, "create_client", Mock(return_value=fresh))
    monkeypatch.setattr(database, "get_user_profile", Mock(return_value={"cargo": "analista", "squad": None}))
    result = database.verify_user("user-b@example.com", "password")
    assert result["id"] == "user-b"
    assert state == {"_supabase_client": fresh}
    old.auth.sign_in_with_password.assert_not_called()


@pytest.mark.parametrize("failure", ["password", "no_session", "different_user", "profile"])
def test_failed_login_does_not_leave_authenticated_client(state, monkeypatch, failure):
    client = signed_in(state)
    monkeypatch.setattr(database, "create_client", Mock(return_value=client))
    if failure == "password":
        client.auth.sign_in_with_password.side_effect = RuntimeError("invalid credentials")
    elif failure == "no_session":
        client.auth.sign_in_with_password.return_value.session = None
    elif failure == "different_user":
        client.auth.sign_in_with_password.return_value.session = NS(user=NS(id="user-b"))
    else:
        monkeypatch.setattr(database, "get_user_profile", Mock(side_effect=RuntimeError("failure")))
    assert database.verify_user("a@example.com", "bad-password") is None
    assert state == {}


@pytest.mark.parametrize("offline", [False, True])
def test_password_reset_uses_current_client_without_logging_in(state, offline):
    client = Mock()
    state["_supabase_client"] = client
    if offline:
        client.auth.reset_password_for_email.side_effect = RuntimeError("offline")
    assert database.reset_password("a@example.com") is not offline
    client.auth.reset_password_for_email.assert_called_once_with("a@example.com")
    assert not state.get("logged_in")
