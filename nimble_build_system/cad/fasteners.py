"""
Holds fastener classes containing the information needed to generate CAD models of fasteners.
"""

class Fastener:
    """
    Class that defines a generic fastener that can be used in the assembly of a device and/or rack.
    """
    _name = None
    _position = (0.0, 0.0, 0.0)
    _explode_translation = (0.0, 0.0, 0.0)
    _size = "M3-0.5"
    _fastener_type = "iso7380_1"
    _direction_axis = "-Z"

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

        super().__init__(
            name,
            position=position,
            explode_translation=explode_translation,
            size=size,
            fastener_type=fastener_type,
            direction_axis=axis,
            human_name=human_name
        )

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


    def __init__(self,
                 name:str,
                 *,
                 position:tuple[float, float, float]=(0.0, 0.0, 0.0),
                 explode_translation:tuple[float, float, float]=(0.0, 0.0, 0.0),
                 size:str,
                 fastener_type:str,
                 axis:str,
                 length:float,
                 human_name:str=""):

        self._length = length
        self._width = float(size)

        super().__init__(name,
                         position=position,
                         explode_translation=explode_translation,
                         size=size,
                         fastener_type=fastener_type,
                         direction_axis=axis,
                         human_name=human_name)


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

    def _gen_human_name(self):
        return f"ziptie ({self.width}x{self.length}mm)"
