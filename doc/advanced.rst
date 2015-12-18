Advanced Topics
===============

Bootloader Customisation
------------------------

By default, both ISOLINUX (for BIOS boot) and GRUB 2 (for EFI boot) are
installed into the images. A ``loopback.cfg`` file is also installed to allow
for the image to be booted while still an ISO image in a filesystem.

You can pass ``--no-isolinux`` to prevent the installation of ISOLINUX to the
image if you do not want ISOLINUX.

You can pass ``--no-grub`` to prevent the installation of GRUB to the image.

If you do not want GRUB installed but you would still like the ``loopback.cfg``
file to be installed, you can pass ``--grub-loopback-only``.

