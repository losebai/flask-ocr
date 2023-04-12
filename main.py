import os
import sys

sys.path.append(os.getcwd())

import server.application  as app


if __name__ == "__main__":
    app.run()