coords = []
for y in range(6):  # 0 to 5
    for x in range(6):  # 0 to 5
        #for z in range(6):  # 0 to 5
        coords.append((x, y, 0))


edges = []
for y in range(6):
    for x in range(6):
        if x < 5:
            edges.append(((x, y, 0), (x+1, y, 0)))  # connect to right neighbor
        if y < 5:
            edges.append(((x, y, 0), (x, y+1, 0)))  # connect to upper neighbor

print (coords, edges)