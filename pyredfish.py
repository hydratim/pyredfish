'''
Goal:
A class that:
    - Is automatically constructed from simple input (such as a spec dictionary)
    - Builds query urls from class hierarchy
    - Automatic relogin if session expired
    - Automatic logout on garbage collection
    - Provides a simple pythonic adaption of the Redfish API
'''

import json
from time import sleep
from functools import partial
import logging

import requests

from __api__ import __api__

requests.adapters.DEFAULT_RETRIES = 100

class InvalidIPAddress(Exception):
    '''Triggered when the user supplies an invalid IP address.'''
    pass


class Redfish:
    '''
    An api client that automatically constructs it self from the spec dictionary.
    '''

    def __init__(self, name, parent, lower, credentials, session=None, session_link=None):
        self.username = credentials[1]
        self.password = credentials[2]
        if not session:
            self.session, response = self.login(credentials[0])
            jdata = response.json()
            self.session_link = jdata["@odata.context"]
        else:
            self.session = session
            self.session_link = session_link
        self.api = "/redfish/v1/"
        self.target = credentials[0]
        self.parent = parent
        self.__subnodes__ = dict()
        self.name = name
        for node in lower.keys():
            if node == "__supports__":
                if "GET" in lower["__supports__"]:
                    def get(self):  # Still nessecary???
                        result = self.request(
                            "GET", "{}/{}".format(parent, name))
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
                    self.post = partial(
                        self.request, "POST", "{}/{}".format(parent, name), json_encoded=False)
                if "PATCH" in lower["__supports__"]:
                    self.patch = partial(
                        self.request, "PATCH", "{}/{}".format(parent, name), json_encoded=False)
                if "DELETE" in lower["__supports__"]:
                    self.delete = partial(
                        self.request, "DELETE", "{}/{}".format(parent, name), json_encoded=False)
            elif node == "%n":
                if parent != "":
                    result = self.request("GET", "{}/{}".format(parent, name))
                else:
                    result = self.request("GET", "{}".format(name))
                for location in result["Members"]:
                    ident = location["@odata.id"][len(
                        "{}{}{}/".format(self.api, parent, name)):].strip("/")
                    if parent != "":
                        self.__subnodes__[ident] = Redfish(ident, "{}/{}".format(parent, name), lower["%n"],
                                                           credentials, self.session, session_link=self.session_link)
                    else:
                        self.__subnodes__[ident] = Redfish(ident, "{}".format(
                            name), lower["%n"], credentials, self.session, session_link=self.session_link)
            else:
                if parent != "":
                    self.__subnodes__[node] = Redfish(node, "{}/{}".format(parent, name), lower[node],
                                                      credentials, self.session, session_link=self.session_link)
                else:
                    self.__subnodes__[node] = Redfish(node, "{}".format(
                        name), lower[node], credentials, self.session, session_link=self.session_link)

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
                logging.exception("tried to delete a non-existant session")

    def __repr__(self):
        return self.__str__()

    def __dict__(self):
        if hasattr(self, "get"):
            return self.get()
        else:
            raise KeyError(
                "Target {} does not support GET".format(self.name or ""))

    def __call__(self, value):
        if hasattr(self, "patch"):
            return self.patch(value)
        else:
            raise TypeError(
                "Target {} does not support PATCH".format(self.name or ""))

    def __getattr__(self, key):
        if key in self.__subnodes__.keys():
            return self.__subnodes__[key]
        else:
            raise AttributeError(
                "{} object has no attribute '{}'".format(self.name or "", key))

    def __getitem__(self, key):
        if key in self.__subnodes__.keys():
            return self.__subnodes__[key]
        else:
            raise AttributeError(
                "{} object has no attribute '{}'".format(self.name or "", key))

    def request(self, method, endpoint, data=None, json_encoded=True, retries=5):
        '''Wrapper function for requests that ensures the client is logged in.'''
        if data is not None:
            data = json.dumps(data)
        response = None
        req = requests.Request(method.upper(), "{}{}{}".format(
            self.target, self.api, endpoint), data=data)
        prepped = self.session.prepare_request(req)
        for i in range(0, retries):
            try:
                response = self.session.send(prepped)
                # Attempt re-login
                if (response.status_code not in [200, 201]) and (retries > 0):
                    self.session, response = self.login(self.target)
                    jdata = response.json()
                    self.session_link = jdata["@odata.context"]
                    sleep(0.25)
                    response = self.request(
                        method, endpoint, data, False, retries-1)
                if response.status_code in [200, 201]:
                    break
            except:
                logging.exception("An exception occured in attempt %i", i)
                sleep(0.25)
        if json_encoded:
            return response.json()
        else:
            return response

    def login(self, host):
        '''Simple login wrapper / authentication handler'''
        username = self.username or "ADMIN"
        password = self.password or "ADMIN"
        if not host:
            raise InvalidIPAddress("You must provide a valid hostname or IP")
        session = requests.Session()
        session.headers.update(
            {"User-Agent": "PyRedfish-1.0.0", "Accept": "Application/json"})
        session.verify = False
        data = {
            "UserName": username,
            "Password": password
        }
        jdata = json.dumps(data)
        response = session.post(
            "{}/redfish/v1/SessionService/Sessions/".format(host), data=jdata)
        x_auth_token = response.headers.get("X-Auth-Token")
        session.headers.update({"X-Auth-Token": x_auth_token})
        return session, response


def connect(target="", username=None, password=None):
    '''Creates a new redfish client'''
    return Redfish(credentials=(target, username, password), name="", parent="", lower=__api__)
