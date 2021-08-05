**********************************
Transfer files: preserve meta-data
**********************************

It very often occurs that you have a bunch of files both on your own system as well as
on the computing cluster that you are working.
In order to keep both in sync, it is advised that you preserve meta-data
(created and modified dates) upon copying.
You can do this for example as follows:

.. code-block:: cpp

    # normal copy
    cp -p source destination

    # remote copy using Secure Copy
    scp -p source destination

    # similar to "scp" but typically faster
    rsync -a source destination
