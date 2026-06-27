import xbmcaddon

def get_credentials():
    addon = xbmcaddon.Addon()

    host = addon.getSetting('host').strip().rstrip('/')
    user = addon.getSetting('username').strip()
    password = addon.getSetting('password').strip()

    if not host.startswith("http"):
        host = "http://" + host

    return host, user, password