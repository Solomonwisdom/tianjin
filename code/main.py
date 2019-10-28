import math
import json

POSITION = [[54,26],[87,11],[48,61],[30,84],[90,45],[89,76],[102,92],[74,111],[132,63],[137,115]]

MISSION = [3,1,4,7,0,2,2,5,5,1]

def test(event, context):
    id = int(event['data'])
    distance = {}
    for i in range(len(POSITION)):
        if i!=id:
            distance[i] = math.sqrt(pow(POSITION[i][0] - POSITION[id][0],2) + pow(POSITION[i][1] - POSITION[id][1],2))
    rank1 = sorted(distance.items(), key=lambda item: item[1])
    #print(rank1)
    res1 = {}
    for i in range(len(rank1)):
        res1[rank1[i][0]] = i
    #print(res1)
    mission = {}
    for i in range(len(MISSION)):
        if i!=id:
            mission[i] = MISSION[i]
    rank2 = sorted(mission.items(), key=lambda item: item[1])
    #print(rank2)
    res2 = {}
    for i in range(len(rank2)):
        res2[rank2[i][0]] = i
    #print(res2)
    res = {}
    for i in range(10):
        if i!=id:
            res[i] = res1[i] + res2[i]
    #print(res)
    rank = sorted(res.items(), key=lambda item: item[1])
    get = rank[0][0]
    res = {
        "get": get,
        "position": POSITION[get],
        "mission": MISSION[get]
    }
    return bytes(json.dumps(res), encoding='utf-8')

if __name__ == '__main__':
    a,b,c = test(9)
    print(a)
    print(b)
    print(c)




