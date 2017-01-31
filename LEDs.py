#TODO LED WAFER VIEW
#TODO LED MEASUREMENTS VIEW
#TODO LED GUI IMPORTER

class LEDs():
    def __init__(self, **kwargs):
        self.importMethods = {"name": [], "method": []}
        self.importMethods["name"].append("Probe Station IV")
        self.importMethods["method"].append(self.probe_station_iv)

    #Import Methods:
    def probe_station_iv(self):
        pass