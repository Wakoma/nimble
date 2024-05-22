"""
This components module contains classes for holding the information for components
in a nimble rack.

`MechanicalComponent` is a base class and can also be used for generic components 
    that have no source code
`GeneratedMechanicalComponent` is a child class of `MechanicalComponent`, it contains
    all the information for exsource to generate the CAD models for this component
`AssembledComponent` is a class that holds very basic assembly information for a given
   `MechanicalComponent` 
"""
import os
from copy import copy, deepcopy
import yaml
from nimble_orchestration.device import Device

class MechanicalComponent:
    """
    This is a generic class for any mechanical component. If it is a generic
    component rather than a generated one then use this class, for generated
    components use the child-class GeneratedMechanicalComponent
    """

    def __init__(self, key: str, name: str, description:str, output_files: list) -> None:
        self._key = key
        self._name = name
        self._description = description
        self._output_files = output_files

    @property
    def key(self):
        """Return the unique key identifying the component"""
        return self._key

    @property
    def name(self):
        """Return the human readable name of the component"""
        return self._name

    @property
    def description(self):
        """Return the description of the component"""
        return self._description

    @property
    def output_files(self):
        """Return a copy of the list of output CAD files that represent the component"""
        return copy(self._output_files)

    @property
    def step_representation(self):
        """
        Return the path to the STEP file that represents this part. Return None
        if not defined
        """
        for output_file in self.output_files:
            if output_file.lower().endswith(('stp','step')):
                return output_file
        return None

    @property
    def stl_representation(self):
        """
        Return the path to the STL file that represents this part. Return None
        if not defined.
        """
        for output_file in self.output_files:
            if output_file.lower().endswith('stl'):
                return output_file
        return None

class GeneratedMechanicalComponent(MechanicalComponent):

    """
    This is a class for a mechanical component that needs to be generated from
    source files.
    """

    def __init__(
        self,
        key: str,
        name: str,
        description: str,
        output_files: list,
        source_files: list,
        parameters: dict,
        application: str
    ) -> None:

        super().__init__(key, name, description, output_files)
        self._source_files = source_files
        self._parameters = parameters
        self._application = application

    def __eq__(self, other):
        if isinstance(other, str):
            return self.key==str
        if isinstance(other, GeneratedMechanicalComponent):
            return self.as_exsource_dict == other.as_exsource_dict
        return NotImplemented

    @property
    def source_files(self):
        """Return a copy of the list of the input CAD files that represent the component"""
        return copy(self._source_files)

    @property
    def parameters(self):
        """Return the parameters associated with generating this mechancial component"""
        return deepcopy(self._parameters)

    @property
    def application(self):
        """Return the name of the application used to process the input CAD files"""
        return self._application

    @property
    def as_exsource_dict(self):
        """Return this object as a dictionary of the part information for exsource"""
        return {
            "key": self.key,
            "name": self.name,
            "description": self.description,
            "output_files": self.output_files,
            "source_files": self.source_files,
            "parameters": self.parameters,
            "application": self.application
        }

class AssembledComponent:
    """
    A class for an assembled component. This includes its position in the model.
    An assembled components cannot yet be nested to create true assemblies
    """

    def __init__(self,
                 key: str,
                 component: MechanicalComponent,
                 position: tuple,
                 step: int,
                 color: tuple | str = None):
        self._key = key
        self._component = component
        self._position = position
        self._step = step
        self._color = color

    @property
    def name(self):
        """
        Return the name of the assembled component. This is the same name as the
        component that is to be assembled.
        """
        return self._component.name

    @property
    def stl_representation(self):
        """
        Return the path to the STL file that represents this part. Return None
        if not defined.
        Note this is the STL in the original poisition not in the assembled position.
        """
        return self._component.stl_representation

    @property
    def key(self):
        """
        A unique key to identify the assembled component.
        """
        return self._key

    @property
    def component(self):
        """
        Return the Object describing the component that is being assembled
        This is either a MechanicalComponent object or a child object such as
        GeneratedMechanicalComponent.
        """
        return self._component

    @property
    def position(self):
        """
        The position at which the component is assembled
        """
        return self._position

    @property
    def step(self):
        """
        The assembly step in which this component is assembled.
        """
        return self._step

    @property
    def color(self):
        """
        The color of this component.
        """
        return self._color


class Shelf:
    """
    A class for all the orchestration information relating to a shelf
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
        This is an AssembledComponent
        """
        return self._assembled_shelf

    @property
    def device(self):
        """
        Return the Device object for the networking component that sits on this shelf
        """
        return self._device

    @property
    def md(self):
        """
        Return the markdown (BuildUp) for the GitBuilding page for assembling this shelf
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
