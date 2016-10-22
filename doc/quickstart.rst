Quickstart
==========

Super Fast Quickstart
---------------------

Building images with live-wrapper is quite simple. For the impatient:

.. code::

  $ sudo apt install live-wrapper
  $ sudo lwr

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

By default, the ISO image will be built using the ``stable`` distribution. If
you'd like to build using ``testing`` or ``unstable`` you can pass the ``-d``
parameter to live-wrapper like so:

.. code-block:: shell

  sudo lwr -d testing

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

.. code::

  $ sudo lwr -e vim -t science-typesetting

Next Steps
----------

To learn more about using live-wrapper, you can read the man page or check out
the :doc:`advanced` section of this documentation.
