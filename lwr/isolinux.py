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
        'libutil.c32'
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
    config = ISOLINUXConfig(cdroot)
    config.detect()
    with open("%s/isolinux.cfg" % cdroot, "w") as cfgout:
        cfgout.write(config.generate_cfg())


def move_files(src, dest):
    for filename in os.listdir(src):
        src_path = os.path.join(src, filename)
        if os.path.isdir(src_path) or os.path.islink(src_path):
            continue
        shutil.copyfile(
            src_path,
            os.path.join(dest, filename))
        os.unlink(src_path)
        cfg_file = os.path.join(dest, filename)
        if cfg_file.endswith('.cfg'):
            for line in fileinput.input(cfg_file, inplace=1):
                lineno = 0
                lineno = string.find(line, '%install%')
                if lineno > 0:
                    line = line.replace('%install%', 'd-i')
                sys.stdout.write(line)

def update_isolinux(cdroot, kernel, ramdisk):
    config = ISOLINUXConfig(cdroot)
    bootdir = os.path.join(cdroot, '..', 'boot')
    isolinux = os.path.join(cdroot, '..', 'isolinux')
    # move files out of cdroot/boot/ into cdroot/isolinux/
    move_files(bootdir, isolinux)
    # need to remove default installgui
    # need to add live.cfg to menu.cfg
