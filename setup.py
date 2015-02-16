"""
Set up back for your environment
back <http://github.com/jmullan/back>
"""

from setuptools import setup
import back.back

setup(
    name="back",
    version=back.back.__version__,
    description="Semi-autmoatic rsync configuration",
    license="GPLv3+",
    author="Jesse Mullan",
    author_email="jmullan@visi.com",
    url="http://github.com/jmullan/back",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: "
        "GNU General Public License v3 or later (GPLv3+)",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3"],
    packages=['back'],
    py_modules=["back"],
    scripts=['bin/back'])
