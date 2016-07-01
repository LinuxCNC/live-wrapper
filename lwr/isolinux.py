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

# pylint: disable=missing-docstring


class ISOLINUXConfig(object):
    """
    Helper class that creates an ISOLINUX configuration based on a
    vmdebootstrap squashfs output directory.
    """

    def detect(self):
        self.versions = detect_kernels()

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

    def generate_di_cfg(self, kernel, ramdisk):  # pylint: disable=no-self-use
        ret = "\n"
        ret += "LABEL Debian Installer\n"
        ret += "  SAY Booting Debian Installer...\" {\n"
        ret += "  KERNEL /d-i/%s\n" % kernel
        ret += "  APPEND initrd=/d-i/%s-%s\n" % ramdisk
        ret += "}\n"
        return ret


def install_isolinux(cdroot):
    if not os.path.exists("%s/boot" % (cdroot,)):
        os.mkdir("%s/boot" % (cdroot,))
    ISOLINUX_DIR = "%s/boot/isolinux" % (cdroot,)
    os.mkdir(ISOLINUX_DIR)
    # FIXME: cannot depend on sysvinit-common - could be the wrong arch or suite
    shutil.copyfile("/usr/lib/syslinux/modules/bios/ldlinux.c32",
                    "%s/ldlinux.c32" % (ISOLINUX_DIR,))
    shutil.copyfile("/usr/lib/ISOLINUX/isolinux.bin",
                    "%s/isolinux.bin" % (ISOLINUX_DIR,))
    config = ISOLINUXConfig()
    config.detect()
    with open("%s/isolinux.cfg" % (ISOLINUX_DIR,), "w") as cfgout:
        cfgout.write(config.generate_cfg())


def update_isolinux(cdroot, kernel, ramdisk):
    isolinux_dir = "%s/boot/isolinux" % (cdroot,)
    config = ISOLINUXConfig()
    with open("%s/isolinux.cfg" % (isolinux_dir,), "a") as cfgout:
        cfgout.write(config.generate_di_cfg(kernel, ramdisk))
