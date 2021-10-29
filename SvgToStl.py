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
import earcut
#import geopandas as gpd
from shapely.geometry import Polygon
# read the SVG file
doc = minidom.parse('tampa-bay-buccaneers-logo6.svg')
# path strings is an array containing the d values from the path in the svg file
path_strings = [path.getAttribute('d') for path
                in doc.getElementsByTagName('path')]
# the color value for each path, not used
color_strings = [path.getAttribute('style') for path
                in doc.getElementsByTagName('path')]
doc.unlink()

#List of list of vertices
global lolov
lolov = []

#List of vertices
global lov
lov = []

#Method to save multiple meshes into one stl
def combined_stl(meshes, save_path="./combined.stl"):
    combined = mesh.Mesh(np.concatenate([m.data for m in meshes]))
    combined.save(save_path, mode=stl.Mode.ASCII)

# Method update the currPoint and add currPoint to vertices
# Returns updated currPoint
def createLine(x, y, vertices):
    arr = np.array([float(x), float(y)])
    currPoint = arr
    vertices = np.append(vertices, currPoint)
    return currPoint

#Draw all the vertices as lines, used mainly for debugging
def drawLines():
    pygame.init()
    surface = pygame.display.set_mode((800,800))
    surface.fill((255,255,255))
    color = (0,0,0)
    for listOfVer in lolov:
        for vert in listOfVer:
            for i in range(0, len(vert)-3, 2):
                pygame.draw.line(surface, color, (vert[i], vert[i+1]), (vert[i+2], vert[i+3]))
                pygame.display.flip()
            time.sleep(.5)
        time.sleep(10)

def drawPolygons(polygons):
    pygame.init()
    surface = pygame.display.set_mode((800,800))
    surface.fill((255,255,255))
    RED = (255, 0, 0)
    screen = pygame.display.set_mode((500, 500))
    for x in polygons:
        pygame.draw.polygon(screen, RED, x, 1)
        pygame.display.update()
        time.sleep(3)
    while True:
        time.sleep(1)

#Draws line for the current vertice, used mainly for debugging
def drawLineCurr():
    pygame.init()
    surface = pygame.display.set_mode((800,800))
    surface.fill((255,255,255))
    color = (0,0,0)
    for i in range(0, len(vertices)-3, 2):
        pygame.draw.line(surface, color, (vertices[i], vertices[i+1]), (vertices[i+2], vertices[i+3]))
        pygame.display.flip()
    input("press enter to continue")

# Loop through each path in path_strings
for path in path_strings:
    #separate each path in path_strings out by letter
    newStr = re.split('([a-zA-Z])', path)
    global currPoint
    currPoint = np.array([0.0,0.0])
    global initialPoint
    initialPoint = np.array([0.0,0.0])
    global vertices
    vertices = np.array([0.0,0.0])

    draw = 0
    #loop through each letter in the path
    for i in range(len(newStr)):
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
            draw = 0

    lov.append(vertices)
    print(len(vertices))
    lolov.append(lov.copy())
    lov.clear()
    
def drawTriangles(triangles):
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    screen = pygame.display.set_mode((500, 500))
    for x in triangles:
        pygame.draw.polygon(screen, RED, x, 1)
        pygame.display.update()
    while True:
        time.sleep(1)

def drawNewTri(newTri, pts):
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    screen = pygame.display.set_mode((500, 500))
    for i in range(0, len(newTri), 3):
        pygame.draw.polygon(screen, RED, [pts[newTri[i]], pts[newTri[i+1]], pts[newTri[i+2]]], 1)
        pygame.display.update()
    time.sleep(5)

def getScreenReady():
    return pygame.display.set_mode((500, 500))
#drawLines()
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

