#!/usr/bin/env python
import time
import serial
import RPi.GPIO as GPIO
from datetime import datetime
import xml.etree.ElementTree as ET
global ser
global res
res = None
ser = None
global mode
mode = 0
remotePin = 14
debug = False

def SetIs480i(value):
    if value:
        Set480i()
    else
        Set240p()

def SetShrinkOn(value):
    if value:
        ShrinkOn()
    else
        ShrinkOff()

def SetAdvancedShrinkOn(value):
    if value:
        AdvancedShrinkOn()
    else
        AdvancedShrinkOff()
        
def Setup():
	global remotePin
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(remotePin, GPIO.IN)
	global ser
	ser = serial.Serial(
	        port='/dev/ttyUSB0', #Replace ttyS0 with ttyAM0 for Pi1,Pi2,Pi0
	        baudrate = 57600, #assuming default
	        parity=serial.PARITY_NONE,
	        stopbits=serial.STOPBITS_ONE,
	        bytesize=serial.EIGHTBITS,
	        timeout=1
	)

# Dictionary to map field names to setter functions
setter_functions = {
    'is480i': SetIs480i,
    'ShrinkH': SetShrinkH,
    'ShrinkV': SetShrinkV,
    'PosH': SetPosH,
    'PosV': SetPosV,
    'ShrinkOn': SetShrinkOn,
    'AdvancedShrinkOn': SetAdvancedShrinkOn,
    'PixelOutX': SetPixelOutX,
    'PixelOutY': SetPixelOutY,
    'PixelOutH': SetPixelOutH,
    'PixelOutV': SetPixelOutV,
    'PixelInX': SetPixelInX,
    'PixelInY': SetPixelInY,
    'PixelInH': SetPixelInH,
    'PixelInV': SetPixelInV,
    'TopH': SetTopH,
    'TopV': SetTopV,
    'BottomH': SetBottomH,
    'BottomV': SetBottomV,
    'ZoomH': SetZoomH,
    'ZoomV': SetZoomV,
    'PanH': SetPanH,
    'PanV': SetPanV,
}

# Function to parse XML and call appropriate setters
def parse_and_set_xml(file_path):
    if not os.path.isfile(file_path):
        print(f"Error: The file '{file_path}' does not exist.")
        return

    # Define the ranges and valid values for each field
    ranges = {
        'is480i': (['false', 'true'], None),
        'ShrinkH': (range(0, 151), None),
        'ShrinkV': (range(0, 151), None),
        'PosH': (range(-255, 256), None),
        'PosV': (range(-255, 256), None),
        'ShrinkOn': (['false', 'true'], None),
        'AdvancedShrinkOn': (['false', 'true'], None),
        'PixelOutX': (range(-255, 256), None),
        'PixelOutY': (range(-255, 256), None),
        'PixelOutH': (range(0, 1921), None),
        'PixelOutV': (range(0, 1081), None),
        'PixelInX': (range(-255, 256), None),
        'PixelInY': (range(-255, 256), None),
        'PixelInH': (range(0, 1921), None),
        'PixelInV': (range(0, 1081), None),
        'TopH': (range(-255, 256), None),
        'TopV': (range(-255, 256), None),
        'BottomH': (range(-255, 256), None),
        'BottomV': (range(-255, 256), None),
        'ZoomH': (range(-255, 256), None),
        'ZoomV': (range(-255, 256), None),
        'PanH': (range(-255, 256), None),
        'PanV': (range(-255, 256), None),
    }
    
    def is_valid(value, valid_range):
        if isinstance(valid_range, list):
            return value in valid_range
        elif isinstance(valid_range, range):
            return value in valid_range
        return False

    try:
        # Parse the XML file
        tree = ET.parse(file_path)
        root = tree.getroot()

        # Iterate through the defined fields
        for field, (valid_range, _) in ranges.items():
            elem = root.find(field)
            if elem is not None:
                value = elem.text.strip()
                if value.lower() in ['false', 'true']:
                    value = value.lower() == 'true'
                else:
                    try:
                        value = int(value)
                    except ValueError:
                        print(f"Invalid value for {field}: {value}")
                        continue
                
                if is_valid(value, valid_range):
                    setter_function = setter_functions.get(field)
                    if setter_function:
                        setter_function(value)
                    else:
                        print(f"No setter function defined for {field}")
                else:
                    print(f"Value {value} for {field} is out of range")
            else:
                print(f"Field {field} not found in XML")
    except ET.ParseError as e:
        print(f"Error parsing XML file: {e}")

