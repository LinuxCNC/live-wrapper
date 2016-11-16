# live-wrapper - Wrapper for vmdebootstrap for creating live images
# (C) Iain R. Learmonth 2015 <irl@debian.org>
# See COPYING for terms of usage, modification and redistribution.
#
# lwr/bootloader.py - Bootloader helpers

import os
from lwr.vm import detect_kernels

class BootloaderConfig(object):

    def __init__(self, cdroot):
        self.cdroot = cdroot
        self.entries = []

    def add_live(self):
        # FIXME: need declarative paths
        self.versions = detect_kernels(self.cdroot)
        self.versions.sort(reverse=True)
        for version in self.versions:
            self.entries.append({
                                 'description': 'Debian GNU/Linux Live (kernel %s)' % (version,),
                                 'type': 'linux',
                                 'kernel': '/live/vmlinuz-%s' % (version,),
                                 'cmdline': 'boot=live components',
                                 'initrd': '/live/initrd.img-%s' % (version,),
                                })

    def add_installer(self, kernel, ramdisk):  # pylint: disable=no-self-use
        self.entries.append({
                             'description': 'Graphical Debian Installer',
                             'type': 'linux',
                             'kernel': '/d-i/gtk/%s' % (os.path.basename(kernel),),
                             'initrd': '/d-i/gtk/%s' % (os.path.basename(ramdisk),),
                            })
        self.entries.append({
                             'description': 'Debian Installer',
                             'type': 'linux',
                             'kernel': '/d-i/%s' % (os.path.basename(kernel),),
                             'initrd': '/d-i/%s' % (os.path.basename(ramdisk),),
                            })

    def add_memtest(self):
        self.entries.append({
                             'description': 'memtest86',
                             'type': 'linux',
                             'kernel': '/boot/memtest86+.bin',
                            })


    def add_hdt(self):
        self.entries.append({
                             'description': 'Hardware Detection Tool (HDT)',
                             'type': 'com32',
                             'kernel': '/isolinux/hdt.c32',
                            })

    def add_submenu(self, description, loadercfg):
        self.entries.append({
                             'description': '%s' % (description),
                             'type': 'menu',
                             'subentries': loadercfg,
                            })
