# Reproduction code

Code used to generate the simulations for "How does network structure impact socially reinforced diffusion?" by Jad Georges Sassine and Hazhir Rahmandad.

## Instructions

To run a simulation, simply run "python run.py" from the command line. You will
need to update the "settings.py" file to change simulation parameters, as well
as the path where all the output will be saved


### Details

In general, in simulation output will be saved in a subfolder, where the subfolder
name corresponds to the simulation parameters. The subfolder will contain different
files where each file corresponds to a rewiring probability. If a file already exists,
for example when we run multiple samples for a given set of parameters, the new output
is appended in a new line. Otherwise, the file is created.
