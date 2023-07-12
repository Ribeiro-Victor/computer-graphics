from OpenGL.GLUT import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT.fonts import GLUT_BITMAP_HELVETICA_18
import sys
import random
import math

POINT_DIAMETER = 24
window_width = 1000
window_height = 800
spline_degree = 1
control_points = []

def initControlPoints(n = 6):
    global control_points
    global window_width
    global window_height
    control_points.clear()
    for i in range(n):
        x = 100 + ((window_width - 200) / (n-1)) * i
        y = 30 + random.randint(POINT_DIAMETER/2, window_height-(POINT_DIAMETER/2))
        control_points.append([x,y])
    
def cox_de_boor(k, d, nodes):
    if (d == 0):
        return lambda u: 1 if (nodes[k] <= u and u < nodes[k + 1]) else 0
    Bk0 = cox_de_boor(k, d - 1, nodes)
    Bk1 = cox_de_boor(k + 1, d - 1, nodes)
    return lambda u: ((u - nodes[k]) / (nodes[k + d] - nodes[k])) * Bk0(u) + ((nodes[k + d + 1] - u) / (nodes[k + d + 1] - nodes[k + 1])) * Bk1(u)

def sampleCurve(pts, step = 0.01):
    n = len(pts)
    b = []
    nodes = [i for i in range(13)]
    for k in range (len(control_points)):
        b.append(cox_de_boor(k, spline_degree, nodes))
    sample = []
    u = spline_degree
    while(u<=n):
        
        # Ajuste para otimizar a função
        start_u = int(u//1)-spline_degree
        end_u = start_u + (spline_degree)
        end_u = min(end_u, len(control_points)-1)

        sum = [0,0]
        for k in range(start_u, end_u+1):
            p = control_points[k]
            w = b[k](u)
            for i in range(2):
                sum[i] += w * p[i]
        sample.append(sum)
        u += step
    return sample

def display():
    glClear (GL_COLOR_BUFFER_BIT)
    glEnable(GL_POINT_SMOOTH)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_BLEND) 
    
    i = 0
    # Desenha os pontos de controle
    for point in control_points:
        # Borda
        glPointSize(POINT_DIAMETER)
        glBegin(GL_POINTS)
        glColor3f(0,0,0)
        glVertex2f(point[0], point[1])
        glEnd()

        # Preenchimento
        glPointSize(POINT_DIAMETER*0.95)
        glBegin(GL_POINTS)
        glColor3f(0, 120/255, 1)
        glVertex2f(point[0], point[1])
        glEnd()

        # Legenda
        glColor3f(0,0,0)
        glRasterPos2f(point[0]+(POINT_DIAMETER)/2, point[1]-(POINT_DIAMETER)/2)
        i+=1
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(str(i)))

    # Desenha os pontos de ligação
    glColor4f(1, 0, 0, 0.3)
    glPointSize(POINT_DIAMETER*0.45)
    for point in sampleCurve(control_points):
        glBegin(GL_POINTS)
        glVertex2f(point[0], point[1])
        glEnd()
    
    # Desenha a legenda com o grau atual
    glColor3f(1,1,1)
    glRectf(0, 0, 100, 30)
    grau_pos = 10
    glColor3f(0, 0, 0)
    for c in 'GRAU:'+str(spline_degree):
        glRasterPos2f(grau_pos,20)
        grau_pos+=14
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(c))
        
    glutSwapBuffers ()

def init ():
    glClearColor (1.0, 1.0, 1.0, 0.0)
    initControlPoints()

def reshape(width, height):
    global window_width
    global window_height
    window_width = width
    window_height = height
    glViewport(0,0,width,height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0,width,height,0)
    glMatrixMode (GL_MODELVIEW)
    # Ajuste para manter o ponto visível na tela
    for point in control_points:
        point[0] = min(max(point[0], POINT_DIAMETER/2), window_width-(POINT_DIAMETER/2))
        point[1] = min(max(point[1], POINT_DIAMETER/2), window_height-(POINT_DIAMETER/2))

picked = None
def mouse (button, state, x, y):
    global picked
    if state!=GLUT_DOWN: return

    picked = None
    for point in control_points:
        dist = math.sqrt(math.pow((point[0]-x), 2) + math.pow((point[1]-y), 2))
        if (dist <= POINT_DIAMETER):
            picked = point
        
    glutPostRedisplay()

def keyboard_handle(key, x, y):
    global spline_degree
    if(key == b'd'):
        spline_degree = max(0, spline_degree-1)
    elif(key == b'D'):
        spline_degree = min(5, spline_degree+1)
    glutPostRedisplay()

def mouse_drag(x, y):
    global window_width
    global window_height
    if picked:
        # Ajuste para evitar que ponto saia da janela visível
        picked[0] = min(max(x, POINT_DIAMETER/2), window_width-(POINT_DIAMETER/2))
        picked[1] = min(max(y, POINT_DIAMETER/2), window_height-(POINT_DIAMETER/2))
    glutPostRedisplay()

def main():
    global window_width
    global window_height
    glutInit(sys.argv)
    glutInitDisplayMode (GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowPosition((glutGet(GLUT_SCREEN_WIDTH)-window_width)//2,
                        (glutGet(GLUT_SCREEN_HEIGHT)-window_height)//2)
    glutInitWindowSize (window_width,window_height)
    glutCreateWindow ("B-spline demo")
    init()
    glutDisplayFunc(display) 
    glutReshapeFunc(reshape)
    glutMouseFunc(mouse)
    glutMotionFunc(mouse_drag)
    glutKeyboardFunc(keyboard_handle)
    glutMainLoop()

main()
