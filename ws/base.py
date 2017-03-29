devices = {
    "1": {
        "type": "oven",
        "on": False,
        "image": "/img/oven_2.png"
        },
    "2": {
        "type":"lamp",
        "on": False,
        "image": "/img/light_2.png"
        },
    "3": {
        "type":"speaker",
        "on": False,
        "image": "/img/speaker_2.png"
        },
    "4": {
        "type":"coffee machine",
        "on": False,
        "image": "/img/coffe_machine_2.png"
        }
}

class CoiotWs:
    def __init__(self):
        pass

    def serve_single_device(self, path, d):
        if len(path) == 1:
            return {
                    "name": "attribute",
                    "accept": list(d.keys()) + ["all"],
                    "description": "attribute to get from the device"
                    }
        if path[1] == "all":
            return d
        elif path[1] in d.keys():
            return d[path[1]]
        raise OSError("unknown attribute: " + path[1])

    def serve_device(self, path, devices):
        if len(path) == 0:
            return {
                    "name": "device",
                    "accept": list(devices.keys()) + ["all"],
                    "description": "device from which to get an attribute"
                    }
        elif path[0] in devices.keys():
            return self.serve_single_device(path, devices[path[0]])
        elif path[0] == "all":
            a={}
            for i,d in devices.items():
                a[i] = self.serve_single_device(path, d)
            return a
        raise OSError("unknown device: " + path[0])

    def serve_v1(self, path):
        if len(path) == 0:
            return { "name": "category",
                    "accept": ["device"],
                    "description": "category of the attribute to get"
                    }
        elif path[0] == "device":
            return self.serve_device(path[1:], devices)
        raise OSError("unknown category: " + path[0])

    def serve(self, request):
        path = [p for p in request.split("/") if p != ""]
        if len(path) == 1:
            return { "name": "version",
                    "accept": ["v1"],
                    "description": "version of the protocol to use"
                    }
        elif path[1] == "v1":
            return self.serve_v1(path[2:])
        raise OSError("unsuported protocol version: " + path[1])
