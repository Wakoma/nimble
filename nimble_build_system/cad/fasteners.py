"""
Holds fastener classes containing the information needed to generate CAD models of fasteners.
"""

# pylint: disable=R0917

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
        direction_axis:str="-Z"
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
        length:float=6.0
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
            direction_axis=axis
        )

    @property
    def length(self):
        """
        Getter for the length of the screw.
        """
        return self._length


class Ziptie(Fastener):
    """
    Ziptie fastener, that shows the straight, ununsed condition only.
    """
    #pylint: disable=R0913

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
                 length:float):

        self._length = length
        self._width = float(size)

        super().__init__(name,
                         position=position,
                         explode_translation=explode_translation,
                         size=size,
                         fastener_type=fastener_type,
                         direction_axis=axis)


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
