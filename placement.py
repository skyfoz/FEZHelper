import requests
import os
from pyvox.models import Vox
from pyvox.parser import VoxParser
import wx

BIN_TO_JSON = "https://maddie480.ovh/celeste/bin-to-json"
JSON_TO_BIN = "https://maddie480.ovh/celeste/json-to-bin"

print("Celeste FEZ Pillar Placer")
print("----------------------------------------\n")
print("0. Quit")
print("1. Place FEZ pillar in map")

choice = input("\nEnter your choice: ")
while choice not in ["0", "1"]:
    print("Invalid choice. Please try again.")
    choice = input("Enter your choice: ")
if choice == "0":
    print("Exiting...")
    os._exit(0)

print("\n----------------------------------------\n")
print("Please select the map BIN file to modify.")

INPUT_BIN = ""
OUTPUT_BIN = ""

app = wx.App(False)
dialog = wx.FileDialog(None, "Choose a map", "", "", "*.bin", wx.FD_OPEN)

if dialog.ShowModal() == wx.ID_OK:
    INPUT_BIN = dialog.GetPath()

dialog.Destroy()

print(f"Selected map: {INPUT_BIN}")

with open(INPUT_BIN, "rb") as f:
    print("Uploading encoded map...")
    resp = requests.post(BIN_TO_JSON, data=f)
    mapJson = resp.json()

print("BIN converted to JSON")


print("\n----------------------------------------\n")


roomNames = [
    level["attributes"]["name"]
    for level in mapJson["children"][0]["children"]
]

print("Available rooms:")
for (i, name) in enumerate(roomNames):
    print(f"{i}. {name}")

selectedRoom = input("\nEnter room name to add your FEZ pillar (case sensitive): ")

while selectedRoom not in roomNames:
    print("\nRoom not found. Please try again.")
    selectedRoom = input("Enter room name to add your FEZ pillar (case sensitive): ")


map = mapJson
levelsNode = map["children"][0]  
level = levelsNode["children"][roomNames.index(selectedRoom)]
entitiesNode = level["children"][5]


existingIds = [
    ent["attributes"]["id"]
    for ent in entitiesNode["children"]
    if "id" in ent.get("attributes", {})
]

newId = (max(existingIds) + 1) if existingIds else 0

fezCenter = {
    "name": "FEZHelper/fezCenter",
    "attributes": {
        "x": 2 * 8,
        "y": 2 * 8,
        "id": newId
    },
    "children": []
}

entitiesNode["children"].append(fezCenter)
print(f"Added refill with id {newId}.")

choice = -1

print("\n----------------------------------------\n")

while choice not in [0, 1]:
    print("\nWhere do you want to save the new map?")
    print("0. Overwrite existing map")
    print("1. Save as new file")
    choice = int(input("Enter your choice: "))
if choice == 0:
    OUTPUT_BIN = INPUT_BIN
elif choice == 1:
    dialog = wx.FileDialog(None, "Save new map as", "", "", "*.bin", wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)

    if dialog.ShowModal() == wx.ID_OK:
        OUTPUT_BIN = dialog.GetPath()

    dialog.Destroy()
else:
    print("Invalid choice. Please try again.")

print("Sending JSON back to get new encoded map")
resp = requests.post(JSON_TO_BIN, json=mapJson)

with open(OUTPUT_BIN, "wb") as f:
    f.write(resp.content)

print("Done! New map saved as:", OUTPUT_BIN)
