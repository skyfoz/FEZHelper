import requests
import os
import wx
from midvoxio.voxio import vox_to_arr
import midvoxio.voxio as voxio
import numpy as np

BIN_TO_JSON = "https://maddie480.ovh/celeste/bin-to-json"
JSON_TO_BIN = "https://maddie480.ovh/celeste/json-to-bin"


def showMainMenu():
    print("Celeste FEZ Pillar Placer")
    print("----------------------------------------\n")
    print("0. Quit")
    print("1. Place FEZ pillar in map")
    
    choice = input("\nEnter your choice: ")
    while choice not in ["0", "1"]:
        print("Invalid choice. Please try again.")
        choice = input("Enter your choice: ")
    
    return choice


def selectBinFile():
    print("\n----------------------------------------\n")
    print("Please select the map BIN file to modify.")
    
    app = wx.App(False)
    dialog = wx.FileDialog(None, "Choose a map", "", "", "*.bin", wx.FD_OPEN)
    
    inputBin = ""
    if dialog.ShowModal() == wx.ID_OK:
        inputBin = dialog.GetPath()
    dialog.Destroy()
    
    print(f"Selected map: {inputBin}")
    
    with open(inputBin, "rb") as f:
        print("Uploading encoded map...")
        resp = requests.post(BIN_TO_JSON, data=f)
        mapJson = resp.json()
    
    print("BIN converted to JSON")
    return inputBin, mapJson


def selectVoxFile():
    print("\n----------------------------------------\n")
    print("Select a .vox file to add your FEZ pillar model.")
    app = wx.App(False)
    dialog = wx.FileDialog(None, "Choose a .vox file", "", "", "*.vox", wx.FD_OPEN)
    
    binVoxPath = ""
    if dialog.ShowModal() == wx.ID_OK:
        binVoxPath = dialog.GetPath()
    dialog.Destroy()
    
    voxArray = vox_to_arr(binVoxPath)
    print(voxArray)
    sideSize = (max(voxArray.shape[0], voxArray.shape[1]), voxArray.shape[2])

    
    return binVoxPath, voxArray, sideSize

def getVoxelSides(voxArray, sideSize):
    sides = [[[None for _ in range(sideSize[1])] for _ in range(sideSize[0])] for _ in range(4)]
    depth = voxArray.shape[2]

    # Front side
    for y in range(voxArray.shape[1]):
        for z in range(depth - 1, -1, -1):
            row = (depth - 1) - z
            for x in range(voxArray.shape[0]):
                if sides[0][row][x] is None or sides[0][row][x][3] == 0:
                    sides[0][row][x] = voxArray[x, y, z]
    
    # Right side
    for x in range(voxArray.shape[0] - 1, -1, -1):
        for z in range(depth - 1, -1, -1):
            row = (depth - 1) - z
            for y in range(voxArray.shape[1]):
                if sides[1][row][y] is None or sides[1][row][y][3] == 0:
                    sides[1][row][y] = voxArray[x, y, z]

    # Back side
    for y in range(voxArray.shape[1] -1, -1, -1):
        for z in range(depth - 1, -1, -1):
            row = (depth - 1) - z
            for x in range(voxArray.shape[0]):
                if sides[2][row][x] is None or sides[2][row][x][3] == 0:
                    sides[2][row][x] = voxArray[x, y, z]
    
    # Left side
    for x in range(voxArray.shape[0]):
        for z in range(depth - 1, -1, -1):
            row = (depth - 1) - z
            for y in range(voxArray.shape[1]):
                if sides[3][row][y] is None or sides[3][row][y][3] == 0:
                    sides[3][row][y] = voxArray[x, y, z]
    return sides


def selectRoom(mapJson):
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
    
    return selectedRoom, roomNames


def getEntitiesNode(mapJson, roomNames, selectedRoom):
    mapObj = mapJson
    levelsNode = mapObj["children"][0]
    level = levelsNode["children"][roomNames.index(selectedRoom)]
    entitiesNode = level["children"][5]
    
    return entitiesNode


def getNextId(entitiesNode):
    existingIds = [
        ent["attributes"]["id"]
        for ent in entitiesNode["children"]
        if "id" in ent.get("attributes", {})
    ]
    
    return (max(existingIds) + 1) if existingIds else 0


def createFezCenter(newId):
    return {
        "name": "FEZHelper/fezCenter",
        "attributes": {
            "x": 2 * 8,
            "y": 2 * 8,
            "id": newId
        },
        "children": []
    }


def addPillarsLoop(entitiesNode, newId):
    while True:
        print("\nDo you want to add another FEZ pillar?")
        print("0. No, save and quit")
        print("1. Yes")
        choice = int(input("Enter your choice: "))
        
        if choice == 1:
            print("In the same room ?")
            print("0. No, select another room")
            print("1. Yes")
            sameRoomChoice = int(input("Enter your choice: "))
            
            newId += 1
            fezCenter = createFezCenter(newId)
            entitiesNode["children"].append(fezCenter)
            print(f"Added refill with id {newId}.")
        elif choice == 0:
            break
        else:
            print("Invalid choice. Please try again.")
    
    return newId


def chooseSaveLocation(inputBin):
    outputBin = ""
    
    while outputBin == "":
        print("\nSAVE OPTIONS:")
        print("0. Overwrite existing map")
        print("1. Save as new file")
        choice = int(input("Enter your choice: "))
        
        if choice == 0:
            outputBin = inputBin
        elif choice == 1:
            dialog = wx.FileDialog(None, "Save new map as", "", "", "*.bin", wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
            
            if dialog.ShowModal() == wx.ID_OK:
                outputBin = dialog.GetPath()
            
            dialog.Destroy()
        else:
            print("Invalid choice. Please try again.")
    
    return outputBin


def saveMap(outputBin, mapJson):
    print("Sending JSON back to get new encoded map")
    resp = requests.post(JSON_TO_BIN, json=mapJson)
    
    with open(outputBin, "wb") as f:
        f.write(resp.content)
    
    print("Done! New map saved as:", outputBin)
    print("\n----------------------------------------\n")


def main():
    while True:
        choice = showMainMenu()
        
        if choice == "0":
            print("Exiting...")
            os._exit(0)
        
        inputBin, mapJson = selectBinFile()

        binVoxPath, voxArray, sideSize = selectVoxFile()
        voxelSides = getVoxelSides(voxArray, sideSize)

        selectedRoom, roomNames = selectRoom(mapJson)

        entitiesNode = getEntitiesNode(mapJson, roomNames, selectedRoom)

        newId = getNextId(entitiesNode)
        fezCenter = createFezCenter(newId)
        entitiesNode["children"].append(fezCenter)
        print(f"Added refill with id {newId}.")
        
        print("\n----------------------------------------\n")

        newId = addPillarsLoop(entitiesNode, newId)

        outputBin = chooseSaveLocation(inputBin)
        saveMap(outputBin, mapJson)


if __name__ == "__main__":
    main()
