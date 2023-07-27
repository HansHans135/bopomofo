"""
Start the application.
"""

import tracemalloc

tracemalloc.start(25)  # Used in src/client/client.py on_ready function.

if __name__ == "__main__":
    import decouple

    from src.main import Bot

    Bot().run(decouple.config("token"))
