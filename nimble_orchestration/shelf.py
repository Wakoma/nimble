import os
import yaml
from cadorchestrator.components import AssembledComponent
from nimble_orchestration.device import Device

class Shelf:
    """
    A class for all the orchestration information relating to a shelf.
    """
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
    def stl_representation(self):
        """
        Return the path to the STL file that represents this shelf. Return None
        if not defined.
        Note this is the STL in the original poisition not in the assembled position.
        """
        return self.assembled_shelf.stl_representation

    @property
    def assembled_shelf(self):
        """
        Return the Object describing the assembled shelf (currently this in an empty
        shelf in the correct location on the rack).
        This is an AssembledComponent.
        """
        return self._assembled_shelf

    @property
    def device(self):
        """
        Return the Device object for the networking component that sits on this shelf.
        """
        return self._device

    @property
    def md(self):
        """
        Return the markdown (BuildUp) for the GitBuilding page for assembling this shelf.
        """
        meta_data = {
            "Tag": "shelf",
            "Make": {
                self.name: {
                    "template": "printing.md",
                    "stl-file": "../build/"+self.stl_representation,
                    "stlname": os.path.split(self.stl_representation)[1],
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
