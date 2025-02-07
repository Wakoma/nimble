"""
Holds fastener classes containing the information needed to generate CAD models of fasteners.
"""

import cadquery as cq
from cq_warehouse.fastener import ButtonHeadScrew, CounterSunkScrew, PanHeadScrew

class Fastener: # pylint: disable=too-many-instance-attributes
    """
    Class that defines a generic fastener that can be used in the assembly of a device and/or rack.
    """
    _name = None
    _position = (0.0, 0.0, 0.0)
    _explode_translation = (0.0, 0.0, 0.0)
    _size = "M3-0.5"
    _fastener_type = "iso7380_1"
    _direction_axis = "-Z"
    _rotation = ((0, 0, 1), 0)
    _face_selector = ">X"
    _fastener_model = None

    def __init__(
        self,
        name:str,
        *,
        position:tuple[float, float, float]=(0.0, 0.0, 0.0),
        explode_translation:tuple[float, float, float]=(0.0, 0.0, 0.0),
        size:str="M3-0.5",
        fastener_type:str="iso7380_1",
        direction_axis:str="-Z",
        human_name:str=""
    ):
        """
        Generic fastener constructor that sets common attributes for all faster types.
        """
        self._name = name
        self._position = position
        self._explode_translation = explode_translation
        self._size = size
        self._fastener_type = fastener_type
        self._direction_axis = direction_axis
        if human_name == "":
            self._human_name = self._gen_human_name
        else:
            self._human_name=human_name

    @property
    def name(self):
        """
        Getter for the name of the fastener.
        """
        return self._name

    @name.setter
    def name(self, name):
        """
        Setter for the name of the fastener.
        """
        self._name = name

    @property
    def human_name(self):
        """
        Getter for the human name of the fastener. This is how it
        will appear in GitBuilding.
        """
        return self._human_name

    @property
    def position(self):
        """
        Getter for the position of the fastener.
        """
        return self._position

    @property
    def explode_translation(self):
        """
        Getter for the explosion translation of the fastener.
        """
        return self._explode_translation

    @property
    def size(self):
        """
        Getter for the size of the fastener.
        """
        return self._size

    @property
    def fastener_type(self):
        """
        Getter for the fastener_type of the fastener.
        """
        return self._fastener_type

    @property
    def direction_axis(self):
        """
        Getter for the direction axis of the fastener.
        """
        return self._direction_axis

    @property
    def rotation(self):
        """
        Getter for the rotation of the fastener.
        """
        return self._rotation

    @rotation.setter
    def rotation(self, rotation):
        """
        Setter for the rotation of the fastener.
        """
        self._rotation = rotation

    @property
    def face_selector(self):
        """
        Getter for the face selector of the fastener.
        """
        return self._face_selector

    @face_selector.setter
    def face_selector(self, face_selector):
        """
        Setter for the face selector of the fastener.
        """
        self._face_selector = face_selector

    @property
    def fastener_model(self):
        """
        Getter for the fastener model of the fastener.
        """
        return self._fastener_model


    def _gen_human_name(self):
        return f"{self.size} {self.fastener_type}"


