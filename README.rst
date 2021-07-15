What does this tool do?

siws

tool create --from path/to/ros.focal.sandbox --bind src .

  create the given folder if it does not already exist
  creates any bind paths inside the given folder
  creates a .siws file in the given folder
    Detect graphics card!
  builds a singularity sandbox

tool shell path/to/siws root

tool shell path/to/ros.focal.sandbox

tool shell 

tool rootshell


.siws
  file that marks the root of a siws workspace
  Includes version of the workspace
  parse with Python's configparser module
