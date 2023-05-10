#----------------------------------------------------------------------------
#-----------          Code By Konrad Peschka             --------------------
#-----------          Institute: UTN - Avellaneda            ----------------
#-----------          DATE : 30/07/2018                    ------------------
#----------------------------------------------------------------------------

#-------------     Updates in the different versions      -------------------
# 1  - First Code that includes the motor functions and Imagen Proccesing
# 2  - Add the Trackbar for turning on and off the motors
# 3  - Add the capability of adjust a range of line color to follow
# 4  - Add the Trackbar to adjust movement speed

#!/usr/bin/python

#declare all the libraries that we will be use 
import io
import picamera
from picamera.array import PiRGBArray
import cv2
import numpy as np
import sys
import math
from multiprocessing.dummy import Pool as ThreadPool

import RPi.GPIO as gpio
import time

#--------------    Declare Names of window and text possitions     ------------

# The grey image is used for most of the calculations and isn't displayed
WINDOW_LINE_IMAGE = 'line image'

# This is displayed on screen with overlays showing the line tracking
WINDOW_DISPLAY_IMAGE = 'display image'

CONTROL_SCAN_RADIUS       = 'Scan Radius'
CONTROL_NUMBER_OF_CIRCLES = 'Scan Number'
CONTROL_LINE_WIDTH        = 'Line Width'
SWITCH_BUTTON 			  = '0 : OFF \n1 : ON'
CONTROL_SPEED 			  = 'Speed Control'

# Resolution of the camera image. larger images allow for more detail, but take more to process.
# valid resolutions include:
#   160 x 120
#   320 x 240
#   640 x 480
#   800 x 600

RESOLUTION_X = 320
RESOLUTION_Y = 240

# This is half the width of the line at the bottom of the screen that we start looking for
# the line we want to follow.
SCAN_RADIUS = RESOLUTION_X / 4
# Start the scan height 10 pixels from the bottom.
SCAN_HEIGHT = RESOLUTION_Y - 10
# This is our centre. We assume that we want to try and track the line in relation to this point
SCAN_POS_X = RESOLUTION_X / 2

# This is the radius that we scan from the last known point for each of the circles
SCAN_RADIUS_REG = 30
# The number of itterations we scan to allow us to look ahead and give us more time
# to make better choices
NUMBER_OF_CIRCLES = 2

#Initialization of the run motor to cero
RUN_MOTOR = 0

#--------  Initialization of the Raspi GPIO I/O   -----------

gpio.setmode(gpio.BOARD)  #aviso
gpio.setwarnings(False)   # desactivo las alertas de puerto

motorA_pwm=7
motorA_1=8
motorA_2=10

motorB_pwm=11
motorB_1=12
motorB_2=13

#   ------ Declaring some time and sleep variables for the motors --------

run_time=0.07     #this time is the forward move time and then the motor will stop 
motor_speed=100      #motor speedwhere0 is lowest and 100 is maximun speed
run_motor =0   		 #create a variable to help debugging the code without obstruction of the motors


#-------------Declaring the Pins for motor A--------------------------

gpio.setup(motorA_pwm,gpio.OUT)
gpio.setup(motorA_1,gpio.OUT)
gpio.setup(motorA_2,gpio.OUT)

#creo un objeto pwm con una frec 100 Hertz para el ENABLE A
pwm_A = gpio.PWM(motorA_pwm, 100)

#-------------Declaring the Pins for motor B--------------------------

gpio.setup(motorB_pwm,gpio.OUT)
gpio.setup(motorB_1,gpio.OUT)
gpio.setup(motorB_2,gpio.OUT)

#creo un objeto pwm con una frec 100 Hertz para el ENABLE B
pwm_B = gpio.PWM(motorB_pwm, 100)

#---------------Just in case we fixed all the pins as LOW------------------

gpio.output(motorA_1,gpio.LOW) #Apago Pin - Motor A
gpio.output(motorA_2,gpio.LOW) #Apago Pin - Motor A
pwm_A.start(0) #arranca con un duty de 0%
gpio.output(motorB_1,gpio.LOW) #Apago Pin - Motor B
gpio.output(motorB_1,gpio.LOW) #Apago Pin - Motor B
pwm_B.start(0) #arranca con un duty de 0%

#--------------------------------------------------------------
#      Declaring the movement functions for the robot
#--------------------------------------------------------------

#-------- Function that stop the motors--------------

