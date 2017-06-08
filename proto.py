# -*- coding: utf-8 -*-
#execfile("/home/volodya/Mechanics/FreeCAD-proto/proto.py")
# Change the path above to point to location of this file
# Then you can copy and paste the line into FreeCAD

import Part, FreeCAD, Drawing
from FreeCAD import Base
from Draft import *
import Draft
from math import *
import random
import string
import imp
import Mesh

print("Script started.")



def inch(a):
	return(a*25.4)
	
def mil(a):
	return(a*25.4e3)
	
def cm(a):
	return(a*10.0)
	
def mm(a):
	return(a)
	
	
Vx=FreeCAD.Vector(1, 0, 0)
Vy=FreeCAD.Vector(0, 1, 0)
Vz=FreeCAD.Vector(0, 0, 1)

#
# Define common hole parameters
# You can use any names, so you can create classes of holes and adjust them later.
#
HolesDict={
	'4x40':{'d_tap': inch(0.089) , 'd_clearance': inch(0.1160), 'd_head': mm(5.3), 'h_head': mm(4)},
	'6x32':{'d_tap': inch(0.1065) , 'd_clearance': inch(0.1440), 'd_head': mm(5.6), 'h_head': mm(4)},
	'8x32':{'d_tap': mm(3.45) , 'd_clearance': mm(4.14), 'd_head': mm(8.6), 'h_head': mm(4.2)},
	'10x32': {'d_tap': mm(4.0386), 'd_clearance': mm(0.19784), 'd_head': inch(0.312), 'h_head': inch(0.190)},
	 '1/4-20': {'d_tap': mm(5.10), 'd_clearance': mm(6.53), 'd_head': inch(0.375), 'h_head': inch(0.375)},
	 'HeaterHole': {'d_clearance': mm(6), 'd_head': mm(6), 'h_head': mm(0)},
	 'ThermistorHole': {'d_clearance': mm(2), 'd_head': mm(2), 'h_head': mm(0)},
	 'FilamentHole': {'d_clearance': mm(2), 'd_head': mm(2), 'h_head': mm(0)},
	 'M2.5': {'d_tap': mm(2.05), 'd_clearance': mm(2.5), 'd_head': mm(3), 'h_head':mm(3)},
	 'M3': {'d_tap': mm(2.5), 'd_clearance': mm(3), 'd_head': mm(5), 'h_head':mm(5)},
	 'M4': {'d_tap': mm(3.30), 'd_clearance': mm(4), 'd_head': mm(6), 'h_head':mm(6)},
	 'M5': {'d_tap': mm(4.2), 'd_clearance': mm(5), 'd_head': mm(8.72), 'h_head': mm(5)},
	 'M6x1': {'d_tap': mm(5.00), 'd_clearance': mm(6), 'd_head': mm(10.22), 'h_head':mm(8)},
	 'M10x1.5': {'d_tap': mm(-5.00), 'd_clearance': mm(10), 'd_head': mm(16.27), 'h_head':mm(10.0)},
	}

	
#
# Define symbolic hole types used in design
#
HolesDict['ExternalMount']=HolesDict['1/4-20']


#
# Material properties
#
# density: kg/m^3
# Y: Pa  (Young's modulus)
# CTE: m/m/K
# Heat capacity: J/kgK
# Thermal conductivity: W/mK
#

MaterialDict={'Al 2024':{'density': 2.78*1e3, 'Y': 73e9, 'CTE': 23.2e-6, 'Heat capacity': 875, 'Thermal conductivity': 121},
		'Al 6061': {'density': 2.7*1e3, 'Y': 68.9e9, 'CTE': 23.6e-6, 'Heat capacity': 896, 
		'Thermal conductivity': 167},
	      'Al 7075':{'density': 2.71*1e3, 'Y': 71.7e9, 'CTE': 23.6e-6, 'Heat capacity': 960,
	        'Thermal conductivity': 130},
	      'BeCu B14 C175102': {'density': 8.77*1e3, 'Y': -1, 'CTE': 17.6e-6, 'Heat capacity': 419, 'Thermal conductivity': 207.7},
	      'BeCu B25 C17200': {'density': 8.36*1e3, 'Y': 134e9, 'CTE': 17.8e-6, 'Heat capacity': 418.64, 'Thermal conductivity': 107.3},
	      'Stainless 304': {'density': 8.03*1e3, 'Y': 193e9, 'CTE': 9.4e-6, 'Heat capacity': 500, 'Thermal conductivity': 16.2}
	      }

