import numpy as np

def GetBezierPoints(p0, p1, p2, p3, points):
    retVal = []
    for i in np.arange(0,1, 1.0/float(points)):
        #print(i)
        if i == 0.0:
            retVal.append(p0)
            continue
        newPoint = (1-i)**3 * p0 + 3*(1-i)**2*i*p1 + 3*(1-i) * i**2 * p2 + i**3 * p3
        retVal.append(newPoint)
    retVal.append(p3)
    return retVal

#x0 = np.array([100.0,100.0])
#x1 = np.array([5.0,5.0])
#x2 = np.array([10.0,10.0])
#x3 = np.array([200.0,200.0])
#print(GetBezierPoints(x0, x1, x2, x3, 5))