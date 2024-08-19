"""
Vivarium process to run MICOM
"""
import numpy as np
from vivarium.core.process import Process
from vivarium.core.engine import Engine

## from MICOM import ....  # TODO all required MICOM imports

import os
import pandas as pd
import micom
from micom import load_pickle
from micom.media import minimal_medium
from micom.logger import logger


##
class MICOM(Process):

    # defaults describes the parameters that the process expects
    defaults = {
        'patient_model': 'ERR260132'
        'species_files': None,
    }

    def __init__(self, parameters=None):
        super().__init__(parameters)
        # in the constructor we initialize all MICOM processes

        # load the species files
        self.parameters['species_files']
        self.species_ids = []  # list of species ids

        # get minimal media
        self.media_molecules = []  # list of media molecules

        # put asserts here to make sure all the relevant information is loaded
        assert self.parameters['species_files'] is not None, 'species_files must be provided'

    def ports_schema(self):
        ports = {
            'media': {  # media is the port name
                mol_id: {
                    '_default': np.array(),  # dic from nutrient id to concentrations
                    '_updater': 'set',  # how the port is updated
                    '_emit': True,  # whether the port is emitted
                    # '_serializer': 'json',  # how the port is serialized
                    # '_divider': 'split',
                } for mol_id in self.media_molecules
            },
            'exchange_bounds': {},
            'species_abundance': {
                species_id: {
                    '_default': 0.0,
                    '_updater': 'set',
                    '_emit': True,
                } for species_id in self.species_ids
            },
            'community_growth_rate': {
                '_default': 0.0,
                '_updater': 'set',
                '_emit': True,
            },
            'exchange fluxes': {},
        }
        return ports

    def next_update(self, interval, states):
        # get the media concentrations
        media = states['media']

        # get the species abundance
        species_abundance = states['species_abundance']

        # set the values in MICOM

        # run MICOM
        # TODO

        com.medium = med[med > 0]
        sol = com.cooperative_tradeoff(fraction=0.5, fluxes=True, pfba=False)
        fluxes = sol.fluxes

        # extract results
        results['fluxes'] = fluxes
        results['media'] = com.medium
        results['growth_rates'] = sol.members["growth_rate"].copy()
        results['community_growth_rate'] = sol.growth_rate

        return {
            # 'media': results['media'],
            'species_abundance': results['species_abundance'],
            'community_growth_rate': results['community_growth_rate'],
            'exchange fluxes': results['exchange fluxes'],
            # 'results': results,
        }




def run_process(total_time=10):

    # create a config
    config = {
        'species_files': ['models/ecoli.json',],
    }
    # create a MICOM process
    micom_process = MICOM(config)

    # define the composite
    processes = {
        'micom': micom_process,
    }
    topology = {
        'micom': {
            'media': ('media', 'micom'),
            'species_abundance': ('species_abundance', 'micom'),
            'community_growth_rate': ('community_growth_rate', 'micom'),
        }
    }

    # make a vivarium simulation
    sim = Engine(processes=processes, topology=topology)

    # run the simulation
    sim.update(total_time)

    # get the data
    data = sim.emitter.get_data()

    print(data)



if __name__ == '__main__':
    run_process()
