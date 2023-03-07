import cadquery as cq
from nimble_end_plate import create as create_end
from nimble_beam import create as create_beam

single_width = 155

width = single_width
depth = single_width
stack_height = "2x3x4"
total_height = 0

for holes in stack_height.split("x"):
    total_height += int(holes) * 25

# Create parts
bottom = create_end(width, depth)
bottom = bottom.rotateAboutCenter((1, 0, 0), 0)
top = create_end(width, depth)
top = bottom.rotateAboutCenter((1, 0, 0), 0)

# Build the assembly
assy = cq.Assembly()
assy.add(bottom, name="bottom_end")
assy.add(create_beam(total_height), name="leg1", loc=cq.Location((-width / 2.0 + 10, -depth / 2.0 + 10, 3)))
assy.add(create_beam(total_height), name="leg2", loc=cq.Location((width / 2.0 - 10, -depth / 2.0 + 10, 3)))
assy.add(create_beam(total_height), name="leg3", loc=cq.Location((width / 2.0 - 10, depth / 2.0 - 10, 3)))
assy.add(create_beam(total_height), name="leg4", loc=cq.Location((-width / 2.0 + 10, depth / 2.0 - 10, 3)))
assy.add(top, name="top_end", loc=cq.Location((0, 0, total_height + 3)))

show_object(assy)
