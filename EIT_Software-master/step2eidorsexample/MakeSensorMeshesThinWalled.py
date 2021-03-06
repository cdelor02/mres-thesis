#%% Make tetra meshes from step files
# This is a script for now but hope to make it a library/function at some point

#%% Load files
import gmsh
import os
import meshio

gmsh.initialize()
gmsh.option.setNumber("General.Terminal", 1)

#inpath='SensorChamberSingle'
inpath='SensorChamber'
outname=inpath # saved as .msh and .vtu

# Let's merge an STEP mesh that we would like to remesh
path = os.path.dirname(os.path.abspath(__file__))
gmsh.merge(os.path.join(path, inpath + ".STEP"))

model = gmsh.model
fields = model.geo

# this opens the result in gmsh. uncomment to view it. you must close gmsh to run the rest of the script
#gmsh.fltk.run()


#%% Make sizing field


# in this case I have defined a plane inside the mesh and made it more refined in the middle

# ignore this by setting lmin and lmax to the same value

Lmin = 0.5 # smallest size in mesh units
Lmax = 5 # biggest size

# see threshold description below
DistMin = 5 # make this bigger as the wall is 2mm thick
DistMax= 25 # radius of outer wall in this example

# line through middle
PointTag1=fields.addPoint(0,0.7,-21, Lmin)
PointTag2=fields.addPoint(0,0.7,21, Lmin)
LineTag=fields.addLine(PointTag1,PointTag2)

# surface at electrode plane

extents=18

PlaneP1=fields.addPoint(-extents,-extents,0,Lmin)
PlaneP2=fields.addPoint(-extents,extents,0,Lmin)
PlaneP3=fields.addPoint(extents,extents,0,Lmin)
PlaneP4=fields.addPoint(extents,-extents,0,Lmin)

PlaneLine1=fields.addLine(PlaneP1,PlaneP2)
PlaneLine2=fields.addLine(PlaneP2,PlaneP3)
PlaneLine3=fields.addLine(PlaneP3,PlaneP4)
PlaneLine4=fields.addLine(PlaneP4,PlaneP1)


LineLoop=fields.addCurveLoop([PlaneLine1,PlaneLine2,PlaneLine3,PlaneLine4])
#Surf=fields.addPlaneSurface([LineLoop])


# update all points
fields.synchronize()

# add a distance field - gives a value of the distance of every point in mesh to points we describe
DistanceField=model.mesh.field.add("Distance")

# create 100 points along the line with made down the middle
model.mesh.field.setNumber(DistanceField, "NNodesByEdge", 100)
model.mesh.field.setNumbers(DistanceField, "EdgesList", [PlaneLine1,PlaneLine2,PlaneLine3,PlaneLine4])

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



# this opens the result in gmsh. uncomment to view it. you must close gmsh to run the rest of the script
gmsh.fltk.run()

#%% Save meshfile 

gmsh.write(os.path.join(path,outname + ".msh"))
gmsh.finalize()

# you can now load the .msh file in paraview


# meshio saves it better to vtu (binary compressed) this makes it easy to load into paraview
m = meshio.Mesh.read(os.path.join(path,outname + ".msh"))
m.write(os.path.join(path, outname + ".vtu"))

# %%


# %%
