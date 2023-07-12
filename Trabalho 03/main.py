import sys
import random
import math

from OpenGL.GLUT import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT.fonts import GLUT_BITMAP_9_BY_15

ang = 0

POINT_DIAMETER = 30
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 1000

spline_degree = 1
NODES = [i for i in range(13)]

control_points = []

def initControlPoints(n = 6):
    # global control_points
    control_points.clear()
    for i in range(n):
        x = 100 + ((WINDOW_WIDTH - 200) / (n-1)) * i
        y = random.randint(POINT_DIAMETER/2, WINDOW_HEIGHT-(POINT_DIAMETER/2))
        control_points.append([x,y])
    # control_points = [[100, 166.10502816454354],
    #                 [168, 400.7690049320902],
    #                 [340, 205.1556003923505],
    #                 [460, 413.2122585334024],
    #                 [580, 202.58735616203003],
    #                 [700, 398.83628908012633]]
    
def cox_de_boor(k, d, nodes):
    if (d == 0):
        return lambda u: 1 if (nodes[k] <= u and u < nodes[k + 1]) else 0
    Bk0 = cox_de_boor(k, d - 1, nodes)
    Bk1 = cox_de_boor(k + 1, d - 1, nodes)
    return lambda u: ((u - nodes[k]) / (nodes[k + d] - nodes[k])) * Bk0(u) + ((nodes[k + d + 1] - u) / (nodes[k + d + 1] - nodes[k + 1])) * Bk1(u)


def sampleCurve(pts, step = 0.01):
    n = len(pts)
    b = []
    for k in range (len(control_points)):
        b.append(cox_de_boor(k, spline_degree, NODES))
    # return b
    # print(b)
    sample = [];
    u = spline_degree
    mySet = set()
    while(u<=n):
        # print('u: ', u)
        
        # Ajuste para otimizar a função
        start_u = int(u//1)-spline_degree
        end_u = start_u + (spline_degree)
        end_u = min(end_u, len(control_points)-1)

        sum = [0,0]
        for k in range(start_u, end_u+1):
            p = control_points[k]
            w = b[k](u)
            # print('w = ', w, 'k = ',k)
            if(w==0):
                mySet.add(k)
                # print('w = ', w, 'k = ',k)
                # print(b[k])
                # print(u)
            for i in range(2):
                sum[i] += w * p[i]
        sample.append(sum)
        u += step
    # print('my set:', mySet)
    # print('-'*100)
    # for s in sample:
    #     print(s)
    return sample



def display():
    glClear (GL_COLOR_BUFFER_BIT);

    
    glEnable (GL_POINT_SMOOTH)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
    glEnable (GL_BLEND) 
    glLoadIdentity()
    
    # glTranslatef(50.0, 50, 0.0)

    # glPointSize(POINT_DIAMETER)
    # glBegin(GL_POINTS);
    # glColor3f(1.0, 1.0, 1.0);
    # glVertex2f(0.0, 0.0);
    # glEnd();

    # glPointSize(POINT_DIAMETER-2)
    # glBegin(GL_POINTS);
    # glColor3f(0.0, 0.0, 150/255);
    # glVertex2f(0.0, 0.0);
    # glEnd();
    i = 0
    # glEnable( GL_BLEND );
    for point in control_points:
        glPointSize(POINT_DIAMETER)
        glBegin(GL_POINTS);
        glColor3f(0,0,0);
        glVertex2f(point[0], point[1]);
        glEnd();

        glPointSize(POINT_DIAMETER*0.95)
        glBegin(GL_POINTS);
        # glColor3f(1/255, 112/255, 75/255)
        glColor3f(0.0, 0.0, 150/255);
        # glColor3f(0.0, 0.0, 0.0);
        i+=1
        glVertex2f(point[0], point[1]);
        glEnd();
    
        glColor3f(0,0,0)
        glRasterPos2f(point[0]+(POINT_DIAMETER)/2, point[1]-(POINT_DIAMETER)/2)
        glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(str(i)))
    



    # glColor4f(1, 0, 0, 0.3)
    glColor4f(255/255, 0/255, 0/255, 0.3)
    glPointSize(POINT_DIAMETER/5)
    for point in sampleCurve(control_points):
        glBegin(GL_POINTS)
        glVertex2f(point[0], point[1]);
        glEnd();
    
    # glColor4f(0/255, 255/255, 0/255, 1)
    # glPointSize(POINT_DIAMETER/6)
    # for point in sampleCurveFast(control_points):
    #     glBegin(GL_POINTS)
    #     glVertex2f(point[0], point[1]);
    #     glEnd();


    glutSwapBuffers ();

def init ():
    glClearColor (1.0, 1.0, 1.0, 0.0);
    # glClearColor (0.0, 0.0, 0.0, 0.0);

def timer(n):
    global spline_degree
    spline_degree = (spline_degree + 1)%6
    glutPostRedisplay();
    glutTimerFunc(2000,timer,0);
    # initControlPoints()

def reshape(width, height):
    global WINDOW_WIDTH
    global WINDOW_HEIGHT
    WINDOW_WIDTH = width
    WINDOW_HEIGHT = height
    glViewport(0,0,width,height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0,width,height,0)
    glMatrixMode (GL_MODELVIEW)
    for point in control_points:
        point[0] = min(max(point[0], POINT_DIAMETER/2), WINDOW_WIDTH-(POINT_DIAMETER/2))
        point[1] = min(max(point[1], POINT_DIAMETER/2), WINDOW_HEIGHT-(POINT_DIAMETER/2))

picked = None

def mouse (button, state, x, y):
    global lastx,lasty,picked
    if state!=GLUT_DOWN: return

    picked = None
    for point in control_points:
        dist = math.sqrt(math.pow((point[0]-x), 2) + math.pow((point[1]-y), 2))
        if (dist <= POINT_DIAMETER):
            picked = point
            print(point)
        
    glutPostRedisplay()

def keyboard_handle(key, x, y):
    global spline_degree
    if(key == b'd'):
        spline_degree = max(0, spline_degree-1)
        print('Diminuir')
    elif(key == b'D'):
        spline_degree = min(5, spline_degree+1)
        print('Aumentar')
    glutPostRedisplay()

def mouse_drag(x, y):
    if picked:
        picked[0] = min(max(x, POINT_DIAMETER/2), WINDOW_WIDTH-(POINT_DIAMETER/2))
        picked[1] = min(max(y, POINT_DIAMETER/2), WINDOW_HEIGHT-(POINT_DIAMETER/2))
    
    glutPostRedisplay()

def main():
    glutInit(sys.argv);
    glutInitDisplayMode (GLUT_DOUBLE | GLUT_RGB);
    glutInitWindowPosition((glutGet(GLUT_SCREEN_WIDTH)-WINDOW_WIDTH)//2,
                        (glutGet(GLUT_SCREEN_HEIGHT)-WINDOW_HEIGHT)//2)
    glutInitWindowSize (WINDOW_WIDTH,WINDOW_HEIGHT)
    glutCreateWindow ("B-spline demo");
    init ();
    initControlPoints()
    glutDisplayFunc(display); 
    glutReshapeFunc(reshape)
    glutMouseFunc(mouse)
    glutMotionFunc(mouse_drag)
    glutKeyboardFunc(keyboard_handle)
    # glutTimerFunc(2000,timer,0);
    glutMainLoop();

main()
