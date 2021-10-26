import xml.etree.ElementTree as ET
from xml.dom import minidom
import re
import numpy as np
from BezierCurve import GetBezierPoints as bp
import pygame
import time
import triangulate
import stl
from stl import mesh
import copy
# read the SVG file
doc = minidom.parse('tampa-bay-buccaneers-logo.svg')
path_strings = [path.getAttribute('d') for path
                in doc.getElementsByTagName('path')]
color_strings = [path.getAttribute('style') for path
                in doc.getElementsByTagName('path')]
doc.unlink()
#print(path_strings)
#print(len(path_strings))
#print(path_strings[0])
#newStr = path_strings[0].split()
global lolov
lolov = []
global lov
lov = []

def combined_stl(meshes, save_path="./combined.stl"):
    combined = mesh.Mesh(np.concatenate([m.data for m in meshes]))
    combined.save(save_path, mode=stl.Mode.ASCII)

def getTriangles(pts):
    tri = []
    plist = []
    if triangulate.IsClockwise(pts):
        plist = pts[::-1]
    else:
        plist = pts[:]
    while len(plist) >= 3:
        a = triangulate.GetEar(plist)
        if a == []:
            break
        tri.append(a)

    return tri

def createLine(x, y, vertices):
    arr = np.array([float(x), float(y)])
    currPoint = arr
    vertices = np.append(vertices, currPoint)
    return currPoint

def singlePolarity(vert):
    sum = 0
    if len(vert) < 4:
        return
    for v in range(0, len(vert),2):
        if v == len(vert) -2:
            #print("(" + str(vert[0]) + "," + str(vert[1]) + "),(" + str(vert[v]) + "," + str(vert[v+1]) + ")")
            sum = sum + (vert[0]-vert[v]) * (vert[1] - vert[v+1])
        else:
            #print("(" + str(vert[v]) + "," + str(vert[v+1]) + "),(" + str(vert[v+2]) + "," + str(vert[v+3]) + ")")
            sum = sum + (vert[v+2]-vert[v]) * (vert[v+3] - vert[v+1])
    if sum < 0:
        print("clockwise")
    else:
        print("ccw")

def drawLines():
    pygame.init()
    surface = pygame.display.set_mode((800,800))
    surface.fill((255,255,255))
    color = (0,0,0)
    for listOfVer in lolov:
        for vert in listOfVer:
            #surface.fill((255,255,255))
            #singlePolarity(vert)
            #time.sleep(1)
            for i in range(0, len(vert)-3, 2):
                pygame.draw.line(surface, color, (vert[i], vert[i+1]), (vert[i+2], vert[i+3]))
                pygame.display.flip()
                time.sleep(.02)
            #time.sleep(1)

def drawLineCurr():
    pygame.init()
    surface = pygame.display.set_mode((800,800))
    surface.fill((255,255,255))
    color = (0,0,0)
    for i in range(0, len(vertices)-3, 2):
        pygame.draw.line(surface, color, (vertices[i], vertices[i+1]), (vertices[i+2], vertices[i+3]))
        pygame.display.flip()
    input("press enter to continue")

def makeVerticesPositive():
    min = 0
    for vert in lov:
        for v in vert:
            if v < min:
                min = v
    print(min)
    if min < 0:
        for vert in lov:
            for i in range(0,len(vert)):
                vert[i] = vert[i] - min

def determinePolarity():
    
    for vert in lov:
        sum = 0
        if len(vert) < 4:
            continue
        for v in range(0, len(vert),2):
            if v == len(vert) -2:
                #print("(" + str(vert[0]) + "," + str(vert[1]) + "),(" + str(vert[v]) + "," + str(vert[v+1]) + ")")
                sum = sum + (vert[0]-vert[v]) * (vert[1] - vert[v+1])
            else:
                #print("(" + str(vert[v]) + "," + str(vert[v+1]) + "),(" + str(vert[v+2]) + "," + str(vert[v+3]) + ")")
                sum = sum + (vert[v+2]-vert[v]) * (vert[v+3] - vert[v+1])
        if sum < 0:
            print("clockwise")
        else:
            print("ccw")
    
