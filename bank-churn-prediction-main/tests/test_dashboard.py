import pytest
from streamlit.testing.v1 import AppTest

def test_login_incorrect():
    at = AppTest.from_file("dashboard.py", default_timeout=30)

    # Set the secrets as if we are in streamlit
    at.secrets["auth"] = {"username": "admin", "password": "password123"}

    at.run()

    # Ensure it's in the login screen initially
    assert at.session_state.logged_in == False

    # The text inputs for username and password
    text_inputs = at.text_input

    # Let's say we set wrong credentials
    text_inputs[0].set_value("wrong_user")
    text_inputs[1].set_value("wrong_password")

    # Click the button "Sisteme Giriş Yap"
    at.button[0].click().run()

    # Check if error message is displayed
    assert "Hatalı kullanıcı adı veya şifre!" in at.error[0].value
    assert at.session_state.logged_in == False

def test_login_correct():
    at = AppTest.from_file("dashboard.py", default_timeout=30)

    # Set the secrets as if we are in streamlit
    at.secrets["auth"] = {"username": "admin", "password": "password123"}

    at.run()

    # Ensure it's in the login screen initially
    assert at.session_state.logged_in == False

    # The text inputs for username and password
    text_inputs = at.text_input

    # Let's say we set correct credentials
    text_inputs[0].set_value("admin")
    text_inputs[1].set_value("password123")

    # Click the button "Sisteme Giriş Yap"
    at.button[0].click().run()

    # Because of st.rerun(), the app redirects to main dashboard.
    assert at.session_state.logged_in == True
