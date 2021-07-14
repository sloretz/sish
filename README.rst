What does this tool do?

singws

tool create --from path/to/ros.focal.sandbox --bind src .

  create the given folder if it does not already exist
  creates any bind paths inside the given folder
  creates a .singws file in the given folder
    Detect graphics card!
  builds a singularity sandbox

tool shell path/to/singws root

tool shell path/to/ros.focal.sandbox

tool shell 

tool rootshell


.singws
  file that marks the root of a singws workspace
  Includes version of the workspace
  parse with Python's configparser module
