# live-build-ng - Live-Build NG
# (C) Iain R. Learmonth 2015 <irl@debian.org>
# See COPYING for terms of usage, modification and redistribution.
#
# lbng/xorriso.py - xorriso helpers

"""
The lbng.xorriso module provides helpers for calling xorriso as part of the
image creation process.

.. note::
    This module requires that the vmdebootstrap modules be available in the
    Python path.
"""

from vmdebootstrap.base import runcmd

class Xorriso:
    """
    This class acts as a wrapper for ``xorriso`` and allows for the command
    line arguments passed to be built based on the settings given to the main
    application.
    """

    def __init__(self, image_output, isolinux=True, grub=True):
        self.image_output = image_output
        self.isolinux = isolinux
        self.grub = grub
        self.args = ['xorriso']

    def build_args(self):
        if len(self.args) > 1:
            cliapp.AppException("Attempted to rebuild xorriso arguments while"
                                "they are already defined!")
        self.args.extend(['-outdev', self.image_output])
        self.args.extend(['map', 'cdroot/', '/'])

        if self.isolinux:
            self.args.extend(['-boot_image', 'isolinux', 'dir=/boot/isolinux'])

        if self.grub:
            self.args.extend(['-as', 'mkisofs', '-eltorito-alt-boot', '-e',
                              'boot/grub/efi.img', '-no-emul-boot',
                              '-isohybrid-gpt-basdat'])

        return self.args

    def build_image(self):
        """
        This will call ``xorriso`` with the arguments built.

        .. note::
            :any:`Xorriso.build_args` must have been called before
            calling :any:`Xorriso.build_image`.

        .. warning::
            The ``xorriso`` binary must be present in the current PATH.
        """
        runcmd(self.args)
