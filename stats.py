from helpers.slack import chatUpdate, postMessage, SlackApiError
import time
from datetime import datetime, timedelta
from helpers.friendly import getFriendlyTime, getFriendlyRemainingTime
from config import SLACK_NEW_POST_INTERVAL, SLACK_UPDATE_INTERVAL, SLACK_POST_CHANNEL, NETWORKS


def buildMessage(dateTimeStart):
    res = "From " + getFriendlyTime(dateTimeStart, seconds=False) + " to " + getFriendlyTime(datetime.utcnow(), seconds=False) + " (" + getFriendlyRemainingTime(datetime.utcnow() - dateTimeStart) + ")"
    dataset = [x for x in NETWORKS[0].archive if x.currentPhase == "Ended" and x.ended.timeStarted >= dateTimeStart]
    if dataset.__len__() == 0:
        res = res + "\nNo coinjoins finished during this interval"
        return res
    successes = [x for x in dataset if x.state.name == "Success"]
    res = res + "\n" + str(successes.__len__()) + " success / " + str(dataset.__len__()) + " total (" + str(round((successes.__len__()/dataset.__len__())*100,2)) + "% success rate)"
    if (successes.__len__() == 0):
        return res
    nbInputsCoinjoined = sum([x.connectionConfirmation.inputsCount for x in successes])
    nbBTCCoinjoined = round(sum([x.connectionConfirmation.totalValue for x in successes]) / 100000000, 2)
    res = res + "\n" + str(nbInputsCoinjoined) + " inputs mixed (" + str(round(nbInputsCoinjoined/successes.__len__(),2)) + " / round)"
    res = res + "\n" + str(nbBTCCoinjoined) + " BTC mixed (" + str(round(nbBTCCoinjoined/successes.__len__(),2)) + " BTC / round - " + str(round(nbBTCCoinjoined/nbInputsCoinjoined,2)) + " BTC / input)"

    totalMinerFees = sum([successes[0].connectionConfirmation.totalValue - successes[0].outputRegistration.totalValue for x in successes])
    res = res + "\n" + str(round(totalMinerFees/100000000, 4)) + " BTC paid as miner fees (" + str(round(totalMinerFees/nbInputsCoinjoined)) + " sats / input)"

    return res

def stats():
    counter = 0
    message = "tmp"
    ts = postMessage(SLACK_POST_CHANNEL, message)
    while True:
        message_time = datetime.fromtimestamp(float(ts))
        counter = counter + 1
        time.sleep(SLACK_UPDATE_INTERVAL)
        message = buildMessage(message_time + timedelta(hours=6))
        chatUpdate(SLACK_POST_CHANNEL, message, ts)
        current_time = datetime.now()
        if (current_time - message_time).total_seconds() >= SLACK_NEW_POST_INTERVAL:
            ts = postMessage(SLACK_POST_CHANNEL, message)