#for commands with correct checksum
def WriteBasic(str):
	global ser
	string = str + "\r"
	if debug:
		print("WriteBasic: " + string)
	arr = bytes(string, 'utf-8')
	ser.write(arr)

#for commands too lazy to compute checksum
def Write(str):
	global ser
	string = str + "??\r"
	if debug:
		print("Write: " + string)
	arr = bytes(string, 'utf-8')
	ser.write(arr)

def Read():
	global ser
	x = ser.read(20)
	if debug:
		print("Read:  " + x.decode("utf-8"))
	return x.decode("utf-8") 

#get 2s complement in hex for 6 bytes
def GetNegHex(nVal):
	val = hex((nVal + (1 << 24)) % (1 << 24)).replace("0x","")
	return val

def GetHexValue(nVal):
	base = None
	if nVal < 0:
		base = GetNegHex(nVal)
	else:
		base = hex(int(nVal)).replace("0x","")
		while (len(base) < 6):
			base = "0" + base
	return base

def SendCommandBasic(str):
	global res
	WriteBasic(str)
	res = Read()
	if len(res) > 2:
		return True
	return False

def SendCommand(str):
	global res
	Write(str)
	res = Read()
	if len(res) > 2:
		return True
	return False

def SetBGColor(y, u, v):
	base = GetHexValue(y)
	cmd = "F040041013B" + base
	SendCommand(cmd)
	base = GetHexValue(u)
	cmd = "F040041013C" + base
	SendCommand(cmd)
	base = GetHexValue(v)
	cmd = "F040041013D" + base
	return SendCommand(cmd)

def ShrinkOn():
	return SendCommand("F040041018E000001")

def ShrinkOff():
	return SendCommand("F040041018E000000")

def PixelShrinkOn():
	return SendCommand("F0400410102000002")

def SimpleShrinkOn():
	return SendCommand("F0400410102000000")

def AdvancedShrinkOn():
	return SendCommand("F0400410102000001")

def SetShrinkH(nVal):
	base = GetHexValue(nVal)
	cmd = "F0400410104" + base
	return SendCommand(cmd)

def SetShrinkV(nVal):
	base = GetHexValue(nVal)
	cmd = "F0400410106" + base
	return SendCommand(cmd)

def Set480i():
	return SendCommand("F0400410083000072")

def Set240p():
	return SendCommand("F0400410083000009")

def SetPixelOutX(nVal):
	base = GetHexValue(nVal)
	cmd = "F040041021F" + base
	return SendCommand(cmd)

def SetPixelOutY(nVal):
	base = GetHexValue(nVal)
	cmd = "F0400410221" + base
	return SendCommand(cmd)

def SetPixelOutH(nVal):
	base = GetHexValue(nVal)
	cmd = "F0400410220" + base
	return SendCommand(cmd)

def SetPixelOutV(nVal):
	base = GetHexValue(nVal)
	cmd = "F0400410222" + base
	return SendCommand(cmd)

def SetPixelInX(nVal):
	base = GetHexValue(nVal)
	cmd = "F040041021B" + base
	return SendCommand(cmd)

def SetPixelInY(nVal):
	base = GetHexValue(nVal)
	cmd = "F040041021D" + base
	return SendCommand(cmd)

