from streamlit.testing.v1 import AppTest


def test_streamlit_app_loads_without_exception():
    app = AppTest.from_file("app.py", default_timeout=15).run()

    assert not app.exception
