"""
This module generates shelves for the nimble rack system. The shelves are matched with devices, and
the shelves are generated based on the device type. The shelves are generated using the
`ShelfBuilder` class from the `nimble_build_system.cad.shelf_builder` module.

Rendering and documentation generation is also supported for the shelves.
"""
import os
import posixpath
import warnings

import yaml
from cadorchestrator.components import AssembledComponent, GeneratedMechanicalComponent
import cadquery as cq
import cadscript

from nimble_build_system.cad import RackParameters
from nimble_build_system.cad.device_placeholder import generate_placeholder
from nimble_build_system.cad.shelf_builder import ShelfBuilder, ziptie_shelf
from nimble_build_system.orchestration.device import Device
from nimble_build_system.orchestration.paths import REL_MECH_DIR



def create_shelf_for(device_id: str,
                     assembly_key: str='Shelf',
                     position: tuple[float, float, float]=(0,0,0),
                     color: str='dodgerblue1',
                     rack_params: RackParameters|None = None,
                     dummy_device_data:dict|None=None):
    """
    Create a shelf for a device based on the device id. The shelf is generated based on the device
    type and dimensions.

    Parameters:
        device_id (str): The id of the device that the shelf is for.
        assembly_key (str): The key for the assembled shelf.
        position (tuple[float, float, float]): The position of the shelf in the rack.
        color (str): The color of the shelf, useful for rendering.
        rack_params (RackParameters): The parameters for the rack that this shelf will be in.
        dummy_device_data (dict): Data used if the device is a dummy device.

        Returns:
            Shelf: A shelf object for the device, instantiating the correct Class.
    """

    if not rack_params:
        rack_params = RackParameters()

    #Dummy is used for development purposes
    if device_id.startswith("dummy-"):
        device = Device(device_id, rack_params, dummy=True, dummy_data=dummy_device_data)
    else:
        device = Device(device_id, rack_params)

    #TODO. We have shelf_id, shekf_key, shelf_type, and shelf_builder_id,
    # None of which are explained well, and the neither the id or the key
    # is truly unique.

    shelf_type = device.shelf_builder_id

    if shelf_type in SHELF_TYPES:
        shelf_class, kwargs = SHELF_TYPES[shelf_type]
    else:
        warnings.warn(RuntimeWarning(f"Unknown shelf type {shelf_type}"))
        shelf_class = Shelf
        kwargs = {}
    return shelf_class(
            device,
            assembly_key,
            position,
            color,
            rack_params,
            **kwargs
    )

