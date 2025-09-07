"""
This module generates shelves for the nimble rack system. The shelves are matched with devices, and
the shelves are generated based on the device type. The shelves are generated using the
`ShelfBuilder` class from the `nimble_build_system.cad.shelf_builder` module.

Rendering and documentation generation is also supported for the shelves.
"""

# pylint: disable=unused-import, line-too-long, too-many-arguments, too-many-lines

import os
import posixpath
import warnings
import logging

import yaml
from cadorchestrator.components import AssembledComponent, GeneratedMechanicalComponent
import cadquery as cq
import cadscript
from cq_annotate.views import explode_assembly

from nimble_build_system.cad import RackParameters
from nimble_build_system.cad.device_placeholder import generate_placeholder
from nimble_build_system.cad.shelf_builder import ShelfBuilder, ziptie_shelf
from nimble_build_system.cad.fasteners import Screw, Ziptie
from nimble_build_system.cad.renderer import generate_render
from nimble_build_system.orchestration.device import Device
from nimble_build_system.orchestration.paths import REL_MECH_DIR


def create_shelf_for(device_id: str,
                       *,
                       assembly_key: str = 'Shelf',
                       position: tuple[float, float, float] = (0, 0, 0),
                       color: str = 'dodgerblue1',
                       rack_params: RackParameters | None = None):
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
    device = Device(device_id, rack_params)

    #TODO. We have shelf_id, shelf_key, shelf_type, and shelf_builder_id,
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
        assembly_key=assembly_key,
        position=position,
        color=color,
        rack_params=rack_params,
        **kwargs
    )


