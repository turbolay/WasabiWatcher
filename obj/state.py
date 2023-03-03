class State:
    def __init__(self) -> None:
        pass

class Ongoing(State):
    def __init__(self) -> None:
        self.name = "Ongoing"
        super().__init__()
        pass

class Success(State):
    def __init__(self, txId, time) -> None:
        self.name = "Success"
        self.txId = txId
        self.time = time
        super().__init__()

class Abort(State):
    def __init__(self, reason, time, failedFast) -> None:
        self.name = "Abort"
        self.reason = reason
        self.time = time
        self.failedFast = failedFast
        super().__init__()