def getSides(pts, holes, topHeight, botHeight):
    retVal = []
    splitPoints = []
    if len(holes) > 0:
        splitPoints.append(pts[0:holes[0]])
        for i in range(len(holes)):
            splitPoints.append(pts[holes[i]:holes[i+1]]) if len(holes)-1 > i else splitPoints.append(pts[holes[i]:len(pts)])
    else:
        splitPoints.append(pts)
        
    for p in splitPoints:
        sideTri = []
        for i in range(0, len(p)):
            if i == len(p)-1:
                sideTri.append(getSideTri(p[i], p[0], topHeight, botHeight))
            else:
                sideTri.append(getSideTri(p[i], p[i+1], topHeight, botHeight))
        cubeSide = mesh.Mesh(np.zeros(len(sideTri) * len(sideTri[0]), dtype=mesh.Mesh.dtype))
        for i in range(0, len(sideTri)):
            for j in range(0,len(sideTri[i])):
                cubeSide.vectors[i*2 + j] = sideTri[i][j]
        retVal.append(cubeSide)

    return retVal

def createStl():
    topHeight = 0
    botHeight = 0
    incrHeight = 10
    smallerInc = 1
    cubes = []
    for listOfVert in lolov:
        topHeight = topHeight + incrHeight
        allVertPts = []
        pts = []
        holes = []
        for v in listOfVert:
            holes.append([])
        
        for vert in listOfVert:
            pts=[]
            for i in range(0, len(vert), 2):
                pts.append([vert[i],vert[i+1]])
            allVertPts.append(pts.copy())
        for j in range(0, len(allVertPts)):
            for i in range(0, len(allVertPts)-1):
                if triangulate.GetArea(allVertPts[i]) < triangulate.GetArea(allVertPts[i+1]):
                    tempPt = allVertPts[i].copy()
                    allVertPts[i] = allVertPts[i+1].copy()
                    allVertPts[i+1] = tempPt.copy()
        polygons = []
        for pt in allVertPts:
            polygons.append(Polygon(pt.copy()))
        drawPolygons(allVertPts)


        ###
        # If a polygon is inside of two polygons
        # duplicate the middle one and add a new layer for it
        ###
        for i in range(0,len(allVertPts)-1):
            if(i > len(allVertPts)-2):
                continue
            for j in range(i+1, len(allVertPts)):
                if(j > len(allVertPts)-1):
                    continue
                if polygons[i].contains(Polygon(allVertPts[j])):
                    print("combine " + str(i) + " with " + str(j))
                    holes[i].append(len(allVertPts[i]))
                    for l in allVertPts[j]:
                        allVertPts[i].append(l)
                    allVertPts.pop(j)
                    polygons.pop(j)
                    holes.pop(j)
        topHeight = topHeight + smallerInc
        for c in range(len(allVertPts)):
            print(1)
            verts = []
            for b in range(len(allVertPts[c])):
                verts.append(allVertPts[c][b][0])
                verts.append(allVertPts[c][b][1])
            newTri = earcut.earcut(verts, holes[c])
            botTri = []
            topTri = []
            topPts = copy.deepcopy(allVertPts[c])
            botPts = copy.deepcopy(allVertPts[c])
            for tp in topPts:
                tp.append(topHeight)
            for bp in botPts:
                bp.append(botHeight)
            for i in range(0, len(newTri), 3):
                topTri.append((topPts[newTri[i]], topPts[newTri[i+1]], topPts[newTri[i+2]]))
                botTri.append((botPts[newTri[i]], botPts[newTri[i+2]], botPts[newTri[i+1]]))
            cubeTop = mesh.Mesh(np.zeros(len(topTri), dtype=mesh.Mesh.dtype))
            for i in range(0,len(topTri)):
                cubeTop.vectors[i] = topTri[i]
            cubeBot = mesh.Mesh(np.zeros(len(verts), dtype=mesh.Mesh.dtype))
            for i in range(0,len(botTri)):
                cubeBot.vectors[i] = botTri[i]
            cubes.append(cubeTop)
            cubes.append(cubeBot)
            sideCubes = getSides(allVertPts[c], holes[c], topHeight, botHeight)
            for side in sideCubes:
                cubes.append(side)
        combined_stl(cubes)
createStl()