##
## Library of convenience functions
##

#
# All dimensions are in mm
#

# Move object so that center of mass is at (0,0,0)
def center_object(b):
	b.Placement.move(b.BoundBox.Center.multiply(-1))
	return(b)
	

# A rectangular slab
def cbox(width, length, height):
	bx=Part.makeBox(width,length,height)
	return(center_object(bx))

def torus(a,b):
	bx=Part.makeTorus(a,b)
	return(center_object(bx))

# cone, a and b are radii of top and bottom disks
def cone(a,b,h,angle=360, p=Vector(0,0,0), v=Vector(0,0,1)):
	bx=Part.makeCone(a,b,h, p, v, angle)
	return(center_object(bx))

def sphere(radius):
	s=Part.makeSphere(radius)
	return(center_object(s))

# A cylinder - same as hole, just to be more descriptive
def ccylinder(diameter, depth):
	return(hole(diameter, depth))

def hole(diameter, depth):
	hole=Part.makeCylinder(0.5*diameter, depth, Base.Vector(0, 0, 0), Base.Vector(0, 0, 1), 360)
	return(center_object(hole))

# vertices is a list of 3-tuples or FreeCAD.Vector()	
def polygon(vertices):
	L=[]
	for i in range(0,len(vertices)):
		L.append(FreeCAD.Vector(vertices[i]))
	p=Part.makePolygon(L)
	return(center_object(p))
	
def helix(pitch, height, radius, angle=0):
	h=Part.makeLongHelix(pitch, height, radius, angle)
	return(center_object(h))

# This does not work as expected in my version of FreeCAD, see replacement function below
#def thread(pitch, depth, height, radius):
	#h=Part.makeThread(pitch, depth, height, radius)
	#return(center_object(h))

def prism3(length, offset, width, height):
	b=Part.makeWedge(-length*0.5, -height*0.5, -width*0.5, -width*0.5, -(length*0.5-offset), length*0.5, height*0.5, width*0.5, width*0.5, -(length*0.5-offset))
	return(center_object(b))

# This function does not create threads, rather it makes a hole to be tapped later
def threaded_hole(type, depth=25):
	hole_par=HolesDict[type]
	return(hole(hole_par['d_tap'], depth))
	
def clearance_hole(type, depth=25):
	hole_par=HolesDict[type]
	return(hole(hole_par['d_clearance'], depth))

def countersink_clearance_hole(type, angle=82.0, depth=mm(25), cdepth=-1):
	hole_par=HolesDict[type]
	h=hole(hole_par['d_clearance'], depth)
	if cdepth<0:
		cd=0.5*hole_par['d_clearance']
	else:
		cd=cdepth
	l=0.5*(depth+hole_par['d_clearance'])+cd
	h=h.fuse(translate(cone(mm(0), l*sin(angle*pi/180.0), l), 0, 0, 0.25*depth-0.25*hole_par['d_clearance']-0.5*cd)) 
	return(h)
	
def bolt_head_hole(type, depth=-1):
	hole_par=HolesDict[type]
	if depth<0:
		depth=hole_par['h_head']
	return(hole(hole_par['d_head'], depth))

def bolt(type, length):
	hole_par=HolesDict[type]
	c=ccylinder(hole_par['d_clearance'], length)
	c=c.fuse(translate(ccylinder(hole_par['d_head'], hole_par['h_head']), 0, 0, -0.5*length-0.5*hole_par['h_head']))
	c=c.removeSplitter()
	return(c)

# Load existing mesh file, such as .stl
def load_mesh(filename):
	m=Mesh.read(filename)
	return(m)


