### Speedup

For the following Euphonic vs. Brille performance comparisons, I will be using 'speedup'

```
speedup = T_euphonic / T_brille
```

Where T_euphonic is the time taken to run the calculation with Euphonic, and T_brille is the time taken to run the calculation with Brille (via Euphonic).

### Brille 0.6.1 results
[windows_i711800H_32GB/powder_map_1667401832.txt](https://github.com/pace-neutrons/brille-performance/blob/master/profile_results/euphonic_1.0.0_54.g2b9c824_brille_0.6.1.dev16_g7698bb6/python/windows_i711800H_32GB/powder_map_1667401832.txt)
shows a performance benefit when using Brille for DOS calculations (`-w dos`) in the `euphonic-powder-map` tool for both quartz and AmSulf.
The speedup for quartz is 1.83, and for AmSulf is 16.69!
LZO shows no speedup, and Nb takes about 10 times longer to run with Brille, so this shows how system dependent these speedups are.
The benefit with quartz and AmSulf is severely reduced when calculating the structure factor (`-w coherent`),
with speedups of 1.23 and 3.01 respectively.

Through cProfile in [windows_i711800H_32GB/powder_map_cprofile_amsulf_1667515800.txt](https://github.com/pace-neutrons/brille-performance/blob/master/profile_results/euphonic_1.0.0_54.g2b9c824_brille_0.6.1.dev16_g7698bb6/python/windows_i711800H_32GB/powder_map_cprofile_amsulf_1667515800.txt)
it can be seen that in the `-w coherent` case for AmSulf, over 790 seconds are spent in the `br_evec_to_eu` method.
This method converts the basis eigenvectors output by Brille to the Cartesian eigenvectors that Euphonic requires.
One way to avoid this conversion is to add a feature to Brille to allow input/output of Cartesian eigenvectors.
This was implemented in https://github.com/brille/brille/pull/88 and released in Brille 0.7.0.

### Brille 0.7.0 results

[windows_i711800H_32GB/powder_map_1675164711.txt](https://github.com/pace-neutrons/brille-performance/blob/master/profile_results/euphonic_1.1.0_79.g1571a40_brille_0.7.0/python/windows_i711800H_32GB/powder_map_1675164711.txt)
Since allowing Cartesian eigenvectors, the performance of `euphonic-powder-map` using Brille and `-w coherent` has improved.
Quartz has a speedup of 1.98, AmSulf has a speedup of 10.23 and now LZO has a small speedup of 1.14. Nb still takes longer to run with Brille.

The speedups are slightly different when looking at calling `calculate_qpoint_phonon_modes` for a large chunk of q-points in a user script, rather than via `euphonic-powder-map` (in `euphonic-powder-map` `calculate_qpoint_phonon_modes` will be called many times for smaller chunks of q-points).
Time for initialising the Brille calculation has been recorded but is not used in the speedups below.
From [windows_i711800H_32GB/interpolate_1675161509.txt](https://github.com/pace-neutrons/brille-performance/blob/master/profile_results/euphonic_1.1.0_79.g1571a40_brille_0.7.0/python/windows_i711800H_32GB/interpolate_1675161509.txt)
the speedup for AmSulf is 6.7, but there is no speedup for quartz, Nb or LZO. It may be something to do with the available memory given that we are calculating
in a large chunk of ~100k q-points, and suggests that Brille may benefit from chunking calculations.

[windows_i711800H_32GB/eubr_tictoc_160801qpts_0chunk_1675427427.txt](https://github.com/pace-neutrons/brille-performance/blob/master/profile_results/euphonic_1.1.0_79.g1571a40_brille_0.7.0/matlab/windows_i711800H_32GB/eubr_tictoc_160801qpts_0chunk_1675427427.txt)
shows the time taken to interpolate via Horace with the default chunk size, and
[windows_i711800H_32GB/eubr_tictoc_160801qpts_10000chunk_1675439887.txt](https://github.com/pace-neutrons/brille-performance/blob/master/profile_results/euphonic_1.1.0_79.g1571a40_brille_0.7.0/matlab/windows_i711800H_32GB/eubr_tictoc_160801qpts_10000chunk_1675439887.txt)
shows the same but with a chunk size of 10000.
Euphonic run times were generally longer for the 10,000 chunk case than for the default chunk case, this is especially true for quartz where time may also be spend initialising the dipole correction calculation.
Brille does not provide a speedup over Euphonic in any case except the AmSulf case for 10,000 q-point chunks (default chunk couldn't be tested as it ran out of memory) where a speedup of 4.47 was found.

Profiling run on IDAaaS shows broadly similar results.