import json, requests, os, zipfile, shutil, time

print("Downloading pmaports zip...")

content = requests.get("https://gitlab.com/postmarketOS/mirror/pmaports/-/archive/master/pmaports-master.zip").content

with open("pmaports.zip", "wb") as file:
    file.write(content)
    file.close()

print("Uncompressing pmaports...")

if os.path.exists("pmaports"):
    shutil.rmtree("pmaports")

os.mkdir("pmaports")

with zipfile.ZipFile("pmaports.zip", 'r') as zip_ref:
    zip_ref.extractall("pmaports")

os.remove("pmaports.zip")

print("Parsing pmaports devices...")

packages = []

for device_branch in ["testing", "downstream", "main", "community"]:
    packages += os.listdir("pmaports/pmaports-master/device/"+device_branch)

packages = [i[7:] for i in packages if i.startswith("device-")]

print("Scratching postmarketos wiki... 0% 0/"+str(len(packages)))

# TODO: remove hardcode
devices = {
    "Xiaomi": {
        "xiaomi-angelican": "Xiaomi Redmi 9C NFC (xiaomi-angelican)",
        "xiaomi-angelica": "Xiaomi Redmi 9C (xiaomi-angelica)",
    }
}

last_percent = 0

index = 0

for code_name in packages:
    while True:
        try:
            search_response = requests.get(
                "https://wiki.postmarketos.org/api.php", 
                params={
                    "format": "json", 
                    "action": "query", 
                    "list": "search", 
                    "srsearch": code_name, 
                    "srlimit": "1"
                }).json()["query"]["search"]
            break
        except:
            pass

        time.sleep(0.1)

    index += 1
    
    if len(search_response) > 0:
        display_name = search_response[0]["title"].split("/")[0]
        vendor = display_name.split(" ")[0].strip()

        if code_name not in display_name:
            continue

        for i in devices:
            if i.lower() == vendor.lower():
                vendor = i
                break

        if vendor not in devices:
            devices[vendor] = {}

        if display_name in devices[vendor].values():
            continue

        devices[vendor][code_name] = display_name

    percent = int(round(index / len(packages) * 100))

    if percent != last_percent:
        print(f"Scratching postmarketos wiki... {percent}% {index}/{len(packages)}")
        last_percent = percent

print("Dumping devices to json...")

devices = dict(sorted(devices.items()))

with open("devices.json", "w") as file:
    json.dump(devices, file)
    file.close()

shutil.rmtree("pmaports")
