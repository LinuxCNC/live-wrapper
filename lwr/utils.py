# live-wrapper - Wrapper for vmdebootstrap for creating live images
# (C) 2016 Neil Williams <codehelp@debian.org>
# See COPYING for terms of usage, modification and redistribution.
#
# lwr/utils.py - data utilities for suites and url information

"""
General utility functions for URLs or handling differences between
suites, architectures or other variants.
"""

import urlparse
import requests
import cliapp

KERNEL = 'vmlinuz'
RAMDISK = 'initrd.gz'
CD_INFO = 'debian-cd_info.tar.gz'


def check_url(url):
    """
    Check that constructed URLs actually give a HTTP 200.
    """
    res = requests.head(url, allow_redirects=True, timeout=30)
    if res.status_code != requests.codes.OK:  # pylint: disable=no-member
        # try using (the slower) get for services with broken redirect support
        res = requests.get(
            url, allow_redirects=True, stream=True, timeout=30)
        if res.status_code != requests.codes.OK:  # pylint: disable=no-member
            raise cliapp.AppException("Resources not available at '%s'" % url)

def cdrom_image_url(mirror, suite, architecture, gtk=False, daily=False):
    """
    Create checked URLs for the di helpers.
    Returns a tuple of base_url, kernel, ramdisk, cd_info in that order.
    """
    if not daily:
        # urlparse.urljoin refuses to use existing subdirs which start with /
        if not mirror.endswith('/'):
            mirror += '/'
        dist_url = urlparse.urljoin(mirror, 'dists/')
        if not suite.endswith('/'):
            suite += '/'
        suite_url = urlparse.urljoin(dist_url, suite)
        if gtk:
            path = 'main/installer-%s/current/images/cdrom/gtk/' % architecture
        else:
            path = 'main/installer-%s/current/images/cdrom/' % architecture
        base_url = urlparse.urljoin(suite_url, path)
    else:
        base_url = "https://d-i.debian.org/daily-images/%s/daily/cdrom/" % architecture
        if gtk:
            base_url += "gtk/"
    kernel = urlparse.urljoin(base_url, KERNEL)
    ramdisk = urlparse.urljoin(base_url, RAMDISK)
    cd_info = urlparse.urljoin(base_url, CD_INFO)
    check_url(base_url)
    check_url(kernel)
    check_url(ramdisk)
    return (base_url, kernel, ramdisk, cd_info)
