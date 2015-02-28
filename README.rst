Informatic
==========

Informatic is an IDE for the Inform 6 interactive fiction development system.
It is written in Python 3, using PyQt5 for its GUI.

Informatic is Copyright (C) 2015 Dominic Delabruere

French translations provided by Hugo Labrande.

Informatic can be used and distributed under the terms of the GNU General
Public License, either version 3 of the License, or (at your option) any later
version. The full text of this license is in the ``LICENSE.GPL3`` file. All the
source code for Informatic is available at
<https://github.com/mrloam/informatic>.

Informatic does not come with the Inform 6 compiler or libraries. These must be
downloaded separately:
<http://www.ifarchive.org/indexes/if-archiveXinfocomXcompilersXinform6.html>

Implemented features
--------------------

* View the source files in a project source directory
* Edit multiple source files in different tabs with syntax highlighting for
  strings and comments
* Compile your project from within the IDE

Features scheduled for upcoming release
---------------------------------------

* Launch your project in an interpreter from within the IDE
* Launch Informatic with a particular project file from the command line
* Edit compiler options in a convenient dialog window
* Search source files
* Goto a numbered line in a source file

Running or installing from source
---------------------------------

If you intend to run or install Informatic from source, it is recommended that
you use a release tarball instead of the source that appears on GitHub. If you
use the source that appears on GitHub, you will have to compile Qt translation
files and resource code yourself using lrelease and pyrcc5 before you run or
install Informatic.

Running or installing Informatic from source requires that you have the
following dependencies installed first:

* Python 3
* Qt 5 (included with some binary distributions of PyQt5)
* PyQt5
* PyQt5.Qsci (the Qscintilla plugin for PyQt5, often included with PyQt5
  binaries)

You can install these on Debian-based Linux systems (like Ubuntu) with the
following command::

    sudo apt-get install python3-pyqt5.qsci

As of 19 January 2015, anyone using Ubuntu 14.10 "Utopic Unicorn" may have
difficulty running Informatic due to a bug in Ubuntu's official
``python3-pyqt5.qsci`` package, documented at
<https://bugs.launchpad.net/ubuntu/+source/qscintilla2/+bug/1391056>. This
problem is not known to affect Ubuntu 14.04 "Trusty Tahr", the latest Long-Term
Service release.

To run Informatic from source without installing it simply run the script
``informatic.pyw`` using a Python 3 interpreter::

    python3 informatic.pyw

Remember to replace python3 with the name of the interpreter on your system. On
some systems it may be ``python`` or ``python34``.

To install Informatic, use the ``install`` command of the included ``setup.py``
script::

    sudo python3 setup.py install

After a successful installation, you should be able to run Informatic from the
command line with ``informatic``.

Running the "frozen" Windows package
------------------------------------

The "frozen" Windows package for Informatic comes with all the dependencies,
so you should only have to run ``informatic.exe``. 