#for s in newStr:
#    print(s)
#print(len(newStr))
#for s in newStr:
 #   print(s)
for path in path_strings:
    newStr = re.split('([a-zA-Z])', path)
    global currPoint
    currPoint = np.array([0.0,0.0])
    global initialPoint
    initialPoint = np.array([0.0,0.0])
    global vertices
    vertices = np.array([0.0,0.0])

    draw = 0
    for i in range(len(newStr)):
        #print(newStr[i])
        #print(newStr[i].strip())
        if newStr[i].strip() == 'm':
            if(len(vertices) > 2): 
                lov.append(vertices.copy())   
            if(currPoint[0] != 0 and currPoint[1] != 0):
                tempPoint = np.asarray(np.array(newStr[i+1].strip().split()[0].split(',')[0:2]), dtype = float)
                currPoint = np.add(tempPoint, currPoint)
                initialPoint = currPoint.copy()
            else:
                initialPoint = np.asarray(np.array(newStr[i+1].strip().split()[0].split(',')[0:2]), dtype = float)
                currPoint = np.asarray(np.array(newStr[i+1].strip().split()[0].split(',')[0:2]), dtype = float)
            vertices = np.empty(1)
            vertices = currPoint.copy()
            for b in range(2, len(newStr[i+1].strip().split())):
                currPoint = createLine(float(newStr[i+1].strip().split()[b].split(',')[0]) + currPoint[0], float(newStr[i+1].strip().split()[b].split(',')[1]) + currPoint[1], vertices)
        elif newStr[i].strip() == 'M':
            lov.append(vertices.copy())   
            vertices = np.empty(1)
            initialPoint = np.empty(1)
            currPoint = np.empty(1)
            initialPoint = np.asarray(np.array(newStr[i+1].strip().split(',')[0:2]), dtype = float)
            currPoint = np.asarray(np.array(newStr[i+1].strip().split(',')[0:2]), dtype = float)
            vertices = np.asarray(np.array(newStr[i+1].strip().split(',')[0:2]), dtype = float)
            for b in range(2, len(newStr[i+1].strip().split(','))):
                currPoint = createLine(float(newStr[i+1].strip().split(',')[b]), float(newStr[i+1].strip().split(',')[b+1]), vertices)
        elif newStr[i].strip() == 'h':
            for x in range(0, len(newStr[i+1].strip().split())):
                currPoint = createLine(float(newStr[i+1].strip().split()[x]) + currPoint[0], currPoint[1], vertices)
        elif newStr[i].strip() == 'H':
            for x in range(0, len(newStr[i+1].strip().split())):
                currPoint = createLine(float(newStr[i+1].strip().split()[x]), currPoint[1], vertices)
        elif newStr[i].strip() == 'v':
            for x in range(0, len(newStr[i+1].strip().split())):
                currPoint = createLine(currPoint[0], float(newStr[i+1].strip().split()[x]) + currPoint[1], vertices)
        elif newStr[i].strip() == 'V':
            for x in range(0, len(newStr[i+1].strip().split())):
                currPoint = createLine(currPoint[0], float(newStr[i+1].strip().split()[x]), vertices)
        elif newStr[i].strip() == 'l':
            line = newStr[i+1].strip().split()
            for l in line:
                arr = np.asarray(np.array(l.strip().split(',')), dtype = float)
                currPoint = np.add(arr, currPoint)
                currPoint = createLine(currPoint[0], currPoint[1], vertices)
        elif newStr[i].strip() == 'L':
            line = newStr[i+1].strip().split()
            for l in line:
                points = l.split(',')
                currPoint = createLine(points[0], points[1], vertices)
        elif newStr[i].strip() == 'c':
            line = newStr[i+1].strip().split()
            if len(line)%3 != 0:
                print("Some error idk c should be divisible by 3")
                if len(line) == 1:
                    for l in line:
                        arr = np.asarray(np.array(l.strip().split(',')), dtype = float)
                        currPoint = np.add(arr, currPoint)
                        currPoint = createLine(currPoint[0], currPoint[1], vertices)
            else:
                for x in range(0, len(line), 3):
                    x1 = np.add(currPoint, np.asarray(np.array(line[x].strip().split(',')), dtype = float))
                    x2 = np.add(currPoint, np.asarray(np.array(line[x+1].strip().split(',')), dtype = float))
                    x3 = np.add(currPoint, np.asarray(np.array(line[x+2].strip().split(',')), dtype = float))
                    newVertices = bp(currPoint, x1, x2, x3, 5)
                    vertices = np.append(vertices, newVertices)
                    currPoint = x3
        elif newStr[i].strip() == 'C':
            line = newStr[i+1].strip().split()
            if len(line)%3 != 0:
                print("some error in C part")
            for x in range(0, len(line), 3):
                x1 = np.asarray(np.array(line[x].strip().split(',')), dtype = float)
                x2 = np.asarray(np.array(line[x+1].strip().split(',')), dtype = float)
                x3 = np.asarray(np.array(line[x+2].strip().split(',')), dtype = float)
                newVertices = bp(currPoint, x1, x2, x3, 5)
                vertices = np.append(vertices, newVertices)
                currPoint = x3
        elif newStr[i].strip() == 'z' or newStr[i].strip() == 'Z':
            if(len(vertices) > 2): 
                vertices = np.append(vertices, initialPoint)
            currPoint = initialPoint.copy()
        else:
            draw = 1
        if draw == 1:
            #drawLineCurr()
            draw = 0

    #print(vertices)
    print(len(vertices))
    lolov.append(lov.copy())
    lov.clear()
