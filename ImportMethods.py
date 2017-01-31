import os

class ImportMethods():
    def __init__(self, **kwargs):
        if "method_id" in kwargs:
            method_id = kwargs.get("method_id")
        else:
            #TODO: What happens when someone doesn't tell you which method to use to import?
            pass


        #Define Methods
        self.MethodsList = {"name": [], "id": [],"method": []}
        self.MethodsList["name"].append("Default")
        self.MethodsList["id"].append(0)
        self.MethodsList["method"].append(self.default)

    def default(self, file):
        #Hack to open with default system application
        os.system("open '%s'" % file)  # Mac
        # os.startfile(filename)#Windows

