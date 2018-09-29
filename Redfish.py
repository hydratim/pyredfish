import requests
from functools import partial
requests.adapters.DEFAULT_RETRIES=100
from time import sleep
import json
'''
Goal:
 - A class that: 
    - Is automatically constructed from simple input (such as a spec dictionary)
    - Builds query urls from class hierarchy
    - Automatic relogin if session expired
    - Automatic logout on garbage collection
    - Provides a simple pythonic adaption of the Redfish API
'''
__spec__ = {
    "Chassis": {
        "__supports__": [
            "GET"
            ],
        "%n": {
            "__supports__": [
                "GET",
                "PATCH"
                ],
            "Thermal": {
                "__supports__": [
                    "GET"
                    ]
                },
            "Power": {
                "__supports__": [
                    "GET"
                    ]
                }
            }
        },
    "Managers": {
        "__supports__": [
            "GET"
            ],
        "%n": {
            "__supports__": [
            "GET"
                ],
            "EthernetInterfaces": {
                "__supports__": [
                    "GET"
                    ],
                "%n": {
                    "__supports__": [
                        "GET"
                        ]
                    }
                },
            "SerialInterfaces": {
                "__supports__": [
                    "GET"
                    ],
                "%n": {
                    "__supports__": [
                        "GET"
                        ]
                    }
                },
            "NetworkProtocol": {
                "__supports__": [
                    "GET"
                    "PATCH"
                    ]
                },
            "LogServices": {
                "__supports__": [
                    "GET"
                    ],
                "%n": {
                    "__supports__": [
                        "GET"
                        ],
                    "Entries": {
                        "__supports__": [
                            "GET"
                            ],
                        "%n": {
                            "__supports__": [
                                "GET"
                                ]
                            }
                        },
                    "Actions": {
                        "__supports__": [
                            ],
                        "LogService.Reset": {
                            "__supports__": [
                                "POST"
                                ]
                            }
                        }
                    }
                },
            "Oem": {
                "__supports__": [
                    ],
                "ActiveDirectory": {
                    "__supports__": [
                        "GET"
                        ]
                    },
                "SMTP": {
                    "__supports__": [
                        "GET"
                        ]
                    },
                "RADIUS": {
                    "__supports__": [
                        "GET"
                        ]
                    },
                "MouseMode": {
                    "__supports__": [
                        "GET"
                        ]
                    },
                "NTP": {
                    "__supports__": [
                        "GET"
                        ]
                    },
                "LDAP": {
                    "__supports__": [
                        "GET"
                        ]
                    }
                },
            "Actions": {
                "__supports__": [
                    ],
                "Manager.Reset": {
                    "__supports__": [
                        "POST"
                        ]
                    }
                }
            }
        },
    "Systems": {
        "__supports__": [
            "GET"
            ],
        "%n": {
            "__supports__": [
                "GET",
                "PATCH"
                ],
            "Processors": {
                "__supports__": [
                    "GET"
                    ]
                },
            "Actions": {
                "__supports__": [
                    ],
                "ComputerSystem.Reset": {
                    "__supports__": [
                        "POST"
                        ]
                    }
                }
            }
        },
    "EventService": {
        "__supports__": [
            "GET",
            "PATCH"
            ],
        "Subscriptions": {
            "__supports__": [
                "GET",
                "POST"
                ],
            "%n": {
                "__supports__": [
                    "GET",
                    "DELETE"
                    ],
                
                }  
            },
        "Actions": {
            "__supports__": [
                ],
            "EventService.SendTestEvent": {
                "__supports__": [
                    "POST"
                    ]
                }
            }
        },
    }

        
