
from config import NETWORKS
from datetime import datetime
import time
import requests
import jsonpickle
from obj.round import ArchiveRound

def core():
    for network in NETWORKS:
        with open (network.serializedPath, "r") as f:
            # TODO: replace by bdd calls
            network.archive = jsonpickle.decode(f.read(), on_missing="error", keys=True)

    # sending get request and saving the response as response object
    while True:
        for network in NETWORKS:
            try:
                r = requests.post(url = network.url, json={"RoundCheckpoints":[]})
                roundsFound = r.json()

                r = requests.get(url = network.urlhm)
                roundsFoundHumanMonitor = r.json()

                for rnd in roundsFound["roundStates"]:
                    try:
                        rndHM = [x for x in roundsFoundHumanMonitor["roundStates"] if rnd["id"] == x["roundId"]]

                        archiveMatch = [x for x in network.archive if x.id in rnd["id"]]
                        archiveRound = None

                        if(archiveMatch == []):
                            archiveRound = ArchiveRound(rnd, rndHM)
                            network.archive.append(archiveRound)
                        else:
                            archiveRound = archiveMatch[0]

                        archiveRound.update(rnd, rndHM, network.archive, roundsFound)

                    except Exception as e:
                        print(e)
                        quit()

                # TODO: replace by bdd calls
                with open(network.serializedPath, "w") as f:
                    f.write(jsonpickle.encode(network.archive))

                with open(network.archivePath, "w") as f:
                    f.write(jsonpickle.encode(network.archive, unpicklable=False))

                print(datetime.now().strftime("%H:%M:%S"))
                time.sleep(1)
            except Exception as ex:
                print(ex)
                time.sleep(1)