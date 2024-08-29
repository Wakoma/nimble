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

    def __init__(self, name, position, explode_translation, size, fastener_type, direction_axis):
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

    def __init__(self, name, position, explode_translation, size, fastener_type, axis, length):
        """
        Screw constructor that additionally sets the length of the screw.
        """
        # pylint: disable=too-many-arguments

        self._length = length

        super().__init__(name, position, explode_translation, size, fastener_type, axis)

    @property
    def length(self):
        """
        Getter for the length of the screw.
        """
        return self._length
