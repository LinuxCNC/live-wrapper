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

    def add_installer(self, kernel, ramdisk, extra=''):  # pylint: disable=no-self-use
        self.entries.append({
                             'description': 'Graphical Debian Installer',
                             'type': 'linux',
                             'kernel': '/d-i/gtk/%s' % (os.path.basename(kernel),),
                             'initrd': '/d-i/gtk/%s' % (os.path.basename(ramdisk),),
                             'cmdline': 'append video=vesa:ywrap,mtrr vga=788 ' + extra
                            })
        self.entries.append({
                             'description': 'Debian Installer',
                             'type': 'linux',
                             'kernel': '/d-i/%s' % (os.path.basename(kernel),),
                             'initrd': '/d-i/%s' % (os.path.basename(ramdisk),),
                             'cmdline': extra
                            })
        self.entries.append({
                             'description': 'Debian Installer with Speech Synthesis',
                             'type': 'linux',
                             'kernel': '/d-i/gtk/%s' % (os.path.basename(kernel),),
                             'initrd': '/d-i/gtk/%s' % (os.path.basename(ramdisk),),
                             'cmdline': 'speakup.synth=soft ' + extra,
                            })
    def add_live_localisation(self):
        # FIXME: need declarative paths
        self.versions = detect_kernels(self.cdroot)
        self.versions.sort(reverse=True)
        with open('/usr/share/live-wrapper/languagelist', 'r') as f:
            lines = f.readlines()
        lang_lines = [ line for line in lines if not line.startswith('#') ]
        for line in lang_lines:
            language = line.split(';') 
            for version in self.versions:
                self.entries.append({
                                 'description': '%s (%s)' % (language[1], language[0],),
                                 'type': 'linux',
                                 'kernel': '/live/vmlinuz-%s' % (version,),
                                 'cmdline': 'boot=live components locales=%s' % (language[5],),
                                 'initrd': '/live/initrd.img-%s' % (version,),
                                })


    def add_submenu(self, description, loadercfg):
        self.entries.append({
                             'description': '%s' % (description),
                             'type': 'menu',
                             'subentries': loadercfg,
                            })

    def is_empty(self, supported_types):
        for entry in self.entries:
            if entry['type'] in supported_types:
                print("Found %r in %r" % (entry, supported_types,))
                return False
        return True
