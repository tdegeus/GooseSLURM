
.. code-block:: bash

    if [[ "${SYS_TYPE}" == *E5v4* ]]; then
        conda activate myenv_E5v4
    elif [[ "${SYS_TYPE}" == *S6g1* ]]; then
        conda activate myenv_S6g1
    fi


.. code-block:: bash

    srun -C E5v4 -p build -c 16 make -j16
    make install
