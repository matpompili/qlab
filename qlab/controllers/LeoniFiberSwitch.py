import visa

class LeoniFiberSwitch:
    """An interface to the Leoni FiberSwitch© series.
    
    Args:
        address (int): The USB address as seen by VISA. If the full address is
            `ASRL42::INSTR`, then `42` should be provided.
        model (int): The number of output channels of the FiberSwitch©.
        dark (int, optional): The number of the channel that will be considered as `dark`.
        
    Note:
        Remember to delete the object when it is not needed anymore, otherwise the 
        USB link will remain busy:
        `del myswitcher`
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
        
    def __del__(self):
        self._link.close()

    def _read_channel(self):
        self._channel = int(self._link.query('ch?'))
        
    @property
    def channel(self):
        return self._channel
    
    @channel.setter
    def channel(self, channel):
        assert channel-1 in range(self._model), "Channel is out of range."
        self._link.write('ch%d' % channel)
        self._channel = int(self._link.query('ch?'))
        assert self._channel == channel, "Something wrong happend, couldn't set the channel."
            
    @property
    def dark(self):
        return self._dark
    
    @dark.setter
    def dark(self, channel):
        assert channel-1 in range(self._model), "Dark channel is out of range."
        self._dark = channel
        
    def go_dark(self):
        if self.dark is not None:
            self.channel = self.dark