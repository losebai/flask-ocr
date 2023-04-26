

class Result:

    def __init__(self) -> None:
        pass
    
    @staticmethod
    def error(message=None):
        result = {
            "code":1001,
            "message":message,
            "data": None
        }
        return result

    @staticmethod
    def ok(data=None):
        result = {
            "code":0,
            "message":"",
            "data": data
        }
        return result