class Screw(Fastener):
    """
    Specific type of fastener that adds screw-specific parameters like length.
    """
    _length = 6  # mm

    def __init__(
        self,
        name:str,
        *,
        position:tuple[float, float, float]=(0.0, 0.0, 0.0),
        explode_translation:tuple[float, float, float]=(0.0, 0.0, 0.0),
        size:str="M3-0.5",
        fastener_type:str="iso7380_1",
        axis:str="-Z",
        length:float=6.0,
        human_name:str=""
    ):
        """
        Screw constructor that additionally sets the length of the screw.
        """

        self._length = length

        # Handle rotation based on the direction axis
        if axis == "X":
            self._rotation = ((0, 1, 0), 90)
            self._face_selector = ">X"
        elif axis == "-X":
            self._rotation = ((0, 1, 0), -90)
            self._face_selector = ">X"
        elif axis == "Y":
            self._rotation = ((1, 0, 0), 90)
            self._face_selector = "<Y"
        elif axis == "-Y":
            self._rotation = ((1, 0, 0), -90)
            self._face_selector = ">Y"
        elif axis == "Z":
            self._rotation = ((0, 1, 0), 0)
            self._face_selector = "<Z"
        elif axis == "-Z":
            self._rotation = ((0, 1, 0), 180)
            self._face_selector = ">Z"

        super().__init__(
            name,
            position=position,
            explode_translation=explode_translation,
            size=size,
            fastener_type=fastener_type,
            direction_axis=axis,
            human_name=human_name
        )

        # Generate the CadQuery model for this fastener
        if self._fastener_type == "iso10642":
            # Create the counter-sunk screw model
            self._fastener_model = cq.Workplane(CounterSunkScrew(size=self._size,
                                        fastener_type=self._fastener_type,
                                        length=self._length,
                                        simple=True).cq_object)
        elif self._fastener_type == "asme_b_18.6.3":
            # Create the cheesehead screw model
            self._fastener_model = cq.Workplane(PanHeadScrew(size=self._size,
                                        fastener_type=self._fastener_type,
                                        length=self._length,
                                        simple=True).cq_object)
        elif self._fastener_type == "iso7380_1":
            # Create a button head screw model
            self._fastener_model = cq.Workplane(ButtonHeadScrew(size=self._size,
                                        fastener_type=self._fastener_type,
                                        length=self._length,
                                        simple=True).cq_object)
        else:
            raise ValueError("Unknown screw type.")

        # Make sure assembly lines are present with each fastener
        self._fastener_model.faces(self._face_selector).tag("assembly_line")


    @property
    def length(self):
        """
        Getter for the length of the screw.
        """
        return self._length

    def _gen_human_name(self):
        if self.fastener_type == "iso10642":
            fastener = "Countersunk Screw"
        elif self.fastener_type == "asme_b_18.6.3":
            fastener = "Pan Head Screw"
        elif self.fastener_type == "iso7380_1":
            fastener = "Button Head Screw"
        else:
            fastener = self.fastener_type
        return f"{self._size_str}x{self.length} {fastener}"

    @property
    def _size_str(self):
        reps = {"M1.6-0.35": "M1.6",
                "M2-0.4": "M2",
                "M2.5-0.45": "M2.5",
                "M3-0.5": "M3",
                "M3.5-0.6": "M3.5",
                "M4-0.7": "M4",
                "M5-0.8": "M5",
                "M6-1": "M6",
                "M8-1": "M8-fine",
                "M8-1.25": "M8",
                "M10-1.25": "M10-fine",
                "M10-1.5": "M10"}
        if self.size in reps:
            return reps[self.size]
        return self.size

