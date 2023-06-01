import sys
import numpy as np
import math
from OpenGL.GLUT import *
from OpenGL.GL import *
from OpenGL.GLU import *
from pyrr.matrix44 import *

shapes = []

class Rect(object):
    def __init__ (self, points, m = create_identity()):
        self.points = points
        self.set_matrix(m)
    def set_point (self, i, p):
        self.points[i] = p
    def set_matrix(self,t):
        self.m = t
        self.invm = inverse(t)
    def contains(self,p):
        p = apply_to_vector(self.invm, [p[0],p[1],0,1])
        xmin = min(self.points[0][0],self.points[1][0])
        xmax = max(self.points[0][0],self.points[1][0])
        ymin = min(self.points[0][1],self.points[1][1])
        ymax = max(self.points[0][1],self.points[1][1])
        return xmin <= p[0] <= xmax and ymin <=p[1] <= ymax
    def draw (self):
        glPushMatrix()
        glMultMatrixf(self.m)
        glRectf(self.points[0][0], self.points[0][1],self.points[1][0], self.points[1][1])
        glPopMatrix()
    

class Circle(object):
    vertices = 40.0
    def __init__ (self, center, radius, m = create_identity()):
        self.center = center
        self.radius = radius
        self.set_matrix(m)
    def set_matrix(self,t):
        self.m = t
        self.invm = inverse(t)
    def contains(self, p):
        p = apply_to_vector(self.invm, [p[0],p[1],0,1])
        d = math.sqrt(pow(p[0]-self.center[0], 2)+pow(p[1]-self.center[1],2))
        return d <= self.radius
    def draw(self):
        glPushMatrix()
        glMultMatrixf(self.m)
        glBegin(GL_POLYGON)
        for i in range(int(self.vertices)+1):
            x = self.radius*math.cos((i*2*math.pi)/self.vertices)
            y = self.radius*math.sin((i*2*math.pi)/self.vertices)
            glVertex2f(x+self.center[0], y+self.center[1])
        glEnd()
        glPopMatrix()
        

def unit_vector(vector):
    return vector / np.linalg.norm(vector)

def angle_between(v1, v2):

    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))

picked = None
modeConstants = ["CREATE RECTANGLE", "CREATE CIRCLE", "TRANSLATE", "ROTATE", "SCALE"]
mode = modeConstants[0]

def reshape( width, height):
    glViewport(0,0,width,height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0,width,height,0)
    glMatrixMode (GL_MODELVIEW)

def mouse (button, state, x, y):
    global lastx,lasty,picked
    if state!=GLUT_DOWN: return
    if mode == "CREATE RECTANGLE":
        shapes.append(Rect([[x,y],[x,y]]))
    elif mode == "CREATE CIRCLE":
        shapes.append(Circle([x, y], 0))
    elif mode == "TRANSLATE":
        picked = None
        for s in shapes:
            if s.contains([x,y]): picked = s
        lastx,lasty = x,y
    elif mode == 'ROTATE':
        picked = None
        for s in shapes:
            if s.contains([x,y]): picked = s
        lastx,lasty = x,y
    elif mode == 'SCALE':
        picked = None
        for s in shapes:
            if s.contains([x,y]): picked = s
        lastx,lasty = x,y
    glutPostRedisplay()


def mouse_drag(x, y):
    if mode == "CREATE RECTANGLE":
        shapes[-1].set_point(1,[x,y])
    elif mode == "CREATE CIRCLE":
        center = shapes[-1].center
        shapes[-1].radius = math.sqrt(math.pow((x-center[0]),2)+math.pow(y-center[1],2))
    elif mode == "TRANSLATE":
        if picked:
            global lastx,lasty
            t = create_from_translation([x-lastx,y-lasty,0])
            picked.set_matrix(multiply(picked.m,t))
            lastx,lasty=x,y
    elif mode == 'ROTATE':
        if picked:
            global lastx,lasty
            if(type(picked) == Rect):
                points = picked.points
                x_center = abs((points[1][0] + points[0][0])/2)
                y_center = abs((points[1][1] + points[0][1])/2)
            else:
                x_center = picked.center[0]
                y_center = picked.center[1]
            start = [lastx-x_center, lasty-y_center]
            end = [x-x_center, y-y_center]
            rot_angle = angle_between(start, end)
            rot_signal = 1
            if((lasty < y and x > x_center) 
               or (lastx > x and y > y_center)
               or (lasty > y and x < x_center)
               or (lastx < x and y < y_center)):
                rot_signal *= -1
            
            t1 = create_from_translation([x_center, y_center,0])
            t2 = create_from_z_rotation(rot_angle*rot_signal)
            t3 = create_from_translation([-1*x_center, -1*y_center,0])
            first_matrix = multiply(t1, picked.m)
            second_matrix = multiply(t2, first_matrix)
            picked.set_matrix(multiply(t3, second_matrix))
            lastx,lasty=x,y
    elif mode == 'SCALE':
        if picked:
            t = create_from_scale([1.001,1,1])
            picked.set_matrix(multiply(picked.m,t))
            lastx,lasty=x,y
    glutPostRedisplay()

def display():
    glClear(GL_COLOR_BUFFER_BIT)
    for s in shapes:
        glColor3f(0.61,0.01,0.18)
        glPolygonMode(GL_FRONT_AND_BACK,GL_FILL)
        s.draw()
        glColor3f(0.01,0.42,0.26)
        glPolygonMode(GL_FRONT_AND_BACK,GL_LINE)
        s.draw()
    glutSwapBuffers()

def createMenu():
    def domenu(item):
        global mode
        mode = modeConstants[item]
        return 0
    glutCreateMenu(domenu)
    for i,name in enumerate(modeConstants):
        glutAddMenuEntry(name, i)
    glutAttachMenu(GLUT_RIGHT_BUTTON)



glutInit(sys.argv)
glutInitDisplayMode (GLUT_DOUBLE | GLUT_RGB)
glutInitWindowSize (800, 600)
glutCreateWindow ("rectangle editor")
glutMouseFunc(mouse)
glutMotionFunc(mouse_drag)
glutDisplayFunc(display); 
glutReshapeFunc(reshape)
createMenu()
glutMainLoop()
