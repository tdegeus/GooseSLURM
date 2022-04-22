Flush output files
==================

By default slurm has a delay (a certain number of lines) before output files are flushed.
This can be annoying when one has limited output.
To fix this, place ``stdbuf -o0 -e0`` in front of you command.
For example:

.. code-block:: bash

    stdbuf -o0 -e0 ./mycode
