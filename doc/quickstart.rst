Quickstart
==========

Super Fast Quickstart
---------------------

Building images with live-wrapper is quite simple. For the impatient:

.. code-block:: shell

 sudo apt install live-wrapper
 sudo lwr

This will build you a file named ``output.iso`` in the current directory
containing a minimal live-image.

.. warning::

 Currently live-wrapper will create a lot of files and directories in the
 current working directory. There is a TODO item to move these to a temporary
 location and clean up afterwards, though this has not yet been fully
 implemented. You may want to use an empty directory to run ``lwr`` in.

Customising the Image
---------------------

There are a number of supported command-line arguments that can be passed to
live-wrapper. These change the behaviour to create a customised image.

Changing the Distribution
~~~~~~~~~~~~~~~~~~~~~~~~~

By default, the ISO image will be built using the ``stretch`` distribution. If
you'd like to build using ``buster`` or ``sid`` you can pass the ``-d``
parameter to live-wrapper like so:

.. code-block:: shell

 sudo lwr -d buster

.. note::

 You must use the codename, and not the suite (e.g. stable), when specifying
 the distribution.

Using an Alternative Mirror
~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default, ``vmdebootstrap`` will use the mirror configured in your
``/etc/apt/sources.list``. If you have a faster mirror available, you may want
to change the mirror you're using to create the image. You can do this with the
``-m`` parameter:

.. code-block:: shell

 sudo lwr -m http://localhost/debian/

Customising Packages
~~~~~~~~~~~~~~~~~~~~

There are two methods of specifying extra packages to be installed into the
live image: the ``-t`` and the ``-e`` paramaters. The difference between these
two parameters is that the list of tasks given to ``-e`` is passed to
``debootstrap`` for installation as part of the initial root filesystem
creation, whereas the packages passed to ``-t`` are installed as part of the
``vmdebootstrap`` hook.

This essentially means that any packages installed using ``-e`` will *not* have
their "Recommends" installed, but will have their "Depends" installed while
packages installed using ``-t`` will have both installed making ``-t`` the
suitable place for the installation of task packages.

There is no reason you cannot pass your entire package list to ``-t``, these
are seperated mainly to help with the readability of parameters passed to
live-wrapper.

For example:

.. code-block:: shell

 sudo lwr -e vim -t science-typesetting

Testing the Image with QEMU
---------------------------

You can easily test your created live images with QEMU.

.. warning:: You will need to increase the amount of memory available to
             QEMU when running the live image. The image will crash if run
             with the default memory limit.

To test the image using BIOS boot:

.. code-block:: shell

 qemu-system-x86_64 -m 2G -cdrom live.iso

For EFI boot you will need to install the ``ovmf`` package and then run:


.. code-block:: shell

 qemu-system-x86_64 -bios /usr/share/ovmf/OVMF.fd -m 2G -cdrom live.iso 

To test with an emulated USB device, run:

.. code-block:: shell

 qemu-system-x86_64 -m 2G -usbdevice disk:live.iso

To test the speech synthesis installer option, you will need to add the
following to the QEMU invocation:

.. code-block:: shell

 -soundhw sb16,es1370,adlib

.. note::

 Using -hda to attach the disk image will prevent the installer from detecting
 the "CD-ROM" as this is not a removable device, it is an emulated attached hard
 disk drive.

Next Steps
----------

To learn more about using live-wrapper, you can read the man page or check out
the :doc:`advanced` section of this documentation.
