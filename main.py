#!/usr/bin/env pybricks-micropython

# ---------------------------------------------------------------
# <name>
#
# <something about starting with a copy of our 2021 code>
#
# <Something about the change log now bing in Git Hub>
#  
# ---------------------------------------------------------------
 
# ---------------------------------------------------------------
# Initialization section from 2021
#  Mostly from example code
# ---------------------------------------------------------------

# these are the libraries of code writen by pybricks (API)
from pybricks.hubs import EV3Brick
from pybricks.parameters import Port, Stop, Direction, Button, Color 
from pybricks.ev3devices import Motor, TouchSensor, ColorSensor, InfraredSensor, UltrasonicSensor, GyroSensor
from pybricks.tools import wait, StopWatch, DataLog
from pybricks.robotics import DriveBase
from pybricks.media.ev3dev import SoundFile, ImageFile

# we got and Ian changed this code from the samples
from menu import wait_for_button
from menu import make_screen

RIGHT_SENSOR_WHITE=90
LEFT_SENSOR_WHITE=90
RIGHT_SENSOR_BLACK=8
LEFT_SENSOR_BLACK=8

# Initialize the EV3.
ev3 = EV3Brick()

# Initialize the motors.
am = Motor(Port.A)
left_motor = Motor(Port.C)
right_motor = Motor(Port.B)

# Initialize the sensors 
line_sensor = right_line_sensor = ColorSensor(Port.S1)
left_line_sensor = ColorSensor(Port.S4)

# Initialize the drive base. <comment about Sturgeon 3000 being 111mm>
robot = DriveBase(left_motor, right_motor, wheel_diameter=90, axle_track=111)

# ipk did creating and Initialize variables for speed and acceleration
# (209, 837, 400, 1600)
straight_speed = 209
straight_acceleration = 837 #837
turn_rate = 50 #400 
turn_acceleration = 1600

# menu variables by Ian
run_number = 0
last_run_number = 3 

# ---------------------------------------------------------------
# These are our reusable functions from 2021
# ---------------------------------------------------------------

def straight_speed(speed):
    # ---------------------------------------------------------------
    # This is the reusable function for changing the straight drive speed
    #  Example: straightspeed(100) to change speed to 100 mm/second
    #  from 2021
    # ---------------------------------------------------------------

    straight_speed = speed
    robot.stop()
    robot.settings(straight_speed, straight_acceleration, turn_rate, turn_acceleration)    
  
def forklift_move(direction,time):
    # ---------------------------------------------------------------
    # This is the function for the forklift retrofitted from 2020 
    #  code from 2021
    # ---------------------------------------------------------------

    speed=200000
    if direction == "down":
        speed = speed * -1

    am.run_time(speed,time)

def dispense_energy_units():
    # ---------------------------------------------------------------
    # This is the reusable function for the 2021 package dispenser
    #  changed to be a 2022 energy unit dispenser
    # ---------------------------------------------------------------

    am.run_time(-2000,700)# speed and time, negative is dispense
    am.run_time(2000,700)# speed and time, positive is reset


def follow_line2( distance, speed = 80, right_or_left_sensor = "right", side_of_line = "left", Kp = 0.8, Ki = 0.0008, Kd =.001):
    '''
    Version 2 of the Digital Magic function to follow a line.  This version by Koen on 12-18-2020 to make it a PID line follower
    and use 2 sensors!

    Parameters:
        distance - mm you want robot to travel
        speed - speed of robot.
        right_or_left_sensor - which sensor are you using ("right" or "left")
        side_of_line = which side of black line are you following ("right" or "left") 
        Kp - proportional gain
        Ki - integral gain 
        Kd - derivative gain      
    '''

    integral = 0
    derivative = 0
    last_error = 0

        
    if (right_or_left_sensor == "right"):
        sensor = right_line_sensor
        target = (RIGHT_SENSOR_WHITE + RIGHT_SENSOR_BLACK) / 2
    else:
        sensor = left_line_sensor
        target = (LEFT_SENSOR_WHITE + LEFT_SENSOR_BLACK) / 2

    robot.reset()
    robot.stop()

    # PID feedback loop
    while robot.state()[0] < distance:
        
        error = sensor.reflection() - target
        integral = integral + error
        derivative = error - last_error
        
        # this is where the digital magic of a PID line follower happens
        turn_rate = Kp * error + Ki * integral + Kd * derivative
        if side_of_line == "left":
            #print(speed - turn_rate)
            right_motor.run(speed - turn_rate)
            left_motor.run(speed + turn_rate)
        else:
            right_motor.run(speed + turn_rate)
            left_motor.run(speed - turn_rate)
        last_error = error
        wait(10)

    robot.stop()  #make sure this is outside the loop!!

# ---------------------------------------------------------------
# OUR 2021 MISSION FUNCTIONS START HERE - SAVE AWHILE
# ---------------------------------------------------------------

