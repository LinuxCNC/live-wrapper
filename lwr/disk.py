# live-wrapper - Wrapper for vmdebootstrap for creating live images
# (C) Iain R. Learmonth 2015 <irl@debian.org>
# See COPYING for terms of usage, modification and redistribution.
#
# lwr/disk.py - .disk folder helpers

"""
This module provides helpers for generating the metadata stored in .disk/ on
the cdroot.
Directory listing of /.disk/
-r--r--r--   1    0    0              29 Sep  8 2015 [ 194732 00]  archive_trace
-r--r--r--   1    0    0               5 Sep  8 2015 [ 194733 00]  base_components
-r--r--r--   1    0    0               0 Sep  8 2015 [    907 00]  base_installable
-r--r--r--   1    0    0               5 Sep  8 2015 [ 194734 00]  cd_type
-r--r--r--   1    0    0              89 Sep  8 2015 [ 194735 00]  info
-r--r--r--   1    0    0              49 Sep  8 2015 [ 194736 00]  udeb_include
"""

import os


def install_disk_info(cdroot):
    """
    This function creates the .disk/info metadata and installs it into the
    cdroot.
    """

    os.makedirs(os.path.join(cdroot, ".disk"))
    with open(os.path.join(cdroot, ".disk", "info", "w")) as i:
        i.write("HELLO")
