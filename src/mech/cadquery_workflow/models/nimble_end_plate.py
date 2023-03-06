import cadquery as cq

single_width = 155

width = single_width
height = single_width

def make_end_plate(width, height):
    # Make the main body
    end = cq.Workplane().rect(width, height).extrude(3)
    
    # Add the corner mounting holes
    end = end.faces("<Z").workplane().pushPoints([(width / 2.0 - 10, height / 2.0 - 10), (-width / 2.0 + 10, -height / 2.0 + 10), (width / 2.0 - 10, -height / 2.0 + 10), (-width / 2.0 + 10, height / 2.0 - 10)]).cskHole(4.7, 10.0, 60)

    end = end.faces("<Z").workplane(invert=True).text("W", 144, 3, cut=True)
    return end

end_plate = make_end_plate(width, height)

show_object(end_plate)