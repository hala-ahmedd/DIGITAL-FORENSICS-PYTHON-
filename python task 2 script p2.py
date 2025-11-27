#needed libaries 
from Registry import Registry
import os

#folder on the local machine that contains the registry files
HIVES_DIR = r"C:\Users\HALA AHMED\Desktop\hives" #customized based as mentioned in the report

#dictionary variable with the file paths
HIVES = {
    "SAM":os.path.join(HIVES_DIR, "SAM"),
    "SYSTEM":os.path.join(HIVES_DIR, "SYSTEM"),
    "SOFTWARE":os.path.join(HIVES_DIR, "SOFTWARE"),
    "NTUSER":os.path.join(HIVES_DIR, "NTUSER.DAT")
}

#function 1: registries paths
def open_key(hive_path, key_path): # registry opening function + error handeling method
    try:
        reg = Registry.Registry(hive_path)
        return reg.open(key_path)
    except Exception:
        return None
    
#function 2: extracting system info
def get_system_info():
    cv = open_key(HIVES["SOFTWARE"], r"Microsoft\Windows NT\CurrentVersion")
    tz = open_key(HIVES["SYSTEM"], r"ControlSet001\Control\TimeZoneInformation")
    return {
        "OS": cv.value("ProductName").value() if cv else "Unknown",
        "Version": cv.value("CurrentVersion").value() if cv else "Unknown",
        "TimeZone": tz.value("TimeZoneKeyName").value() if tz else "Unknown"
    }

#function 3: extracting the user accounts 
def get_user_accounts():
    key = open_key(HIVES["SAM"], r"SAM\Domains\Account\Users\Names")
    return [k.name() for k in key.subkeys()] if key else []

#function 4: extracting the installed applications
def get_installed_apps():
    paths = [
        r"Microsoft\Windows\CurrentVersion\Uninstall",
        r"Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
    ]
    apps = []
    for path in paths:
        key = open_key(HIVES["SOFTWARE"], path)
        if not key:
            continue #error handeling 
        #recursive search
        for sub in key.subkeys():
            vals = {v.name(): v.value() for v in sub.values()}
            name = vals.get("DisplayName")
            if name:
                apps.append({
                    "Name": name,
                    "Version": vals.get("DisplayVersion", "Unknown"), #error handeling method too 
                    "Publisher": vals.get("Publisher", "Unknown")
                })
    return apps

# function 5: extracting the usb devices
def get_usb_history():
    key = open_key(HIVES["SYSTEM"], r"ControlSet001\Enum\USBSTOR")
    usb = []
    if not key:
        return usb
    for dev in key.subkeys():
        for inst in dev.subkeys():
            try:
                friendly = inst.value("FriendlyName").value()
            except:
                friendly = dev.name()
            usb.append({
                "Device": dev.name(),
                "Instance": inst.name(),
                "FriendlyName": friendly
            })
    return usb

#function 6:extracting the types commands
def get_run_mru():
    key = open_key(HIVES["NTUSER"], r"Software\Microsoft\Windows\CurrentVersion\Explorer\RunMRU")
    if not key:
        return []
    return [
        {"Key": v.name(), "Command": v.value()}
        for v in key.values()
        if v.name() != "MRUList"
    ]

#MAIN FUNCTION: orchestration 
def main():
    print("\nSYSTEM INFO")
    info = get_system_info()
    for k, v in info.items():
        print(f"{k}: {v}")

    print("\nUSER ACCOUNTS")
    for user in get_user_accounts():
        print(" -", user)

    print("\nINSTALLED APPLICATIONS")
    apps = get_installed_apps()
    for app in apps:
        print(f" - {app['Name']} | {app['Version']} | {app['Publisher']}")
    print(f"Total: {len(apps)}")

    print("\nUSB HISTORY")
    usb = get_usb_history()
    for u in usb:
        print(f" - {u['Device']} | {u['Instance']} | {u['FriendlyName']}")
    print(f"Total USB devices: {len(usb)}")

    print("\nCOMMAND HISTORY (RunMRU)")
    for cmd in get_run_mru():
        print(f" {cmd['Key']} -> {cmd['Command']}")

if __name__ == "__main__": 
    main()#provoking step