def SetPixelInH(nVal):
	base = GetHexValue(nVal)
	cmd = "F040041021C" + base
	return SendCommand(cmd)

def SetPixelInV(nVal):
	base = GetHexValue(nVal)
	cmd = "F040041021E" + base
	return SendCommand(cmd)

def SetPosH(nVal):
	base = GetHexValue(nVal)
	cmd = "F04004100DA" + base
	return SendCommand(cmd)

def SetPosV(nVal):
	base = GetHexValue(nVal)
	cmd = "F04004100DB" + base
	return SendCommand(cmd)

def SetPanH(nVal):
	base = GetHexValue(nVal)
	cmd = "F040041009F" + base
	return SendCommand(cmd)

def SetPanV(nVal):
	base = GetHexValue(nVal)
	cmd = "F04004100A0" + base
	return SendCommand(cmd)

def SetCropH(nVal):
	base = GetHexValue(nVal)
	cmd = "F0400410223" + base
	return SendCommand(cmd)

def SetCropV(nVal):
	base = GetHexValue(nVal)
	cmd = "F0400410224" + base
	return SendCommand(cmd)

def SetTopH(nVal):
	base = GetHexValue(nVal)
	cmd = "F04104100B6" + base
	return SendCommand(cmd)

def SetTopV(nVal):
	base = GetHexValue(nVal)
	cmd = "F04104100B7" + base
	return SendCommand(cmd)

def SetBottomH(nVal):
	base = GetHexValue(nVal)
	cmd = "F04104100DE" + base
	return SendCommand(cmd)

def SetBottomV(nVal):
	base = GetHexValue(nVal)
	cmd = "F04104100DF" + base
	return SendCommand(cmd)

def SetZoomH(nVal):
	base = GetHexValue(nVal)
	cmd = "F0400410103" + base
	return SendCommand(cmd)

def SetZoomV(nVal):
	base = GetHexValue(nVal)
	cmd = "F0400410105" + base
	return SendCommand(cmd)

def Mode99b(): #4:3 pi modded
	global res
	res = True
	myres = Set240p()
	myres = SetShrinkH(100)
	myres = SetShrinkV(95)
	myres = SetPosH(0)
	myres = SetPosV(60)
	myres = ShrinkOn()
	myres = AdvancedShrinkOn()	
	myres = SetPixelOutX(0)
	myres = SetPixelOutY(0)
	myres = SetPixelOutH(1920)
	myres = SetPixelOutV(1080)

	myres = SetPixelInX(0)
	myres = SetPixelInY(0)
	myres = SetPixelInH(1600)
	myres = SetPixelInV(1080)
	myres = SetZoomH(110)
	myres = SetZoomV(100)

	myres = SetTopH(-72)
	myres = SetTopV(0)

	myres = SetBottomH(-120)
	myres = SetBottomV(0)

	myres = SetPanH(0)
	myres = SetPanV(0)

def Mode10(): #4:3 pi 480i
	global res
	res = True
	myres = Set480i()
	myres = SetShrinkH(100)
	myres = SetShrinkV(95)
	myres = SetPosH(0)
	myres = SetPosV(60)
	myres = ShrinkOn()
	myres = AdvancedShrinkOn()	
	myres = SetPixelOutX(0)
	myres = SetPixelOutY(0)
	myres = SetPixelOutH(1920)
	myres = SetPixelOutV(1080)

	myres = SetPixelInX(0)
	myres = SetPixelInY(0)
	myres = SetPixelInH(1600)
	myres = SetPixelInV(1080)
	myres = SetZoomH(110)
	myres = SetZoomV(100)

	myres = SetTopH(-72)
	myres = SetTopV(0)

	myres = SetBottomH(-120)
	myres = SetBottomV(0)

	myres = SetPanH(0)
	myres = SetPanV(0)

