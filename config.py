from obj.network import Network

BASE_FOLDER = "./"

NETWORKS = [
    Network(
        "Main", # name
        "https://wasabiwallet.io/WabiSabi/status", # url round states
        "https://wasabiwallet.io/WabiSabi/human-monitor", # url human monitor
        BASE_FOLDER + "data/mainet/clear.json", # data path in clear text
        BASE_FOLDER + "data/mainet/serialized.json", # data path in serialized json
    ),
    Network(
        "Testnet",
        "https://wasabiwallet.co/WabiSabi/status",
        "https://wasabiwallet.co/WabiSabi/human-monitor",
        BASE_FOLDER + "data/testnet/clear.json",
        BASE_FOLDER + "data/testnet/serialized.json",
    )
]

SLACK_API_TOKEN = "xxxxx"
SLACK_UPDATE_INTERVAL = 1
SLACK_NEW_POST_INTERVAL = 3600
SLACK_POST_CHANNEL = "C04HLD8PMS5"