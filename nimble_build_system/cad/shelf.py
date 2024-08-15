import cadquery as cq
from nimble_build_system.cad.device_placeholder import generate_placeholder
from nimble_build_system.cad.shelf_builder import ShelfBuilder
from cadorchestrator.components import AssembledComponent
from nimble_build_system.orchestration.device import Device
import os
import yaml

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
    _assembled_shelf = None
    _unit_width = 6  # 6 or 10 inch rack

    def __init__(self,
                 assembled_shelf: AssembledComponent,
                 device: Device):
        self._assembled_shelf = assembled_shelf
        self._device = device


    @property
    def name(self):
        """
        Return the name of the shelf. This is the same name as the
        component.
        """
        return self.assembled_shelf.name


    @property
    def device(self):
        """
        Return the Device object for the networking component that sits on this shelf.
        """
        return self._device


    @property
    def assembled_shelf(self):
        """
        Return the Object describing the assembled shelf (currently this in an empty
        shelf in the correct location on the rack).
        This is an AssembledComponent.
        """
        return self._assembled_shelf


    def generate_device_model(self):
        """
        Generates the device model only.
        """
        # Generate the placeholder device so that it can be used in the assembly step
        device = generate_placeholder(self.name, self._device.width, self._device.depth, self._device.height)
        return device


    def generate_shelf_model(self):
        """
        Generates the shelf model only.
        """
        pass


    def generate_shelf_stl(self, shelf_model=None):
        """
        Generates the STL file for the shelf.
        """
        stl_path = os.path.join("..", "build", self.name+".stl")

        cq.exporters.export(shelf_model, stl_path)

        return stl_path


    def generate_assembly_step(self, shelf_model=None, device_model=None, with_fasteners=True, exploded=False, annotated=False):
        """
        Generates an assembly showing the assembly step between a device
        and a shelf, generated solely based on the device ID.
        """
        pass


    def get_render(self, assy, camera_pos, format="png"):
        """
        Generates a render of the assembly.
        """

        # TODO - Use the PNG functionality in CadQuery to generate a PNG render
        # TODO - Maybe also need other formats such as glTF

        pass


    def generate_docs(self):
        """
        Return the markdown (BuildUp) for the GitBuilding page for assembling this shelf.
        """

        # Allows us to generate the model only when needed
        shelf_model = self.generate_shelf_model()

        # Generate the STL file for the shelf and save the path to use it in the docs
        stl_representation = self.generate_shelf_stl(shelf_model)

        meta_data = {
            "Tag": "shelf",
            "Make": {
                self.name: {
                    "template": "printing.md",
                    "stl-file": "../build/"+stl_representation,
                    "stlname": os.path.split(stl_representation)[1],
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


class RaspberryPiShelf(Shelf):
    """
    A shelf for Raspberry Pi models.
    """
    variants = {
        "Raspberry_Pi_4B": {"description": "A shelf for a Raspberry Pi 4B", "step_path": "N/A"},
        "Raspberry_Pi_5": {"description": "A shelf for a Raspberry Pi 5", "step_path": "N/A"},
    }


    def __init__(self,
                 assembled_shelf: AssembledComponent,
                 device: Device) -> None:
        super().__init__(assembled_shelf, device)


    def generate_shelf_model(self):
        """
        Generates the shelf model only.
        """
        screw_dist_x = 49
        screw_dist_y = 58
        dist_to_front = 23.5
        offset_x = -13
        builder = ShelfBuilder(self._device.height_in_u, width="standard", depth=111, front_type="full")
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
                x_pos=x, y_pos=y, hole_type="M3-tightfit", base_thickness=5.5, base_diameter=7
            )

        return builder.get_body().cq()


    def generate_assembly_step(self, shelf_model=None, device_model=None, with_fasteners=True, exploded=False, annotated=False):
        """
        Generates an assembly showing the assembly step between a device
        and a shelf, optionally with fasteners.
        """

        # Generate the assembly
        assy = cq.Assembly()
        assy.add(shelf_model, name="shelf", color=cq.Color(0.996, 0.867, 0.0, 1.0))
        assy.add(device_model, name="device", color=cq.Color(0.565, 0.698, 0.278, 1.0))

        return assy
