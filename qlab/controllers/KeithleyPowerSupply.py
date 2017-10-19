import visa
import numpy as np

class KeithleyPowerSupply:
    """An interface to the Keithley 2231A DC Power Supply.

    Args:
        address (int): The USB address as seen by VISA. If the full address is
            `ASRL42::INSTR`, then `42` should be provided.
        settings (int, optional): The settings that will be recalled once the
            connection is established.

    Raises:
        AssertionError: If the connection fails raises an exception.

    Examples:
        Connect to a Keithley 2231A at address `ASRL42::INSTR`

        >>> my_pwr_supply = KeithleyPowerSupply(address=42)

        Let's set all three voltages to 1.23 V

        >>> my_pwr_supply.voltages = [1.23, 1.23, 1.23]

        Finally, let's enable the outputs

        >>> my_pwr_supply.output = True

    Note:
        Remember to delete the object when it is not needed anymore, otherwise the
        USB link will remain busy:

        >>> del my_pwr_supply
    """

    def __init__(self, address, settings=1):
        # Check whether the resource is visible to PyVISA
        address_string = "ASRL%d::INSTR" % address
        assert address_string in visa.ResourceManager().list_resources(), \
            "Address not available."

        self._link =  visa.ResourceManager().open_resource(address_string)

        self._link.write('*RST;\n*CLS')
        self._alive = True
        try:
            if "Keithley instruments, 2231A" not in self._link.query('*IDN?'):
                self._alive = False
        except:
            self._alive = False
        if not self._alive:
            self._link.close()
            raise AssertionError("Keithley 2231A not found.")

        self._link.write('*RST;\n*CLS;\nsystem:remote\n*RCL %d' % settings)
        self._link.write('apply:voltage 0,0,0');
        self._link.write('output:state 1');

        self._voltages = np.array([0,0,0])
        self._output = True

    def __del__(self):
        self._link.close()

    @property
    def voltages(self):
        return self._voltages

    @voltages.setter
    def voltages(self, volts):
        volts = np.array(volts)
        assert volts.size == 3, "Too many or too few voltages provided."
        self._link.write('apply:voltage %f,%f,%f' % tuple(np.around(volts, 3)))
        self._voltages = np.around(volts, 3)

    @property
    def output(self):
        return self._output

    @output.setter
    def output(self, status):
        assert type(status) is bool, "Only True and False are accepted."
        self._link.write('output:state %d' % int(status))
        self._output = status
