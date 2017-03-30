devices = {
    "1": {
        "type": "oven",
        "on": False,
        "image": lambda d: "oven_2.png" if not d['on'] else "oven_2_on.png"
        },
    "2": {
        "type":"lamp",
        "on": False,
        "image": lambda d: "light_2.png" if not d['on'] else "light_2_on.png"
        },
    "3": {
        "type":"speaker",
        "on": False,
        "image": "speaker_2.png"
        },
    "4": {
        "type":"coffee machine",
        "on": False,
        "image": lambda d: "coffee_machine_2.png" if not d['on'] else "coffee_machine_2_on.png"
        }
}

class CoiotWs:
    def __init__(self):
        pass

    def get_single_device(self, path, d):
        if len(path) == 1:
            return {
                    "name": "attribute",
                    "accept": list(d.keys()) + ["*"],
                    "description": "attribute to get from the device"
                    }
        p = path[1]
        if p == "*":
            return {n: v if not callable(v) else v(d) for (n,v) in d.items() }
        elif p in d.keys():
            a = d[p]
            if callable(a):
                return a(d)
            return a
        raise OSError("unknown attribute: " + p)

    def set_single_device(self, path, data, d):
        if path[1] == "*":
            assert(type(data) is dict)
            assert(all((a in d.keys() for a in data.keys())))
            for k,v in data.items():
                d[k] = v
        elif path[1] in d.keys():
            assert(type(data) is type(d[path[1]]))
            d[path[1]] = data
        else:
            raise OSError("unknown attribute: " + path[1])

    def get_device(self, path, devices):
        if len(path) == 0:
            return {
                    "name": "device",
                    "accept": list(devices.keys()) + ["*"],
                    "description": "device from which to get an attribute"
                    }
        elif path[0] in devices.keys():
            return self.get_single_device(path, devices[path[0]])
        elif path[0] == "*":
            a={}
            for i,d in devices.items():
                a[i] = self.get_single_device(path, d)
            return a
        raise OSError("unknown device: " + path[0])

    def set_device(self, path, data, devices):
        if path[0] in devices.keys():
            return self.set_single_device(path, data, devices[path[0]])
        elif path[0] == "*":
            a={}
            for i,s in data.items():
                self.set_single_device(path, data, s, devices[i])
            return a
        raise OSError("unknown device: " + path[0])

    def get_v1(self, path):
        if len(path) == 0:
            return { "name": "category",
                    "accept": ["device"],
                    "description": "category of the attribute to get"
                    }
        elif path[0] == "device":
            return self.get_device(path[1:], devices)
        raise OSError("unknown category: " + path[0])

    def set_v1(self, path, data):
        if path[0] == "device":
            return self.set_device(path[1:], data, devices)
        raise OSError("unknown category: " + path[0])

    def get(self, request):
        path = [p for p in request.split("/") if p != ""]
        if len(path) == 1:
            return { "name": "version",
                    "accept": ["v1"],
                    "description": "version of the protocol to use"
                    }
        elif path[1] == "v1":
            return self.get_v1(path[2:])
        raise OSError("unsuported protocol version: " + path[1])

    def set(self, request, data):
        path = [p for p in request.split("/") if p != ""]
        if path[1] == "v1":
            return self.set_v1(path[2:], data)
        raise OSError("unsuported protocol version: " + path[1])
