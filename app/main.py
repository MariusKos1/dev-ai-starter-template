"""Entry point for the Helsinki AI Tourist Assistant."""

if __name__ == "__main__":
    import streamlit.web.cli as stcli
    import sys

    sys.argv = ["streamlit", "run", "app/ui.py"]
    stcli.main()
