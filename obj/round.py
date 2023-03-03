from datetime import datetime, timedelta
from obj.phase import ConnectionConfirmation, Ended, InputRegistration, OutputRegistration, TransactionSigning
from obj.state import Abort, Ongoing, Success

class ArchiveRound:
    def __init__(self, rnd, rndHM):
        self.id = rnd["id"][-6:]
        self.created = datetime.strptime(rnd["inputRegistrationStart"].split(".")[0], "%Y-%m-%dT%H:%M:%S")
        self.state = Ongoing()
        self.blame = []
        self.concurrentRegistrationRounds = []
        self.maxSuggestedAmount = 0 if rndHM == [] else round(rndHM[0]['maxSuggestedAmount'],2)

        self.currentPhase = ""
        self.inputRegistration = InputRegistration(self.created, datetime.strptime(rnd["inputRegistrationEnd"].split(".")[0], "%Y-%m-%dT%H:%M:%S"))
        self.connectionConfirmation = ConnectionConfirmation(self.inputRegistration.timeEnd, None)
        self.outputRegistration = OutputRegistration(None, None)
        self.transactionSigning = TransactionSigning(None, None)
        self.ended = Ended(None)

    def getCurrentPhase(self):
        if(self.currentPhase == ""):
            return None
        if(self.currentPhase == self.inputRegistration.name):
            return self.inputRegistration
        if(self.currentPhase == self.connectionConfirmation.name):
            return self.connectionConfirmation
        if(self.currentPhase == self.outputRegistration.name):
            return self.outputRegistration
        if(self.currentPhase == self.transactionSigning.name):
            return self.transactionSigning
        if(self.currentPhase == self.ended.name):
            return self.outputRegistration

    def update(self, rnd, rndHM, archive, roundsFound):
        self.setBlame(rnd["blameOf"], archive)

        receivedPhase = rnd["phase"]
    
        self.inputRegistration.update(rndHM)
        if(receivedPhase == 0):
            if(self.blame == ""):
                self.setConcurrentRegistrationRounds(roundsFound)
            if(self.getCurrentPhase() != self.inputRegistration):
                self.currentPhase = self.inputRegistration.name
            return

        self.connectionConfirmation.update(rnd, self.inputRegistration.inputsCount)
        if(receivedPhase == 1):
            if(self.getCurrentPhase() != self.connectionConfirmation):
                self.currentPhase = self.connectionConfirmation.name
            return

        self.outputRegistration.update(rnd)
        if(receivedPhase == 2):
            if(self.getCurrentPhase() != self.outputRegistration):
                currentTime = datetime.utcnow()
                self.connectionConfirmation.timeEnd = currentTime
                self.outputRegistration.timeStarted = currentTime
                self.currentPhase = self.outputRegistration.name
            return
            
        self.transactionSigning.update(rnd, self.connectionConfirmation.inputsCount)
        if(receivedPhase == 3):
            if(self.getCurrentPhase() != self.transactionSigning):
                currentTime = datetime.utcnow()
                self.outputRegistration.timeEnd = currentTime
                self.transactionSigning.timeStarted = currentTime
                self.currentPhase = self.transactionSigning.name
            return

        currentTime = datetime.utcnow()
        if(self.getCurrentPhase() != None):
            self.getCurrentPhase().timeEnd = currentTime
        else:
            self.transactionSigning.timeEnd = None
        self.ended.timeStarted = currentTime
        self.currentPhase = self.ended.name

        self.endRound(rnd)

    def setBlame(self, blame, archive):
        if blame[-6:] == '000000':
            self.blame = []
        else:
            combo = []
            currentBlame = blame[-6:]
            while True:
                combo.append(currentBlame)
                nextRound = [x for x in archive if currentBlame == x.id]
                if nextRound != []:
                    if nextRound[0].blame == []:
                        break
                    currentBlame = nextRound[0].blame[0]
                else:
                    break
            self.blame = combo

    def setConcurrentRegistrationRounds(self, roundsFound):
        remaining = (self.inputRegistration.timeEnd - datetime.utcnow())
    
        if(remaining > timedelta(minutes=1)):
            for tmpRnd in roundsFound["roundStates"]:
                tmpRemaining = (datetime.strptime(tmpRnd["inputRegistrationEnd"].split(".")[0], "%Y-%m-%dT%H:%M:%S") - datetime.utcnow())
                if((not self.id in tmpRnd["id"]) and tmpRnd["phase"] == 0 and tmpRemaining > timedelta(minutes=1)):
                    self.concurrentRegistrationRounds.append(tmpRnd["id"][-6:])
    
    def endRound(self, rnd):
        endRoundState = rnd["endRoundState"]
        if endRoundState == 4:
            # TODO: txid
            self.state = Success(None, datetime.utcnow())
        else:
            reason = ""
            failedFast = False
            if endRoundState == 0:
                reason = "No Info"
            if endRoundState == 1:
                reason = "AbortedWithError"
            elif endRoundState == 2:
                reason = "AbortedNotEnoughAlices"
            elif endRoundState == 3:
                reason = "TransactionBroadcastFailed"
            elif endRoundState == 5 and endRoundState == 6:
                reason = "NotAllAlicesSign" if endRoundState == 5 else "AbortedNotEnoughAlicesSigned"
                if(self.transactionSigning.timeStarted != None and self.transactionSigning.timeEnd != None):
                    # failed fast if transaction signing aborted in less than 75s
                    failedFast = timedelta(self.transactionSigning.timeEnd - self.transactionSigning.timeStarted).total_seconds() < 75
            elif endRoundState == 7:
                reason = "AbortedNotAllAlicesConfirmed"
            elif endRoundState == 8:
                reason = "AbortedLoadBalancing"

            self.state = Abort(reason, datetime.utcnow(), failedFast)