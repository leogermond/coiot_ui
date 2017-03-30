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

class CoiotWsError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message
        self.code = 500

class SubNotFound(CoiotWsError):
    def __init__(self, name, value, accept):
        super().__init__("unknown "+name+": "+value)
        self.name = name
        self.value = value
        self.accept = accept
        self.code = 404

class CoiotWs:
    def __init__(self):
        pass

    def route_sub_get(self, path, name, description, **accept):
        if len(path) == 0:
            return {'name': name, 'description': description, 'accept': list(accept.keys())}
        p, psub = path[0], path[1:]
        for k,v in accept.items():
            if p == k:
                return v[0](psub, *v[1])
        raise SubNotFound(name, p, accept)

    def get_single_device(self, path, d):
        return self.route_sub_get(path,
                "attribute", "attribute to get from the device",
                **{ k: (lambda p, d, a: a(d) if callable(a) else a, [d, v]) for (k,v) in d.items() },
                **{"*": (lambda p, d: {n: v if not callable(v) else v(d) for (n,v) in d.items() }, [d])})

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
        return self.route_sub_get(path,
                "device", "device from which to get an attribute",
                **{ k: (self.get_single_device, [v]) for (k,v) in devices.items() },
                **{"*": (lambda p, d: {k: self.get_single_device(p, v) for (k,v) in d.items() }, [devices])})

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
        return self.route_sub_get(path,
                "category", "category of attribute to get",
                device = (self.get_device, [devices]))

    def set_v1(self, path, data):
        p, psub = path[0], path[1:]
        if p == "device":
            return self.set_device(psub, data, devices)
        raise OSError("unknown category: " + p)

    def get(self, request):
        path = [p for p in request.split("/") if p != ""]
        return self.route_sub_get(path[1:],
                "version", "version of the protocol to use",
                v1 = (self.get_v1, []))

    def set(self, request, data):
        path = [p for p in request.split("/") if p != ""]
        p, psub = path[1], path[2:]
        if p == "v1":
            return self.set_v1(psub, data)
        raise OSError("unsuported protocol version: " + p)