#makeVerticesPositive()
#determinePolarity()

#WHITE = (255, 255, 255)
#BLACK = (0, 0, 0)
#RED = (255, 0, 0)
#GREEN = (0, 255, 0)
#BLUE = (0, 0, 255)
#screen = pygame.display.set_mode((500, 500))
#for x in triangles:
#    pygame.draw.polygon(screen, RED, x, 1)
#    pygame.display.update()
#while True:
#    time.sleep(1)
drawLines()
def getSideTri(pt1, pt2, top, bot):
    p1t = pt1.copy()
    p2t = pt2.copy()
    p1b = pt1.copy()
    p2b = pt2.copy()
    p2t.append(top)
    p2b.append(bot)
    p1t.append(top)
    p1b.append(bot)
    retVal = []
    retVal.append([p1t, p1b, p2t])
    retVal.append([p1b, p2b, p2t])
    return retVal

def createStl():
    topHeight = 0
    botHeight = 0
    incrHeight = 10
    cubes = []
    for listOfVert in lolov:
        topHeight = topHeight + incrHeight
        for vert in listOfVert:
            pts = []
            for i in range(0, len(vert), 2):
                pts.append([vert[i],vert[i+1]])
            triangles = getTriangles(pts)
            botTri = copy.deepcopy(triangles)
            topTri = copy.deepcopy(triangles)
            sideTri = []
            for t in topTri:
                for v in t:
                    if len(v) == 2:
                        v.append(topHeight)
            for t in botTri:
                for v in t:
                    if len(v) == 2:
                        v.append(botHeight)
            cubeTop = mesh.Mesh(np.zeros(len(topTri), dtype=mesh.Mesh.dtype))
            for i in range(0,len(topTri)):
                cubeTop.vectors[i] = topTri[i]
            cubeBot = mesh.Mesh(np.zeros(len(botTri), dtype=mesh.Mesh.dtype))
            for i in range(0,len(botTri)):
                cubeBot.vectors[i] = [botTri[i][0], botTri[i][2], botTri[i][1]]
            for i in range(0, len(pts)):
                if i == len(pts)-1:
                    sideTri.append(getSideTri(pts[i], pts[0], topHeight, botHeight))
                else:
                    sideTri.append(getSideTri(pts[i], pts[i+1], topHeight, botHeight))
            cubeSide = mesh.Mesh(np.zeros(len(sideTri) * len(sideTri[0]), dtype=mesh.Mesh.dtype))
            for i in range(0, len(sideTri)):
                for j in range(0,len(sideTri[i])):
                    #print("i is " + str(i) + " and j is " + str(j))
                    cubeSide.vectors[i*2 + j] = sideTri[i][j]
            cubes.append(cubeTop)
            cubes.append(cubeBot)
            cubes.append(cubeSide)
    combined_stl(cubes)