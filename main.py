#!/usr/bin/env pybricks-micropython

# -----------------------------------------------------------------
# Coach's programming of the Sturgeon 3000 as the 2022 Hooey Sucker
# -----------------------------------------------------------------

# imports
from pybricks.hubs import EV3Brick
from pybricks.parameters import Port, Stop, Direction, Button, Color 
from pybricks.ev3devices import Motor, TouchSensor, ColorSensor, InfraredSensor, UltrasonicSensor, GyroSensor
from pybricks.tools import wait, StopWatch, DataLog
from pybricks.robotics import DriveBase
from pybricks.media.ev3dev import SoundFile, ImageFile

from menu import wait_for_button, make_screen

import operator

BACK_SENSOR_WHITE=99
FRONT_SENSOR_WHITE=73
BACK_SENSOR_BLACK=8
FRONT_SENSOR_BLACK=6
  
# Initialize the EV3.
ev3 = EV3Brick()

# Initialize the motors.
am = Motor(Port.A)
left_motor = Motor(Port.C)
right_motor = Motor(Port.B)

# Initialize the sensors 
back_line_sensor = ColorSensor(Port.S1)  #was right
front_line_sensor = ColorSensor(Port.S4) #was left

# Initialize the drive base. <comment about Sturgeon 3000 being 111mm>
robot = DriveBase(left_motor, right_motor, wheel_diameter=90, axle_track=111)

# ipk did creating and Initialize variables for speed and acceleration
# (209, 837, 400, 1600)
straight_speed = 209
straight_acceleration = 837 #837
turn_rate = 50 #400 
turn_acceleration = 1600

def reep():
    am.run_time(-200,2000)

def reset_reeper():
    am.run_time(200,2000)

def menu1():

    # menu variables
    run_number = 0
    last_run_number = 5 

    while True:
    # Draw screen based on what run we are on
        if run_number == 0:
            make_screen(ev3,"Line Follow Test"," +  -  -  -  -  -  - ","", ""," "," ")

        elif run_number == 1:
            make_screen(ev3,"Watch Sensors"," -  +  -  -  -  -  - ","", ""," "," ")

        elif run_number == 2:
            make_screen(ev3,"Clean Wheels"," -  -  +  -  -  -  - ","", ""," "," ")

        elif run_number == 3:
            make_screen(ev3,"TV Windmill"," -  -  -  +  -  -  - ","", ""," "," ")

        elif run_number == 4:
            make_screen(ev3,"Dino Ride"," -  -  -  -  +  -  - ","", ""," "," ")

        elif run_number == 5:
            make_screen(ev3,"Forklift Demo"," -  -  -  -  -  +  - ","", ""," "," ")


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
                followline2(1300, speed = 120, right_or_left_sensor = "left", side_of_line = "left", Kp = 1.0, Ki = 0.0008, Kd =.001)

            elif run_number == 1:
                watch_sensors()

            elif run_number == 2:
                clean_wheels()

            elif run_number == 3:
                tv_windmill()

            elif run_number == 4:
                dino() 

            elif run_number == 5:
                forklift_demo()            

            # Move on to next run screen
            if run_number < last_run_number: 
                run_number = run_number + 1
            else:
                run_number = 0  

def clean_wheels():
    robot.straight(1500)

def set_turn_rate(rate):

    # ---------------------------------------------------------------
    # This is the reusable function for changing the robot turn rate
    #  Example: set_turn_rate(100) to change speed to 100 mm/second
    # ---------------------------------------------------------------

    turn_rate = rate
    robot.stop()
    robot.settings(straight_speed, straight_acceleration, turn_rate, turn_acceleration)    

def set_straight_speed(speed):
    # ---------------------------------------------------------------
    # This is the reusable function for changing the straight drive speed
    #  Example: set_straight_speed(100) to change speed to 100 mm/second
    #  from 2021
    # ---------------------------------------------------------------

    straight_speed = speed
    robot.stop()
    robot.settings(straight_speed, straight_acceleration, turn_rate, turn_acceleration)    
  
def forklift_move(direction,time):
    # ---------------------------------------------------------------
    # This is the function for the forklift retrofitted from 2020 
    #  code from 2021
    # forklift_move("up",2500)
    # forklift_move("down",2500)
    # ---------------------------------------------------------------

    speed=200
    if direction == "down":
        speed = speed * -1

    am.run_time(speed,time)

def forklift_demo():
    forklift_move("up",2500)
    forklift_move("down",2500)

