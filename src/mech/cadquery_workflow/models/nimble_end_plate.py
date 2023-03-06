import cadquery as cq


def create(width, height):
    # Make the main body
    end = cq.Workplane().rect(width, height).extrude(3)
    
    # Add the corner mounting holes
    end = end.faces("<Z").workplane().pushPoints([(width / 2.0 - 10, height / 2.0 - 10), (-width / 2.0 + 10, -height / 2.0 + 10), (width / 2.0 - 10, -height / 2.0 + 10), (-width / 2.0 + 10, height / 2.0 - 10)]).cskHole(4.7, 10.0, 60)

    end = end.faces("<Z").workplane(invert=True).text("W", 144, 3, cut=True)

    end.faces(">Z").edges("%CIRCLE").edges(">Y and >X").tag("hole1")
    # rv.faces(">Z").edges("%CIRCLE").edges("<Z").tag("hole2")

    return end

