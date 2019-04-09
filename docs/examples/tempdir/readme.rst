***************************
Temporary working directory
***************************

Overview
========

This script exploits a temporary directory on the compute node to avoid costly read/write actions over the network.

In particular it does the following:

1.   Copy files to a temporary directory on the compute node (which is in this case automatically provided by the queuing system).

2.   Run the job (while reading and writing locally on the compute node).

3.   Copy all files back to the directory from which the job is submitted (on the head node).

Here only items 1 and 3 use the network. During the computation all actions are local on the compute node. Often, quite some efficiency can be gained by doing this.

File structure
==============

This example assumes a file structure where (almost) everything that a simulation needs, and all its output, are located in a single directory (which may have arbitrary sub-directories). For example:

.. code-block:: none

    /home/user/...
    | - simulation
      | - job.slurm
      | - ... (code, input)


**It is vital that you submit from this directory, to copy only the files relevant to this simulation**:

.. code-block:: bash

    $ cd /home/user/.../simulation
    $ sbatch job.slurm

.. note::

    :ref:`Gsub <scripts_Gsub>` can be called from everywhere but guarantees this behaviour.

If the job terminates (the simulation is finished, or it is cut by the queuing system) all files that are in the `simulation` on the compute node are copied back to the directory in the home folder (on the head node). After that the folder looks like

.. code-block:: none

    /home/user/...
    | - simulation
      | - job.slurm
      | - ... (code, input)
      | - ... (output)


Job script
==========

[:download:`source: job.slurm <job.slurm>`]

.. literalinclude:: job.slurm
   :language: bash

.. note::

    To facilitate writing job-scripts, it can be created using the GooseSLURM Python module: [:download:`source: writeJob.py <writeJob.py>`].

Code explained
--------------

Language selection
^^^^^^^^^^^^^^^^^^

.. literalinclude:: job.slurm
   :language: bash
   :lines: 1

Resource allocation
^^^^^^^^^^^^^^^^^^^

Definition of the language that this script is written in (BASH in this case).

.. literalinclude:: job.slurm
   :language: bash
   :lines: 2-7

Allocation of resources. These lines are interpreted by the ``sbatch`` command, but are then ordinary comments when the script run on the compute node.

Directory selection
^^^^^^^^^^^^^^^^^^^

.. literalinclude:: job.slurm
   :language: bash
   :lines: 9-17

Definition of:

*   ``workdir``: the temporary directory on the compute node, here taken from the ``${TMPDIR}`` provided by SLURM. Reading from and writing to the ``workdir`` is local on the compute node, and does not involve the cluster's internal network.
*   ``submitdir``: the directory from which the ``sbatch`` command is run. It is assumed that this is the simulation directory (``/home/user/.../simulation`` above). All files/directory in this folder are copied back and forth. **Be sure to select the correct directory here.**

Copy to the compute-node
^^^^^^^^^^^^^^^^^^^^^^^^

.. literalinclude:: job.slurm
   :language: bash
   :lines: 19-36

1.  Optionally create or clear the temporary directory on the compute node (``workdir``).
2.  Copy all files/directory in ``submitdir`` to the temporary directory on the compute node (over the cluster's internal network).

Copy back to the head-node (when the job finishes)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. literalinclude:: job.slurm
   :language: bash
   :lines: 38-59

Define a function that will be run when the job ends (exits normally, or is voluntarily or involuntarily terminated by the queuing system). This function will copy everything (including all the generated results) back to the ``submitdir``, which again involves the cluster's internal network. Note that this may overwrite files in ``submitdir``.

If temporary files are created that you do not need anymore (for example build files, executables, debug output, ...) it is wise to delete it by uncommenting and modifying line 46. This way these files are created before copying them over the network.

Actual job
^^^^^^^^^^

.. literalinclude:: job.slurm
   :language: bash
   :lines: 51-

Here you can do what you want. Remember that all read and write operations in the current directory (i.e. all files like ``./somepath``) are local on the compute node (which is as efficient as reading and writing gets). Avoid here to do anything involving the home folder, as that is a network mount.




