# live-wrapper - Wrapper for vmdebootstrap for creating live images
# (C) Iain R. Learmonth 2015 <irl@debian.org>
# See COPYING for terms of usage, modification and redistribution.
#
# lwr/grub.py - Grub 2 helpers

"""
The lwr.grub module contains helpers for GRUB 2 including the installation
of GRUB files to the cdroot and the generation of the grub.cfg and loopback.cfg
files.
"""

import os

def generate_cfg(bootconfig, submenu=False):
    if not submenu:
        ret = ("if [ ${iso_path} ] ; then\nset loopback=\"" +
               "findiso=${iso_path}\"\nfi\n\n")
    else:
        ret = str()
    for entry in bootconfig.entries:
        if entry['type'] == "menu":
            ret += "submenu \"%s\" {\n"  % (entry['description'],)
            ret += generate_cfg(entry['subentries'], submenu=True)
            ret += "}\n"
        if entry['type'] == "linux": 
            ret += "menuentry \"%s\" {\n" % (entry['description'],)
            ret += "  linux  %s %s \"${loopback}\"\n" % (entry['kernel'], entry.get('cmdline', ''),)
            if entry.get('initrd') is not None:
                ret += "  initrd %s\n" % (entry['initrd'],)
            ret += "}\n"
    return ret

def install_grub(cdroot, bootconfig):
    """
    Can use cdroot as a relative path inside the actual cdroot.
    The d-i/ and live/ directories are used directly.
    """
    cfg = generate_cfg(bootconfig)
    with open("%s/boot/grub/grub.cfg" % (cdroot,), "a") as cfgout:
        cfgout.write(cfg)
    with open("%s/boot/grub/loopback.cfg" % (cdroot,), "w") as loopout:
        loopout.write("source /grub/grub.cfg")