def part_from_mesh(mesh, tolerance=0.1):
	mpp=Part.Shape()
	mpp.makeShapeFromMesh(mesh.Topology, tolerance)
	return(mpp)

def normalize_name(name):
	return(name.replace(" ", "_"))

def use_document(name):
	try:
		App.setActiveDocument(normalize_name(name))
	except:
		App.newDocument(normalize_name(name))

def remove_part(name):
	App.ActiveDocument.removeObject(normalize_name(name))
	
def remove_all_parts():
	for a in App.ActiveDocument.findObjects():
		remove_part(a.Name)

def rotate_all_parts(axis, angle, base=FreeCAD.Vector(0, 0, 0)):
	base=FreeCAD.Vector(base)
	for a in App.ActiveDocument.findObjects():
		if a.Type == "Part::Feature":
			a.Shape.rotate(base, axis, angle)

def new_part(name, object=None, color=None, transparency=None, parent=None):
	part=FreeCAD.ActiveDocument.addObject("Part::Feature", normalize_name(name))
	if parent!=None:
		parent.addObject(part)
	if object!=None :
		part.Shape=object
	if color==None:
		part.ViewObject.ShapeColor=(random.random(), random.random(), random.random())
	else:
		part.ViewObject.ShapeColor=color
		
	if transparency!=None:
		part.ViewObject.Transparency=transparency
	#App.activeDocument().recompute()
	update_document()
	return(part)
	
def get_part(name):
	part=FreeCAD.ActiveDocument.getObject(normalize_name(name))
	return(part)

def new_group(name):
	part=FreeCAD.ActiveDocument.addObject("App::DocumentObjectGroup", normalize_name(name))
	update_document()
	return(part)

def new_annotation(text, text_position=0.0, position=(0.0, 0.0, 0.0), name=None, object=None, color=None, transparency=None, parent=None):
	if name==None:
		n=text[0]
	else:
		n=name
	l=FreeCAD.ActiveDocument.addObject("App::AnnotationLabel", normalize_name(n))
	l.LabelText=text
	l.TextPosition = text_position
	l.BasePosition = position
	update_document()
	return(l)

def update_document():
	App.activeDocument().recompute()

# These are symbolic names to be used in functions below

LeftX=0
InY=1
BottomZ=2
RightX=3
OutY=4
TopZ=5

CenterX=100
CenterY=101
CenterZ=102
Center=103

Length=200
Width=201
Thickness=202


# Get dimensions of part name - centerpoint, centers along any axis, width, length, height 
def get_measure(name, measure=None):
	bb1=get_part(name).Shape.BoundBox
	bb=(bb1.XMin, bb1.YMin, bb1.ZMin, bb1.XMax, bb1.YMax, bb1.ZMax)
	if measure==None:
		return(bb)
		
	if measure==Center:
		return((0.5*(bb[3]+bb[0]), 0.5*(bb[4]+bb[1]),0.5*(bb[5]+bb[2])))
		
	if measure>=200:
		return(bb[measure-200+3]-bb[measure-200])
		
	if measure>=100:
		return(0.5*(bb[measure-200+3]+bb[measure-200]))
		
	return(bb[measure])
	
# This gives indices of faces farthest apart along some direction - a way to query object
def extreme_faces(shape, direction):
	faces=shape.Faces
	direction=FreeCAD.Vector(direction)
	v_min=0.0
	v_max=0.0
	i_min=-1
	i_max=-1
	for i in range(0, len(faces)):
		a=direction.dot(faces[i].CenterOfMass)
		if (i_min<0) | (a<v_min):
			i_min=i
			v_min=a
		if (i_max<0) | (a>v_max):
			i_max=i
			v_max=a
	return((i_min, i_max))

