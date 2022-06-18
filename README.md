# gim4305-modeling

Data https://docs.google.com/spreadsheets/d/1nlnZG5WGFuQxeDsTwgNr5HTVJFa46MuTIRdcbiKB9q4/edit#gid=0 

## Notes
0.12Nm and 0.13Nm RMS torque makes the motor housing too hot to touch! It seems like the Moteus turns off around 850 jumps at 0.2Nm. Derate temperature is 50c, fault temperature is 75c, but moteus is only reaching 46c when it turns off around 840 jumps.

## Usage
### leader_follower.py
Experimenting with unilateral, bilateral, and custom force exchange teleop modes. Found that any kind of bilateral position exchange feels very sluggish. Exchanging force leads to instability.