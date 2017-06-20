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
from lwr.apt_udeb import get_apt_handler

# pylint: disable=missing-docstring

def generate_cfg(bootconfig, submenu=False):
    ret = str()
    if not submenu:
        first = True
        ret += "INCLUDE stdmenu.cfg\n"
        ret += "MENU title Main Menu\n"
    else:
        first = False
     
    for entry in bootconfig.entries:
        label = "%s" % (entry['description'],)
        if entry['type'] is 'menu':
           if entry['subentries'].is_empty(["menu", "linux", "linux16", "com32"]):
               continue
           ret += "MENU begin advanced\n"
           ret += "MENU title %s\n" % (label,)
           ret += generate_cfg(entry['subentries'], submenu=True) 
           ret += " LABEL mainmenu \n "
           ret += " MENU label Back\n "
           ret += " MENU exit\n "
           ret += " MENU end\n "
          
        # do not want to default to menus
        if first:
            ret += "DEFAULT %s\n" % (label,)
            first = False
        if entry['type'].startswith('linux') or entry['type'] is 'com32':
            type = 'linux' if entry['type'].startswith('linux') else entry['type']
            ret += "LABEL %s\n" % (label,)
            ret += "  SAY \"Booting %s...\"\n" % (entry['description'],)
            ret += "  %s %s\n" % (entry['type'], entry['kernel'],)
            if entry.get('initrd') is not None:
                ret += "  APPEND initrd=%s %s\n" % (entry['initrd'], entry.get('cmdline', ''),)
            elif entry.get('cmdline') is not None:
                ret += "  APPEND %s\n" % (entry['cmdline'],)
        ret += "\n"
    return ret

def install_isolinux(cdroot, mirror, suite, architecture, bootconfig):
    """
    Download and unpack the correct syslinux-common
    and isolinux packages for isolinux support.
    ISOLINUX looks first in boot/isolinux/ then isolinux/ then /
    This function puts all files into isolinux/
    """
    destdir = tempfile.mkdtemp()
    handler = get_apt_handler(destdir, mirror, suite, architecture)
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

    # Fix the menu display size in stdmeny.cfg (#861421)
    runcmd(['sed', '-i', 's,menu rows 12,menu rows 8,g',
                os.path.join(cdroot, 'stdmenu.cfg')])