# This is a very neat function - given a shape and a point in space it finds a nearest geometric element (FACE, EDGE or SOLIDS)
# Very useful to find edges to chamfer for example
def closest_object(shape, vtype, location):
	vtype=string.upper(vtype)
	if vtype=="FACE":
		v=shape.Faces
	elif vtype=="EDGE":
		v=shape.Edges
	elif vtype=="SOLIDS":
		v=shape.Solids
	else :
		print ("Unknown object type=%s" % (vtype))
		return None

	location=FreeCAD.Vector(location)
	v_min=0.0
	i_min=-1
	for i in range(0, len(v)):
		a=(v[i].CenterOfMass-location).Length
		if ((i_min<0) | (a<v_min)):
			i_min=i
			v_min=a
	print ("Found %s %d at distance %f" % (vtype, i_min, v_min))
	return(i_min)

# Several functions that manipulate shapes

def translate(b, v):
	b2=b.copy()
	b2.Placement.move(FreeCAD.Vector(v))
	return(b2)
	
def translate(b, v0, v1, v2):
	b2=b.copy()
	b2.Placement.move(FreeCAD.Vector(v0, v1, v2))
	return(b2)

def mirror(b, direction=Vz, base=(0,0,0)):
	b2=b.copy()
	b2.mirror(FreeCAD.Vector(base), FreeCAD.Vector(direction))
	return(b2)
	
def extrude(b, v):
	b2=b.copy()
	b2.extrude(FreeCAD.Vector(v))
	return(b2)
	
def extrude(b, v0, v1, v2):
	b.extrude(FreeCAD.Vector(v0, v1, v2))
	return(b)
	
def rotate(b, axis, angle, base=FreeCAD.Vector(0, 0, 0)):
	b2=b.copy()
	b2.rotate(FreeCAD.Vector(base), FreeCAD.Vector(axis), angle)
	return(b2)



def new_view(b, dir=(0.0, 0.0, 1.0), X=0, Y=0, scale=1.0, rotation=0, name="View", hidden_lines=False):
	v=App.activeDocument().addObject('Drawing::FeatureViewPart', name)
	#App.activeDocument().View.Source = b
	#App.activeDocument().View.Direction = (0.0,0.0,1.0)
	v.Source=b
	v.Direction=dir
	v.ShowHiddenLines=hidden_lines
	v.X=scale*X
	v.Y=scale*Y
	v.Scale=scale
	v.Rotation=rotation
	#print(v.ViewResult)
	return(v)
	
def new_drawing(name="Page"):
	d=App.activeDocument().addObject('Drawing::FeaturePage', name)
	#App.activeDocument().Page.Template=App.getResourceDir()+'Mod/Drawing/Templates/A3_Landscape.svg'
	d.Template=App.getResourceDir()+'Mod/Drawing/Templates/A3_Landscape.svg'
	return(d)
	

# This creates threads by moving a triangle along Helix
# This is pretty complicated so watch out for surface defects
def thread(pitch, height, diameter, internal=False):
	h=helix(pitch=pitch, height=height, radius=0.5*diameter)
	
	size1=pitch
	
	
	if internal:
		offset=0.5*diameter-pitch*0.5*(tan(math.pi/3.0)-tan(math.pi/6.0))
		tooth=translate(polygon([(0, 0, 0.5*size1), (0, 0, -0.5*size1), (size1*0.5*tan(math.pi/3.0), 0, 0), (0, 0, 0.5*size1)]), offset, 0, 0) 
	else:
		offset=0.5*diameter-pitch*sin(math.pi*3/20)
		tooth=translate(polygon([(0, 0, 0.5*size1), (0, 0, -0.5*size1), (size1*0.5*tan(math.pi/3.0), 0, 0), (0, 0, 0.5*size1)]), -offset, 0, 0) 
	c=h.makePipeShell([tooth,tooth], True, True, 0)
	c=c.removeSplitter()
	return(c)