def stop_motors():
	# Motor A
	gpio.output(motorA_1,gpio.LOW)
	gpio.output(motorA_2,gpio.LOW)
	pwm_A.ChangeDutyCycle(0)
	# Motor B
	gpio.output(motorB_1,gpio.LOW)
	gpio.output(motorB_2,gpio.LOW)
	pwm_B.ChangeDutyCycle(0)


#---------- Function to move forward ------------------
	
def forward_move(speed):
	# Motor A
	gpio.output(motorA_1,gpio.LOW)
	gpio.output(motorA_2,gpio.HIGH)
	pwm_A.ChangeDutyCycle(speed)
	# Motor B
	gpio.output(motorB_1,gpio.LOW)
	gpio.output(motorB_2,gpio.HIGH)
	pwm_B.ChangeDutyCycle(speed)
	
#---------- Function to move forward -----------------
	
def backward_move(speed):
	# Motor A
	gpio.output(motorA_1,gpio.LOW)
	gpio.output(motorA_2,gpio.HIGH)
	pwm_A.ChangeDutyCycle(speed)
	# Motor B
	gpio.output(motorB_1,gpio.LOW)
	gpio.output(motorB_2,gpio.LOW)
	pwm_B.ChangeDutyCycle(speed)
	
#---------- Function to turn right ------------------
	
def turn_right(speed):
	# Motor A
	gpio.output(motorA_1,gpio.LOW)
	gpio.output(motorA_2,gpio.HIGH)
	pwm_A.ChangeDutyCycle(speed)
	# Motor B
	gpio.output(motorB_1,gpio.LOW)
	gpio.output(motorB_2,gpio.LOW)
	pwm_B.ChangeDutyCycle(speed)
	
#---------- Function to turn left ------------------
	
def turn_left(velocidad):
	# Motor A
	gpio.output(motorA_1,gpio.LOW)
	gpio.output(motorA_2,gpio.LOW)
	pwm_A.ChangeDutyCycle(velocidad)
	# Motor B
	gpio.output(motorB_1,gpio.LOW)
	gpio.output(motorB_2,gpio.HIGH)
	pwm_B.ChangeDutyCycle(velocidad)



#--------- Here are all the Functions that scan the a line over the floor ------------

def scanLine(image, display_image, point, radius):
		x = point[0];
		y = point[1];

		scan_start = x - radius
		scan_end = x + radius
		row = image[y]
		data = np.empty(radius*2)
		data[:] = row[scan_start:scan_end]

		# Draw a line where we are reading the data
		cv2.line(display_image, (scan_start, y), (scan_end, y), (255, 0, 0), 2)
		cv2.circle(display_image, (scan_start, y), 5, (255, 0, 0), -1, 8, 0)
		cv2.circle(display_image, (scan_end, y), 5, (255, 0, 0), -1, 8, 0)
		#print("scanline x:{} y:{} - start x:{} end x:{} - {}".format(x, y, scan_start, scan_end, SCAN_DATA))
		return data;


def coordinateFromPoint(origin, angle, radius):
		xo = origin[0]
		yo = origin[1]

		# Work out the co-ordinate for the pixel on the circumference of the circle
		x = xo - radius * math.cos(math.radians(angle))
		y = yo + radius * math.sin(math.radians(angle))

		# We only want whole numbers
		x = int(round(x))
		y = int(round(y))
		return (x, y);

def scanCircle(image, display_image, point, radius, look_angle):
		x = point[0];
		y = point[1];
		scan_start = x - radius
		scan_end = x + radius

		endpoint_left = coordinateFromPoint(point, look_angle - 90, radius)
		endpoint_right = coordinateFromPoint(point, look_angle + 90, radius)

		#print("scanline left:{} right:{} angle:{}".format(endpoint_left, endpoint_right, look_angle))
		# Draw a circle to indicate where we start and end scanning.
		cv2.circle(display_image, (endpoint_left[0], endpoint_left[1]), 5, (255, 100, 100), -1, 8, 0)
		cv2.circle(display_image, (endpoint_right[0], endpoint_right[1]), 5, (100, 255, 100), -1, 8, 0)
		cv2.line(display_image, (endpoint_left[0], endpoint_left[1]), (endpoint_right[0], endpoint_right[1]), (255, 0, 0), 1)
		cv2.circle(display_image, (x, y), radius, (100, 100, 100), 1, 8, 0)

		# We are only going to scan half the circumference
		data = np.zeros(shape=(180, 3))

		# Getting the co-ordinates and value for every degree in the semi circle
		startAngle = look_angle - 90

		returnVal = True
		for i in range(0, 180, 1):
				current_angle = startAngle + i
				scan_point = coordinateFromPoint(point, current_angle, radius)

				if inImageBounds(image, scan_point[0], scan_point[1]):
						imageValue = image[scan_point[1]][scan_point[0]]
						data[i] = [imageValue, scan_point[0], scan_point[1]]
				else:
						returnVal = False
						break;

		return returnVal, data;

