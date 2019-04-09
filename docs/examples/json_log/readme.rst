
*************
JSON log-file
*************

This example demonstrated how to manually write a log-file in the ``SLURM_SUBMIT_DIR`` (the directory, on the head node, from which the job is submitted) when the job is submitted. This file, `job.slurm.json <job.slurm.json>`_, is formatted using JSON to facilitate (automatic) readability.

Job script
==========

[:download:`source: job.slurm <job.slurm>`]

.. literalinclude:: job.slurm
   :language: bash
