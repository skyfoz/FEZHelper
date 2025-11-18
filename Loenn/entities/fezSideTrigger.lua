local fezSideTrigger = {}

fezSideTrigger.name = "FEZHelper/fezSideTrigger"
fezSideTrigger.depth = 10000;
fezSideTrigger.nodeLimits = {4, 4}
fezSideTrigger.fillColor = {0.5, 0.5, 1, 0.5}
fezSideTrigger.borderColor = {0.5, 0.5, 1, 1}



fezSideTrigger.placements = {
    name = "FEZ Side Trigger",
    placementType = "rectangle",
    data = {
        width = 8,
        height = 8,
    }
}

fezSideTrigger.nodeLineRenderType = "line"

return fezSideTrigger