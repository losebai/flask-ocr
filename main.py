import os
import sys

sys.path.append(os.getcwd())

from server.application import app


if __name__ == "__main__":
    app.run()