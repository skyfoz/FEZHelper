local fezSideContainer = {}

fezSideContainer.name = "FEZHelper/fezSideContainer"
fezSideContainer.depth = 10000;
fezSideContainer.nodeLimits = {4, 4}
fezSideContainer.fillColor = {0.5, 0.5, 1, 0.5}
fezSideContainer.borderColor = {0.5, 0.5, 1, 1}



fezSideContainer.placements = {
    name = "FEZ Side Container",
    placementType = "rectangle",
    data = {
        width = 8,
        height = 8,
    }
}

fezSideContainer.nodeLineRenderType = "line"

return fezSideContainer