class Shelf():
    """
    Base shelf class that can be interrogated to get all of the renders and docs.
    """

    variants = {
        "generic": "A generic cable tie shelf",
        "stuff": "A shelf for general stuff such as wires. No access to the front",
        "stuff-thin": "A thin version of the stuff shelf",
        "nuc": "A shelf for an Intel NUC",
        "usw-flex": "A shelf for a Ubiquiti USW-Flex",
        "usw-flex-mini": "A shelf for a Ubiquiti Flex Mini",
        "anker-powerport5": "A shelf for an Anker PowerPort 5",
        "anker-a2123": "A shelf for an Anker 360 Charger 60W (a2123)",
        "anker-atom3slim": "A shelf for an Anker PowerPort Atom III Slim (AK-194644090180)",
        "hdd35": "A shelf for an 3.5\" HDD",
        "dual-ssd": "A shelf for 2x 2.5\" SSD",
        "raspi": "A shelf for a Raspberry Pi",
    }
    _variant = None
    _device = None
    _device_model = None
    _shelf_model = None
    _assembled_shelf = None
    _device_depth_axis = None  # Can be items like "-X", "X", "-Y", etc
    _device_offset = (0, 0, 0)  # Offsets to put the device for the correct assembly position
    _unit_width = 6  # 6 or 10 inch rack


    def __init__(self,
                 device: Device,
                 assembly_key: str,
                 position: tuple[float, float, float],
                 color: str,
                 rack_params: RackParameters):

        self._rack_params = rack_params

        self._device = device

        #Note that "assembled shelf" is the CadOrchestrator AssembledComponent
        # object not the full calculation in CadQuery of the physical assembly!
        self._assembled_shelf = self._generate_assembled_shelf(assembly_key,
                                                               position,
                                                               color)
        #Note docs can only be generated after self._assembled_shelf is set
        self._assembled_shelf.component.set_documentation(self.generate_docs())


    @property
    def height_in_u(self):
        """
        Return the height of the shelf in standard rack units/increments.
        """
        return self._device.height_in_u


    def _generate_assembled_shelf(self,
                                  assembly_key: str,
                                  position: tuple[float, float, float],
                                  color: str):
        shelf_key = self._device.shelf_key
        source = os.path.join(REL_MECH_DIR, "components/cadquery/tray_6in.py")
        source = posixpath.normpath(source)

        component = GeneratedMechanicalComponent(
            key=shelf_key,
            name=f"{self._device.name} shelf",
            description="A shelf for " + self._device.name,
            output_files=[
                f"./printed_components/{shelf_key}.step",
                f"./printed_components/{shelf_key}.stl",
            ],
            source_files=[source],
            parameters={
                "device_id": self._device.id,
            },
            application="cadquery"
        )

        return AssembledComponent(
            key=assembly_key,
            component=component,
            data = {
                'position': position,
                'color': color
            },
            include_key=True,
            include_stepfile=True
        )


    @property
    def name(self):
        """
        Return the name of the shelf. This is the same name as the
        component.
        """
        return self._assembled_shelf.name


    @property
    def device(self):
        """
        Return the Device object for the networking component that sits on this shelf.
        """
        return self._device


    @property
    def assembled_shelf(self) -> AssembledComponent:
        """
        Return the Object describing the assembled shelf (currently this in an empty
        shelf in the correct location on the rack).
        This is an AssembledComponent.
        """
        return self._assembled_shelf


    @property
    def shelf_component(self) -> GeneratedMechanicalComponent:
        """
        Return the Object describing shelf object, this is a
        `cadorchestrator.component.GeneratedMechanicalComponent`
        """
        return self._assembled_shelf.component


    def generate_device_model(self):
        """
        Generates the device model only.
        """
        # Generate the placeholder device so that it can be used in the assembly step,
        # but do not generated if it has been generated already.
        if self._device_model is None:
            device = generate_placeholder(self.name,
                                        self._device.width,
                                        self._device.depth,
                                        self._device.height)

            # Once the device model has been generated once, save it so that it can be reused in
            # assemblies and such
            self._device_model = device

        return self._device_model


    def generate_shelf_model(self):
        """
        Generates the shelf model only.
        """
        # Generate the shelf model, but do not generate if it has been generated already.
        if self._shelf_model is None:
            shelf = ziptie_shelf(self.height_in_u)
            self._shelf_model = shelf

        return self._shelf_model


    def generate_assembly_model(self):
        """
        Generates an CAD model of the shelf assembly showing assembly step between
        a device and a shelf. This can be optionally be exploded.
        It is generated solely based on the device ID.
        """

        # Get and orient the device model properly in relation to the shelf
        device = self.generate_device_model()
        if self._device_depth_axis == "X":
            device = device.rotateAboutCenter((0, 0, 1), 90)
        elif self._device_depth_axis == "-X":
            device = device.rotateAboutCenter((0, 0, 1), -90)
        elif self._device_depth_axis == "Y":
            device = device.rotateAboutCenter((1, 0, 0), 90)
        elif self._device_depth_axis == "-Y":
            device = device.rotateAboutCenter((1, 0, 0), -90)
        elif self._device_depth_axis == "Z":
            device = device.rotateAboutCenter((0, 1, 0), 90)
        elif self._device_depth_axis == "-Z":
            device = device.rotateAboutCenter((0, 1, 0), -90)

        # Move the device to the correct position on the shelf
        device = device.translate((self._device_offset[0],
                                   self._device_offset[1],
                                   self._device_offset[2]))

        # Create the assembly holding all the parts that go into the shelf unit
        assy = cq.Assembly()
        assy.add(device, name="device", color=cq.Color(0.996, 0.867, 0.0, 1.0))
        assy.add(self.generate_shelf_model().cq(),
                 name="shelf",
                 color=cq.Color(0.565, 0.698, 0.278, 1.0))

        return assy


    def get_render(self, assy, camera_pos, image_format="png"):
        """
        Generates a render of the assembly.
        """

        # TODO - Use the PNG functionality in CadQuery to generate a PNG render
        # TODO - Maybe also need other formats such as glTF
        #pylint: disable=unused-argument
        return NotImplemented


    def generate_docs(self):
        """
        Return the markdown (BuildUp) for the GitBuilding page for assembling this shelf.
        """
        stlfilename = self.shelf_component.stl_representation
        meta_data = {
            "Tag": "shelf",
            "Make": {
                self.name: {
                    "template": "printing.md",
                    "stl-file": stlfilename,
                    "stlname": os.path.split(stlfilename)[1],
                    "material": "PLA",
                    "weight-qty": "50g",
                }
            }
        }
        md = f"---\n{yaml.dump(meta_data)}\n---\n\n"
        md += f"# Assembling the {self.name}\n\n"
        md += "{{BOM}}\n\n"
        md += "## Position the "+self._device.name+" {pagestep}\n\n"
        md += "* Take the ["+self.name+"]{make, qty:1, cat:printed} you printed earlier\n"
        md += "* Position the ["+self._device.name+"]{qty:1, cat:net} on the shelf\n\n"
        md += "## Secure the "+self._device.name+" {pagestep}\n\n"
        md += ">!! **TODO**  \n>!! Need information on how the item is secured to the shelf."

        return  md

