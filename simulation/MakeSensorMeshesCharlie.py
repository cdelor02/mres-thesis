# EDITED VERSION OF JAMES' "MakeSensorMeshes.py", FOR TESTING A FINGER ACTUATOR DESIGN

# NEED .STEP FILE OF MODEL TO RUN THIS PROGRAM

#%% Make tetra meshes from step files
# This is a script for now but hope to make it a library/function at some point

#%% Load files
import gmsh
import os
import meshio

gmsh.initialize()
gmsh.option.setNumber("General.Terminal", 1)

inpath= 'pneunet_approximate_test_first_bend_INFLATE' #'pneunet_approximate_test'#'finger_two_bend_hollow'
outname=inpath # saved as .msh and .vtu

# Let's merge an STEP mesh that we would like to remesh
path = os.path.dirname(os.path.abspath(__file__))
gmsh.merge(os.path.join(path, inpath + ".STEP"))

model = gmsh.model
fields = model.geo

# this opens the result in gmsh. uncomment to view it. you must close gmsh to run the rest of the script
#gmsh.fltk.run()


#%% Make sizing field

# As we want to move the electrodes around inside the sensor, I thought the easiest thing would
# be to refine the mesh along the entire inner surface, that way we dont have to remesh if we move the 
# electrodes 

# define a line through the middle  x=0 y=0.7 z=-21 - 21
# todo - define the line in the cad model
# could use the MathEval option too?

Lmin = 1 #5 # smallest size in mesh units
Lmax = 1 #0.5 # biggest size

# see threshold description below
DistMin = 20 #8 + 2 # diameter of hole in the middle is 16, so give it 2 mm beyond this of Lmin size elements
DistMax= 25 # radius of outer wall in this example


# points 9 and 10, creating a line which goes through the finger centerline
PointTag1 = fields.addPoint(15, 10, 0, Lmin)
#PointTag2 = fields.addPoint(-20.3, 10, 0, Lmin) # use this as second point if finger is bent
PointTag2 = fields.addPoint(-75, 10, 0, Lmin) # use this as second point if finger is straight

# find midpoint of end of finger (the middle of the surface)
# https://www.meracalculator.com/graphic/3dimensional-midpoint.php
# Between points 3 and 11

# fingertip for one bend finger 
#x1 = -143.922 /2 
#y1 = 10
#z1 = -62.679 / 2
#PointTag3 = fields.addPoint(x1, y1, z1, Lmin) # 3rd point (fingertip) in single bend finger model


#x2 = -96.6023/2
#y2 = 10
#z2 = -35.3589/2
#PointTag3 = fields.addPoint(x2, y2, z2, Lmin) # 3rd point (2nd joint) in two bend finger model

#x3 = -129.2819/2
#y3 = 10
#z3 = -91.9614/2
#PointTag4 = fields.addPoint(x3, y3, z3, Lmin) # 4th point (fingertip) in two bend finger model



LineTag=fields.addLine(PointTag1, PointTag2)
#LineTag=fields.addLine(PointTag2, PointTag3) # include this for one and two bend models
#LineTag=fields.addLine(PointTag3, PointTag4) # include this for two bend model


# update all points
fields.synchronize()

# add a distance field - gives a value of the distance of every point in mesh to points we describe
DistanceField=model.mesh.field.add("Distance")

# create 100 points along the line with made down the middle
model.mesh.field.setNumber(DistanceField, "NNodesByEdge", 100)
model.mesh.field.setNumbers(DistanceField, "EdgesList", [LineTag])

# We then define a `Threshold' field, which uses the return value of the
# `Distance' field 1 in order to define a simple change in element size
# depending on the computed distances
#
# LcMax -                         /------------------
#                               /
#                             /
#                           /
# LcMin -o----------------/
#        |                |       |
#      Point           DistMin DistMax
ThresField=model.mesh.field.add("Threshold")
model.mesh.field.setNumber(ThresField, "IField", DistanceField)
model.mesh.field.setNumber(ThresField, "LcMin", Lmin)
model.mesh.field.setNumber(ThresField, "LcMax", Lmax)
model.mesh.field.setNumber(ThresField, "DistMin", DistMin)
model.mesh.field.setNumber(ThresField, "DistMax", DistMax)

# set this threshold field as the background sizing field
model.mesh.field.setAsBackgroundMesh(ThresField)

# turn off any sizing based on geometry
gmsh.option.setNumber("Mesh.CharacteristicLengthExtendFromBoundary", 0)
gmsh.option.setNumber("Mesh.CharacteristicLengthFromPoints", 0)
gmsh.option.setNumber("Mesh.CharacteristicLengthFromCurvature", 0)

# this opens the result in gmsh. uncomment to view it. you must close gmsh to run the rest of the script
#gmsh.fltk.run()

#%% Generate mesh

gmsh.model.mesh.generate(3)

# Sadly I havent figured out how to add the post processing view automatically
#f=gmsh.view.add('SizeField')
#gmsh.view.addListData(f,"SP",1,ThresField)
#gmsh.view.addModelData(t,0,model.getEntityName)

# these take a while to run so i recommend turning them off to start with
# then run them when you are happy with the sizing field choice

model.mesh.optimize('',niter=10)
model.mesh.optimize('Netgen',niter=20)

gmsh.fltk.run()

# this opens the result in gmsh. uncomment to view it. you must close gmsh to run the rest of the script


#%% Save meshfile 

gmsh.write(os.path.join(path,outname + ".msh"))
gmsh.finalize()

# you can now load the .msh file in paraview


# meshio saves it better to vtu (binary compressed) this makes it easy to load into paraview
m = meshio.Mesh.read(os.path.join(path,outname + ".msh"))
m.write(os.path.join(path, outname + ".vtu"))

