## Directory structure

* `force_constants` - contains force constants files for test materials
* `profile_results` - contains profiling results
* `profile_scripts` - contains scripts for running Matlab/Python profiling

## Profile results

Directory structure is `euphonic_version_brille_version` -> `matlab/python` -> `machine` -> `results files`

**euphonic_version_brille_version**

Each directory is named after the version of Euphonic/Brille used e.g. `euphonic_1.0.0_54.g2b9c824_brille_0.6.1.dev16_g7698bb6` is Euphonic version `1.0.0_54.g2b9c824_brille_0.6.1.dev16_g7698bb6` and Brille version `euphonic_1.0.0_54.g2b9c824_brille_0.6.1.dev16_g7698bb6`.

`old` directory contains profiling results of an old version of Brille (not recorded) but is retained anyway.

**matlab/python**

``matlab`` contains results of running Euphonic with Horace via Matlab, ``python`` contains Python-only results

**machine**

Describes the machine the profiling was run on. e.g. ``windows_i711800H_32GB`` was run on a Windows machine with an Intel i7-11800H processor and 32GB of RAM. 

### Results files

``eubr_tictoc_Xqpts_Ychunk_Z`` is created by the ``eubr_profile.m`` script with ``do_profile = false``.
``X`` is the number of q-points, ``Y`` is the ``chunk`` variable and ``Z`` is the timestamp (so subsequent runs don't overwrite the results file).
To avoid the overhead of the Matlab profiler, Matlab's ``tic`` and ``toc`` were used to get the timing results.
The results file contains the time taken to interpolate with Euphonic, to initialise the Brille grid, and to interpolate with Brille.
Each is run N (usually 3) times.

``interpolate_Z.txt`` is created by the ``interpolate_profile.py`` script.
``Z`` is a timestamp so subsequent runs don't overwrite the results file.
Python's ``time`` is used to get timings.
The results file shows the time to interpolate with Euphonic and Brille for 160801 q-points (contained in the ``profile_scripts/qpts_160801.txt`` file), the time to initialise the Brille grid, and the time taken to calculate the structure factors (this is just for a comparison to see if structure factor calculations are the bottleneck yet) for the materials in the ``force_constants`` directory.
Each is run N (usually 3) times.


``interpolate_cprofile_Z.txt`` is created by the ``interpolate_cprofile.py`` script.
``Z`` is a timestamp so subsequent runs don't overwrite the results file.
This does the same thing as the ``interpolate_profile.py`` script except uses cProfile to determine specifically where timing is being spent, rather than using Python ``time``.
This may not give realistic timings overall but is useful to see where time is actually spent.

``powder_map_Z.txt`` is created by the ``powder_map_profile.py`` script.
``Z`` is a timestamp so subsequent runs don't overwrite the results file.
This results file shows the time taken to run Euphonic's ``euphonic-powder-map`` script using DOS weighting (so only ``calculate_qpoint_frequencies is used``)
and structure factor weighting (so ``calculate_qpoint_phonon_modes`` is used) for both Euphonic and Brille for different materials.
The paramaters using in running the script are shown on the first line of the results file.
Each is run N (usually 3) times.

``powder_map_cprofile_Z.txt`` is created by the ``powder_map_profile_cprofile.py`` script.
``Z`` is a timestamp so subsequent runs don't overwrite the results file.
This does the same thing as the ``powder_map_profile.py`` script except uses cProfile to determine specifically where timing is being spent, rather than using Python ``time``.

``brille_npts_Z.txt`` is created by the ``brille_npts_profile.py`` script.
``Z`` is a timestamp so subsequent runs don't overwrite the results file.
Python's ``time`` is used to get timings.
This results file shows the time to initialise and interpolate with the Brille grid for different grid sizes.
It was used to test if more grid points would affect the interpolation time.
Each was repeated N (usually 3) times.

## Profile scripts

Most scripts have been briefly described above. The other contained files are:

``qpts_160801.txt`` - a plain text file containing 160,801 q-points.
These were generated with Horace 3.6.2 using ``lattice = [1., 1., 1., 90, 90, 90]; cut = d2d(lattice, [1 0 0 0], [-5,0.025,5], [0 1 0 0], [-5,0.025,5]);``.
This was used so MATLAB and Python could use the same q-points.

``utils.py`` contains various common utilities for running the scripts.
e.g. the platform name, the number of threads to use, the location and names of files and the material information.