import cadquery as cq
from nimble_end_plate import make_end_plate
from nimble_beam import make_beam

single_width = 155

width = single_width
height = single_width


# def make_end_plate(width, height):
#     # Make the main body
#     end = cq.Workplane().rect(width, height).extrude(3)
    
#     # Add the corner mounting holes
#     end = end.faces("<Z").workplane().pushPoints([(width / 2.0 - 10, height / 2.0 - 10), (-width / 2.0 + 10, -height / 2.0 + 10), (width / 2.0 - 10, -height / 2.0 + 10), (-width / 2.0 + 10, height / 2.0 - 10)]).cskHole(4.7, 10.0, 60)

#     end = end.faces("<Z").workplane(invert=True).text("W", 72, 3, cut=True)
#     return end

# Create parts
bottom = make_end_plate(width, height)
bottom = bottom.rotateAboutCenter((1, 0, 0), 0)
beam = make_beam()

# Build the assembly
assy = cq.Assembly()
assy.add(bottom, name="bottom_end")
assy.add(make_beam(), name="leg1")
#assy.add(make_beam(), name="leg2")

assy.constrain("bottom_end@faces@>Z", "leg1@faces@<Z", "Axis")
assy.constrain("bottom_end@faces@>Z", "leg1@faces@<Z", "Plane")
#assy.constrain("bottom_end@faces@<X", "leg1?X", "Axis")
assy.solve()

show_object(assy)
