# live-wrapper - Wrapper for vmdebootstrap for creating live images
# (C) Iain R. Learmonth 2015 <irl@debian.org>
# See COPYING for terms of usage, modification and redistribution.
#
# lwr/memtest.py - memtest helpers

import os
import shutil
import tempfile
import cliapp
from vmdebootstrap.base import runcmd

from lwr.apt_udeb import get_apt_handler

def install_memtest(cdroot, mirror, suite, architecture):
    """
    Download and unpack the memtest86+ package.
    """
    destdir = tempfile.mkdtemp()
    handler = get_apt_handler(destdir, mirror, suite, architecture)
    filename = handler.download_package('memtest86+', destdir)
    # these files are put directly into cdroot/boot
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
