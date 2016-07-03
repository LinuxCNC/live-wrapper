# live-wrapper - Wrapper for vmdebootstrap for creating live images
# (C) Iain R. Learmonth 2015 <irl@debian.org>
# See COPYING for terms of usage, modification and redistribution.
#
# lwr/isolinux.py - ISOLINUX helpers

"""
The lwr.isolinux module contains helpers for isolinux including the
installation of isolinux files to the cdroot and the generation of the
isolinux.cfg files.
Directory listing of /isolinux/
advanced.cfg boot.cat hdt.c32 install.cfg isolinux.bin isolinux.cfg
ldlinux.c32 libcom32.c32 libutil.c32 live.cfg menu.cfg splash.png
stdmenu.cfg vesamenu.c32
"""

import os
import shutil
import tempfile
import cliapp
from vmdebootstrap.base import runcmd
from lwr.vm import detect_kernels
from lwr.apt_udeb import AptUdebDownloader

# pylint: disable=missing-docstring


class ISOLINUXConfig(object):
    """
    Helper class that creates an ISOLINUX configuration based on a
    vmdebootstrap squashfs output directory.
    """

    def __init__(self, cdroot):
        self.cdroot = cdroot
        self.versions = None

    def detect(self):
        self.versions = detect_kernels(self.cdroot)

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
        ret += "  APPEND initrd=/d-i/%s\n" % ramdisk
        ret += "}\n"
        return ret

def prepare_download(destdir, mirror, suite, architecture):
    apt_handler = AptUdebDownloader(destdir)
    apt_handler.mirror = mirror
    apt_handler.architecture = architecture
    apt_handler.suite = suite
    apt_handler.components = ['main']
    apt_handler.prepare_apt()
    return apt_handler


def install_isolinux(cdroot, mirror, suite, architecture):
    """
    Download and unpack the correct syslinux-common
    and isolinux packages for isolinux support.
    """
    if not os.path.exists("%s/isolinux" % (cdroot,)):
        os.mkdir("%s/isolinux" % (cdroot,))
    ISOLINUX_DIR = "%s/isolinux" % (cdroot,)
    destdir = tempfile.mkdtemp()
    handler = prepare_download(destdir, mirror, suite, architecture)
    filename = handler.download_package('syslinux-common', destdir)
    if filename:
        runcmd(['dpkg', '-x', filename, destdir])
        shutil.copyfile(
            os.path.join(destdir, "usr/lib/syslinux/modules/bios/ldlinux.c32"),
            "%s/ldlinux.c32" % (ISOLINUX_DIR,))
    else:
        raise cliapp.AppException('Unable to download syslinux-common')
    filename = handler.download_package('isolinux', destdir)
    if filename:
        runcmd(['dpkg', '-x', filename, destdir])
        shutil.copyfile(
            os.path.join(destdir, "usr/lib/ISOLINUX/isolinux.bin"),
            "%s/isolinux.bin" % (ISOLINUX_DIR,))
    else:
        raise cliapp.AppException('Unable to download isolinux')
    handler.clean_up_apt()
    shutil.rmtree(destdir)
    config = ISOLINUXConfig(cdroot)
    config.detect()
    with open("%s/isolinux.cfg" % (ISOLINUX_DIR,), "w") as cfgout:
        cfgout.write(config.generate_cfg())


def update_isolinux(cdroot, kernel, ramdisk):
    isolinux_dir = "%s/boot/isolinux" % (cdroot,)
    config = ISOLINUXConfig(cdroot)
    with open("%s/isolinux.cfg" % (isolinux_dir,), "a") as cfgout:
        cfgout.write(config.generate_di_cfg(kernel, ramdisk))
