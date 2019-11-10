
*************
Python module
*************

Installation
============

pip
---

Installing GooseSLUM proceeds easily with ``pip``:

.. code-block:: bash

    cd /path/to/GooseSLURM
    pip install .

.. note::

    *   Be sure to use the proper executable for ``pip`` (it could for example be ``pip3``).
    *   Add the ``--user`` option to the ``pip``-command to install in the user's home-folder.

Overview
========

Write job scripts
-----------------

.. autosummary::

  GooseSLURM.scripts.plain
  GooseSLURM.scripts.tempdir
  GooseSLURM.files.cmake

Parse ps
--------

.. autosummary::

  GooseSLURM.ps.read_interpret
  GooseSLURM.ps.read
  GooseSLURM.ps.interpret
  GooseSLURM.ps.colors

Parse squeue
------------

.. autosummary::

  GooseSLURM.squeue.read_interpret
  GooseSLURM.squeue.read
  GooseSLURM.squeue.interpret
  GooseSLURM.squeue.colors

Parse sinfo
-----------

.. autosummary::

  GooseSLURM.sinfo.read_interpret
  GooseSLURM.sinfo.read
  GooseSLURM.sinfo.interpret
  GooseSLURM.sinfo.colors

Rich strings
------------

.. autosummary::

  GooseSLURM.rich.String
  GooseSLURM.rich.Integer
  GooseSLURM.rich.Float
  GooseSLURM.rich.Duration
  GooseSLURM.rich.Memory

Print
-----

.. autosummary::

  GooseSLURM.table.print_long
  GooseSLURM.table.print_columns
  GooseSLURM.table.print_list


Duration
--------

.. autosummary::

  GooseSLURM.duration.asSeconds
  GooseSLURM.duration.asUnit
  GooseSLURM.duration.asHuman
  GooseSLURM.duration.asSlurm

Memory
------

.. autosummary::

  GooseSLURM.memory.asBytes
  GooseSLURM.memory.asUnit
  GooseSLURM.memory.asHuman
  GooseSLURM.memory.asSlurm

Documentation
=============

GooseSLURM.scripts
------------------

.. automodule:: GooseSLURM.scripts
  :members:

GooseSLURM.files
----------------

.. automodule:: GooseSLURM.files
  :members:

GooseSLURM.ps
-------------

.. automodule:: GooseSLURM.ps
  :members:

GooseSLURM.squeue
-----------------

.. automodule:: GooseSLURM.squeue
  :members:

GooseSLURM.sinfo
----------------

.. automodule:: GooseSLURM.sinfo
  :members:

GooseSLURM.rich
---------------

.. automodule:: GooseSLURM.rich
  :members:

GooseSLURM.table
----------------

.. automodule:: GooseSLURM.table
  :members:

GooseSLURM.duration
-------------------

.. automodule:: GooseSLURM.duration
  :members:

GooseSLURM.memory
-----------------

.. automodule:: GooseSLURM.memory
  :members:
