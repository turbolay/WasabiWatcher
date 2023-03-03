class Network():
    archive = None
    def __init__(self, name, url, urlhm, archivePath, serializedPath):
        self.name = name
        self.url = url
        self.urlhm = urlhm
        self.archivePath = archivePath
        self.serializedPath = serializedPath