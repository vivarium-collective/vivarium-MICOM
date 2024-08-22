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

#%% temp - micom model test bench

sample_id = 'ERR260132'

com = load_pickle("models/" + sample_id + ".pickle")

#%%




#%%

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
        self.com = load_pickle('models/'+str(self.parameters['patient_model'])+'.pkl')
        self.parameters['species_files']
        self.species_ids = list(self.com.taxonomy['id'])  # list of species ids
        self.exchanges = [exc.id for exc in self.com.exchanges]
        self.internal_exchanges = [iexc.id for iexc in self.com.internal_exchanges]
        self.reactions = [rxn.id for rxn in self.com.reactions]
        # get minimal media
        self.media_molecules = list(self.com.medium.keys())  # list of media molecules

        # put asserts here to make sure all the relevant information is loaded
        assert self.parameters['species_files'] is not None, 'species_files must be provided'

    def ports_schema(self):
        ports = {
            'media': {  # media is the port name
                mol_id: {
                    '_default': 0.0,  # dic from nutrient id to concentrations
                    '_updater': 'set',  # how the port is updated
                    '_emit': True,  # whether the port is emitted
                    # '_serializer': 'json',  # how the port is serialized
                    # '_divider': 'split',
                } for mol_id in self.media_molecules
            },
            'exchange_bounds': {},
            'species_abundance': {
                str(species_id): {
                    '_default': 0.0,
                    '_updater': 'set',
                    '_emit': True,
                } for species_id in self.species_ids
            },'growth_rates': {
                str(species_id):{
                '_default': 0.0,
                '_updater': 'set',
                '_emit': True,
            } for species_id in self.com.abundances.index
        },
            'community_growth_rate': {
                '_default': 0.0,
                '_updater': 'set',
                '_emit': True,
            },
            'fluxes': {
                str(rxn): {
                    '_default': 0.0,  # dic from nutrient id to concentrations
                    '_updater': 'set',  # how the port is updated
                    '_emit': True  # whether the port is emitted
                } for rxn in self.reactions
            },
        }
        return ports

    def next_update(self, interval, states):
        # get the media concentrations
        media_input = states['media']

        # get the species abundance
        species_abundance = states['species_abundance']

        # set the values in MICOM

        # run MICOM
        # TODO

        com.medium = media_input[media_input > 0]
        sol = com.cooperative_tradeoff(fraction=0.5, fluxes=True, pfba=False)
        fluxes_sol = sol.fluxes

        fluxes = {}

        for rxn in self.reactions:
            flux_search = rxn.split('__')
            if len(flux_search) == 2:
                fluxes[rxn] = fluxes_sol.loc[flux_search[1],flux_search[0]]
            elif len(flux_search) == 1:
                fluxes[rxn] = fluxes_sol.loc['medium',rxn]

        growth_rates = {
            str(species_id):
                sol.members["growth_rate"][str(species_id)]
            for species_id in self.species_ids
        }


        return {
            'growth_rates': growth_rates,
            'community_growth_rate': sol.growth_rate,
            'fluxes': fluxes
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