def Mode9(): #4:3 pc486
	global res
	res = True
	myres = Set480i()
	myres = SetShrinkH(99)
	myres = SetShrinkV(96)
	myres = SetPosH(0)
	myres = SetPosV(100)
	myres = ShrinkOn()
	myres = AdvancedShrinkOn()	
	myres = SetPixelOutX(0)
	myres = SetPixelOutY(0)
	myres = SetPixelOutH(1920)
	myres = SetPixelOutV(1080)

	myres = SetPixelInX(0)
	myres = SetPixelInY(0)
	myres = SetPixelInH(1920)
	myres = SetPixelInV(1080)
	myres = SetZoomH(108)
	myres = SetZoomV(100)

	myres = SetTopH(-50)
	myres = SetTopV(0)

	myres = SetBottomH(-120)
	myres = SetBottomV(0)

	myres = SetPanH(0)
	myres = SetPanV(0)


def Mode1(): #16:9
	global res
	res = True
	myres = Set240p()
	myres = SetShrinkH(95)
	myres = SetShrinkV(95)
	myres = SetPosH(51)
	myres = SetPosV(53)
	myres = ShrinkOn()
	myres = AdvancedShrinkOn()	
	myres = SetPixelOutX(0)
	myres = SetPixelOutY(0)
	myres = SetPixelOutH(1920)
	myres = SetPixelOutV(1080)

	myres = SetPixelInX(0)
	myres = SetPixelInY(0)
	myres = SetPixelInH(1920)
	myres = SetPixelInV(1080)
	myres = SetZoomH(100)
	myres = SetZoomV(100)

	myres = SetTopH(120)
	myres = SetTopV(0)

	myres = SetBottomH(120)
	myres = SetBottomV(0)

	myres = SetPanH(0)
	myres = SetPanV(0)


#bad 16:9 squashed
def Mode0(): #16:9
	global res
	res = True
	myres = Set240p()
	myres = SetShrinkH(100)
	myres = SetShrinkV(100)
	myres = SetPosH(100)
	myres = SetPosV(53)
	myres = ShrinkOn()
	myres = PixelShrinkOn()
	myres = SetPixelOutX(0)
	myres = SetPixelOutY(0)
	myres = SetPixelOutH(1920)
	myres = SetPixelOutV(1080)

	myres = SetPixelInX(0)
	myres = SetPixelInY(0)
	myres = SetPixelInH(1920)
	myres = SetPixelInV(1080)
	myres = SetTopH(120)
	myres = SetTopV(0)

	myres = SetBottomH(120)
	myres = SetBottomV(0)
	myres = SetZoomH(100)
	myres = SetZoomV(100)
	myres = SetPanH(0)
	myres = SetPanV(0)

def Mode2(): #4:3 #Pocket Fighter base, NG Sega CD, NEOGEO
	global res
	res = True	
	myres = Set240p()
	myres = SetShrinkH(100)
	myres = SetShrinkV(95)
	myres = SetPosH(0)
	myres = SetPosV(100)
	myres = ShrinkOn()
	myres = AdvancedShrinkOn()	
	myres = SetPixelOutX(0)
	myres = SetPixelOutY(0)
	myres = SetPixelOutH(1920)
	myres = SetPixelOutV(1080)

	myres = SetPixelInX(0)
	myres = SetPixelInY(0)
	myres = SetPixelInH(1600)
	myres = SetPixelInV(1080)
	myres = SetTopH(-60)
	myres = SetTopV(0)

	myres = SetBottomH(-120)
	myres = SetBottomV(0)
	myres = SetZoomH(110)
	myres = SetZoomV(100)
	myres = SetPanH(0)
	myres = SetPanV(0)