class StuffShelf(Shelf):
    """
    A generic shelf for devices that do not have a specific shelf type.
    """
    ##TODO: Perhaps make a "dummy" device for "stuff"?
    def __init__(self,
                 device: Device,
                 assembly_key: str,
                 position: tuple[float, float, float],
                 color: str,
                 rack_params: RackParameters,
                 thin: bool=False):

        super().__init__(device, assembly_key, position, color, rack_params)
        self.thin = thin

    def generate_shelf_model(self) -> cadscript.Body:
        """
        A shelf for general stuff such as wires. No access to the front
        """
        if self._shelf_model is None:
            width = "broad" if not self.thin else "standard"
            builder = ShelfBuilder(
                self.height_in_u, width=width, depth="standard", front_type="w-pattern"
            )
            builder.make_tray(sides="w-pattern", back="open")
            self._shelf_model = builder.get_body()

        return self._shelf_model


class NUCShelf(Shelf):
    """
    Shelf class for an Intel NUC device.
    """
    def generate_shelf_model(self) -> cadscript.Body:
        """
        A shelf for an Intel NUC
        """
        builder = ShelfBuilder(
            self.height_in_u, width="broad", depth="standard", front_type="full"
        )
        builder.cut_opening("<Y", builder.inner_width, 4)
        builder.make_tray(sides="w-pattern", back="open")
        builder.add_mounting_hole_to_bottom(x_pos=0, y_pos=35, base_thickness=4, hole_type="M3cs")
        builder.add_mounting_hole_to_bottom(x_pos=0, y_pos=120, base_thickness=4, hole_type="M3cs")
        return builder.get_body()

class USWFlexShelf(Shelf):
    """
    Shelf class for a Ubiquiti USW-Flex device.
    """
    def generate_shelf_model(self) -> cadscript.Body:
        """
        A shelf for a Ubiquiti USW-Flex
        """
        if self._shelf_model is None:
            builder = ShelfBuilder(
                self.height_in_u, width="standard", depth=119.5, front_type="full"
            )
            builder.cut_opening("<Y", builder.inner_width, 4)
            builder.make_tray(sides="w-pattern", back="open")
            # add 2 mounting bars on the bottom plate
            sketch = cadscript.make_sketch()
            sketch.add_rect(8, 60, center="X", pos=[(-17.5, 42), (+17.5, 42)])
            base = cadscript.make_extrude("XY", sketch, builder.rack_params.tray_bottom_thickness)
            sketch.cut_circle(d=3.8, pos=[(-17.5, 30 + 42), (+17.5, 30 + 42)])
            base2 = cadscript.make_extrude("XY", sketch, 5)
            builder.get_body().add(base).add(base2)
            self._shelf_model = builder.get_body()

        return self._shelf_model

