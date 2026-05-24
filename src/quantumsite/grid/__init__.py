coords = []
for y in range(6):  # 0 to 5
    for x in range(6):  # 0 to 5
        #for z in range(6):  # 0 to 5
        coords.append((x, y, 0))



edges = []
for y in range(6):
    for x in range(6):
        coord1 = (x, y , 0)
        idx1 = coords.index(coord1)
        if x < 5:
            coord2 = (x + 1, y, 0)
            idx2 = coords.index(coord2)
            edges.append((idx1, idx2))  # connect to right neighbor
        if y < 5:
            coord3 = (x, y + 1, 0)
            idx3 = coords.index(coord3)
            edges.append((idx1, idx3))  # connect to upper neighbor

print(coords)
print(edges)
