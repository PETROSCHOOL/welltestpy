# -*- coding: utf-8 -*-
"""
Created on Fri Nov 18 19:13:55 2016

@author: Sebastian Mueller
"""
from __future__ import absolute_import, division, print_function

from copy import deepcopy as dcopy
import numpy as np

import matplotlib.pyplot as plt
# suppress the standard keybinding 's' for saving
plt.rcParams['keymap.save'] = ''
# use the ggplot style like R
plt.style.use('ggplot')


def triangulate(distances, prec, all_pos=False):
    '''
    try to triangulate points by given distances within a symmetric matrix
    'distances' with distances[i,j] = |pi-pj|

    thereby p0 will be set to the origin (0,0) and p1 to (|p0-p1|,0)
    '''

    if not distvalid(distances, prec/3.0):
        raise ValueError("Given distances are not valid")

    pntscount = np.shape(distances)[0]

    res = []

    # try to triangulate with all posible starting-point constellations
    for n in range(pntscount-1):
        for m in range(n+1, pntscount):
            print("")
            print("Startingconstelation {} {}".format(n, m))
            tmpres = triangulatesgl(distances, n, m, prec)

            for i in tmpres:
                res.append(i)

            if res != [] and not all_pos:
                break
        if res != [] and not all_pos:
            break

    if res == []:
        print("damn")
        return []

    res = rotate(res)

    print("number of overall results: {}".format(len(res)))
    sol = [res[0]]

    for i in range(1, len(res)):
        addable = True
        for j in sol:
            addable &= not solequal(res[i], j, prec)
        if addable:
            sol.append(res[i])

    return sol


def triangulatesgl(distances, sp1, sp2, prec):
    '''
    try to triangulate points, with startingpoints sp1 and sp2
    and a given precicion

    thereby sp1 will be at the origin (0,0) and sp2 will be at (|sp2-sp1|,0)
    '''

    res = []

    if distances[sp1, sp2] < -0.5:
        return res

    pntscount = np.shape(distances)[0]

    res = [pntscount*[0]]

    dis = distances[sp1, sp2]

    res[0][sp1] = np.array([0., 0.])
    res[0][sp2] = np.array([dis, 0.])

    for i in range(pntscount-2):
        print("add point {}".format(i))
        iterres = []
        for sglres in res:
            tmpres, state = addpoints(sglres, distances, prec)

            if state == 0:
                for k in tmpres:
                    iterres.append(dcopy(k))

        if iterres == []:
            return []
        res = dcopy(iterres)

    print("number of temporal results: {}".format(len(res)))

    return res


def addpoints(sol, distances, prec):
    '''
    tries for each point to add it to a given solution-approach
    gives all possibilties and a status about the solution:
        state = 0: possibilities found
        state = 1: no possibilities
        state = 2: solution-approach has a contradiction with a point
    '''

    res = []

    posfound = False

    # generate all missing points in the solution approach
    pleft = []
    for n, m in enumerate(sol):
        if np.ndim(m) == 0:
            pleft.append(n)

    # try each point to add to the given solution-approach
    for i in pleft:
        ires, state = addpoint(sol, i, distances, prec)

        # if a point is addable, add new solution-approach to the result
        if state == 0:
            posfound = True
            for j in ires:
                res.append(dcopy(j))
        # if one point gives a contradiction, return empty result and state 2
        elif state == 2:
            return [], 2

    # if no point is addable, return empty result and state 1
    if posfound:
        return res, 0

    return res, 1


def addpoint(sol, i, distances, prec):
    '''
    tries to add point i to a given solution-approach
    gives all possibilties and a status about the solution:
        state = 0: possibilities found
        state = 1: no possibilities but no contradiction
        state = 2: solution-approach has a contradiction with point i
    '''

    res = []

    # if i is already part of the solution return it
    if np.ndim(sol[i]) != 0:
        return [sol], 0

    # collect the points already present in the solution
    solpnts = []
    for n, m in enumerate(sol):
        if np.ndim(m) != 0:
            solpnts.append(n)

    # number of present points
    pntscount = len(solpnts)

    # try to add the point in all possible constellations
    for n in range(pntscount-1):
        for m in range(n+1, pntscount):
            tmppnt, state = pntcoord(sol, i, solpnts[n], solpnts[m],
                                     distances, prec)

            # if possiblities are found, add them (at most 2! (think about))
            if state == 0:
                for pnt in tmppnt:
                    res.append(dcopy(sol))
                    res[-1][i] = pnt

            # if one possiblity or a contradiction is found, return the result
            if state != 1:
                return res, state

    # if the state remaind 1, return empty result and no contradiction
    return res, state