def findInCircle(display_image, scan_data):
		data = np.zeros(shape=(len(scan_data) -1, 1))
		data[0] = 0
		data[len(data)-1] = 0
		for index in range(1, len(data)):
				data[index] = scan_data[index - 1][0] - scan_data[index][0]

		# left and right should be the boundry values.
		# first element will be the image value
		# second element will be the index of the data item
		left = [0,0]
		right = [0,0]

		for index in range(0, len(data)):
				if data[index] > left[1]:
						left[1] = data[index]
						left[0] = index

				if data[index] < right[1]:
						right[1] = data[index]
						right[0] = index

		leftx = int(scan_data[left[0]][1])
		lefty = int(scan_data[left[0]][2])
		lefti = left[0]
		rightx = int(scan_data[right[0]][1])
		righty = int(scan_data[right[0]][2])
		righti = right[0]

		centre_index = int(round((righti + lefti)/2))

		position = [int(scan_data[centre_index][1]), int(scan_data[centre_index][2])]

		# mid point, where we believe is the centre of the line
		cv2.circle(display_image, (position[0], position[1]), 5, (255, 255, 255), -1, 8, 0)
		# left boundrary dot on the line
		cv2.circle(display_image, (leftx, lefty), 2, (0, 0, 102), 2, 8, 0)
		# right boundrary dot on the line
		cv2.circle(display_image, (rightx, righty), 2, (0, 0, 102), 2, 8, 0)

		return position;

def inImageBounds(image, x, y):
		return x >=0 and y >= 0 and y < len(image) and x < len(image[y])

def findLine(display_image, scan_data, x, y, radius):
		data = np.empty(len(scan_data) -1)
		data[0] = 0
		data[len(data)-1] = 0
		for index in range(1, len(data)):
				data[index] = scan_data[index - 1] - scan_data[index]

		scan_start = x - radius
		scan_end = x + radius

		left = [0,0]
		right = [0,0]

		for index in range(0, len(data)):
				if data[index] > left[1]:
						left[1] = data[index]
						left[0] = index

				if data[index] < right[1]:
						right[1] = data[index]
						right[0] = index


		line_position = (right[0] + left[0]) / 2
		#print("line position {} {}, {} - {}".format(scan_start, left, right, line_position))
		# mid point, where we believe is the centre of the line
		#cv2.circle(display_image, (scan_start + line_position, y), 5, (0, 204, 102), -1, 8, 0)
		# left boundrary dot on the line
		#cv2.circle(display_image, (scan_start + left[0], y), 5, (0, 0, 102), -1, 4, 0)
		# right boundrary dot on the line
		#cv2.circle(display_image, (scan_start + right[0], y), 5, (0, 0, 102), -1, 4, 0)
		return (scan_start + line_position, y);

def lineAngle(point1, point2):
		angle = round(math.atan2((point2[1] - point1[1]), -(point2[0] - point1[0]))*180/math.pi)
		return angle

def lineLength(point1, point2):
		dx = point1[0] - point2[0]
		dy = point1[1] - point2[1]
		return int(round(math.sqrt(dx*dx + dy*dy)));

def onScanRadiusChange(newValue):
		global SCAN_RADIUS_REG
		SCAN_RADIUS_REG = newValue
		return;

def onCircleScanChange(newValue):
		global NUMBER_OF_CIRCLES
		NUMBER_OF_CIRCLES = newValue
		return;

def onLineWidthChange(newValue):
		global SCAN_RADIUS
		SCAN_RADIUS = int(round(newValue/2))
		return;

def turnOnOffChange(newValue):
		global RUN_MOTOR
		RUN_MOTOR = newValue
		return;

def speedChange(newValue):
		global motor_speed
		motor_speed = newValue
		return;

