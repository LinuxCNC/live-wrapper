"""
live-build-ng - Live-Build NG
(C) Iain R. Learmonth 2015 <irl@debian.org>
See COPYING for terms of usage, modification and redistribution.

lbng/grub.py - Grub 2 helpers
"""

import os
import shutil
from lbng.vm import detect_kernels

class GrubConfig():
    """
    Helper class that creates a Grub 2 configuration based on a
    vmdebootstrap squashfs output directory.
    """

    def __init__(self, cdroot):
        self.versions = detect_kernels(cdroot)

    def generate_cfg(self):
        ret = "if [ ${iso_path} ] ; then\nset loopback="findiso=${iso_path}"\nfi\n\n"
        self.versions.sort(reverse=True)
        for version in self.versions:
            ret += "menuentry \"Debian GNU/Linux Live (kernel %s)\" {\n" % (version,)
            ret += "  linux  /live/vmlinuz-%s boot=live components \"${loopback}\"\n"  % (version,)
            ret += "  initrd /live/initrd.img-%s\n" % (version,)
            ret += "}\n"
        return ret

def install_grub(cdroot, cdhelp):
    shutil.copytree("%s/grub" % (cdhelp,), "%s/boot/grub" % (cdroot,))
    with open("%s/boot/grub/grub.cfg" % (cdroot,), "a") as cfgout:
        cfgout.write(GrubConfig(cdroot).generate_cfg())
    with open("%s/boot/grub/loopback.cfg" % (cdroot,), "w") as loopout:
        loopout.write("source /boot/grub/grub.cfg")
