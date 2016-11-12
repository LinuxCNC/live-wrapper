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
import sys
import shutil
import string
import fileinput
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
        # FIXME: need declarative paths
        self.versions = detect_kernels(os.path.join(self.cdroot, '..'))

    def generate_cfg(self):
        ret = str()
        self.versions.sort(reverse=True)
        first = True
        #ret += "DEFAULT live\n"
        #ret += "  menu default\n"
        ret += "UI vesamenu.c32\n"
        for version in self.versions:
            label = "Debian Live (%s)\n" % (version,)
            if first:
                ret += "DEFAULT %s\n" % (label,)
            ret += "LABEL %s\n" % (label,)
            if first:
                ret += "  MENU DEFAULT\n"
            ret += "  SAY Booting Debian GNU/Linux Live (kernel %s)...\" \n" % (version,)
            ret += "  KERNEL /live/vmlinuz-%s\n" % (version,)
            ret += "  APPEND initrd=/live/initrd.img-%s boot=live components\n" % (version,)
            ret += "\n"
            first = False
        return ret

    def generate_di_cfg(self, kernel, ramdisk, gtk=False):  # pylint: disable=no-self-use
        if gtk:
            ret = "\n"
            ret += "LABEL Graphical Debian Installer\n"
            ret += "  SAY Booting Debian Installer...\" {\n"
            ret += "  KERNEL /d-i/gtk/%s\n" % os.path.basename(kernel)
            ret += "  APPEND initrd=/d-i/gtk/%s\n" % os.path.basename(ramdisk)
            ret += "}\n"
        else:
            ret = "\n"
            ret += "LABEL Debian Installer\n"
            ret += "  SAY Booting Debian Installer...\" {\n"
            ret += "  KERNEL /d-i/%s\n" % os.path.basename(kernel)
            ret += "  APPEND initrd=/d-i/%s\n" % os.path.basename(ramdisk)
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


def install_memtest(cdroot, mirror, suite, architecture):
    """
    Download and unpack the memtest86+ package.
    """
    destdir = tempfile.mkdtemp()
    handler = prepare_download(destdir, mirror, suite, architecture)
    filename = handler.download_package('memtest86+', destdir)
    # these files are put directly into cdroot/live
    memtest86_file = 'memtest86+.bin'
    if filename:
        runcmd(['dpkg', '-x', filename, destdir])
        shutil.copyfile(
            os.path.join(destdir, "boot/%s" % memtest86_file),
            "%s/%s" % (cdroot, memtest86_file))
    else:
        handler.clean_up_apt()
        shutil.rmtree(destdir)
        raise cliapp.AppException('Unable to download memtest86+')
    handler.clean_up_apt()
    shutil.rmtree(destdir)

def add_memtest_menu(cdroot, config_file):
    memstr='''label memtest
menu label ^Memory Diagnostic Tool (memtest86+)
linux ../live/memtest86+.bin
'''
    with open("%s/%s" % (cdroot, config_file), "a") as cfgout:
        cfgout.write(memstr)


def add_hdt_menu(cdroot, config_file):
    hdtstr='''label hdt
menu label ^Hardware Detection Tool (HDT)
com32 hdt.c32
'''
    with open("%s/%s" % (cdroot, config_file), "a") as cfgout:
        cfgout.write(hdtstr)


def install_isolinux(cdroot, mirror, suite, architecture):
    """
    Download and unpack the correct syslinux-common
    and isolinux packages for isolinux support.
    ISOLINUX looks first in boot/isolinux/ then isolinux/ then /
    This function puts all files into isolinux/
    """
    destdir = tempfile.mkdtemp()
    handler = prepare_download(destdir, mirror, suite, architecture)
    filename = handler.download_package('syslinux-common', destdir)
    # these files are put directly into cdroot/isolinux
    syslinux_files = [
        'ldlinux.c32', 'libcom32.c32', 'vesamenu.c32',
        'libutil.c32', 'libmenu.c32', 'libgpl.c32', 'hdt.c32'
    ]
    if filename:
        runcmd(['dpkg', '-x', filename, destdir])
        for syslinux_file in syslinux_files:
            shutil.copyfile(
                os.path.join(destdir, "usr/lib/syslinux/modules/bios/%s" % syslinux_file),
                "%s/%s" % (cdroot, syslinux_file))
    else:
        handler.clean_up_apt()
        shutil.rmtree(destdir)
        raise cliapp.AppException('Unable to download syslinux-common')
    filename = handler.download_package('isolinux', destdir)
    if filename:
        runcmd(['dpkg', '-x', filename, destdir])
        shutil.copyfile(
            os.path.join(destdir, "usr/lib/ISOLINUX/isolinux.bin"),
            "%s/isolinux.bin" % cdroot)
    else:
        handler.clean_up_apt()
        shutil.rmtree(destdir)
        raise cliapp.AppException('Unable to download isolinux')
    handler.clean_up_apt()
    shutil.rmtree(destdir)

def add_live_menu(cdroot, cfg_file):
    config = ISOLINUXConfig(cdroot)
    config.detect()
    with open("%s/%s" % (cdroot, cfg_file), "w") as cfgout:
        cfgout.write(config.generate_cfg())

def add_installer_menu(cdroot, cfg_file, kernel, ramdisk):
    config = ISOLINUXConfig(cdroot)
    config.detect()
    with open("%s/%s" % (cdroot, cfg_file), "w") as cfgout:
        cfgout.write(config.generate_di_cfg(kernel, ramdisk, gtk=False))
        cfgout.write(config.generate_di_cfg(kernel, ramdisk, gtk=True))