#
# Example function, it returns a shape that can be assigned to a named part
#
def tuning_fork(width=mm(30), length=mm(150), height=mm(6)):
	c=cbox(width, length, height)
	
	# Move the box so that the left edge is at 0
	c=translate(c, 0, 0.5*length, 0)
	
	# Cutout the gap between tines
	# We want the height big enough so there is no ambiguity of what is removed
	c=c.cut(translate(cbox(0.3*width, length, 2*height), 0, mm(60)+0.5*length, 0))
	
	# Some M3 holes in case we want to attach it to something:
	for y in (mm(10), mm(20), mm(30), mm(40), mm(50)):
		c=c.cut(translate(threaded_hole("M3", mm(10)), 0, y, 0))
	
	# Round outer edges:
	c=c.makeFillet(mm(3), [c.Edges[closest_object(c, "EDGE", (0.5*width+mm(1), length+mm(1), mm(0)))]])
	c=c.makeFillet(mm(3), [c.Edges[closest_object(c, "EDGE", (-0.5*width-mm(1), length+mm(1), mm(0)))]])

	# Of course we could have just used a list:
	c=c.makeChamfer(mm(3), [c.Edges[closest_object(c, "EDGE", (0.5*width+mm(1), -mm(1), mm(0)))], c.Edges[closest_object(c, "EDGE", (-0.5*width-mm(1), -mm(1), mm(0)))]])

	# Some parameters
	print("Tuning fork volume=%f mm^3 weight[Al 6061]=%f kg" % (c.Volume, c.Volume*1e-9*MaterialDict["Al 6061"]["density"],))
	
	# An optional statement - removes extra lines from the shape
	# Sometimes useful to for 3d printer slicers
	c=c.removeSplitter()
	return(c)

# Example function - design with tuning fork

def design():
	# Groups are useful to manipulate many parts at once
	Forks=new_group("Forks")

	f1=new_part("fork1", translate(rotate(tuning_fork(), Vz, 0), 0, 0, 0) , transparency=80, parent=Forks)

	f2=new_part("fork2", translate(rotate(tuning_fork(length=mm(100)), Vz, 0), mm(40), 0, 0) , transparency=80, parent=Forks)

	f3=new_part("fork3", translate(rotate(tuning_fork(length=mm(200)), Vz, 0), mm(80), 0, 0) , transparency=80, parent=Forks)

def tuning_fork_drawing():
	
	d=new_drawing("tuning_fork_drawing")
	bp=new_part("tuning_fork", tuning_fork(), transparency=80, parent=d)
	
	#d.addObject(new_view(bp, X=inch(1)-get_measure("bearing_plateH", LeftX), Y=inch(1)+get_measure("bearing_plateH", OutY), scale=0.5))
	
	d.addObject(new_view(bp, X=inch(1)-get_measure("tuning_fork", InY), Y=inch(2)-get_measure("tuning_fork", LeftX), dir=(0.0, 0.0, 1.0), scale=1.0, rotation=90.0, hidden_lines=True))
	
	d.addObject(new_view(bp, X=inch(9)-get_measure("tuning_fork", InY), Y=inch(2)-get_measure("tuning_fork", BottomZ), dir=(1.0, 0.0, 0.0), scale=1.0, rotation=-90.0, hidden_lines=True))

	d.addObject(new_view(bp, X=inch(9)-get_measure("tuning_fork", LeftX), Y=inch(7)-get_measure("tuning_fork", BottomZ), dir=(0.0, 1.0, 0.0), scale=1.0, rotation=-90.0, hidden_lines=True))


	d.addObject(new_view(bp, X=inch(1)-get_measure("tuning_fork", InY), Y=inch(9)-get_measure("tuning_fork", LeftX), dir=(1.0, 1.0, 1.0), scale=1.0, rotation=90.0, hidden_lines=True))

	#l=new_annotation(["Horizontal bearing plate"], text_position=(3.0, 0.0, 0.0), position=(1.0, 3.0, 0), name="MyNote")

	App.ActiveDocument.recompute()

use_document("Prototype")
remove_all_parts()

# Single part test area
#bp=new_part("fork1", tuning_fork(), transparency=80)

# Uncomment of lines below to see the entire design or a drawing for specific part
# 

design()

#tuning_fork_drawing()


#mp=new_part("test_mesh", translate(rotate(rotate(part_from_mesh(load_mesh(u"/home/volodya/Mechanics/part.stl")), Vz, -90), Vy, 180), mm(24.5), mm(27), mm(37.75)))


update_document()

print "All done !"