class USWFlexMiniShelf(Shelf):
    """
    Shelf class for a Ubiquiti Flex Mini device.
    """
    def generate_shelf_model(self) -> cadscript.Body:
        """
        A shelf for a for Ubiquiti Flex Mini
        """
        if self._shelf_model is None:
            rack_params = RackParameters(tray_side_wall_thickness=3.8)
            builder = ShelfBuilder(
                self.height_in_u,
                width="standard",
                depth=73.4,
                front_type="full",
                rack_params=rack_params
            )
            builder.cut_opening("<Y", 85, offset_y=5, size_y=19)
            builder.make_tray(sides="slots", back="slots")
            builder.cut_opening(">Y",
                                30,
                                offset_y=builder.rack_params.tray_bottom_thickness,
                                depth=10)
            builder.add_mounting_hole_to_side(
                y_pos=59, z_pos=builder.height / 2, hole_type="M3-tightfit", side="both"
            )
            builder.add_mounting_hole_to_back(
                x_pos=-75 / 2, z_pos=builder.height / 2, hole_type="M3-tightfit"
            )
            builder.add_mounting_hole_to_back(
                x_pos=+75 / 2, z_pos=builder.height / 2, hole_type="M3-tightfit"
            )
            self._shelf_model =  builder.get_body()

        return self._shelf_model

class AnkerShelf(Shelf):
    """
    Shelf class for an Anker PowerPort 5, Anker 360 Charger 60W (a2123), etc
    """
    def __init__(self,
                 device: Device,
                 assembly_key: str,
                 position: tuple[float, float, float],
                 color: str,
                 rack_params: RackParameters,
                 internal_width: float = 56,
                 internal_depth: float = 90.8,
                 internal_height: float = 25,
                 front_cutout_width: float = 53):

        #pylint: disable=too-many-arguments

        super().__init__(device, assembly_key, position, color, rack_params)
        self.internal_width = internal_width
        self.internal_depth = internal_depth
        self.internal_height = internal_height
        self.front_cutout_width = front_cutout_width

    def generate_shelf_model(self) -> cadscript.Body:
        """
        A shelf for an Anker PowerPort 5, Anker 360 Charger 60W (a2123),  or Anker PowerPort Atom
        III Slim (AK-194644090180)
        """
        if self._shelf_model is None:
            self._shelf_model = ziptie_shelf(
                self.height_in_u,
                internal_width=self.internal_width,
                internal_depth=self.internal_depth,
                internal_height=self.internal_height,
                front_cutout_width=self.front_cutout_width
            )

        return self._shelf_model

class HDD35Shelf(Shelf):
    """
    Shelf class for a 3.5" hard drive device.
    """
    def generate_shelf_model(self) -> cadscript.Body:
        """
        A shelf for an 3.5" HDD
        """
        if self._shelf_model is None:
            width = 102.8  # 101.6 + 1.2 clearance
            screw_pos1 = 77.3  # distance from front
            screw_pos2 = screw_pos1 + 41.61
            screw_y = 7  # distance from bottom plane
            builder = ShelfBuilder(
                self.height_in_u, width="standard", depth="standard", front_type="w-pattern"
            )
            builder.make_tray(sides="slots", back="open")
            mount_sketch = cadscript.make_sketch()
            mount_sketch.add_rect(
                (width / 2, builder.inner_width / 2 + builder.rack_params.tray_side_wall_thickness),
                21,
                pos=[(0, screw_pos1), (0, screw_pos2)],
            )
            mount_sketch.chamfer("<X", (builder.inner_width - width) / 2)
            mount_sketch.mirror("X")
            builder.get_body().add(cadscript.make_extrude("XY", mount_sketch, 14))
            builder.add_mounting_hole_to_side(
                y_pos=screw_pos1,
                z_pos=screw_y + builder.rack_params.tray_bottom_thickness,
                hole_type="HDD",
                side="both",
            )
            builder.add_mounting_hole_to_side(
                y_pos=screw_pos2,
                z_pos=screw_y + builder.rack_params.tray_bottom_thickness,
                hole_type="HDD",
                side="both",
            )
            self._shelf_model = builder.get_body()

        return self._shelf_model

