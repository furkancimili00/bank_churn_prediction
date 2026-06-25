import pytest
from streamlit.testing.v1 import AppTest

def test_successful_login():
    at = AppTest.from_file("dashboard.py")
    at.secrets['auth'] = {'username': 'admin', 'password': '123'}
    at.run(timeout=10)

    # Enter credentials
    at.text_input[0].input("admin").run(timeout=10)
    at.text_input[1].input("123").run(timeout=10)

    # Click login button
    at.button[0].click().run(timeout=10)

    # Assert successful login
    assert at.session_state["logged_in"] is True

def test_failed_login():
    at = AppTest.from_file("dashboard.py")
    at.secrets['auth'] = {'username': 'admin', 'password': '123'}
    at.run(timeout=10)

    # Enter wrong credentials
    at.text_input[0].input("admin").run(timeout=10)
    at.text_input[1].input("wrongpassword").run(timeout=10)

    # Click login button
    at.button[0].click().run(timeout=10)

    # Assert failed login
    assert at.session_state["logged_in"] is False
    assert len(at.error) > 0
    assert "Hatalı kullanıcı adı veya şifre" in at.error[0].value
