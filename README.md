# Student-Robotics-Simulator
The standard Student Robotics Simulator with a collection of classes and functions to make everything easier.

To install:

I'VE ONLY BEEN ABLE TO GET THIS TO WORK WITH LINUX!!

Make sure you have install python2.7. It is installed by defualt on many systems.

clone the git repositiory or download it.

navigate to the correct Directory in a terminal:


run:

$> pip install -r requirements.txt

This will install all the python dependencies

Then run:

$> sudo apt-get install python-dev python-pip python-pygame python-yaml
$> sudo pip install pypybox2d

This will install other dependencies


Creating and running Files:

You can either write code into /robot.py or into /ben/main.py

To start the simulation run:

$> python <robot_file_1.py> <robot_file_2.py> <robot_file_3.py> <robot_file_4.py>

To only run one ommit the other files. e.g:

$> python run.py robot.py

It is important to note that matplotlib cannot be running on more than one robot file at a time. Something to do with threading prevents it from working correctly.

Coding the robot:

Refer to https://www.studentrobotics.org/docs/ for information on the default objects and methods.
The files in the folder ben provide extra functionality. To use them import them into your file. See main.py as an example.



