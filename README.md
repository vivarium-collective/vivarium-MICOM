# Vivarium-MICOM

This is a prototype of a dynamic implementation of micom using vivarium

1. To generate an executable micom community model, run:
   * cd examples/test_scripts
   * python build_models.py
2. process.py defines a vivarium process to run micom dynamically with updated media composition at each time step. It performs a test run of the vivarium process with 20 time steps. Resulting simulation output is saved as 'out/test_output.pickle'
3. plot_flux_dynamics.py generates time course plots of fluxes and saves figure under the 'out' directory.