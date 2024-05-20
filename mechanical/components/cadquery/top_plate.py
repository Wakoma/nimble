
"""
cq-cli script using cadscript to generate the topplate of a nimble rack.
As of yet this cannot hold an instrument.
"""
import cadscript as cad

from nimble_builder.nimble_end_plate import create_end_plate

# parameters to be set in exsource-def.yaml file
width = 100
depth = 100
height = 3


def create(width, depth, height):
    """
    just create end plate, not further changes needed
    """
    return create_end_plate(width, depth, height)

if __name__ == "__main__" or __name__ == "__cqgi__" or "show_object" in globals():
    result = create(width, depth, height)
    cad.show(result)  # when run in cq-cli, will return result
