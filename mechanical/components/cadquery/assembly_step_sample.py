from mechanical.components.cadquery.tray_6in import create_6in_shelf
import cadquery as cq
from cadquery.vis import show
from cq_annotate.views import explode_assembly
from cq_annotate.callouts import add_assembly_lines


def m2_5_screw(length=6.0):
    """
    Generates a simplified model of an M2.5 screw for the assembly.
    """

    # The threaded portion
    screw = (
        cq.Workplane()
        .workplane(centerOption="CenterOfBoundBox")
        .circle(2.5 / 2.0)
        .extrude(length)
    )

    # Overall head shape
    screw = (
        screw.faces(">Z")
        .circle(4.5 / 2.0)
        .extrude(2.5)
    )

    # Add the hex drive cutout
    screw = (
        screw.faces(">Z")
        .workplane(centerOption="CenterOfBoundBox")
        .polygon(6, 2.0)
        .cutBlind(-2.0)
    )

    # Tag the bottom face for an assembly line
    screw.faces("<Z").tag("assembly_line")

    return screw


def assemble(explode=False, annotate=True, export_format="png", rpi=None):
    """
    Builds a sample assembly, explodes and annotates it.
    """

    # The top-level assembly
    assy = cq.Assembly()

    # Generate the shelf
    shelf = create_6in_shelf("raspi", 1).cq()
    assy.add(shelf, name="shelf", color=cq.Color(0.996, 0.867, 0.0, 1.0))

    # Add the Raspberry Pi to the assembly
    rpi = rpi.rotateAboutCenter((1, 0, 0), 90).rotateAboutCenter((0, 0, 1), -90)
    # rpi.faces("<Z").tag("assembly_line")
    assy.add(rpi, name="rpi",
                  loc=cq.Location((-2.5, 24, 11)),
                  color=cq.Color(0.565, 0.698, 0.278, 1.0),
                  metadata={"explode_loc": cq.Location((0, 0, 30))},

    )

    # Add the mounting screws for the RPi
    screw_length = 6.0
    screw_starting_height = 1.0
    screw_explode_height = 60.0
    assy.add(
        m2_5_screw(length=screw_length),
        name="screw_1",
        loc=cq.Location((-13.0, 23.5, screw_starting_height)),
        color=cq.Color(0.04, 0.5, 0.67, 1.0),
        metadata={"explode_loc": cq.Location((0, 0, screw_explode_height))},
    )
    assy.add(
        m2_5_screw(length=screw_length),
        name="screw_2",
        loc=cq.Location((36.0, 23.5, screw_starting_height)),
        color=cq.Color(0.04, 0.5, 0.67, 1.0),
        metadata={"explode_loc": cq.Location((0, 0, screw_explode_height))},
    )
    assy.add(
        m2_5_screw(length=screw_length),
        name="screw_3",
        loc=cq.Location((-13.0, 81.5, screw_starting_height)),
        color=cq.Color(0.04, 0.5, 0.67, 1.0),
        metadata={"explode_loc": cq.Location((0, 0, screw_explode_height))},
    )
    assy.add(
        m2_5_screw(length=screw_length),
        name="screw_4",
        loc=cq.Location((36.0, 81.5, screw_starting_height)),
        color=cq.Color(0.04, 0.5, 0.67, 1.0),
        metadata={"explode_loc": cq.Location((0, 0, screw_explode_height))},
    )

    # Annotate with assembly lines, if requested
    if annotate:
        add_assembly_lines(assy, line_diameter=0.5)

    # Created the exploded assembly, if requested
    if explode:
        explode_assembly(assy)

    return assy


if __name__ == "__main__":
    # Import the Raspberry Pi STEP model
    # We do this here and pass it because it is a very detailed step and takes awhile to load
    # Downloaded from https://grabcad.com/library/raspberry-pi-4-model-b-1#!
    rpi = cq.importers.importStep("/home/jwright/Downloads/raspberry_pi_4_model_b.step")

    # Exploded and annotated Raspberry Pi shelf-component combo
    assy = assemble(explode=True, annotate=True, rpi=rpi)

    # Use the same options to export each image
    png_opts = {
        "width": 600,
        "height": 600,
        "camera_position": (65, -50, 75),
        "view_up_direction": (0, 0, 1),
        "focal_point": (20, 10, 35),
        "parallel_projection": True,
        "background_color": (1.0, 1.0, 1.0),
        "clipping_range": (0, 400),
    }
    svg_opts = {
        "width": 600,
        "height": 600,
        "marginLeft": 75,
        "marginTop": 100,
        "showAxes": False,
        "projectionDir": (0.1, 0.1, 0.1),
        "strokeWidth": 0.75,
        "strokeColor": (225, 225, 225),
        "hiddenColor": (0, 0, 255),
        "showHidden": False,
    }

    # 01 - Export an annotated and exploded assembly step to PNG
    assy.save("./build/images/01_exploded_and_annotated.png", opt=png_opts)

    # 02 - Export an annotated and exploded assembly step to SVG
    assy_compound = assy.toCompound()
    cq.exporters.export(assy_compound.rotate((0, 0, 0), (1, 0, 0), -90), "./build/images/02_exploded_and_annotated.svg", opt=svg_opts)

    # Exploded but not annotated Raspberry Pi shelf-component combo
    assy = assemble(explode=True, annotate=False, rpi=rpi)

    # 03 - Export an exploded but not annotated assembly step to PNG
    assy.save("./build/images/03_exploded_but_not_annotated.png", opt=png_opts)

    # 04 - Export an exploded but not annotated assembly step to SVG
    assy_compound = assy.toCompound()
    cq.exporters.export(assy_compound.rotate((0, 0, 0), (1, 0, 0), -90), "./build/images/04_exploded_but_not_annotated.svg", opt=svg_opts)

    # Assembled with annotation lines
    assy = assemble(explode=False, annotate=True, rpi=rpi)

    # 05 - Export an assembled and annotated assembly step to PNG
    assy.save("./build/images/05_assembled_and_annotated.png", opt=png_opts)

    # 06 - Export an assembed and annotated assembly step to SVG
    assy_compound = assy.toCompound()
    cq.exporters.export(assy_compound.rotate((0, 0, 0), (1, 0, 0), -90), "./build/images/06_assembled_and_annotated.svg", opt=svg_opts)

    # Plain, unannotated assembly
    assy = assemble(explode=False, annotate=False, rpi=rpi)

    # 07 - Export a plain assembled assembly step to PNG
    assy.save("./build/images/07_assembled_plain.png", opt=png_opts)

    # 06 - Export an assembed and annotated assembly step to SVG
    assy_compound = assy.toCompound()
    cq.exporters.export(assy_compound.rotate((0, 0, 0), (1, 0, 0), -90), "./build/images/08_assembled_plain.svg", opt=svg_opts)

    # show(assy)
