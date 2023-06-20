from server.application import app


if __name__ == "__main__":
    "cmd uvicorn app:app"
    app.run()