def Mode3(): #4:3 #Sonic, NG Neogeo
	global res
	res = True	
	myres = Set240p()

	myres = SetShrinkH(100)
	myres = SetShrinkV(95)
	myres = SetPosH(0)
	myres = SetPosV(100)
	myres = ShrinkOn()
	myres = AdvancedShrinkOn()	
	myres = SetPixelOutX(0)
	myres = SetPixelOutY(0)
	myres = SetPixelOutH(1920)
	myres = SetPixelOutV(1080)

	myres = SetPixelInX(0)
	myres = SetPixelInY(0)
	myres = SetPixelInH(1600)
	myres = SetPixelInV(1080)
	myres = SetTopH(20)
	myres = SetTopV(0)

	myres = SetBottomH(-120)
	myres = SetBottomV(0)
	myres = SetZoomH(110)
	myres = SetZoomV(100)
	myres = SetPanH(0)
	myres = SetPanV(0)

def Mode4(): #3:2 #GBA
	global res
	res = True	
	myres = Set240p()

	myres = SetShrinkH(99)
	myres = SetShrinkV(87)
	myres = SetPosH(30)
	myres = SetPosV(53)
	myres = ShrinkOn()
	myres = AdvancedShrinkOn()	
	myres = SetPixelOutX(0)
	myres = SetPixelOutY(0)
	myres = SetPixelOutH(1920)
	myres = SetPixelOutV(1080)

	myres = SetPixelInX(0)
	myres = SetPixelInY(0)
	myres = SetPixelInH(1400)
	myres = SetPixelInV(1080)
	myres = SetTopH(15)
	myres = SetTopV(0)

	myres = SetBottomH(0)
	myres = SetBottomV(0)
	myres = SetZoomH(108)
	myres = SetZoomV(100)
	myres = SetPanH(0)
	myres = SetPanV(0)

def Mode5(): #Gameboy
	global res
	res = True	
	myres = Set240p()

	myres = SetShrinkH(95)
	myres = SetShrinkV(95)
	myres = SetPosH(0)
	myres = SetPosV(60)
	myres = ShrinkOn()
	myres = AdvancedShrinkOn()	
	myres = SetPixelOutX(0)
	myres = SetPixelOutY(0)
	myres = SetPixelOutH(1920)
	myres = SetPixelOutV(1080)

	myres = SetPixelInX(0)
	myres = SetPixelInY(0)
	myres = SetPixelInH(1920)
	myres = SetPixelInV(1080)
	myres = SetTopH(-15)
	myres = SetTopV(0)

	myres = SetBottomH(0)
	myres = SetBottomV(0)
	myres = SetZoomH(115)
	myres = SetZoomV(100)
	myres = SetPanH(0)
	myres = SetPanV(0)


def Mode6(): #NES Megaman 3
	global res
	res = True	
	myres = Set240p()

	myres = SetShrinkH(99)
	myres = SetShrinkV(100)
	myres = SetPosH(0)
	myres = SetPosV(53)
	myres = ShrinkOn()
	myres = AdvancedShrinkOn()	
	myres = SetPixelOutX(0)
	myres = SetPixelOutY(0)
	myres = SetPixelOutH(1920)
	myres = SetPixelOutV(1080)

	myres = SetPixelInX(0)
	myres = SetPixelInY(0)
	myres = SetPixelInH(1920)
	myres = SetPixelInV(1080)
	myres = SetTopH(-120)
	myres = SetTopV(0)

	myres = SetBottomH(120)
	myres = SetBottomV(0)
	myres = SetZoomH(147)
	myres = SetZoomV(100)
	myres = SetPanH(40)
	myres = SetPanV(0)

def Mode7(): #Pi 4:3 240p
	global res
	res = True
	myres = Set240p()
	
	myres = SetShrinkH(100)
	myres = SetShrinkV(95)
	myres = SetPosH(0)
	myres = SetPosV(100)
	myres = ShrinkOn()
	myres = AdvancedShrinkOn()	
	myres = SetPixelOutX(0)
	myres = SetPixelOutY(0)
	myres = SetPixelOutH(1920)
	myres = SetPixelOutV(1080)

	myres = SetPixelInX(0)
	myres = SetPixelInY(0)
	myres = SetPixelInH(1920)
	myres = SetPixelInV(1080)
	myres = SetTopH(-120)
	myres = SetTopV(0)

	myres = SetBottomH(-120)
	myres = SetBottomV(0)
	myres = SetZoomH(116)
	myres = SetZoomV(100)
	myres = SetPanH(0)
	myres = SetPanV(0)

