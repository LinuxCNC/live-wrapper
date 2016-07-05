# live-wrapper - Wrapper for vmdebootstrap for creating live images
# (C) Iain R. Learmonth 2015 <irl@debian.org>
# See COPYING for terms of usage, modification and redistribution.
#
# lwr/grub.py - Grub 2 helpers

"""
The lwr.grub module contains helpers for GRUB 2 including the installation
of GRUB files to the cdroot and the generation of the grub.cfg and loopback.cfg
files.
"""

import os
from lwr.vm import detect_kernels

# pylint: disable=missing-docstring


class GrubConfig(object):
    """
    Helper class that creates a Grub 2 configuration based on a
    vmdebootstrap squashfs output directory.
    """

    def __init__(self, cdroot):
        self.cdroot = cdroot
        self.versions = None

    def detect(self):
        self.versions = detect_kernels(self.cdroot)

    def generate_cfg(self):
        ret = ("if [ ${iso_path} ] ; then\nset loopback=\"" +
               "findiso=${iso_path}\"\nfi\n\n")
        self.versions.sort(reverse=True)
        for version in self.versions:
            ret += "menuentry \"Debian GNU/Linux Live (kernel %s)\" {\n" % (version,)
            ret += "  linux  /live/vmlinuz-%s boot=live components \"${loopback}\"\n" % (version,)
            ret += "  initrd /live/initrd.img-%s\n" % (version,)
            ret += "}\n"
        return ret

    def generate_di_cfg(self, kernel, ramdisk):  # pylint: disable=no-self-use
        # FIXME: add gtk, advanced and other configs.
        ret = "\n"
        ret += "menuentry \"Debian Installer \" {\n"
        ret += "  linux  /d-i/%s\n" % os.path.basename(kernel)
        ret += "  initrd /d-i/%s\n" % os.path.basename(ramdisk)
        ret += "}\n"
        return ret


def install_grub(cdroot):
    """
    Can use cdroot as a relative path inside the actual cdroot.
    The d-i/ and live/ directories are used directly.
    """
    config = GrubConfig(cdroot)
    config.detect()
    with open("%s/boot/grub/grub.cfg" % (cdroot,), "a") as cfgout:
        cfgout.write(config.generate_cfg())
    with open("%s/boot/grub/loopback.cfg" % (cdroot,), "w") as loopout:
        loopout.write("source /grub/grub.cfg")


def update_grub(cdroot, kernel, ramdisk):
    config = GrubConfig(cdroot)
    with open("%s/boot/grub/grub.cfg" % (cdroot,), "a") as cfgout:
        cfgout.write(config.generate_di_cfg(kernel, ramdisk))