class DualSSDShelf(Shelf):
    """
    Shelf class for two 2.5" solid state drive devices.
    """
    def generate_shelf_model(self) -> cadscript.Body:
        """
        A shelf for two 2.5" SSDs
        """
        if self._shelf_model is None:
            rack_params = RackParameters()
            width = 70
            screw_pos1 = 12.5  # distance from front
            screw_pos2 = screw_pos1 + 76
            screw_y1 = 6.6  # distance from bottom plane
            screw_y2 = screw_y1 + 11.1
            builder = ShelfBuilder(
                self.height_in_u,
                width=width + 2 * rack_params.tray_side_wall_thickness,
                depth=111,
                front_type="w-pattern",
                base_between_beam_walls="none",
                beam_wall_type="none",
            )
            builder.make_tray(sides="slots", back="open")
            for x, y in [
                (screw_pos1, screw_y2),
                (screw_pos2, screw_y2),
                (screw_pos1, screw_y1),
                (screw_pos2, screw_y1),
            ]:
                builder.add_mounting_hole_to_side(
                    y_pos=x,
                    z_pos=y + rack_params.tray_bottom_thickness,
                    hole_type="M3-tightfit",
                    side="both",
                    base_diameter=11,
                )
            self._shelf_model = builder.get_body()

        return self._shelf_model

class RaspberryPiShelf(Shelf):
    """
    A shelf for Raspberry Pi models.
    """
    variants = {
        "Raspberry_Pi_4B": {"description": "A shelf for a Raspberry Pi 4B", "step_path": "N/A"},
        "Raspberry_Pi_5": {"description": "A shelf for a Raspberry Pi 5", "step_path": "N/A"},
    }

    def __init__(self,
                 device: Device,
                 assembly_key: str,
                 position: tuple[float, float, float],
                 color: str,
                 rack_params: RackParameters,
                 device_depth_axis: float = "X",
                 device_offset: tuple[float, float, float] = (0, 0, 0)):

        #pylint: disable=too-many-arguments

        super().__init__(device, assembly_key, position, color, rack_params)
        self._device_depth_axis = device_depth_axis
        self._device_offset = device_offset

    def generate_shelf_model(self):
        """
        Generates the shelf model only.
        """
        if self._shelf_model is None:
            screw_dist_x = 49
            screw_dist_y = 58
            dist_to_front = 23.5
            offset_x = -13
            builder = ShelfBuilder(self.height_in_u,
                                width="standard",
                                depth=111,
                                front_type="full")
            builder.cut_opening("<Y", (-15, 39.5), size_y=(6, 25))
            builder.cut_opening("<Y", (-41.5, -25.5), size_y=(6, 22))
            builder.make_tray(sides="ramp", back="open")
            for x, y in [
                (offset_x, dist_to_front),
                (offset_x + screw_dist_x, dist_to_front),
                (offset_x, dist_to_front + screw_dist_y),
                (offset_x + screw_dist_x, dist_to_front + screw_dist_y),
            ]:
                builder.add_mounting_hole_to_bottom(
                    x_pos=x,
                    y_pos=y,
                    hole_type="base-only",
                    base_thickness=builder.rack_params.tray_bottom_thickness,
                    base_diameter=20,
                )
                builder.add_mounting_hole_to_bottom(
                    x_pos=x,
                    y_pos=y,
                    hole_type="M3-tightfit",
                    base_thickness=5.5,
                    base_diameter=7
                )

            self._shelf_model = builder.get_body()

        return self._shelf_model


# Dictionary of shelf types and their corresponding class and kwargs as tuple
# (class, keyword-arguments)
SHELF_TYPES= {
    "generic": (Shelf, {}),
    "stuff": (StuffShelf, {}),
    "stuff-thin": (StuffShelf, {"thin":True}),
    "nuc": (NUCShelf, {}),
    "usw-flex": (USWFlexShelf, {}),
    "usw-flex-mini": (USWFlexMiniShelf, {}),
    "anker-powerport5": (AnkerShelf, {
        "internal_width": 56,
        "internal_depth": 90.8,
        "internal_height": 25,
        "front_cutout_width": 53
    }),
    "anker-a2123": (AnkerShelf, {
        "internal_width": 86.5,
        "internal_depth": 90,
        "internal_height": 20,
        "front_cutout_width": 71
    }),
    "anker-atom3slim": (AnkerShelf, {
        "internal_width": 70,
        "internal_depth": 99,
        #should be 26 high but this height create interference of the shelf
        "internal_height": 25,
        "front_cutout_width": 65
    }),
    "hdd35": (HDD35Shelf, {}),
    "dual-ssd": (DualSSDShelf, {}),
    "raspi": (RaspberryPiShelf, {
        "device_depth_axis": "-X",
        "device_offset": (12, 50, 15)
    })
}