def Mode8(): #16:9 480i
	global res
	res = True
	myres = Set480i()
	myres = SetShrinkH(95)
	myres = SetShrinkV(95)
	myres = SetPosH(51)
	myres = SetPosV(53)
	myres = ShrinkOn()
	myres = AdvancedShrinkOn()	
	myres = SetPixelOutX(0)
	myres = SetPixelOutY(0)
	myres = SetPixelOutH(1920)
	myres = SetPixelOutV(1080)

	myres = SetPixelInX(0)
	myres = SetPixelInY(0)
	myres = SetPixelInH(1920)
	myres = SetPixelInV(1080)
	myres = SetZoomH(100)
	myres = SetZoomV(100)

	myres = SetTopH(120)
	myres = SetTopV(0)

	myres = SetBottomH(120)
	myres = SetBottomV(0)

	myres = SetPanH(0)
	myres = SetPanV(0)

def ModeTest():
    global res
    res = True
    file_path = '/tmp/trial.txt'
    parse_and_set_xml(file_path)
    
def Test(): #select DVI-1
	res = True
	res = SendCommand("F0410410116000010") and res
	#res = SendCommand("F0410410240000") and res
	#res = SendCommandBasic("F841041024017") and res
	res = SendCommandBasic("F84104100B68B") and res
	res = SendCommandBasic("F84104100B78C") and res
	res = SendCommandBasic("F84104100DEB3") and res
	res = SendCommandBasic("F84104100DFB4") and res
	res = SendCommandBasic("F84104100A378") and res
	res = SendCommandBasic("F84104100C196") and res
	res = SendCommandBasic("F84104102431A") and res
	return res

def ChangeMode(increment):
	ChangeModeSpecific(mode + increment)

def ChangeModeSpecific(val):
	global mode
	oldMode = mode
	mode = val
	if (mode > 10):
		mode = 0
	if (mode < 0):
		mode = 10
	if(mode == 0):
		Mode0()
	elif(mode == 1):
		Mode1()
	elif(mode == 2):
		Mode2()
	elif(mode == 3):
		Mode3()
	elif(mode == 4):
		Mode4()
	elif(mode == 5):
		Mode5()
	elif(mode == 6):
		Mode6()
	elif(mode == 7):
		Mode7()
	elif(mode == 8):
		Mode8()
	elif(mode == 9):
		Mode9()
	elif(mode == 10):
		Mode10()
	else:
		mode = oldMode
		ChangeModeSpecific(mode)

def convertHex(binaryValue):
	tmpB2 = int(str(binaryValue),2) #Tempary propper base 2
	return hex(tmpB2)

def getBinary():
	global remotePin
	#Internal vars
	num1s = 0 #Number of consecutive 1s read
	binary = 1 #The binary value
	command = [] #The list to store pulse times in
	previousValue = 0 #The last value
	value = GPIO.input(remotePin) #The current value
	
	#Waits for the sensor to pull pin low
	while value:
		value = GPIO.input(remotePin)
		
	#Records start time
	startTime = datetime.now()
	
	while True:
		#If change detected in value
		if previousValue != value:
			now = datetime.now()
			pulseTime = now - startTime #Calculate the time of pulse
			startTime = now #Reset start time
			command.append((previousValue, pulseTime.microseconds)) #Store recorded data
			
		#Updates consecutive 1s variable
		if value:
			num1s += 1
		else:
			num1s = 0
		
		#Breaks program when the amount of 1s surpasses 10000
		if num1s > 10000:
			break
			
		#Re-reads pin
		previousValue = value
		value = GPIO.input(remotePin)
		
	#Converts times to binary
	for (typ, tme) in command:
		if typ == 1: #If looking at rest period
			if tme > 1000: #If pulse greater than 1000us
				binary = binary *10 +1 #Must be 1
			else:
				binary *= 10 #Must be 0
			
	if len(str(binary)) > 34: #Sometimes, there is some stray characters
		binary = int(str(binary)[:34])
	return binary



