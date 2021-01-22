
****
Tips
****


Use conda to pre-build
======================

When using a compiled code it can be useful to build once (on the appropriate hardware)
and simply use the executable in a job.
If you want to avoid using the path of the executable, you can install the executable.
A nice way to do this is to install it in a virtual *conda* environment.
This was you can create a *conda* environment relevant to your batch of jobs without having to
worry too much about naming:
You can have many different *conda* environments to overcome potential naming conflicts,
and, moreover, you can easily throw them away and start over.

CMake
-----

To install inside a *conda* environment add the following to your ``CMakeLists.txt``

.. code-block:: cmake

    if (APPLE)
        set_target_properties(${PROJECT_NAME} PROPERTIES MACOSX_RPATH ON)
    else()
        set_target_properties(${PROJECT_NAME} PROPERTIES
            BUILD_WITH_INSTALL_RPATH 1
            SKIP_BUILD_RPATH FALSE)
    endif()

    set_target_properties(${PROJECT_NAME} PROPERTIES
        INSTALL_RPATH_USE_LINK_PATH TRUE)

    install(TARGETS ${PROJECT_NAME} DESTINATION bin)

Then, before building, activate your *conda* environment:

.. code-block:: bash

    conda activate myenv

Then build with the following

.. code-block:: bash
    :emphasize-lines: 4

    cd /path/to/your/CMakeLists
    mkdir build
    cd build
    cmake .. -DCMAKE_INSTALL_PREFIX:PATH="${CONDA_PREFIX}"
    make
    make install

whereby the ``-DCMAKE_INSTALL_PREFIX:PATH="${CONDA_PREFIX}"`` will make sure that the
executable is stored in the active *conda* environment.

With hardware optimisation & different hardware configurations
--------------------------------------------------------------

Suppose that you have multiple hardware layouts of compute nodes,
and that your are building with hardware-specific optimisations.
In that case a nice option is to create (identical) *conda* environments for each hardware
layout, and build and install the executable for the different hardware layouts.
Then, in the job, you simply activate the right *conda* environment based on the
hardware on which the job runs.

Consider having two types of hardware configurations ``E5v4`` and ``s6g1``, then we will
create two *conda* environments, ``myenv_E5v4`` and ``myenv_s6g1``, and build
(on the respective hardware layouts) and install to the relevant environment:

.. code-block:: bash

    cd /path/to/your/CMakeLists
    mkdir build
    cd build

For the first environment:

.. code-block:: bash

    conda activate myenv_E5v4
    cmake .. -DCMAKE_INSTALL_PREFIX:PATH="${CONDA_PREFIX}"
    srun -C E5v4 -p build -c 16 make -j16
    make install

and similarly for the second environment:

.. code-block:: bash

    conda activate myenv_s6g1
    cmake .. -DCMAKE_INSTALL_PREFIX:PATH="${CONDA_PREFIX}"
    srun -C s6g1 -p build -c 16 make -j16
    make install

Then, in the job-script include the following:

.. code-block:: bash
    :emphasize-lines: 3-7

    source ~/miniconda3/etc/profile.d/conda.sh

    if [[ "${SYS_TYPE}" == *E5v4* ]]; then
        conda activate myenv_E5v4
    elif [[ "${SYS_TYPE}" == *s6g1* ]]; then
        conda activate myenv_s6g1
    fi
