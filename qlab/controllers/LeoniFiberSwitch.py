import visa

__all__ = ['LeoniFiberSwitch']

class LeoniFiberSwitch:
    """An interface to the Leoni FiberSwitch© series.

    Args:
        address (int): The USB address as seen by VISA. If the full address is
            `ASRL42::INSTR`, then `42` should be provided.
        model (int): The number of output channels of the FiberSwitch©.
        dark (int, optional): The number of the channel that will be considered as `dark`.

    Raises:
        AssertionError: If the connection to the FiberSwitch© fails raises an exception.

    Examples:
        Connect to a Leoni FiberSwitch© model 1x8 at address `ASRL42::INSTR`

        >>> my_switcher = LeoniFiberSwitch(address=42, model=8)

        Let's read in which ``channel`` the FiberSwitch© is

        >>> print(my_switcher.channel)
        6

        Let's switch to ``channel`` 3 and check again

        >>> my_switcher.channel = 3
        >>> print(my_switcher.channel)
        3

        Using the ``dark`` channels
        
        >>> my_switcher.channel = 5
        >>> my_switcher.dark = 8
        >>> my_switcher.dark_on()
        True
        >>> print(my_switcher.channel)
        8
        >>> my_switcher.dark_off()
        True
        >>> print(my_switcher.channel)
        5

    Note:
        Remember to delete the object when it is not needed anymore, otherwise the
        USB link will remain busy:

        >>> del my_switcher
    """

    def __init__(self, address, model, dark=None):
        assert model in [4,8], "Model should be either 4 or 8."
        self._model = model

        # Check whether the resource is visible to PyVISA
        address_string = "ASRL%d::INSTR" % address
        assert address_string in visa.ResourceManager().list_resources(), \
            "Address not available."

        # Connect to the given address and check that it is indeed a
        # FiberSwitch© and that the model is correct
        self._link =  visa.ResourceManager().open_resource(address_string)
        self._link.baud_rate = 57600

        self._alive = True
        try:
            if self._link.query('type?') != 'eol 1x%d\r\n' % model:
                self._alive = False
        except:
            self._alive = False
        if not self._alive:
            self._link.close()
            raise AssertionError("FiberSwitch© not found.")

        if dark is not None:
            self.dark = dark
        else:
            self._dark = None

        self._read_channel()
        self._is_dark = False
        self._channel_backup = self._channel

    def __del__(self):
        self._link.close()

    def _read_channel(self):
        self._channel = int(self._link.query('ch?'))

    @property
    def channel(self):
        """The output channel of the FiberSwitch©."""
        return self._channel

    @channel.setter
    def channel(self, channel):
        assert channel-1 in range(self._model), "Channel is out of range."
        self._link.write('ch%d' % channel)
        self._channel = int(self._link.query('ch?'))
        assert self._channel == channel, "Something wrong happend, couldn't set the channel."

    @property
    def dark(self):
        """The channel that is used as a `dead end` of the FiberSwitch©."""
        return self._dark

    @dark.setter
    def dark(self, channel):
        assert channel-1 in range(self._model), "Dark channel is out of range."
        self._dark = channel

    def dark_on(self):
        """Switch to the ``dark`` channel.

        Returns:
            bool: True if it was not in dark state, False otherwise.

        Raises:
            AssertionError: if the ``dark`` channel was not set.
        """
        assert self.dark is not None, "No dark channel was set."
        if self._is_dark is False:
            self._channel_backup = self._channel
            self.channel = self.dark
            return True
        return False


    def dark_off(self):
        """Switch back to the channel that was on before ``dark_on``.

        Returns:
            bool: True if it was not in dark state, False otherwise.

        Raises:
            AssertionError: if the ``dark`` channel was not set.
        """
        assert self.dark is not None, "No dark channel was set."
        if self._is_dark is True:
            self.channel = self._channel_backup
            return True
        return False
