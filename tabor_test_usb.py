from time import sleep
import pywinusb.hid as hid

# Tabor Electronics USB Info for Lucid Devices Models
teVendorId  = 0x168C
teLucidDesktopId  = 0x6002  # Use this for Lucid Desktop - 6GHz
teLucidPortableId = 0x6081  # Use this for Lucid Portable - 6GHz + 1 Channel
teLucidBenchtopId = 0x1202  # Use this for Lucid Benchtop - 12GHz + 2 Channels

BUFFER_SIZE = 256

# Read data 
def readData(data):
    strData = ''.join([str(elem) for i, elem in enumerate(data)])
    if len(data) == 0:
        print("Data is empty")
    elif strData and not strData.isspace() and strData.isprintable():
        for c in data:
            if c != 0:
                print(chr(c), end = "")
    return None

# Send a SCPI command
def send_scpi_cmd(device, scpi_cmd):
    if not device:
        print ("No device provided")
        return

    device.open()
    buffer=[0x00]*BUFFER_SIZE #USB packet size
    sendData = bytearray(scpi_cmd, 'utf-8')
    sendData_len = len(scpi_cmd)

    for  i in range(0, sendData_len):
        buffer[i+3] = sendData[i]

    device.send_output_report(buffer)
    sleep(0.1)
    device.set_raw_data_handler(readData)
    device.close()

def initialize_device(lucid_device): 
    send_scpi_cmd(lucid_device, '*RST\n') # reset the tabor first
    send_scpi_cmd(lucid_device, ':INST 1\n') # select the channel
    send_scpi_cmd(lucid_device, ':INST:ACT 1\n')  # don't know what this command do

def get_identity(lucid_device):
    print('Identification\n')
    send_scpi_cmd(lucid_device, '*IDN?\n')

def set_output(seconds):
    send_scpi_cmd(lucid_device, ':OUTPut ON\n')
    sleep(seconds)
    send_scpi_cmd(lucid_device, ':OUTPut OFF\n')

def set_frequency(lucid_device):
    freq=int(input('Freqency (in Hz)='))
    pow=int(input('Power(in dBm)='))
    send_scpi_cmd(lucid_device, 'FREQuency {}\n'.format(freq))
    send_scpi_cmd(lucid_device, 'POWer {}\n'.format(pow))
    set_output(10)
    print("Freq: ")
    send_scpi_cmd(lucid_device, '*FREQuency?\n')
    print("\nPower: ")
    send_scpi_cmd(lucid_device, '*POWer?\n')
    

def sweep_freq(lucid_device):
    start = int(input("Enter start Freq(in Hz, not less than 100Khz): "))
    steps = int(input("Enter desired steps: "))
    stop = int(input("Enter stop Freq(Hz): "))
    time = float(input("Enter time (sec): "))
    send_scpi_cmd(lucid_device,'FRSWeep:STARt {}\n '.format(start)) # now taking value below 100000
    send_scpi_cmd(lucid_device,'FRSWeep:STEPs {}'.format(steps))
    send_scpi_cmd(lucid_device,'FRSWeep:STOP {}\n '.format(stop))
    send_scpi_cmd(lucid_device,'FRSWeep:TIME {}\n'.format(time))
    send_scpi_cmd(lucid_device,'FRSWeep:DIR 1')

    send_scpi_cmd(lucid_device,'FRSWeep 1')
    set_output(10)
    send_scpi_cmd(lucid_device,'FRSWeep 0')
    print("Sweep Done\n")
    send_scpi_cmd(lucid_device,'FRSWeep:STARt?\n')
    print("\n")
    send_scpi_cmd(lucid_device,'FRSWeep:STOP?')
    print("\n")
    send_scpi_cmd(lucid_device,'FRSWeep:STEPs?')
    print("\n")
    send_scpi_cmd(lucid_device,'FRSWeep:TIME?')
    print("\n")
    send_scpi_cmd(lucid_device,'FRSWeep:DIRection?')
    print("\n")
    

def list_mode(lucid_device, freq_list):
    send_scpi_cmd(lucid_device, 'LIST:DELete:ALL')
    print("\n Previous list deleted\n")
    for i in range(len(freq_list[0])):
        send_scpi_cmd(lucid_device, 'LIST:DEFine {},{},{},{},{},{}'.format(freq_list[0][i], freq_list[1][i],freq_list[2][i], \
                                                                        freq_list[3][i], freq_list[4][i], freq_list[5][i]))

        sleep(1)
    print("\n List loaded \n")

    send_scpi_cmd(lucid_device,'LIST ON')
    set_output(20)
    send_scpi_cmd(lucid_device,'LIST OFF')
    print("List Done\n")
    send_scpi_cmd(lucid_device,':LIST:DEF?')




# main code 
print("\n")
lucid_device = hid.HidDeviceFilter(vendor_id=teVendorId, product_id=teLucidBenchtopId).get_devices()[0]
if not lucid_device:
    print("No device found. Set proper product_id !!")
    exit
else:
    initialize_device(lucid_device)

    #get_identity(lucid_device)


    #set_frequency(lucid_device)

    #sweep_freq(lucid_device)

    set_list=[[1,2,3,4],[100e3,200e3,50e3,400e3],[0,0,0,0],[0,0,0,1],[0,0,0,0],\
                  [1e9,2e9,3e9,4e9]]
    
    list_mode(lucid_device, set_list)
