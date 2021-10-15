# CISProgrammingAssignments
Programming Assignments for Computer Integrated Surgery 1 (FA'21)

# Programming Assignment 1

Assignment 1: Basic transformations & pivot calibration
The main focus of assignment 1 is development of mathematical tools and subroutines that you may use in subsequent assignments. The specific goals are:
1. Develop (or develop proficiency with) a Cartesian math package for 3D points, rotations, and frame transformations.
2. Develop a 3D point set to 3D point set registration algorithm
3. Develop a “pivot” calibration method.
4. Given a distortion calibration data set, as described above, compute the “expected” values C! (expected) for the C! :
ii
a. For each calibration data frame ! ! ! ! ! ! , compute the [,D,",D ,A,",A ,C,",C ]
1 ND 1 NA 1 NC
transformation FD between optical tracker and EM tracker coordinates. I.e., compute
a f r a m e F s u c h t h a t D! = F • d! . D jDj
!
b. Similarly, compute a transformation FA between calibration object and optical tracker !
coordinates. I.e., A = F • a . jAj
! c. Given F and F , compute C!(expected) = F−1 •F •c .
DAiDAi d. Output C! (expected) (see file formats below)
i
You will use this code in Assignment 2 to calibrate for the distortion.
5. Apply the EM tracking data to perform a pivot calibration for the EM probe and determine the position relative to the EM tracker base coordinate system of the dimple in the calibration post. The suggested procedure is as follows.
a. Use the first “frame” of pivot calibration data to define a local “probe” coordinate
system and use this to compute g! the midpoint of the observed points
One simple method is as follows. First compute
! G! = F [ k ] • g
.
jGj
!1∑! G0=N G
c. Now use the method discussed in class to solve the system 6
!
j
j G
Then translate the observations relative to this midpoint. I.e., compute
g=G−G jj0
There are alternative methods, many of which involve rotating g! . But this isn’t j
particularly critical. Your pivot calibration will determine a tip coordinates !t G
defined in the same probe coordinate system. I.e., if FG(t) gives the position and orientation of the pointer body at time t with respect to some tracker coordinate
!
system, then FG(t)i tG gives the coordinates of the pointer tip with respect to the same
tracker coordinate system.
b. For each “frame” k of pivot data, compute a transformation FG [k] such that
!!
!
P" = F [ k ] • "t
dimple
G G
!
6. Apply the optical tracking data to perform a pivot calibration of the optical tracking probe. The suggested method is the same as above except that you should first use your value for FD
to transform the optical tracker beacon positions into EM tracker coordinates. Note that the optical tracker may not be in exactly the same position and orientation with respect to the EM tracker base for each observation frame of optical tracker data, so this is an important step.