class Klass(object):

    def __init__(self, name, parent, lower, username, password, target, session=None, api="/redfish/v1/", session_link=None):
        if not session:
            self.session, response = self.login(target, username, password)
            jdata = response.json()
            self.session_link = jdata["@odata.context"]
        else:
            self.session=session
            self.session_link = session_link
        self.api = api
        self.target = target
        self.username = username
        self.password = password
        self.parent = parent
        self.__subnodes__ = dict()
        self.name = name
        for node in lower.keys():
            if node == "__supports__":
                if "GET" in lower["__supports__"]:
                    def get(self):
                        result = self.request("GET", "{}/{}".format(parent,name))
                        for cruft in ["@odata.type", "@odata.id", "@odata.context", "Members@odata.count", "RelatedItem", "Members", "Links", "ComputerSystems", "ContainedBy"]:
                            if cruft in result.keys():
                                del result[cruft]
                        for duplicate in self.__subnodes__.keys():
                            if duplicate in result.keys():
                                del result[duplicate]
                            if "Descendants" not in result:
                                result["Descendants"] = list()
                            result["Descendants"].append(duplicate)
                        return result
                    self.get = partial(get, self)
                if "POST" in lower["__supports__"]:
                    self.post = partial(self.request, "POST", "{}/{}".format(parent,name), json_encoded=False)
                if "PATCH" in lower["__supports__"]:
                    self.patch = partial(self.request, "PATCH", "{}/{}".format(parent,name), json_encoded=False)
                if "DELETE" in lower["__supports__"]:
                    self.delete = partial(self.request, "DELETE", "{}/{}".format(parent,name), json_encoded=False)
            elif node == "%n":
                if parent != "":
                    result = self.request("GET", "{}/{}".format(parent, name))
                else:
                    result = self.request("GET", "{}".format(name))
                for location in result["Members"]:
                    ident = location["@odata.id"][len("{}{}{}/".format(api, parent, name)):].strip("/")
                    if parent != "":
                        self.__subnodes__[ident] = Klass(ident, "{}/{}".format(parent, name), lower["%n"], username, password, target, self.session, api=api, session_link=self.session_link)
                    else:
                        self.__subnodes__[ident] = Klass(ident, "{}".format(name), lower["%n"], username, password, target, self.session, api=api, session_link=self.session_link)
            else:
                if parent != "":
                    self.__subnodes__[node] = Klass(node, "{}/{}".format(parent, name), lower[node], username, password, target, self.session, api=api, session_link=self.session_link)
                else:
                    self.__subnodes__[node] = Klass(node, "{}".format(name), lower[node], username, password, target, self.session, api=api, session_link=self.session_link)
    
    def __str__(self):
        if hasattr(self, "get"):
            data = self.get()
            return json.dumps(data, indent=4)
        else: 
            return json.dumps(self.__subnodes__.keys(), indent=4)
            
    def __del__(self):
        if (self.parent == "") and (self.name == ""):
            try:
                self.session.delete(self.session_link)
            except:
                pass
        super(Klass, self).__del__()
            
            
    def __repr__(self):
        return self.__str__()
            
    def __dict__(self):
        if hasattr(self, "get"):
            return self.get()
        else: 
            return super(Klass, self).__dict__()
            
    def __call__(self, value):
        if hasattr(self, "patch"):
            return self.patch(value)
        else: 
            return super(Klass, self).__call__(value)
            
    def __getattr__(self, key):
        if key in self.__subnodes__.keys():
            return self.__subnodes__[key]
        else:
            raise AttributeError("{} object has no attribute '{}'".format(self.name or "", key))
            
    def __getitem__(self, key):
        if key in self.__subnodes__.keys():
            return self.__subnodes__[key]
        else:
            raise AttributeError("{} object has no attribute '{}'".format(self.name or "", key))
            
    def request(self, method, endpoint, data=None, json_encoded=True, retries=5):
        if data is not None:
            data = json.dumps(data)
        response = None
        req = requests.Request(method.upper(),"{}{}{}".format(self.target, self.api, endpoint), data=data)
        prepped = self.session.prepare_request(req)
        for i in range(0, 3):
            try:
                response = self.session.send(prepped)
                if (response.status_code not in [200, 201]) and (retries > 0):
                    self.session, response = self.login(self.target, self.username, self.password)
                    jdata = response.json()
                    self.session_link = jdata["@odata.context"]
                    sleep(0.25)
                    response = self.request(method, endpoint, data, False, retries-1)
                if response.status_code in [200, 201]:
                    break
            except Exception as e:
                sleep(0.25)
        if json_encoded:
            return response.json()
        else:
            return response
        
    def login(self, host, username=None, password=None):
        username = username or "ADMIN"
        password = password or "ADMIN"
        if not host:
            raise Exception("You must provide a valid hostname or IP")
        session = requests.Session()
        session.headers.update({"User-Agent":"Nerdalize-Redfish-1.0.0", "Accept":"Application/json"})
        session.verify = False
        data = {
            "UserName": username,
            "Password": password
        }
        jdata=json.dumps(data)
        response = session.post("{}/redfish/v1/SessionService/Sessions/".format(host), data=jdata)
        global login_result
        login_result = response
        global X_Auth_Token
        X_Auth_Token = response.headers.get("X-Auth-Token")
        session.headers.update({"X-Auth-Token": X_Auth_Token})
        return session, response
  
    
def API(target="", username=None, password=None, api="/redfish/v1/"):
    return Klass(target=target, username=username, password=password, name="", parent="", lower=__spec__, api=api)
        
