# Student-Robotics-Simulator
The standard Student Robotics Simulator with a collection of classes and functions to make everything easier.

To install:

I'VE ONLY BEEN ABLE TO GET THIS TO WORK WITH LINUX!!

Make sure you have install python2.7. It is installed by defualt on many systems.

clone the git repositiory or download it.

navigate to the correct Directory in a terminal:


run:

$> sudo apt-get install python-dev python-pip python-pygame python-yaml python-tk python-matplotlib

$> sudo pip install setuptools pypybox2d




Creating and running Files:

You can either write code into robot/robot.py or into robot/main.py

To start the simulation run:

$> python run.py robot_file.py

To run a Simulation of multiple robots (4 max), run:

$> python run.py <robot_file_1.py> <robot_file_2.py> <robot_file_3.py> <robot_file_4.py>



Coding the robot:

Refer to https://www.studentrobotics.org/docs/ for information on the default objects and methods.
The files in the folder robot/ben provide extra functionality. To use them import them into your file. See main.py as an example.