class Shelf():
    """
    Base shelf class that can be interrogated to get all of the renders and docs.
    """

    # pylint: disable=too-many-instance-attributes

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
        "raspi": "A shelf for a Raspberry Pi",
    }
    _variant = None
    _device = None
    _device_model = None
    _shelf_model = None
    _shelf_assembly_model = None
    _exploded_shelf_assembly_model = None
    _assembled_shelf = None
    _device_depth_axis = None  # Can be items like "-X", "X", "-Y", etc
    _device_offset = (0, 0, 0)  # Offsets to put the device for the correct assembly position
    _device_explode_translation = (0, 0, 0)  # Where to move the device to during an explode
    _hole_locations = None  # List of hole locations for the device
    _fasteners = []  # List of screw positions for the device
    _unit_width = 6  # 6 or 10 inch rack
    _renders = None  # Renders that are available for each shelf type
    _width_category = "standard"  # Width category for the shelf ("broad" vs "standard" vs custom)
    # Hole location parameters
    _screw_dist_x = None
    _screw_dist_y = None
    _dist_to_front = None
    _offset_x = None

    def __init__(self,
                 device: Device,
                 *,
                 assembly_key: str,
                 position: tuple[float, float, float],
                 color: str,
                 rack_params: RackParameters
                 ):

        self._rack_params = rack_params

        self._device = device
        self._setup_assembly()
        #Note that "assembled shelf" is the CadOrchestrator AssembledComponent
        # object not the full calculation in CadQuery of the physical assembly!
        self._assembled_shelf = self._generate_assembled_shelf(assembly_key,
                                                               position,
                                                               color)
        #Note docs can only be generated after self._assembled_shelf is set
        self._assembled_shelf.component.set_documentation(self.generate_docs())

    def _setup_assembly(self):
        """
        This is called during init to set up how the device is assembled and rendered
        This must be called before setting the documentation as this uses the renders
        and fasteners set here
        """
        # Make some sane guesses at the device positioning
        if self._device.width is None or self._device.depth is None:
            self._device_depth_axis = "X"
            x_offset = 0.0
            y_offset = 0.0
        elif self._device.width < self._device.depth:
            self._device_depth_axis = "Y"
            x_offset = self._device.depth / 2.0
            y_offset = 0.0
        else:
            self._device_depth_axis = "X"
            x_offset = 0.0
            y_offset = self._device.width / 2.0

        # Protect against a non-existent device height
        if self._device.height is None:
            device_height = 0.0
        else:
            device_height = self._device.height

        self._device_offset = (x_offset, y_offset, device_height / 2.0 + 2.0)
        self._device_explode_translation = (0, 0, 50)

        self._fasteners = [
            Ziptie(name=None,
                   position=(0, 28.75, 1.0),
                   explode_translation=(0.0, 0.0, -40.0),
                   size="4",
                   fastener_type="ziptie",
                   axis="-X",
                   length=300),
            Ziptie(name=None,
                   position=(0, 86.25, 1.0),
                   explode_translation=(0.0, 0.0, -40.0),
                   size="4",
                   fastener_type="ziptie",
                   axis="-X",
                   length=300),
        ]
        self._renders = {"assembled":
                             {"order": 1,
                              "render_options": {"color_theme": "default",
                                                 "view": "front-top-right",
                                                 "zoom": 1.0,
                                                 "add_device_offset": False,
                                                 "add_fastener_length": False,
                                                 "annotate": False,
                                                 "explode": False}},
                         "annotated":
                             {"order": 0,
                              "render_options": {"color_theme": "default",
                                                 "view": "back-bottom-right",
                                                 "add_device_offset": False,
                                                 "add_fastener_length": False,
                                                 "zoom": 1.0,
                                                 "annotate": True,
                                                 "explode": True}}}  # Render options for the shelf

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
            data={
                'position': position,
                'color': color,
                'device': self._device.id
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
    def width_category(self):
        """
        Return the width category for the shelf.
        """
        return self._width_category

    @width_category.setter
    def width_category(self, value):
        """
        Set the width category for the shelf.
        """
        self._width_category = value

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

    @property
    def screw_dist_x(self):
        """
        Return the distance between the screws on the x-axis.
        """
        return self._screw_dist_x

    @screw_dist_x.setter
    def screw_dist_x(self, value):
        """
        Set the distance between the screws on the x-axis.
        """
        self._screw_dist_x = value

    @property
    def screw_dist_y(self):
        """
        Return the distance between the screws on the y-axis.
        """
        return self._screw_dist_y

    @screw_dist_y.setter
    def screw_dist_y(self, value):
        """
        Set the distance between the screws on the y-axis.
        """
        self._screw_dist_y = value

    @property
    def dist_to_front(self):
        """
        Return the distance to the front of the shelf.
        """
        return self._dist_to_front

    @dist_to_front.setter
    def dist_to_front(self, value):
        """
        Set the distance to the front of the shelf.
        """
        self._dist_to_front = value

    @property
    def offset_x(self):
        """
        Return the offset on the x-axis.
        """
        return self._offset_x

    @offset_x.setter
    def offset_x(self, value):
        """
        Set the offset on the x-axis.
        """
        self._offset_x = value

    @property
    def hole_locations(self):
        """
        Return the hole locations for the device.
        """
        return self._hole_locations

    @hole_locations.setter
    def hole_locations(self, value):
        """
        Set the hole locations for the device.
        """
        self._hole_locations = value

    @property
    def renders(self):
        """
        All of the renders that are available for a shelf and their render options.
        """
        return self._renders

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

    def generate_assembly_model(self, render_options=None):
        """
        Generates an CAD model of the shelf assembly showing assembly step between
        a device and a shelf. This can be optionally be exploded.
        It is generated solely based on the device ID.
        """

        # There is a false positive on the cq.Location constructor. If I make pylint happy it breaks
        # the method dispatch. If I make Python happy, pylint fails.
        # pylint: disable=no-value-for-parameter
        # pylint: disable=protected-access
        # pylint: disable=too-many-branches
        # pylint: disable=too-many-statements
        # pylint: disable=too-many-function-args

        # Get and orient the device model properly in relation to the shelf
        device = self.generate_device_model()
        if self._device_depth_axis == "X":
            device = device.rotateAboutCenter((0, 0, 1), 90)
        elif self._device_depth_axis == "-X":
            device = device.rotateAboutCenter((0, 0, 1), -90)
        elif self._device_depth_axis == "Y":
            device = device.rotateAboutCenter((0, 0, 1), 0)  # No rotation needed
        elif self._device_depth_axis == "-Y":
            device = device.rotateAboutCenter((0, 0, 1), -180)
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
        assy.add(device, name="device",
                 color=cq.Color(0.996, 0.867, 0.0, 1.0),
                 metadata={
                     "explode_translation": cq.Location(self._device_explode_translation)
                 })
        assy.add(self.generate_shelf_model().cq(),
                 name="shelf",
                 color=cq.Color(0.565, 0.698, 0.278, 1.0))

        # Add the fasteners to the assembly
        for i, fastener in enumerate(self._fasteners):
            # Get the CadQuery model for the fastener
            cur_fastener = fastener.fastener_model

            # Figure out what the name of the screw should be
            if fastener.name is None:
                fastener.name = f"fastener_{i}"

            # Figure out if extra extensions to the assembly lines have been requested
            if render_options["add_device_offset"]:
                x_offset = self._device_explode_translation[0]
                y_offset = self._device_explode_translation[1]
                z_offset = self._device_explode_translation[2]
            else:
                x_offset = 0
                y_offset = 0
                z_offset = 0

            # Check to see if the fastener length should be added to the assembly line length
            if render_options["add_fastener_length"]:
                x_offset += fastener.length
                y_offset += fastener.length
                z_offset += fastener.length

            # Add the fastener to the assembly
            assy.add(cur_fastener,
                     name=fastener.name,
                     loc=cq.Location(fastener.position, fastener.rotation[0], fastener.rotation[1]),
                     color=cq.Color(0.5, 0.5, 0.5, 1.0),
                     metadata={
                         "explode_translation": cq.Location(
                             (fastener.explode_translation[0],
                              fastener.explode_translation[1],
                              fastener.explode_translation[2])),
                         "assembly_line_length": (
                             abs(x_offset) +
                             abs(fastener.explode_translation[0]),
                             abs(y_offset) +
                             abs(fastener.explode_translation[1]),
                             abs(z_offset) +
                             abs(fastener.explode_translation[2])
                         )
                     })

        self._shelf_assembly_model = assy

        # Handle assembly explosion
        if render_options["explode"]:
            # If the exploded shelf assembly has already been generated, do not re-generate it
            if self._exploded_shelf_assembly_model is None:
                self._exploded_shelf_assembly_model = self._shelf_assembly_model._copy()
                explode_assembly(self._exploded_shelf_assembly_model)

            return self._exploded_shelf_assembly_model

        return self._shelf_assembly_model

    def list_renders(self):
        """
        Return a list of all the renders that can be generated for the shelf.
        """
        return self.renders.keys()

    def list_render_files(self):
        """
        Return a list of all the render paths that can be generated for the shelf.
        This is done so that the documentation generate will know where to find the files.
        """

        ordered_types = sorted([(r["order"], r_type) for r_type, r in self.renders.items()])
        render_types = [i[1] for i in ordered_types]
        return [self.render_filename(render_type) for render_type in render_types]

    def render_filename(self, render_type):
        """
        Return the file name for a given render type.
        """
        shelf_name = self.name.replace(" ", "_")
        return f"{shelf_name}_{render_type}.png"

    def generate_renders(self, base_path=None):
        """
        Generate all the renders for the shelf, using each one's specific render options.
        """

        # Step through each render type and generate the render
        for render_type, render in self.renders.items():
            # Get the base shelf name for the render filename
            file_path = os.path.join(base_path, self.render_filename(render_type))
            cur_render_options = render["render_options"]

            # Call the generic rendering method and pass it the model we want it to export to PNG
            generate_render(model=self.generate_assembly_model(render_options=cur_render_options),
                            file_path=file_path,
                            render_options=cur_render_options)

    def _fasteners_for_doc(self):
        fastener_dict = {}
        for fastener in self._fasteners:
            if fastener.human_name() in fastener_dict:
                fastener_dict[fastener.human_name()]["qty"] += 1
            else:
                fastener_dict[fastener.human_name()] = {"qty": 1}
        return fastener_dict

    @property
    def _fastener_str(self):
        fasteners = self._fasteners_for_doc()
        fastener_strs = []
        for name, data in fasteners.items():
            qty = data["qty"]
            fastener_strs.append(f"{qty} [{name}]" + "{qty:" + str(qty) + "}")
        if len(fastener_strs) == 0:
            return ""
        if len(fastener_strs) == 1:
            return fastener_strs[0]
        if len(fastener_strs) == 2:
            return fastener_strs[0] + " and " + fastener_strs[0]
        fastener_strs[-1] = "and " + fastener_strs[-1]
        return ", ".join(fastener_strs)

    def generate_docs(self):
        """
        Return the markdown (BuildUp) for the GitBuilding page for assembling this shelf.
        """
        stlfilename = posixpath.normpath("../build/" + self.shelf_component.stl_representation)
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
        md += "## Position the " + self._device.name + " {pagestep}\n\n"
        md += "* Take the [" + self.name + "]{make, qty:1, cat:printed} you printed earlier\n"
        fastener_str = self._fastener_str
        if fastener_str:
            md += "* Position the [" + self._device.name + "]{qty:1, cat:net} on the shelf as shown\n"
            md += f"* Fasten it in place using {fastener_str}.\n"
        else:
            md += "* Push fit the [" + self._device.name + "]{qty:1, cat:net} on the shelf as shown\n"
        md += "\n\n"
        for render in self.list_render_files():
            md += f"![](../build/renders/{render})\n"

        return md


class BroadShelf(Shelf):
    """
    Base shelf class for broad shelves.
    """

    def __init__(self,
                 device: Device,
                 *,
                 assembly_key: str,
                 position: tuple[float, float, float],
                 color: str,
                 rack_params: RackParameters
                 ):
        super().__init__(
            device,
            assembly_key=assembly_key,
            position=position,
            color=color,
            rack_params=rack_params
        )
        self.width_category = "broad"


class StuffShelf(Shelf):
    """
    A generic shelf for devices that do not have a specific shelf type.
    """

    ##TODO: Perhaps make a "dummy" device for "stuff"?
    def __init__(self,
                 device: Device,
                 *,
                 assembly_key: str,
                 position: tuple[float, float, float],
                 color: str,
                 rack_params: RackParameters,
                 thin: bool = False):
        super().__init__(device,
                         assembly_key=assembly_key,
                         position=position,
                         color=color,
                         rack_params=rack_params)
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


class NUCShelf(BroadShelf):
    """
    Shelf class for an Intel NUC device.
    """
    # this comes from a well rendered body.
    reference_offset = (0.0, 78.0, 29.5)

    def get_offset(self):
        """
        Adjust the Z-offset of `target_dims` so that it sits with the same bottom Z
        as `ref_dims`, assuming both offsets are center-based.

        Parameters:
            ref_dims (tuple): (depth, width, height) of the reference body (in mm)
            target_dims (tuple): (depth, width, height) of the body to align (in mm)
            ref_offset (tuple): (x, y, z) offset of the reference body

        Returns:
            tuple: (x, y, z) offset for the target body
        """

        _, _, h_ref = (112, 117, 51)
        _, _, h_target = self.get_shelf_dimensions()
        x_ref, y_ref, z_ref = self.reference_offset

        # Calculate bottom Z of reference
        z_bottom_ref = z_ref - h_ref / 2.0

        # New Z offset for target so its bottom aligns with the reference bottom
        z_target = z_bottom_ref + h_target / 2.0

        return x_ref, y_ref, z_target

    def get_shelf_dimensions(self):
        """
        Function gets the shelf dimensions based on the device data from devices.json?
        """

        return self._device.width, self._device.depth, self._device.height

    def _setup_assembly(self):
        # Device location settings
        self._device_depth_axis = "Y"
        self._device_offset = self.get_offset()
        self._device_explode_translation = (0.0, 0.0, 60.0)

        logging.debug("depth: %s, width: %s, height: %s", self._device.depth, self._device.width, self._device.height)
        logging.debug("atts: %s\n%s", dir(self._device), self._device.__dict__)


        # Gather all the mounting screw locations
        self.hole_locations = [
            (0.0, 35.0, 0.0),
            (0.0, 120.0, 0.0),
        ]

        self._fasteners = [
            Screw(name=None,
                  position=self.hole_locations[0],
                  explode_translation=(0.0, 0.0, 35.0),
                  size="M3-0.5",
                  fastener_type="iso10642",
                  axis="-Z",
                  length=6),
            Screw(name=None,
                  position=self.hole_locations[1],
                  explode_translation=(0.0, 0.0, 35.0),
                  size="M3-0.5",
                  fastener_type="iso10642",
                  axis="-Z",
                  length=6),
        ]
        self._renders = {"assembled":
                             {"order": 1,
                              "render_options": {"color_theme": "default",
                                                 "view": "front-top-right",
                                                 "add_device_offset": False,
                                                 "add_fastener_length": False,
                                                 "zoom": 1.15,
                                                 "annotate": False,
                                                 "explode": False}},
                         "annotated":
                             {"order": 0,
                              "render_options": {"color_theme": "default",
                                                 "view": "front-bottom-right",
                                                 "add_device_offset": True,
                                                 "add_fastener_length": True,
                                                 "zoom": 1.15,
                                                 "annotate": True,
                                                 "explode": True}}}  # Renders for the shelf

    def generate_shelf_model(self) -> cadscript.Body:
        """
        A shelf for an Intel NUC
        """
        builder = ShelfBuilder(
            self.height_in_u, width=self.width_category, depth="standard", front_type="full"
        )
        builder.cut_opening("<Y", builder.inner_width, offset_y=4)
        builder.make_tray(sides="w-pattern", back="open")
        builder.add_mounting_hole_to_bottom(x_pos=0, y_pos=35, base_thickness=4, hole_type="M3cs")
        builder.add_mounting_hole_to_bottom(x_pos=0, y_pos=120, base_thickness=4, hole_type="M3cs")
        return builder.get_body()


class USWFlexShelf(Shelf):
    """
    Shelf class for a Ubiquiti USW-Flex device.
    """

    def _setup_assembly(self):
        # Device location settings
        self._device_depth_axis = "X"
        self._device_offset = (0.0, 58.0, 18.0)
        self._device_explode_translation = (0.0, 0.0, 100.0)

        # Gather all the mounting screw locations
        self.hole_locations = [
            (-17.5, 30 + 42, 0.0),
            (+17.5, 30 + 42, 0.0)
        ]

        self._fasteners = [
            Screw(name=None,
                  position=self.hole_locations[0],
                  explode_translation=(0.0, 0.0, 40.0),
                  size="M4-0.7",
                  fastener_type="iso7380_1",
                  axis="-Z",
                  length=8),
            Screw(name=None,
                  position=self.hole_locations[1],
                  explode_translation=(0.0, 0.0, 40.0),
                  size="M4-0.7",
                  fastener_type="iso7380_1",
                  axis="-Z",
                  length=8),
        ]
        self._renders = {"assembled":
                             {"order": 1,
                              "render_options": {"color_theme": "default",
                                                 "view": "front-top-right",
                                                 "zoom": 1.15,
                                                 "add_device_offset": False,
                                                 "add_fastener_length": False,
                                                 "annotate": False,
                                                 "explode": False}},
                         "annotated":
                             {"order": 0,
                              "render_options": {"color_theme": "default",
                                                 "view": "front-bottom-right",
                                                 "add_device_offset": True,
                                                 "add_fastener_length": True,
                                                 "zoom": 1.15,
                                                 "annotate": True,
                                                 "explode": True}}}  # Render options for the shelf

    def generate_shelf_model(self) -> cadscript.Body:
        """
        A shelf for a Ubiquiti USW-Flex
        """
        if self._shelf_model is None:
            builder = ShelfBuilder(
                self.height_in_u, width=self.width_category, depth=119.5, front_type="full"
            )
            builder.cut_opening("<Y", builder.inner_width, offset_y=4)
            builder.make_tray(sides="w-pattern", back="open")
            # add 2 mounting bars on the bottom plate
            sketch = cadscript.make_sketch()
            sketch.add_rect(8, 60, center="X", pos=[(-17.5, 42), (+17.5, 42)])
            builder.get_body().add_extrude("<Z[-3]",
                                           sketch,
                                           -builder.rack_params.tray_bottom_thickness - 2.0)
            builder.get_body().cut_hole("<Z[-3]",
                                        r=3.8 / 2.0,
                                        pos=[(-17.5, 30 + 42), (+17.5, 30 + 42)])
            self._shelf_model = builder.get_body()

        return self._shelf_model


class USWFlexMiniShelf(Shelf):
    """
    Shelf class for a Ubiquiti Flex Mini device.
    """

    def _setup_assembly(self):
        # Device location settings
        self._device_depth_axis = "Y"
        self._device_offset = (0.0, 36.0, 13.0)
        self._device_explode_translation = (0.0, 0.0, 50.0)

        # Gather all the mounting screw locations
        self.hole_locations = [
            (-57.5, 59.0, 14.0),
            (57.5, 59.0, 14.0),
            (-37.5, 73.5, 14.0),
            (37.5, 73.5, 14.0),
        ]

        self._fasteners = [
            Screw(name=None,
                  position=self.hole_locations[0],
                  explode_translation=(0.0, 0.0, 20.0),
                  size="M4-0.7",
                  fastener_type="iso7380_1",
                  axis="-X",
                  length=4),
            Screw(name=None,
                  position=self.hole_locations[1],
                  explode_translation=(0.0, 0.0, 20.0),
                  size="M4-0.7",
                  fastener_type="iso7380_1",
                  axis="X",
                  length=4),
            Screw(name=None,
                  position=self.hole_locations[2],
                  explode_translation=(0.0, 0.0, 20.0),
                  size="M4-0.7",
                  fastener_type="iso7380_1",
                  axis="-Y",
                  length=4),
            Screw(name=None,
                  position=self.hole_locations[3],
                  explode_translation=(0.0, 0.0, 20.0),
                  size="M4-0.7",
                  fastener_type="iso7380_1",
                  axis="-Y",
                  length=4),
        ]
        self._renders = {"assembled":
                             {"order": 1,
                              "render_options": {"color_theme": "default",
                                                 "view": "front-top-right",
                                                 "zoom": 1.0,
                                                 "add_device_offset": False,
                                                 "add_fastener_length": False,
                                                 "annotate": False,
                                                 "explode": False}},
                         "annotated":
                             {"order": 0,
                              "render_options": {"color_theme": "default",
                                                 "view": "back-top-right",
                                                 "add_device_offset": False,
                                                 "add_fastener_length": True,
                                                 "zoom": 1.0,
                                                 "annotate": True,
                                                 "explode": True}}}  # Render options for the shelf

    def generate_shelf_model(self) -> cadscript.Body:
        """
        A shelf for a for Ubiquiti Flex Mini
        """
        if self._shelf_model is None:
            rack_params = RackParameters(tray_side_wall_thickness=3.8)
            builder = ShelfBuilder(
                self.height_in_u,
                width=self.width_category,
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
            self._shelf_model = builder.get_body()

        return self._shelf_model


class AnkerShelf(Shelf):
    """
    Shelf class for an Anker PowerPort 5, Anker 360 Charger 60W (a2123), etc
    """

    def __init__(self,
                 device: Device,
                 *,
                 assembly_key: str,
                 position: tuple[float, float, float],
                 color: str,
                 rack_params: RackParameters,
                 internal_width: float = 56,
                 internal_depth: float = 90.8,
                 internal_height: float = 25,
                 front_cutout_width: float = 53):
        super().__init__(device,
                         assembly_key=assembly_key,
                         position=position,
                         color=color,
                         rack_params=rack_params)
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

    def _setup_assembly(self):
        # Device location settings
        self._device_depth_axis = "X"
        self._device_offset = (0.0, self._device.width / 2.0 + 1.5, 8.5)
        self._device_explode_translation = (0.0, 0.0, 40.0)

        self._fasteners = [
            Screw(name=None,
                  position=(-self._device.depth / 2.0 - 7.0,
                            self._device.width / 2.0 + 3.75,
                            self._device.height / 3.0 + 0.25),
                  explode_translation=(0.0, 0.0, 35.0),
                  size="#6-32",
                  fastener_type="asme_b_18.6.3",
                  axis="-X",
                  length=6),
            Screw(name=None,
                  position=(-self._device.depth / 2.0 - 7.0,
                            self._device.width / 2.0 + 45.35,
                            self._device.height / 3.0 + 0.25),
                  explode_translation=(0.0, 0.0, 35.0),
                  size="#6-32",
                  fastener_type="asme_b_18.6.3",
                  axis="-X",
                  length=6),
            Screw(name=None,
                  position=(self._device.depth / 2.0 + 7.0,
                            self._device.width / 2.0 + 3.75,
                            self._device.height / 3.0 + 0.25),
                  explode_translation=(0.0, 0.0, 35.0),
                  size="#6-32",
                  fastener_type="asme_b_18.6.3",
                  axis="X",
                  length=6),
            Screw(name=None,
                  position=(self._device.depth / 2.0 + 7.0,
                            self._device.width / 2.0 + 45.35,
                            self._device.height / 3.0 + 0.25),
                  explode_translation=(0.0, 0.0, 35.0),
                  size="#6-32",
                  fastener_type="asme_b_18.6.3",
                  axis="X",
                  length=6),
        ]
        self._renders = {"assembled":
                             {"order": 1,
                              "render_options": {"color_theme": "default",
                                                 "view": "front-top-right",
                                                 "zoom": 1.15,
                                                 "add_device_offset": False,
                                                 "add_fastener_length": False,
                                                 "annotate": False,
                                                 "explode": False}},
                         "annotated":
                             {"order": 0,
                              "render_options": {"color_theme": "default",
                                                 "view": "back-bottom-right",
                                                 "add_device_offset": False,
                                                 "add_fastener_length": True,
                                                 "zoom": 1.15,
                                                 "annotate": True,
                                                 "explode": True}}}  # Render options for the shelf

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
                self.height_in_u,
                width=self.width_category,
                depth="standard",
                front_type="w-pattern"
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

    def _setup_assembly(self):

        # Device location settings
        self._device_depth_axis = "X"
        self._device_offset = (0.0, self._device.width / 2.0 + 1.5, 8.5)
        self._device_explode_translation = (0.0, 0.0, 30.0)

        self._fasteners = [
            Screw(name=None,
                  position=(-self._device.depth / 2.0 - 2.55,
                            self._device.width - 11.75,
                            8.65),
                  explode_translation=(0.0, 0.0, 20.0),
                  size="#6-32",
                  fastener_type="asme_b_18.6.3",
                  axis="-X",
                  length=6),
            Screw(name=None,
                  position=(-self._device.depth / 2.0 - 2.55,
                            12.75,
                            8.65),
                  explode_translation=(0.0, 0.0, 20.0),
                  size="#6-32",
                  fastener_type="asme_b_18.6.3",
                  axis="-X",
                  length=6),
            Screw(name=None,
                  position=(self._device.depth / 2.0 + 2.55,
                            self._device.width - 11.75,
                            8.65),
                  explode_translation=(0.0, 0.0, 20.0),
                  size="#6-32",
                  fastener_type="asme_b_18.6.3",
                  axis="X",
                  length=6),
            Screw(name=None,
                  position=(self._device.depth / 2.0 + 2.55,
                            12.75,
                            8.65),
                  explode_translation=(0.0, 0.0, 20.0),
                  size="#6-32",
                  fastener_type="asme_b_18.6.3",
                  axis="X",
                  length=6),
        ]
        self._renders = {"assembled":
                             {"order": 1,
                              "render_options": {"color_theme": "default",
                                                 "view": "front-top-right",
                                                 "zoom": 1.15,
                                                 "add_device_offset": False,
                                                 "add_fastener_length": False,
                                                 "annotate": False,
                                                 "explode": False}},
                         "annotated":
                             {"order": 0,
                              "render_options": {"color_theme": "default",
                                                 "view": "back-bottom-right",
                                                 "add_device_offset": False,
                                                 "add_fastener_length": True,
                                                 "zoom": 1.15,
                                                 "annotate": True,
                                                 "explode": True}}}  # Renders for the shelf

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
    # pylint: disable=too-many-instance-attributes

    variants = {
        "Raspberry_Pi_4B": {"description": "A shelf for a Raspberry Pi 4B", "step_path": "N/A"},
        "Raspberry_Pi_5": {"description": "A shelf for a Raspberry Pi 5", "step_path": "N/A"},
    }

    def _setup_assembly(self):

        # Screw hole parameters
        self.screw_dist_x = 49
        self.screw_dist_y = 58
        self.dist_to_front = 23.5
        self.offset_x = -13

        self._device_depth_axis = "Y"
        self._device_offset = (11.5, 42.5, 6.2)
        self._device_explode_translation = (0.0, 0.0, 25.0)
        # Gather all the mounting screw locations
        self.hole_locations = [
            (self.offset_x, self.dist_to_front),
            (self.offset_x + self.screw_dist_x, self.dist_to_front),
            (self.offset_x, self.dist_to_front + self.screw_dist_y),
            (self.offset_x + self.screw_dist_x, self.dist_to_front + self.screw_dist_y),
        ]

        self._fasteners = [
            Screw(name=None,
                  position=self.hole_locations[0] + (7.0,),
                  explode_translation=(0.0, 0.0, 45.0),
                  size="M3-0.5",
                  fastener_type="iso7380_1",
                  axis="Z",
                  length=6),
            Screw(name=None,
                  position=self.hole_locations[1] + (7.0,),
                  explode_translation=(0.0, 0.0, 45.0),
                  size="M3-0.5",
                  fastener_type="iso7380_1",
                  axis="Z",
                  length=6),
            Screw(name=None,
                  position=self.hole_locations[2] + (7.0,),
                  explode_translation=(0.0, 0.0, 45.0),
                  size="M3-0.5",
                  fastener_type="iso7380_1",
                  axis="Z",
                  length=6),
            Screw(name=None,
                  position=self.hole_locations[3] + (7.0,),
                  explode_translation=(0.0, 0.0, 45.0),
                  size="M3-0.5",
                  fastener_type="iso7380_1",
                  axis="Z",
                  length=6)
        ]
        self._renders = {"assembled":
                             {"order": 1,
                              "render_options": {"color_theme": "default",
                                                 "view": "back-top-right",
                                                 "add_device_offset": False,
                                                 "add_fastener_length": False,
                                                 "zoom": 1.25,
                                                 "annotate": False,
                                                 "explode": False}},
                         "annotated":
                             {"order": 0,
                              "render_options": {"color_theme": "default",
                                                 "view": "back-top-right",
                                                 "add_device_offset": False,
                                                 "add_fastener_length": True,
                                                 "zoom": 1.25,
                                                 "annotate": True,
                                                 "explode": True}}}  # Renders for the shelf

    def generate_shelf_model(self):
        """
        Generates the shelf model only.
        """

        if self._shelf_model is None:
            builder = ShelfBuilder(self.height_in_u,
                                   width=self.width_category,
                                   depth=111,
                                   front_type="full")
            builder.cut_opening("<Y", (-15, 39.5), size_y=(6, 25))
            builder.cut_opening("<Y", (-41.5, -25.5), size_y=(6, 22))
            builder.make_tray(sides="ramp", back="open")
            for x, y in self.hole_locations:
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
SHELF_TYPES = {
    "generic": (Shelf, {}),
    "stuff": (StuffShelf, {}),
    "stuff-thin": (StuffShelf, {"thin": True}),
    "nuc": (NUCShelf, {}),
    "flex": (USWFlexShelf, {}),
    "usw-flex": (USWFlexShelf, {}),
    "usw-flex-mini": (USWFlexMiniShelf, {}),
    "flexmini": (USWFlexMiniShelf, {}),
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
    "raspi": (RaspberryPiShelf, {})
}
