"""
Tenut
"""

import tefnut.webui.webservice as webservice
import platform


def start_server():
    print("===========Starting up Tefnut=============")
    webservice.load_application()
    return webservice.app


app = start_server()


if __name__ == "__main__":
    print("===========Starting up Tefnut for vscode=============")
    print(f"Python Version: {platform.python_version()}")
    webservice.app.run(
        use_debugger=False, use_reloader=False, passthrough_errors=True, host="0.0.0.0"
    )