def pntcoord(sol, i, n, m, distances, prec):
    '''
    generate coordinates for point i in constellation to points m and n
    check if these coordinates are valid with all other points in the solution
    '''

    tmppnt = []

    state = 1

    pntscount = len(sol)

    # if no distances known, return empty result and the unknown-state
    if distances[i, n] < -0.5 or distances[i, m] < -0.5:
        return tmppnt, state

    # if the Triangle inequality is not fullfilled give a contradiction
    if distances[i, n] + distances[i, m] < dist(sol[n], sol[m]):
        state = 2
        return tmppnt, state

    # generate the affine rotation to bring the points in the right place
    g = affinef(*invtranmat(*tranmat(sol[n], sol[m])))

    # generate the coordinates
    x = xvalue(distances[i, n], distances[i, m], dist(sol[n], sol[m]))
    y1, y2 = yvalue(distances[i, n], distances[i, m], dist(sol[n], sol[m]))

    # generate the possible positons
    pos1 = g(np.array([x, y1]))
    pos2 = g(np.array([x, y2]))

    valid1 = True
    valid2 = True

    # check if the possible positions are valid
    for k in range(pntscount):
        if np.ndim(sol[k]) != 0 and distances[i, k] > -0.5:
            valid1 &= abs(dist(sol[k], pos1)-distances[i, k]) < prec
            valid2 &= abs(dist(sol[k], pos2)-distances[i, k]) < prec

    # if any position is valid, add it to the result
    if valid1 or valid2:
        state = 0
        same = abs(y1-y2) < prec/4.0
        if valid1:
            tmppnt.append(dcopy(pos1))
        if valid2 and not same:
            tmppnt.append(dcopy(pos2))
    # if the positions are not valid, give a contradiction
    else:
        state = 2

    return tmppnt, state


def solequal(sol1, sol2, prec):
    '''
    compare two different solutions with a given precicion and return True
    if they equal
    '''

    res = True

    for sol_1, sol_2 in zip(sol1, sol2):
        if np.ndim(sol_1) != 0 and np.ndim(sol_2) != 0:
            res &= dist(sol_1, sol_2) < prec
        elif np.ndim(sol_1) != 0 and np.ndim(sol_2) == 0:
            return False
        elif np.ndim(sol_1) == 0 and np.ndim(sol_2) != 0:
            return False

    return res


def rotate(res):
    '''
    rotate all solutions in res so that p0 is at the origin and p1 is on
    the positive x-axes
    '''

    rotres = dcopy(res)

    for rot_i, rot_e in enumerate(rotres):
        g = affinef(*tranmat(rot_e[0], rot_e[1]))
        for rot_e_j, rot_e_e in enumerate(rot_e):
            rotres[rot_i][rot_e_j] = g(rot_e_e)

    return rotres


def distvalid(dis, err=0.0, verbose=True):
    '''
    check if the given distances between the points are valid, i.e. if they
    fullfill the triangle-equation
    '''

    valid = True
    valid &= np.all(dis == dis.T)
    valid &= np.all(dis.diagonal() == 0.0)

    pntscount = np.shape(dis)[0]

    for i in range(pntscount-2):
        for j in range(i+1, pntscount-1):
            for k in range(j+1, pntscount):
                if dis[i, j] > -0.5 and dis[i, k] > -0.5 and dis[j, k] > -0.5:
                    valid &= dis[i, j] + dis[j, k] >= dis[i, k]-abs(err)
                    valid &= dis[i, k] + dis[k, j] >= dis[i, j]-abs(err)
                    valid &= dis[j, i] + dis[i, k] >= dis[j, k]-abs(err)

                    if verbose and not dis[i, j] + dis[j, k] >= dis[i, k]:
                        print("{} {} {} for {}{}".format(i, j, k, i, k))
                    if verbose and not dis[i, k] + dis[k, j] >= dis[i, j]:
                        print("{} {} {} for {}{}".format(i, j, k, i, j))
                    if verbose and not dis[j, i] + dis[i, k] >= dis[j, k]:
                        print("{} {} {} for {}{}".format(i, j, k, j, k))

    return valid


def xvalue(a, b, c):
    '''
    defines the x-value for the upper point of a triangle,
    where c is the length of the down side starting in the origin and
    lying on the x-axes, a is the distance of the unknown point to the origen
    and b is the distance of the unknown point to the righter given point
    '''

    return (a**2 + c**2 - b**2)/(2*c)


