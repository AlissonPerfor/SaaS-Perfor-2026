"""SDK e Streamlit reais; somente o transporte remoto é simulado."""
import json
import time
from pathlib import Path
from unittest.mock import patch

import httpx
from streamlit.testing.v1 import AppTest
from supabase import ClientOptions, create_client

from core import auth, database


def test_two_streamlit_users_keep_sdk_tokens_and_project_state_isolated():
    script = '''
import streamlit as st
from core import auth
from core.context import init_project_context
if auth.check_login():
    init_project_context()
    st.write(st.session_state.user_data["email"])
    st.button("Logout", on_click=auth.logout)
else:
    auth.show_login_page()
'''
    def user(identity):
        return {"id": identity, "aud": "authenticated", "role": "authenticated",
                "email": f"{identity}@example.com", "created_at": "2026-01-01T00:00:00Z",
                "app_metadata": {}, "user_metadata": {}}

    def handler(request):
        if request.url.path.endswith("/token"):
            identity = json.loads(request.content)["email"].split("@")[0]
            return httpx.Response(200, json={"access_token": identity,
                "refresh_token": f"refresh-{identity}", "token_type": "bearer",
                "expires_in": 3600, "expires_at": int(time.time()) + 3600,
                "user": user(identity)})
        identity = request.headers["authorization"].removeprefix("Bearer ")
        if request.url.path.endswith("/user"):
            return httpx.Response(200, json=user(identity))
        if request.url.path.endswith("/usuarios"):
            return httpx.Response(200, json=[{"cargo": "analista", "squad": None}])
        if request.url.path.endswith("/projetos"):
            return httpx.Response(200, json=[{"id": name, "analista_email": f"{name}@example.com"} for name in ("a", "b")])
        if request.url.path.endswith("/logout"):
            assert request.url.params["scope"] == "local"
            return httpx.Response(204)
        raise AssertionError(f"Unexpected request: {request.url.path}")

    with httpx.Client(transport=httpx.MockTransport(handler)) as transport:
        def factory(url, key, options):
            options.httpx_client = transport
            return create_client(url, key, options=options)

        def login(app, identity):
            app.text_input[0].input(f"{identity}@example.com")
            app.text_input[1].input("test-password")
            app.button[1].click().run()
            assert not app.exception

        with patch.object(database, "create_client", side_effect=factory):
            first, second = AppTest.from_string(script), AppTest.from_string(script)
            for app in (first, second):
                app.secrets["supabase"] = {"url": "https://example.supabase.co", "key": "test-key"}
                app.run()
            login(first, "a")
            login(second, "b")
            for app, identity in ((first, "a"), (second, "b"), (first, "a")):
                app.run()
                assert not app.exception
                assert app.session_state["user_data"]["id"] == identity
                assert [p["id"] for p in app.session_state["projetos_visiveis"]] == [identity]
                assert app.session_state["_supabase_client"].auth.get_session().access_token == identity
            first.session_state["report"] = "private-a"
            first.button[0].click().run()
            second.run()
            assert second.session_state["logged_in"] is True
            assert second.session_state["user_data"]["id"] == "b"
            login(first, "b")
            assert "report" not in first.session_state
            assert first.session_state["projeto_ativo"] is None
            assert [p["id"] for p in first.session_state["projetos_visiveis"]] == ["b"]
            assert first.session_state["_supabase_client"] is not second.session_state["_supabase_client"]