#------------------------------------------------------------------------------------------------------------------------
#-----------------------------           Here begin the real Main CODE       --------------------------------------------
#------------------------------------------------------------------------------------------------------------------------


def main():
		# Create the in-memory stream
		stream = io.BytesIO()


		# Create a window
		cv2.namedWindow(WINDOW_DISPLAY_IMAGE)
		# position the window on the left-site
		cv2.moveWindow(WINDOW_DISPLAY_IMAGE, 0, 0)

		cv2.namedWindow(WINDOW_LINE_IMAGE)

		# position the window on the left-site
		cv2.moveWindow(WINDOW_LINE_IMAGE, 120, 120)

		# -----------  Add the Trackbars to our Window Display  ---------------
		
		#cv.CreateTrackbar(trackbarName, windowName, start value, maximum value,a pointer to see if trackbare has changed)
		cv2.createTrackbar(CONTROL_SCAN_RADIUS, WINDOW_DISPLAY_IMAGE, 5, 50, onScanRadiusChange)
		#cv2.setTrackbarPos(trackbarname, winname, new pos) 
		cv2.setTrackbarPos(CONTROL_SCAN_RADIUS, WINDOW_DISPLAY_IMAGE, SCAN_RADIUS_REG)


		cv2.createTrackbar(CONTROL_NUMBER_OF_CIRCLES, WINDOW_DISPLAY_IMAGE, 0, 7, onCircleScanChange)
		cv2.setTrackbarPos(CONTROL_NUMBER_OF_CIRCLES, WINDOW_DISPLAY_IMAGE, NUMBER_OF_CIRCLES)

		
		cv2.createTrackbar(CONTROL_LINE_WIDTH, WINDOW_DISPLAY_IMAGE, 0, RESOLUTION_X, onLineWidthChange)
		cv2.setTrackbarPos(CONTROL_LINE_WIDTH, WINDOW_DISPLAY_IMAGE, SCAN_RADIUS *3)

		# create switch for ON/OFF functionality
		cv2.createTrackbar(SWITCH_BUTTON, WINDOW_DISPLAY_IMAGE, 0, 1, turnOnOffChange)
		cv2.setTrackbarPos(SWITCH_BUTTON, WINDOW_DISPLAY_IMAGE, RUN_MOTOR)

		# create Trackbar to adjust motor Speed
		cv2.createTrackbar(CONTROL_SPEED, WINDOW_DISPLAY_IMAGE, 0, 100, speedChange)
		cv2.setTrackbarPos(CONTROL_SPEED, WINDOW_DISPLAY_IMAGE, motor_speed)
		
			 

		returnString = """
Press Esc to end the program
Using camera resolution: {}x{}
Centre point: {}:{}
Scan radius: {}
Number of search itterations: {}
Baseline Width: {}
""".format(RESOLUTION_X, RESOLUTION_Y, SCAN_POS_X, SCAN_HEIGHT, SCAN_RADIUS_REG, NUMBER_OF_CIRCLES, SCAN_RADIUS *2)

		print(returnString)

		# Open connection to camera
		with picamera.PiCamera() as camera:
				# Set camera resolution
				camera.resolution = (RESOLUTION_X, RESOLUTION_Y)
				camera.vflip = True
				camera.hflip = True

				# Start loop
				while True:
						# Get the tick count so we can keep track of performance
						e1 = cv2.getTickCount()
						
						# Capture image from camera
						camera.capture(stream, format='jpeg', use_video_port=True)
						

						# Convert image from camera to a numpy array
						data = np.fromstring(stream.getvalue(), dtype=np.uint8)

						# Decode the numpy array image
						image = cv2.imdecode(data, cv2.IMREAD_COLOR)

						# Empty and return the in-memory stream to beginning
						stream.seek(0)
						stream.truncate(0)

						#-----------------------Processing the line color ---------------------

						blur = cv2.GaussianBlur(image, (5,5),0)
   						# Convert BGR to HSV
						hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)

    					# Threshold the HSV image for only green colors
    					#elnp.array es mas eficiente y rapido con el manejo de memoria
						lower_line = np.array([0,0,0])
    						#upper_line= np.array([200,200,200])
						upper_line= np.array([140,140,140])
    
    					# Threshold the HSV image to get only green colors
						line_image = cv2.inRange(hsv, lower_line, upper_line)
    
    					# Blur the mask
    						#line_image = cv2.GaussianBlur(mask, (5,5),0)


						#---------------------------------------------------------------------------

						display_image = cv2.copyMakeBorder(image, 0, 0, 0, 0, cv2.BORDER_REPLICATE)

						center_point = (SCAN_POS_X, SCAN_HEIGHT)

						# Scan a horizontal line based on the centre point
						# We could just use this data to work out how far off centre we are and steer accordingly.
						# Get a data array of all the falues along that line
						# scan_data is an array containing:
						#   - pixel value
						scan_data = scanLine(line_image, display_image, center_point, SCAN_RADIUS)
						# The center point we believe the line we are following intersects with our scan line.
						point_on_line = findLine(display_image, scan_data, SCAN_POS_X, SCAN_HEIGHT, SCAN_RADIUS)

						# Start scanning the arcs
						# This allows us to look ahead further ahead at the line and work out an angle to steer
						# From the intersection point of the line, scan in an arc to find the line
						# The scan data contains an array
						#   - pixel value
						#   - x co-ordinate
						#   - y co-ordinate
						returnVal, scan_data = scanCircle(line_image, display_image, point_on_line, SCAN_RADIUS_REG, -90)
						previous_point = point_on_line
						# in the same way ads the findLine, go through the data, find the mid point and return the co-ordinates.
						last_point = findInCircle(display_image, scan_data)
						cv2.line(display_image, (previous_point[0], previous_point[1]), (last_point[0], last_point[1]), (255, 255, 255), 1)

						actual_number_of_circles = 0
						for scan_count in range(0, NUMBER_OF_CIRCLES):
								returnVal, scan_data = scanCircle(line_image, display_image, last_point, SCAN_RADIUS_REG, lineAngle(previous_point, last_point))

								# Only work out the next itteration if our point is within the bounds of the image
								if returnVal == True:
										actual_number_of_circles += 1
										previous_point = last_point
										last_point = findInCircle(display_image, scan_data)
										cv2.line(display_image, (previous_point[0], previous_point[1]), (last_point[0], last_point[1]), (255, 255, 255), 1)
								else:
										break;

						# Draw a line from the centre point to the end point where we last found the line we are following
						cv2.line(display_image, (center_point[0], center_point[1]), (last_point[0], last_point[1]), (0, 0, 255), 1)


						# ---------------------------     Display the image  ----------------------------

						cv2.imshow(WINDOW_DISPLAY_IMAGE, display_image)
						cv2.imshow(WINDOW_LINE_IMAGE, line_image)

						# This is the maximum distance the end point of our search for a line can be from the centre point.
						line_scan_length = SCAN_RADIUS_REG * (actual_number_of_circles + 1)
						# This is the measured line length from the centre point
						line_length_from_center = lineLength(center_point, last_point)
						center_y_distance = center_point[1] - last_point[1]
						e2 = cv2.getTickCount()
						center_x_distance = center_point[0] - last_point[0]

						# Angulo
						bearing = lineAngle(center_point, last_point) *-1 -90

						# Stop counting all work is done at this point and calculate how we are doing.
						fps = 1000/ ((e2 -e1)/cv2.getTickFrequency() *1000)

						returnString = "fps {} - bearing {} - x{} y{} look distance:{} distance from origin:{}".format(
									  int(round(fps)),
									  bearing,
									  center_x_distance,
									  center_y_distance,
									  line_scan_length,
									  line_length_from_center)
						print(returnString)
						
						direccion = -bearing

						# ----------------------------- Control Movimiento  ---------------------------------

						if center_y_distance >= 40:
							if direccion <= 20 and direccion >= -20:
								if RUN_MOTOR == 0:
									stop_motors()
								else:
									forward_move(motor_speed)
									time.sleep(run_time)
								print("adelante")
								stop_motors()

							elif direccion > 20:
								if RUN_MOTOR == 0:
									stop_motors()
								else:
									turn_right(motor_speed)
									time.sleep(run_time)
								print("derecha")
								stop_motors()

							elif direccion < -20:
								if RUN_MOTOR == 0:
									stop_motors()
								else:
									turn_left(motor_speed)
									time.sleep(run_time)
								print("izquierda")
								stop_motors()
						else:
							stop_motors()
							print("parar")

						# Wait for ESC to end program
						c = cv2.waitKey(7) % 0x100
						if c == 27:
								break
		print("Closing program")
		cv2.destroyAllWindows()
		print ("All windows should be closed")
		return;

if __name__ == "__main__":
		main()