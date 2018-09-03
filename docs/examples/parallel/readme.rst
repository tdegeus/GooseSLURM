
************
GNU parallel
************

Overview
========

This example focuses on a case in which you claim (or are given) more than one CPU on one node, which will be used to run several instances of a serial processes in parallel (for example using different input parameters, or for different statistical realizations). This case is relevant for example when the queuing system restricts allocation to entire nodes. In that case, no matter how many CPUs-per-node you would demand you would be given all CPUs on the node, so you should better make good use of it.

The idea is to use `GNU Parallel <https://www.gnu.org/software/parallel/>`_ to do all the work for you. It is designed to run several serial processes in parallel. It is a simple ``perl`` script which is easy to 'install' ([see below](#local-installation-of-parallel)).  What it basically does is to run some (nested) loop in parallel. Each iteration of this loop contains a (long) process (e.g. Matlab, Python, your own executable, ...). Parallel then runs ``N`` processes at the same time (where ``N`` is the number of CPUs you have available). As soon as one process finishes, the next process is submitted, and so on until your entire loop is finished. It is perfectly fine that not all processes take the same amount of time, as soon as one CPU is freed, another process is started. And the great thing is: its syntax is extremely easy.

.. note::

    GNU Parallel also allows parallelization one several nodes. In the present context this in not very relevant as you can just submit several single node jobs. Should you be interested consult the manual.

Job script
==========

[:download:`source: job.slurm <job.slurm>`]

.. literalinclude:: job.slurm
   :language: bash

Code explained
--------------

The job script has to following parts:

.. literalinclude:: job.slurm
   :language: bash
   :lines: 1

Definition of the language that this script is written in (BASH in this case).

.. literalinclude:: job.slurm
   :language: bash
   :lines: 2-7

Allocation of resources. These lines are interpreted by the ``sbatch`` command, but are then ordinary comments when the script run on the compute node. Notice that in this case 5 CPUs on one node are demanded.

.. literalinclude:: job.slurm
   :language: bash
   :lines: 9

Run your executable in parallel. In this case the executable is mimicked using the `echo` command, which provided with two arguments. As an example a nested loop is run with the first argument an index in the range 1-12 and the second argument a name which gets the values 'summer' or 'winter'.

Behavior
========

The job is submitted using

.. code-block:: bash

    $ sbatch job.slurm

Once the job is completed, the output can be inspected:

[:download:`source: job.slurm.out <job.slurm.out>`]

.. code-block:: bash

    $ cat job.slurm.out

    1 summer
    1 winter
    2 summer
    2 winter
    3 summer
    3 winter
    4 summer
    4 winter
    5 summer
    5 winter
    6 summer
    6 winter
    7 summer
    7 winter
    8 summer
    8 winter
    9 summer
    9 winter
    10 summer
    10 winter
    11 summer
    11 winter
    12 summer
    12 winter

where we clearly see the effect of the nested loop.

To check that the processes actually are run in parallel one can:

1.  Log in to the node

    .. code-block:: bash

        $ ssh ...

    where the host name of the compute node that job runs on, is listed in the output of the ``squeue`` command.

2.  Use ``top`` or ``htop`` to inspect the running processes:

    .. code-block:: bash

        $ htop

    (You can limit the output to your account by typing ``u`` and then your user name.)

.. note::

    This example runs too fast to really see anything. It becomes obvious for a more realistic (slower) process.

Other usage
===========

Read commands from text file
----------------------------

An easy option is to store a list of commands in a plain text file:

.. code-block:: bash

    somoprogram 1 1 1
    somoprogram 1 1 2
    somoprogram 1 1 3
    somoprogram 1 2 1
    somoprogram 1 2 2
    somoprogram 1 2 3
    ...

These commands can then be executed in parallel using

.. code-block:: bash

    parallel :::: example.txt

.. note::

    Don't forget to specify the number of processors to use:

    .. code-block:: bash

        parallel --max-procs=${SLURM_CPUS_PER_TASK} :::: example.txt

Local installation of parallel
==============================

To 'install' GNU parallel into your home folder, for example under ``~/opt``.

1.  `Download the latest version of GNU Parallel <http://ftp.gnu.org/gnu/parallel/>`_. *You'll find 'parallel-latest.tar.bz2' on the bottom of the page.*

2.  Make the directory ``~/opt`` if it does not yet exist

    .. code-block:: bash

        $ mkdir $HOME/opt

3.  'Install' GNU Parallel:

    .. code-block:: bash

        $ tar jxvf parallel-latest.tar.bz2
        $ cd parallel-XXXXXXXX
        $ ./configure --prefix=$HOME/opt
        $ make
        $ make install

    Note that the relevant files will be installed in ``~/opt/bin``.

4.  Add ``~/opt/bin`` to your path:

    .. code-block:: bash

        $ export PATH=$HOME/opt/bin:$PATH

    To make this permanent, add this line to your ``~/.bashrc`` (or some equivalent configuration file), see for example `this page <https://www.cyberciti.biz/faq/set-environment-variable-linux/>`_.