def yvalue(b, a, c):
    '''
    defines the two possible y-values for the upper point of a triangle,
    where c is the length of the down side starting in the origin and
    lying on the x-axes, a is the distance of the unknown point to the origen
    and b is the distance of the unknown point to the righter given point
    '''

    # ckeck flatness to eliminate numerical errors when the triangle is flat
    if a+b <= c or a+c <= b or b+c <= a:
        return 0.0, -0.0

    res = 2*((a*b)**2 + (a*c)**2 + (b*c)**2)
    res -= a**4 + b**4 + c**4
    # in case of numerical errors set res to 0 (hope you check validty before)
    res = max(res, 0.0)
    res = np.sqrt(res)
    res /= 2*c
    return res, -res


def tranmat(a, b):
    '''
    defines the coefficents for the affine-linear function f(x)=Ax+s which
    fullfills that A is a rotation-matrix, f(a) = [0,0] and f(b) = [|b-a|,0]
    '''
    A = np.zeros((2, 2))
    A[0, 0] = b[0] - a[0]
    A[1, 1] = b[0] - a[0]
    A[1, 0] = -(b[1] - a[1])
    A[0, 1] = +(b[1] - a[1])
    A /= dist(a, b)
    s = -np.dot(A, a)
    return A, s


def invtranmat(A, s):
    '''
    defines the coefficents for the affine-linear function g(x)=Bx+t which
    is inverse to f(x)=Ax+s
    '''
    B = np.linalg.inv(A)
    t = -np.dot(B, s)
    return B, t


def affinef(A, s):
    '''
    gives an affine-linear function f(x) = Ax+s
    '''
    def func(x):
        '''
        affine-linear function func(x) = Ax+s
        '''
        return np.dot(A, x)+s
    return func


def affinef_pnt(a1, a2, b1, b2, prec=0.01):
    '''
    gives an affine-linear function that maps f(ai) = bi
    if |a2-a1| == |b2-b1| with respect to the given precision
    '''
    if not abs(dist(a1, a2)-dist(b1, b2)) < prec:
        raise ValueError("Points are not in isometric relation")

    func_a = affinef(*tranmat(a1, a2))
    func_b = affinef(*invtranmat(*tranmat(b1, b2)))

    def func(x):
        '''
        affine-linear function func(ai) = bi
        '''
        return func_b(func_a(x))
    return func


def dist(v, w):
    '''
    gives the distance between two given vectors v and w
    '''

    return np.linalg.norm(np.array(v) - np.array(w))


def sym(A):
    '''
    gives the symmetrize version of a given lower or upper triangle-matrix A
    '''

    return A + A.T - np.diag(A.diagonal())


def plotres(res, names=None, filename=None):
    '''
    plots all solutions in res and labels the points with the names in names
    '''

    # calculate Column- and Row-count for quadratic shape of the plot
    # total number of plots
    Tot = len(res)
    # columns near the square-root but tendentially wider than tall
    Cols = int(np.ceil(np.sqrt(Tot)))
    # enough rows to catch all plots
    Rows = int(np.ceil(Tot/Cols))
    # Possition numbers as array
    Pos = np.arange(1, Tot+1)

    # generate names for points if undefined
    if names is None:
        names = []
        for i in range(len(res[0])):
            names.append("p"+str(i))

    # genearte commen borders for all plots
    xmax = 0.0
    xmin = 0.0
    ymax = 0.0
    ymin = 0.0

    for i in res:
        for j in i:
            xmax = max(j[0], xmax)
            xmin = min(j[0], xmin)
            ymax = max(j[1], ymax)
            ymin = min(j[1], ymin)

    # add some space around the points in the plot
    space = 0.2*max(abs(xmax - xmin), abs(ymax - ymin))

    fig = plt.figure(dpi=75, figsize=[3*Cols, 3*Rows])
    fig.suptitle('Possible Well-constellations', fontsize=18)

    for i, result in enumerate(res):
        ax = fig.add_subplot(Rows, Cols, Pos[i])  # , sharex=True, sharey=True)
        ax.set_title("Result nr.: {}".format(i))
        ax.set_xlim([xmin-space, xmax+space])
        ax.set_ylim([ymin-space, ymax+space])
        ax.set_aspect('equal')
        for j, name in enumerate(names):
            ax.scatter(result[j][0], result[j][1], color="C1")
            ax.annotate(" "+name, (result[j][0], result[j][1]))

    fig.tight_layout(rect=[0, 0.03, 1, 0.95])

    if filename is not None:
        plt.savefig(filename, format="pdf")

    plt.show()
