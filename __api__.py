'''
The Redfish V1.0 API Definition
'''

__api__ = {
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