def dispense():
    # ---------------------------------------------------------------
    # This is the reusable function for the 2021 package dispenser
    #  changed to be a 2022 energy unit dispenser
    # ---------------------------------------------------------------

    am.run_time(-2000,700)# speed and time, negative is dispense
    am.run_time(2000,700)# speed and time, positive is reset

def follow_line( distance, speed = 80, desired_sensor = "back", side_of_line = "left", Kp = 0.8, Ki = 0.0008, Kd =.001):

    # Enter a negative distance to drive in reverse.  This matches pybricks robot.straight method

    # creating a text file to analyze the following performance for tuning
    title = open("title.txt", "w")
    data = open("data.csv" , "w")

    title.write("Speed=" + str(speed) + " Kp=" + str(Kp) + " Ki=" +  str(Ki) + " Kd=" + str(Kd))
    data.write("Reading,Target,Sensor" + "\n")
    
    
    integral = 0
    derivative = 0
    last_error = 0
    reading = 1
        
    if (desired_sensor == "back"):
        sensor = back_line_sensor
        target = (BACK_SENSOR_WHITE + BACK_SENSOR_BLACK) / 2
    else:
        sensor = front_line_sensor
        target = (FRONT_SENSOR_WHITE + FRONT_SENSOR_BLACK) / 2

    robot.reset()
    robot.stop()

    if (distance >= 0):
        we_are_not_there_yet = operator.lt 
        print("lt - forward")
    else:
        we_are_not_there_yet = operator.gt
        print("gt - reverse")


    print(robot.state()[0], distance)

    # PID feedback loop
    while we_are_not_there_yet(robot.state()[0],distance):  #ya, like I can teach a kid this
        #print(robot.state()[0], distance)
        
        error = sensor.reflection() - target
        integral = integral + error
        derivative = error - last_error
        
        # this is where the digital magic of a PID line follower happens
        turn_rate = Kp * error + Ki * integral + Kd * derivative

        data.write(str(reading) + "," + str(target) + "," + str(target + turn_rate) + "\n")
        reading = reading + 1

        if side_of_line == "left":
            right_motor.run(speed - turn_rate)
            left_motor.run(speed + turn_rate)
        else:
            right_motor.run(speed + turn_rate)
            left_motor.run(speed - turn_rate)
        last_error = error
        wait(10)

    robot.stop()  #make sure this is outside the loop!!
    title.close()
    data.close()

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

def dino():
    set_straight_speed(1000)
    robot.straight(2000)

def tv_windmill():
    # TV
    set_straight_speed(300)
    robot.straight(430)
    set_straight_speed(100)
    robot.straight(50)
    set_straight_speed(300)
    robot.straight(-140)

    # Windmill
    set_turn_rate(200)
    robot.turn(-45)
    robot.straight(430)
    robot.turn(90)

    #Drive to windmill and load units
    robot.straight(250)
    robot.straight(-40)
    wait(30)
    robot.straight(50)
    robot.straight(-40)
    wait(30)
    robot.straight(50)
    robot.straight(-40)
    wait(30)
    robot.straight(50)
    robot.straight(-200)

    robot.turn(-90)
    robot.straight(-700)

def slam_bang_finish():
    robot.straight(-400)
    robot.turn(-30)
    robot.straight(-475) #475
    robot.turn(-80) #80
    robot.straight(255  )
    robot.straight(-575)
    robot.straight(200)
 
def oil():
    '''
    # oil rig mission by Esther and Brayden
    set_straight_speed(300) 
    robot.straight(-750)
    robot.turn(53)
    robot.straight(250)

    # Pump the well 3 times
    robot.straight(-100)
    robot.straight(120)
    robot.straight(-100)
    robot.straight(120)
    '''

    # drive back energy from solar farm
    follow_line(-560, speed = -200, desired_sensor = "back", side_of_line = "left", Kp=0.3, Ki = 0.0000, Kd = 0.0)

    '''
    # reep the energy
    reep()
    follow_line(285, speed = 300, desired_sensor = "front", side_of_line = "left", Kp=0.5, Ki = 0.0000, Kd = 0.0)
    robot.turn(-55) 
    robot.straight(250)
    robot.turn(5)
    robot.straight(750)
    reset_reeper()
    '''

ev3.speaker.beep(100)
ev3.speaker.beep(900)
ev3.speaker.beep(100)
ev3.speaker.beep(900)



# Call desired menu system
# menu1()
oil()

# reep()
# reset_reeper()


