# live-wrapper - Wrapper for vmdebootstrap for creating live images
# (C) Iain R. Learmonth 2015 <irl@debian.org>
# See COPYING for terms of usage, modification and redistribution.
#
# lwr/isolinux.py - ISOLINUX helpers

"""
The lwr.isolinux module contains helpers for isolinux including the
installation of isolinux files to the cdroot and the generation of the
isolinux.cfg files.
"""

import os
import shutil
from lwr.vm import detect_kernels


class ISOLINUXConfig:
    """
    Helper class that creates an ISOLINUX configuration based on a
    vmdebootstrap squashfs output directory.
    """

    def __init__(self, cdroot):
        self.versions = detect_kernels(cdroot)

    def generate_cfg(self):
        ret = str()
        self.versions.sort(reverse=True)
        first = True
        ret += "DEFAULT live\n"
        for version in self.versions:
            if first:
                ret += "LABEL live\n"
            else:
                ret += "LABEL live-%s\n" % (version,)
            ret += "  SAY Booting Debian GNU/Linux Live (kernel %s)...\" {\n" % (version,)
            ret += "  KERNEL /live/vmlinuz-%s\n" % (version,)
            ret += "  APPEND initrd=/live/initrd.img-%s boot=live components\n" % (version,)
            ret += "}\n"
            first = False
        return ret


def install_isolinux(cdroot):
    if not os.path.exists("%s/boot" % (cdroot,)):
        os.mkdir("%s/boot" % (cdroot,))
    ISOLINUX_DIR = "%s/boot/isolinux" % (cdroot,)
    os.mkdir(ISOLINUX_DIR)
    shutil.copyfile("/usr/lib/syslinux/modules/bios/ldlinux.c32",
                    "%s/ldlinux.c32" % (ISOLINUX_DIR,))
    shutil.copyfile("/usr/lib/ISOLINUX/isolinux.bin",
                    "%s/isolinux.bin" % (ISOLINUX_DIR,))
    with open("%s/isolinux.cfg" % (ISOLINUX_DIR,), "w") as cfgout:
        cfgout.write(ISOLINUXConfig(cdroot).generate_cfg())