def test_real_sdk_refresh_identity_headers_and_local_logout(monkeypatch):
    requests = []

    def handler(request):
        requests.append(request)
        user = {"id": "user-a", "aud": "authenticated", "role": "authenticated",
                "email": "a@example.com", "created_at": "2026-01-01T00:00:00Z",
                "app_metadata": {}, "user_metadata": {}}
        if request.url.path.endswith("/token"):
            refreshing = request.url.params.get("grant_type") == "refresh_token"
            return httpx.Response(200, json={
                "access_token": "refreshed-token" if refreshing else "initial-token",
                "refresh_token": "refresh-token", "token_type": "bearer",
                "expires_in": 3600, "expires_at": int(time.time()) + (3600 if refreshing else -60),
                "user": user})
        if request.url.path.endswith("/user"):
            return httpx.Response(200, json=user)
        if request.url.path.endswith("/logout"):
            return httpx.Response(204)
        if request.url.path.endswith("/usuarios"):
            return httpx.Response(200, json=[{"cargo": "analista", "squad": None}])
        raise AssertionError(f"Unexpected request: {request.method} {request.url}")

    with httpx.Client(transport=httpx.MockTransport(handler)) as transport:
        def factory(url, key, options):
            options.httpx_client = transport
            return create_client(url, key, options=options)

        state = {}
        monkeypatch.setattr(database.st, "session_state", state)
        monkeypatch.setattr(database.st, "secrets", {"supabase": {"url": "https://example.supabase.co", "key": "test-key"}})
        monkeypatch.setattr(database, "create_client", factory)
        user = database.verify_user("a@example.com", "test-password")
        assert user and user["id"] == "user-a"
        state.update(logged_in=True, user_data=user)
        first = database.get_supabase()
        assert auth.check_login()
        assert any(r.url.params.get("grant_type") == "refresh_token" for r in requests)
        assert next(r for r in requests if r.url.path.endswith("/user")).headers["authorization"] == "Bearer refreshed-token"
        assert first.options.headers["Authorization"] == "Bearer refreshed-token"

        second = create_client("https://example.supabase.co", "test-key", options=ClientOptions(auto_refresh_token=False, httpx_client=transport))
        second.auth.sign_in_with_password({"email": "a@example.com", "password": "test-password"})
        monkeypatch.setattr(auth.st, "rerun", lambda: None)
        auth.logout()
        assert state == {}
        assert first.auth.get_session() is None
        assert second.auth.get_session() is not None
        assert next(r for r in requests if r.url.path.endswith("/logout")).url.params["scope"] == "local"


def test_main_login_and_recovery_dialog_render_without_secrets():
    app = AppTest.from_file(str(Path(__file__).parents[1] / "main.py")).run()
    assert not app.exception
    assert [field.label for field in app.text_input] == ["E-mail corporativo", "Senha"]
    app.button[0].click().run()
    assert not app.exception
    assert any(field.key == "reset_email_input_dialog" for field in app.text_input)


def test_recovery_dialog_submission():
    # AppTest reexecuta o script inteiro, não apenas o fragmento do diálogo.
    app = AppTest.from_string("from core.auth import render_forgot_password_dialog\nrender_forgot_password_dialog()").run()
    with patch.object(database, "get_supabase") as client:
        app.text_input(key="reset_email_input_dialog").input("a@example.com")
        next(button for button in app.button if button.label == "Enviar link de redefinição").click().run()
        assert not app.exception
        client.return_value.auth.reset_password_for_email.assert_called_once_with("a@example.com")


def test_real_streamlit_form_login_clears_old_state_and_logout():
    script = '''
import streamlit as st
from core import auth
if auth.check_login():
    st.write("Authenticated")
    st.button("Logout", on_click=auth.logout)
else:
    auth.show_login_page()
'''
    user = type("User", (), {"id": "user-a", "email": "a@example.com", "user_metadata": {}})()
    session = type("Session", (), {"user": user, "access_token": "test-token"})()
    with patch.object(database, "create_client") as factory, patch.object(database, "get_user_profile", return_value={"cargo": "analista", "squad": None}):
        client = factory.return_value
        client.auth.sign_in_with_password.return_value = type("Response", (), {"user": user, "session": session})()
        client.auth.get_session.return_value = session
        client.auth.get_user.return_value = type("Response", (), {"user": user})()
        app = AppTest.from_string(script)
        app.secrets["supabase"] = {"url": "https://example.supabase.co", "key": "test-key"}
        app.run()
        app.session_state["report"] = "old-private-report"
        app.text_input[0].input("a@example.com")
        app.text_input[1].input("test-password")
        app.button[1].click().run()
        assert not app.exception
        assert app.session_state["logged_in"] is True
        assert "report" not in app.session_state
        app.button[0].click().run()
        assert not app.exception
        assert "user_data" not in app.session_state
        assert "_supabase_client" not in app.session_state
        client.auth.sign_out.assert_called_once_with({"scope": "local"})