class Ziptie(Fastener):
    """
    Ziptie fastener, that shows the straight, ununsed condition only.
    """
    #pylint: disable=too-many-arguments

    _thickness = 1.6  # mm
    _width = 4  # mm
    _length = 100  # mm
    _fastener_type = "ziptie"
    _state = "straight"  # can also be "wrapped"
    _wrapped_height = 1.0  # The shelf height in mm, and thus the max opening size of this ziptie
    _wrapped_width = 125.4  # The width of the ziptie when wrapped around the shelf


    def __init__(self,
                 name:str,
                 *,
                 position:tuple[float, float, float]=(0.0, 0.0, 0.0),
                 explode_translation:tuple[float, float, float]=(0.0, 0.0, 0.0),
                 size:str,
                 fastener_type:str,
                 axis:str,
                 length:float,
                 human_name:str="",
                 wrapped_height:float=1.0,
                 wrapped_width:float=125.4,
                 fastener_state="wrapped"):

        self._length = length
        self._width = float(size)
        self._wrapped_height = wrapped_height
        self._wrapped_width = wrapped_width
        self._state = fastener_state

        # Handle the rotation and face selector based on the direction axis
        if axis == "X":
            self._rotation = ((0, 0, 1), -90)
            self._face_selector = ">Z"
        elif axis == "-X":
            self._rotation = ((0, 0, 1), 90)
            self._face_selector = ">Z"
        elif axis == "Y":
            self._rotation = ((0, 0, 1), 0)
            self._face_selector = ">Z"
        elif axis == "-Y":
            self._rotation = ((0, 0, 1), 180)
            self._face_selector = ">Z"
        elif axis == "Z":
            self._rotation = ((1, 0, 0), 0)
            self._face_selector = ">X"
        elif axis == "-Z":
            self._rotation = ((1, 0, 0), 180)
            self._face_selector = ">X"

        super().__init__(name,
                         position=position,
                         explode_translation=explode_translation,
                         size=size,
                         fastener_type=fastener_type,
                         direction_axis=axis,
                         human_name=human_name)

        # Generate the CadQuery model for this fastener
        self.generate_model()


    def generate_model(self):
        """
        Separate method to generate the model so the state (straight vs wrapped) can be changed
        on the fly.
        """

        # Generate the straight CadQuery model for this fastener
        if self._state == "wrapped":
            # Create the outer loop of the zip tie
            sketch  = (cq.Sketch()
                .rect(self._wrapped_width, self.wrapped_height)
                .vertices()
                .fillet(2.0)
            )
            sketch_offset = sketch.copy().wires().offset(self._thickness)

            # Cteate the looped shape of the zip tie
            self._fastener_model = (cq.Workplane("YZ")
                        .workplane(offset=-self._width / 2.0)
                        .move(0.0, self._wrapped_height / 2.0 - 3.0)
                        .placeSketch(sketch_offset)
                        .extrude(self._width))
            self._fastener_model = (self._fastener_model.faces(">X")
                            .workplane(offset=-self._width / 2.0)
                            .move(0.0, self._wrapped_height / 2.0 - 3.0)
                            .placeSketch(sketch)
                            .cutThruAll())
        else:
            # Create the ziptie spine
            self._fastener_model = cq.Workplane().box(self._width,
                                                    self._length,
                                                    self._thickness)

            # Create the ziptie head
            self._fastener_model = (self._fastener_model.faces(">Z")
                                                        .workplane(invert=True)
                                                        .move(0.0, self._length / 2.0)
                                                        .rect(self._width + 2.0, self._width + 2.0)
                                                        .extrude(self._thickness + 3.0))

            # Chamfer the insertion end of the ziptie
            self._fastener_model = (self._fastener_model.faces(">Y")
                                                        .edges(">X and |Z")
                                                        .chamfer(length=self._width / 4.0,
                                                            length2=self._width * 2.0))
            self._fastener_model = (self._fastener_model.faces(">Y")
                                                        .edges("<X and |Z")
                                                        .chamfer(length=self._width / 4.0,
                                                            length2=self._width * 2.0))

            # Add the slot in the head for insertion of the tail
            self._fastener_model = (self._fastener_model.faces(">Z")
                                                        .workplane(invert=True)
                                                        .move(0.0, -(self._length / 2.0))
                                                        .rect(self._width, self._thickness)
                                                        .cutThruAll())

            # Make sure assembly lines are present with each fastener
            self._fastener_model.faces(self._face_selector).tag("assembly_line")


    @property
    def length(self):
        """
        Getter for the length of the screw.
        """
        return self._length


    @property
    def thickness(self):
        """
        Getter for the thickness of the ziptie.
        """
        return self._thickness


    @property
    def width(self):
        """
        Getter for the width of the ziptie.
        """
        return self._width

    @property
    def state(self):
        """
        Getter for the state of the fastener.
        """
        return self._state

    @state.setter
    def state(self, state):
        """
        Setter for the state of the fastener.
        """
        self._state = state

        self.generate_model()


    @property
    def wrapped_height(self):
        """
        Getter for the wrapped height of the fastener in U.
        """
        return self._wrapped_height

    @wrapped_height.setter
    def wrapped_height(self, height):
        """
        Setter for the wrapped height of the fastener in U.
        """
        self._wrapped_height = height

    def _gen_human_name(self):
        return f"ziptie ({self.width}x{self.length}mm)"
