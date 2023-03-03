from datetime import datetime
from obj.time import TimeCoin, TimeCount, TimeOutput

class Phase:
    def __init__(self, id, name, timeStarted, timeEnd) -> None:
        self.id = id
        self.name = name
        self.timeStarted = timeStarted
        self.timeEnd = timeEnd

class InputRegistration(Phase):
    def __init__(self, timeStarted, timeEnd) -> None:
        self.inputsCount = 0
        self.timeline = []
        super().__init__(0, "InputRegistration", timeStarted, timeEnd)
        pass

    def update(self, rndHM):
        try:
            self.inputsCount = max(0, self.inputsCount) if rndHM == [] else rndHM[0]["inputCount"]
            self.timeline.append(TimeCount(min(datetime.utcnow(), self.timeEnd), self.inputsCount))
        except:
            pass

class ConnectionConfirmation(Phase):
    def __init__(self, timeStarted, timeEnd) -> None:
        self.inputsCount = 0
        self.confirmationsMissing = 0
        self.totalValue = 0
        self.timeline = []
        super().__init__(1, "ConnectionConfirmation", timeStarted, timeEnd)
        pass

    def update(self, rnd, registeredInputs):
        try:
            currentTime = datetime.utcnow()
            for input in [x for x in rnd["coinjoinState"]["events"] if x["Type"] == "InputAdded"]:
                if([x for x in self.timeline if x.coin == input["coin"]] == []):
                    self.timeline.append(TimeCoin(currentTime, input["coin"]))
            self.inputsCount = self.timeline.__len__()
            self.confirmationsMissing = max(0, registeredInputs - self.inputsCount)
            self.totalValue = sum([x.coin["txOut"]["value"] for x in self.timeline])
        except Exception as e:
            pass
    
class OutputRegistration(Phase):
    def __init__(self, timeStarted, timeEnd) -> None:
        self.outputsCount = 0
        self.totalValue = 0
        self.timeline = []
        super().__init__(2, "OutputRegistration", timeStarted, timeEnd)
        pass

    def update(self, rnd):
        try:
            currentTime = datetime.utcnow()
            for output in [x for x in rnd["coinjoinState"]["events"] if x["Type"] == "OutputAdded"]:
                if([x for x in self.timeline if x.output == output["output"]] == []):
                    self.timeline.append(TimeOutput(currentTime, output["output"]))
            self.outputsCount = self.timeline.__len__()
            self.totalValue = sum([x.output["value"] for x in self.timeline])
        except Exception as e:
            pass

class TransactionSigning(Phase):
    def __init__(self, timeStarted, timeEnd) -> None:
        self.signaturesCount = 0
        self.signaturesMissing = 0
        self.timeline = []
        super().__init__(3, "TransactionSigning", timeStarted, timeEnd)
        pass

    def update(self, rnd, confirmedInputsCount):
        try:
            self.signaturesCount = rnd["coinjoinState"]["witnesses"].__len__()
            self.timeline.append(TimeCount(datetime.utcnow(), self.signaturesCount))
            self.missing = max(0, confirmedInputsCount - self.count)
        except:
            pass

class Ended(Phase):
    def __init__(self, timeStarted) -> None:
        super().__init__(4, "Ended", timeStarted, None)
        pass