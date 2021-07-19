siws - Singularity Workspaces
-----------------------------

``siws`` simplifies creating and opening shells into `Singularity <https://singularity.hpcng.org/>` containers for the purpose of developing software inside of them.

How do I use it?
==================

First use ``siws create`` to create a container with access to your source code.
Any time you want to be in that container, use ``siws rootshell`` or ``siws shell``.
The former opens a shell as the root user, and the latter opens a shell as your current user.
Use ``rootshell`` when you want to install dependencies, and ``shell`` when you want to build and test your code.

Here's an example.

.. code-block:: console

  # Make a folder and put some code in it
  $ mkdir ~/siws_bionic_example/ && cd ~/siws_bionic_example
  $ git clone https://github.com/octocat/Hello-World.git
  # ...
  # Create a container running Ubuntu Bionic that has access to Hello-World
  $ siws create --from library://ubuntu:18.04 --bind Hello-World ~/siws_bionic_example
  # ...
  # Open a shell as root to install important dependencies
  $ siws rootshell
  Singularity> apt update && apt install -y cowsay
  # ...
  # Exit the shell with Ctrl-D
  # Open a normal shell and do important work
  $ siws shell
  Singularity> cowsay < Hello-World/README


I've used singularity before - what does this do for me?
========================================================

This tool creates a Singularity sandbox and offers shortcuts for getting shells into the container with binds.
You could do most of what this tool does with bash aliases.
