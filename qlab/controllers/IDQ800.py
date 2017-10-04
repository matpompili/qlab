from ctypes import WinDLL, c_long, create_string_buffer, POINTER, byref, c_int, c_uint
import time
from operator import itemgetter

class IDQ800:
    """An interface to the ID Quantique ID800 TDC
    """
    
    def __init__(self, n_boxes, dll_path = "C:\\Users\\Utente\\Desktop\\Programmi Python\\userlib\\lib\\tdcbase.dll"):
        self._n_boxes = n_boxes
        self._dll_path = dll_path
        self._dll_lib = WinDLL(dll_path)
        
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
                time.sleep(acq_time)
                
                #Stop all the boxes
                for i, box in enumerate(self._boxes):
                    self._dll_lib.TDC_connect(c_int(box[0]))
                    self._dll_lib.TDC_writeTimestamps()

            except:
                done = False
                print("Got error from IDQ, retrying.")