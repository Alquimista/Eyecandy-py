#!/usr/bin/python
# -*- coding: utf-8 -*-
import math
import sys
from PyQt4 import QtGui, QtCore



def polar2rec(r, w):
    theta = math.radians(w)
    x, y = round(r * math.cos(theta), 4), round(r * math.sin(theta), 4)
    if x <= 0 and x > -1:
        x = 0
    if y <= 0 and y > -1:
        y = 0
    return x, y

def draw_poligon(r, l):
    iangle = 360 / float(l)
    if l % 2 != 0:
        angle = 90 + (iangle / 2.0)
    else:
        angle = 90
    pdraw = []
    draw = []
    for i in range(l + 1):
        pdraw.append(polar2rec(r, angle))
        angle += iangle
    return pdraw

def draw_line_poligon(r, l):
    poligon = draw_poligon(r, l)
    npoints = l
    for i in range(npoints):
        yield (poligon[i][0], poligon[i][1], poligon[i+1][0], poligon[i+1][1])

def draw_star(r1, r2, l):
    iangle = 360 / float(l)
    if l % 2 != 0:
        angle1 = 90 + (iangle / 2.0)
    else:
        angle1 = 90
    angle2 = angle1 + (iangle / 2.0)
    pdraw = []
    draw = []
    for i in range((l * 2) + 1):
        pdraw.append(polar2rec(r1, angle1))
        pdraw.append(polar2rec(r2, angle2))
        angle1 += iangle
        angle2 += iangle
    return pdraw

def draw_line_star(r1, r2, l):
    poligon = draw_star(r1, r2, l)
    npoints = l * 2
    for i in range(npoints):
        yield (poligon[i][0], poligon[i][1], poligon[i+1][0], poligon[i+1][1])


class Example(QtGui.QWidget):
    
    def __init__(self):
        super(Example, self).__init__()
        
        self.initUI()
        
    def initUI(self):      
        self.setGeometry(300, 300, 280, 270)
        self.setWindowTitle('Pen styles')
        self.show()

    def paintEvent(self, e):
        qp = QtGui.QPainter()
        qp.begin(self)
        self.drawLines(qp)
        qp.end()
        
    def drawLines(self, qp):
        pen = QtGui.QPen(QtCore.Qt.black, 2, QtCore.Qt.SolidLine)

        qp.setPen(pen)

        # for x1, y1, x2, y2 in draw_line_poligon(40, 5):
        #     y1 += 100
        #     y2 += 100
        #     x1 += 100
        #     x2 += 100
        #     qp.drawLine(x1, y1, x2, y2)

        for x1, y1, x2, y2 in draw_line_star(40, 20, 6):
            y1 += 100
            y2 += 100
            x1 += 100
            x2 += 100
            qp.drawLine(x1, y1, x2, y2)
              
        
def main():
    
    app = QtGui.QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()