def flip_engine():
    # ---------------------------------------------------------------
    # way more simple cargo plane only function
    # This is a simplified function from old run_number1b() that just does Flip Engine 
    # ---------------------------------------------------------------

    #set the speed
    straightspeed(109)

    #drive to line Watch Sensors
    robot.straight(280)

    #follow line (until right before the sharp turn)
    followline(550,75)
    robot.stop()
    
    #drive strait ahead then to motor
    robot.straight(210)
    robot.turn(40)
    robot.straight(46)

    # Lift the attachment fliping motor
    am.run_time(speed = -1500,time=1200)

    
    #bring it on home fast
    robot.turn(-50)
    straightspeed(500)
    robot.straight(-800)

def cargo_plane():

    #position the attachment arm
    am.run_time(speed=250,time=950)

    #must stop to change speed
    robot.stop()

    #set the speed
    straightspeed(200)

    #drive to line 
    robot.straight(655)
    ev3.speaker.beep(800)  
    
    #bring da hammer down slightly
    am.run_time(speed=1500,time=1200)

    #must stop to change speed
    robot.stop()

    #drive home fast
    straightspeed(500)
    robot.straight(-750)

def plattooning_trucks(): 
    # ---------------------------------------------------------------
    # This is the function for plattooning trucks  
    # ---------------------------------------------------------------

    #set the speed
    straightspeed(109)

    #drive to line and follow it awhile
    robot.straight(150)
    followline(200,75) 
    ev3.speaker.beep(200)  # DEBUG BEEP 1

    #turn toward the other truck.  The wait is how long it turns
    robot.drive(speed=75, turn_rate=20)
    wait(1500) #2400 ipk
    ev3.speaker.beep(400)  #DEBUG BEEP 2

    #turn less toward the other truck.  The wait is how long it turns
    robot.drive(speed=75, turn_rate=1)
    wait(1200) #2400 ipk
    ev3.speaker.beep(600)  #DEBUG BEEP 3

    #push the truck onto the latch
    straightspeed(75)
    robot.straight(120)
    ev3.speaker.beep(800)  #DEBUG BEEP 4

    #back up to push unused capacity - the wait is how long it turns
    robot.drive(speed=-1000, turn_rate=20)
    wait(1200)
    robot.straight(-300)
    robot.stop()

def plattooning_trucks2(): 

    # ---------------------------------------------------------------
    # This is 2nd version of the function for plattooning trucks testing gyro
    # ---------------------------------------------------------------

    #drive straight out and turn toward other truck and then straight again to latch
    print("Drive North")

    #gyro_straight(500, robotSpeed=150)
    robot.straight(500)

    print("Turn East")
    gyro_turn(88, speed=150)

    print("Drive East")
    #gyro_straight(400, robotSpeed=80)
    robot.straight(400)

def connect_cargo():
    # ---------------------------------------------------------------
    # This is the function for connect cargo   
    # --------------------------------------------------------------- 

    #set the speed
    straightspeed(200)

    #drive to circle 
    robot.straight(620)

    #drive back 
    robot.straight(-700)

def innovation_model(): 
    # ---------------------------------------------------------------
    # This is the function for delivering innovation model  
    # ---------------------------------------------------------------

    #set the speed
    straightspeed(130)

    #drive to circle 
    robot.straight(1130)

    #turn towards circle
    ## COACH THINKS NEED A TURN SPEED SETTER HERE HE MESSED WITH VARIABLE
    #robot.turn(-50) #12-5-21 lmh
    #robot.turn(-90)  #12-6-21 -kahk
    robot.turn(-65)  ##NEED COMMENT

    #drive forward a litttle bit # 
    robot.straight(35)  #12-6-21 -kahk

    #drive back a tiny bit 
    #robot.straight(-70) #12-5-21 -lmh
    robot.straight(-100)  #12-6-21 -kahk

    #turn toward door
    #robot.turn(140) #12-5-21 -lmh
    #robot.turn(190)  #12-6-21 -kahk ipk 220 190
    robot.turn(90) ## NEED COMMENT

    #drive toward door
    robot.straight(250)

    #turn back toward door #12-6-21 -kahk
    robot.turn(-40)  

    #drive toward door
    robot.straight(70)

    #deliver package
    packagedispenser()

    #drive back a tiny bit
    robot.straight(-70)

