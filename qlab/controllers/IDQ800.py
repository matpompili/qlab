from ctypes import c_long, create_string_buffer, POINTER, byref, c_int, c_uint, WinDLL
from time import sleep
from operator import itemgetter
from os import path

class IDQ800:
    """An interface to the ID Quantique ID800 TDC.

    Args:
        n_boxes (int): The number of ID800 connected to the computer.
        dll_path (str, optional): The absolute path to `tdcbase.dll`.
            Default: search in the package directory.

    Raises:
        AssertionError: If ``n_boxes`` ID800s are not available

    Examples:
        Connect to 3 ID800s

        >>> my_idq = IDQ800(n_boxes = 3)

        Let's run an acquisition for 5.3 seconds

        >>> my_idq.run_acquisition(acq_time = 5.3)

        Now three files have been created:
        - `timestamps1.bin`
        - `timestamps2.bin`
        - `timestamps3.bin`

        The ID800s are numbered according to their serial numbers,
        in increasing order. So `timestamps1.bin` is relative to the lowest S/N.

    Note:
        Remeber to  close the connection to the ID800s with

        >>> del my_idq
    """

    def __init__(self, n_boxes, dll_path = None):
        self._n_boxes = n_boxes

        if dll_path is not None:
            self._dll_path = dll_path
        else:
            self._dll_path = path.join(path.dirname(__file__), 'tdcbase.dll')
        self._dll_lib = WinDLL(self._dll_path)

        # Discover
        discovered_boxes = c_long(0)
        self._dll_lib.TDC_discover(byref(discovered_boxes))

        # Check right number
        assert discovered_boxes.value == self._n_boxes, \
            'We expected exactly %d boxes, but %d are available.' % (self._n_boxes, discovered_boxes.value)

        # Read serials
        self._serials_dict = {}
        for box_id in range(self._n_boxes):
           # We are only intersted in the serial
            serial = create_string_buffer(10)
            null_ptr = POINTER(c_int)()
            self._dll_lib.TDC_getDeviceInfo(c_uint(box_id), null_ptr , null_ptr, serial, null_ptr)
            # Extract the serial from the raw data returned
            self._serials_dict.update({box_id : serial.raw[-5:-1].decode('utf-8')})

        # Order boxes by serial
        self._boxes = sorted(self._serials_dict.items(), key=itemgetter(1))

    def __del__(self):
        self._dll_lib.TDC_deInit()

    def run_acquisition(self, acq_time = 1.0, file_prefix="timestamps", file_suffix=".bin"):
        done = False
        #IDQ dll randomly gives an access violation error on the second TDC_writeTimestamps(). We keep trying until it works.
        while (not done):
            try:
                done = True
                #Start all the boxes
                for i, box in enumerate(self._boxes):
                    self._dll_lib.TDC_connect(c_int(box[0]))
                    self._dll_lib.TDC_writeTimestamps(str.encode(file_prefix + str(i+1) + file_suffix), c_int(1))

                #Wait time seconds
                sleep(acq_time)

                #Stop all the boxes
                for i, box in enumerate(self._boxes):
                    self._dll_lib.TDC_connect(c_int(box[0]))
                    self._dll_lib.TDC_writeTimestamps()

            except:
                done = False
                print("Got error from IDQ, retrying.")
