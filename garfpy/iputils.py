import ipaddress

def is_private(target):
    try:
        ip_obj = ipaddress.ip_address(target)
        if ip_obj.is_private:
            return True
    except ValueError:
        if "crate.lan" in target.lower():
            return True
        if "crate.zip" in target.lower():
            return True
        if "memtec.org" in target.lower():
            return True
        if "crateit.net" in target.lower():
            return True
        if "garfbot.art" in target.lower():
            return True
    return False