ButtonsNames = ["UP","DOWN","LEFT","RIGHT","Vol+","Vol-","CH+","CH-","CHANNEL0","CHANNEL1","CHANNEL2","CHANNEL3","CHANNEL4","CHANNEL5","CHANNEL6","CHANNEL7","CHANNEL8","CHANNEL9","Digits","Last","PREVIOUS", "NEXT", "BACK15", "FORWARD15","Red","Green","Yellow","Blue", "PLAY","UP","DOWN","CH+","CH-","CHANNEL0","CHANNEL1","CHANNEL2","CHANNEL3","CHANNEL4","CHANNEL5","CHANNEL6","CHANNEL7","CHANNEL8","CHANNEL9","BACK15","FORWARD15","Red","Green","PLAY","PREVIOUS","NEXT"]
Buttons = [0x300fdc837,0x300fd28d7,0x300fd8877,0x300fd48b7,0x300fd12ed,0x300fd926d,0x300fd52ad,0x300fdd22d,0x300fd30cf,0x300fd40bf,0x300fdc03f,0x300fd20df,0x300fda05f,0x300fd609f,0x300fde01f,0x300fd10ef,0x300fd906f,0x300fd50af,0x300fdd02f,0x300fdb04f,0x300fd2ad5,0x300fdaa55,0x300fd6a95,0x300fdea15,0x300fd32cd,0x300fdb24d,0x300fd728d,0x300fdf20d, 0x300fd8a75,0x300ffa857,0x300ffe01f,0x300ffe21d,0x300ffa25d,0x300ff6897,0x300ff30cf,0x300ff18e7,0x300ff7a85,0x300ff10ef,0x300ff38c7,0x300ff5aa5,0x300ff42bd,0x300ff4ab5,0x300ff52ad,0x300ff9867,0x300ffb04f,0x300ff629d,0x300ff906f,0x300ffc23d,0x300ff22dd,0x300ff02fd]
ModeNames=["0. 16:9 240p older", "1. 16:9 240p","2. 4:3 A 240p", "3. 4:3 B 240p", "4. 3:2 240p", "5. Gameboy 240p", "6. NES 240p", "7. 4:3 C 240p", "8. 16:9 480i", "9. 4:3 480i B","10. 4:3 480i","11. Invalid"]
Setup()
ChangeModeSpecific(1)
myRes = False
while(myRes == False):
	myRes = Test()
SetBGColor(15, 131, 120) #set bg color to close to black

while True:
	try:
		inData = convertHex(getBinary()) #Runs subs to get incomming hex value
#		print(inData)
		for button in range(len(Buttons)):#Runs through every value in list
			if hex(Buttons[button]) == inData: #Checks this against incomming
				if ButtonsNames[button] == "CH+":
					ChangeMode(1)
					break
				elif ButtonsNames[button] == "CH-":
					ChangeMode(-1)
					break
				elif ButtonsNames[button].find("CHANNEL") != -1:
					chanVal = ButtonsNames[button][7:len(ButtonsNames[button])]
					chanVal = int(chanVal)
					ChangeModeSpecific(chanVal)
					break

				elif ButtonsNames[button] == ("Digits"):
					chanVal = 10
					ChangeModeSpecific(chanVal)

					break
				elif ButtonsNames[button] == ("Last"):
					chanVal = 11
					ChangeModeSpecific(chanVal)

					break
                elif ButtonsNames[button] == ("Red"):
					ModeTest()

					break

	except Exception as e:
		print("Remote exception caught " + str(e))
