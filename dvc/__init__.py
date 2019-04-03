"""
DVC
----
Make your data science projects reproducible and shareable.
"""

from __future__ import unicode_literals

import os
import warnings


VERSION_BASE = "0.34.1"
__version__ = VERSION_BASE

PACKAGEPATH = os.path.abspath(os.path.dirname(__file__))
HOMEPATH = os.path.dirname(PACKAGEPATH)
VERSIONPATH = os.path.join(PACKAGEPATH, "version.py")


def _update_version_file():
    """Dynamically update version file."""
    try:
        from git import Repo
        from git.exc import InvalidGitRepositoryError
    except ImportError:
        return __version__

    try:
        repo = Repo(HOMEPATH)
    except InvalidGitRepositoryError:
        return __version__

    sha = repo.head.object.hexsha
    short_sha = repo.git.rev_parse(sha, short=6)
    dirty = ".mod" if repo.is_dirty() else ""
    ver = "{}+{}{}".format(__version__, short_sha, dirty)

    # Write a helper file, that will be installed with the package
    # and will provide a true version of the installed dvc
    with open(VERSIONPATH, "w+") as fobj:
        fobj.write("# AUTOGENERATED by dvc/__init__.py\n")
        fobj.write('version = "{}"\n'.format(ver))

    return ver


def _remove_version_file():
    """Remove version.py so that it doesn't get into the release."""
    if os.path.exists(VERSIONPATH):
        os.unlink(VERSIONPATH)


if os.path.exists(os.path.join(HOMEPATH, "setup.py")):
    # dvc is run directly from source without installation or
    # __version__ is called from setup.py
    if (
        os.getenv("APPVEYOR_REPO_TAG", "").lower() != "true"
        and os.getenv("TRAVIS_TAG", "") == ""
        and os.getenv("DVC_TEST", "").lower() != "true"
    ):
        __version__ = _update_version_file()
    else:  # pragma: no cover
        _remove_version_file()
else:  # pragma: no cover
    # dvc was installed with pip or something. Hopefully we have our
    # auto-generated version.py to help us provide a true version
    try:
        from dvc.version import version

        __version__ = version
    except Exception:
        pass

VERSION = __version__


# Ignore numpy's runtime warnings: https://github.com/numpy/numpy/pull/432.
# We don't directly import numpy, but our dependency networkx does, causing
# these warnings in some environments. Luckily these warnings are benign and
# we can simply ignore them so that they don't show up when you are using dvc.
warnings.filterwarnings("ignore", message="numpy.dtype size changed")
warnings.filterwarnings("ignore", message="numpy.ufunc size changed")

# Ignore paramiko's warning: https://github.com/paramiko/paramiko/issues/1386.
# This only affects paramiko 2.4.2 and should be fixed in the next version.
# Cryptography developers decided that it is a brilliant idea not to inherit
# from DeprecationWarning [1] because it is invisible by default, and decided
# to spam everyone instead. So it is their fault and not paramiko's.
#
# [1] https://github.com/pyca/cryptography/blob/2.6.1/src/cryptography/
#     utils.py#L14
try:
    from cryptography.utils import CryptographyDeprecationWarning

    warnings.simplefilter("ignore", CryptographyDeprecationWarning)
except ImportError:
    pass
