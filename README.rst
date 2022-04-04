sish - Apptainer Shells for Developement
----------------------------------------

``sish`` simplifies creating and opening shells into `Apptainer <https://apptainer.org/>`_ containers for the use case of developing software inside of them.

Tutorial
========

Part 1: The simple case - one container
+++++++++++++++++++++++++++++++

Create a folder with some source code.

.. code-block:: console

  $ mkdir -p my_workspace/src
  $ cd my_workspace

Let's make an Ubuntu Focal container **in this folder** and give it the name ``focal``.

.. code-block:: console

  $ create-sish-container --bind src/ --from docker://ubuntu:focal --name focal

Open a root shell and install any extra software you need in the container.

.. code-block:: console

  $ rsish

Open a normal shell and get to work

.. code-block:: console

  $ sish


Part 2: Multiple containers in one folder
+++++++++++++++++++++++++++++++++++++++++

Let's make an Ubuntu Bionic container **in this folder** and give it the name ``bionic``.

.. code-block:: console

  $ create-sish-container --bind src/ --from docker://ubuntu:bionic --name bionic

Open a root shell and install any extra software you need in the container.

.. code-block:: console

  $ rsish bionic

Open a normal shell and get to work

.. code-block:: console

  $ sish bionic

Still need access to the Ubuntu Focal container?
It's still there, but now you need to use the container's name when opening shells.

.. code-block:: console

  $ sish focal

I've used singularity/Apptainer before - what does this do for me?
==================================================================

This tool creates an Apptainer sandbox with reasonable options and binds for developing code.
Sandboxes are persistent, so no need to worry about shutting down your computer and losing your work.
It uses ``--fakeroot`` so you don't need to use ``sudo`` or be root to start a container.
It assumes an NVidia graphics card is installed and passes in the ``--nv`` flag.
