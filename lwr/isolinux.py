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

def generate_cfg(bootconfig):
    ret = str()
    first = True
    ret += "UI vesamenu.c32\n"
    ret += "INCLUDE stdmenu.cfg\n"
    for entry in bootconfig.entries:
        if entry['type'] is not 'linux':
            continue
        label = "%s" % (entry['description'],)
        if first:
            ret += "DEFAULT %s\n" % (label,)
        ret += "LABEL %s\n" % (label,)
        ret += "  SAY \"Booting %s...\"\n" % (entry['description'],)
        ret += "  LINUX %s\n" % (entry['kernel'],)
        if entry.get('initrd') is not None:
            ret += "  APPEND initrd=%s %s\n" % (entry['initrd'], entry.get('cmdline', ''),)
        elif entry.get('cmdline') is not None:
            ret += "  APPEND %s\n" % (entry['cmdline'],)
        ret += "\n"
        first = False
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


def install_isolinux(cdroot, mirror, suite, architecture, bootconfig):
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
        shutil.copyfile(
            os.path.join(destdir, "usr/lib/syslinux/memdisk"),
            "%s/memdisk" % (cdroot,))
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

    cfg = generate_cfg(bootconfig)
    with open("%s/%s" % (cdroot, "menu.cfg"), "w") as cfgout:
        cfgout.write(cfg)