def new_run():
    '''
    This is the new run for state by ipk that goes to the eastern side of the board and does missions
    '''
    #position the attachment arm
    am.run_time(speed=-400,time=800)
    
    #go to line
    robot.straight(170)

    #follow line
    follow_line2(distance=730, speed = 120, right_or_left_sensor = "right", side_of_line = "left", Kp = 0.6, Ki = 0.0008, Kd = 2.0)

    #lower arm
    am.run_time(speed=400,time=600)

    #knock over bridge
    robot.straight(80)

    #position the attachment arm
    am.run_time(speed=-400,time=600)

    #drive ahead
    robot.straight(270)

    #lower arm
    am.run_time(speed=400,time=600)

    #backup into bridge
    robot.straight(-130)

    #a little turn
    robot.turn(5)

    #position the attachment arm
    am.run_time(speed=-400,time=800)

    #follow line to hellacopter
    follow_line2(distance=800, speed = 120, right_or_left_sensor = "right", side_of_line = "left", Kp = 0.8, Ki = 0.0008, Kd = 2.0)

    #backup a little
    robot.straight(-100)

    #turn and catch line
    robot.turn(85)
    robot.straight(60)
    ev3.speaker.beep(200)  # DEBUG BEEP 1

    #follow line to rr bridge
    follow_line2(distance=350, speed = 80, right_or_left_sensor = "left", side_of_line = "right", Kp = 1.0, Ki = 0.0008, Kd = 2.0)

    #lower arm to rr bridge
    am.run_time(speed=-400,time=1100)

    #raise arm
    am.run_time(speed=400,time=1100)

    #backup to catch train
    robot.straight(-200)    

    #lower arm
    am.run_time(speed=-400,time=800)

    #pull train
    follow_line2(distance=220, speed = 80, right_or_left_sensor = "left", side_of_line = "right", Kp = .8, Ki = 0.0008, Kd = 2.0)

    #raise arm
    am.run_time(speed=400,time=800)

    #backup to catch train
    robot.straight(-220)

    #lower arm
    am.run_time(speed=-400,time=800)

    #pull train
    follow_line2(distance=250, speed = 80, right_or_left_sensor = "left", side_of_line = "right", Kp = .8, Ki = 0.0008, Kd = 2.0)

def blade():
    
    robot.drive(speed = 500, turn_rate = 70)
    wait(1000)
    robot.stop()
    ev3.speaker.beep(800)  
    robot.drive(speed = 500, turn_rate = 10)
    wait(1500)
    robot.drive(speed = -500, turn_rate = 0)
    wait(3000)
    robot.stop()

# ---------------------------------------------------------------
# OUR 2022 MISSION FUNCTIONS START HERE (move to other files)
# ---------------------------------------------------------------

def watch_sensors():
    wait(1000)
    
    left_motor.reset_angle(0)
    right_motor.reset_angle(0)


    while (ev3.buttons.pressed() == []):
        ev3.screen.clear()

        ev3.screen.draw_text(1, 20, "R Line:")
        ev3.screen.draw_text(100, 20, right_line_sensor.reflection())
        ev3.screen.draw_text(1, 40, "L Line:")
        ev3.screen.draw_text(100, 40, left_line_sensor.reflection())
        ev3.screen.draw_text(1, 60, "R Motor:")
        ev3.screen.draw_text(100, 60, right_motor.angle())
        ev3.screen.draw_text(1, 80, "L Motor:")
        ev3.screen.draw_text(100, 80, left_motor.angle())
        ev3.screen.draw_text(1, 100, "V (8231):")
        ev3.screen.draw_text(100, 100, ev3.battery.voltage())
        wait(100)
    
    # Now wait for the button to be released, from example code.  If you don't do this, the button that ends it executes next loop.
    while any(ev3.buttons.pressed()):
        pass

def right_motor_run():
    am.run(1000)

# ---------------------------------------------------------------
# This is the menu system (changed from the example code by Ian)
# ---------------------------------------------------------------

ev3.speaker.beep(100)
ev3.speaker.beep(900)
ev3.speaker.beep(100)
ev3.speaker.beep(900)

while True:
    # Draw screen based on what run we are on
    if run_number == 0:
        make_screen(ev3,"Line Follow Test"," -  -  -  -  -  -  + ","", ""," "," ")

    elif run_number == 1:
        make_screen(ev3,"Watch Sensors"," -  -  -  -  -  -  + ","", ""," "," ")

    elif run_number == 2:
        make_screen(ev3,"Right Motor Run"," -  -  -  -  -  -  + ","", ""," "," ")

    elif run_number == 3:
        make_screen(ev3,"Watch Sensors"," -  -  -  -  -  -  + ","", ""," "," ")


    # Wait for one button to be selected.
    button = wait_for_button(ev3)

    # Now you can do something, based on which button was pressed.
    if button == Button.LEFT:
        if run_number > 0: 
            run_number = run_number - 1
        else:
            run_number = last_run_number

    elif button == Button.RIGHT:
        if run_number < last_run_number: 
            run_number = run_number + 1
        else:
            run_number = 0

    elif button == Button.UP:
        if run_number > 0: 
            run_number = run_number - 1
        else:
            run_number = last_run_number

    elif button == Button.DOWN:
        if run_number < last_run_number: 
            run_number = run_number + 1
        else:
            run_number = 0

    elif button == Button.CENTER:
        if run_number == 0:
            followline2( 1300, speed = 120, right_or_left_sensor = "left", side_of_line = "left", Kp = 1.0, Ki = 0.0008, Kd =.001)
        elif run_number == 1:
            watch_sensors()

        elif run_number == 2:
            right_motor_run()

        elif run_number == 3:
            watch_sensors()

                    

        # Move on to next run screen
        if run_number < last_run_number: 
            run_number = run_number + 1
        else:
            run_number = 0  
