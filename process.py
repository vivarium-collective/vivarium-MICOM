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

# sample_id = 'ERR260132'
#
# com = load_pickle('models/' + sample_id + '.pickle')

#%%




#%%

##
class MICOM(Process):

    # defaults describes the parameters that the process expects
    defaults = {
        'patient_model': 'ERR260132',
        'species_files': None,
    }

    def __init__(self, parameters=None):
        super().__init__(parameters)
        # in the constructor we initialize all MICOM processes

        # load the species files
        self.com = load_pickle('models/'+str(self.parameters['patient_model'])+'.pickle')
        #self.parameters['species_files']
        self.species_ids = list(self.com.taxonomy['id'])  # list of species ids
        self.exchanges = [exc.id for exc in self.com.exchanges]
        self.internal_exchanges = [iexc.id for iexc in self.com.internal_exchanges]
        self.reactions = [rxn.id for rxn in self.com.reactions] #retrieve reaction ids to save flux outputs
        self.reactions = list(filter(lambda x: 'biomass(e)' not in x, self.reactions))
        # get minimal media
        self.media_molecules = list(self.com.medium.keys())  # list of media molecules

        # put asserts here to make sure all the relevant information is loaded


    def ports_schema(self):
        ports = {
            'media': {  # media is the port name
                mol_id: {
                    '_default': 1000.0,  # dic from nutrient id to concentrations
                    '_updater': 'accumulate',  # how the port is updated
                    '_emit': True,  # whether the port is emitted
                    # '_serializer': 'json',  # how the port is serialized
                    # '_divider': 'split',
                } for mol_id in self.media_molecules
            },
            # 'exchange_bounds': {},
            # 'species_abundance': {
            #     str(species_id): {
            #         '_default': 0.0,
            #         '_updater': 'set',
            #         '_emit': True,
            #     } for species_id in self.species_ids
            # },
            # 'growth_rates': {
            #     str(species_id):{
            #     '_default': 0.0,
            #     '_updater': 'set',
            #     '_emit': True,
            #     } for species_id in self.com.abundances.index
            # },
            # 'community_growth_rate': {
            #     '_default': 0.0,
            #     '_updater': 'set',
            #     '_emit': True,
            # },
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
        # species_abundance = states['species_abundance']

        # set the values in MICOM
        # TODO

        # run MICOM

        self.com.medium = media_input
        sol = self.com.cooperative_tradeoff(fraction=0.5, fluxes=True, pfba=False)
        fluxes_sol = sol.fluxes
        # update fluxes port from micom output
        fluxes = {}

        for rxn in self.reactions:

            rxn_spc = list(filter(lambda x: x in rxn,self.species_ids))

            if len(rxn_spc) !=0:
                spc = rxn_spc[0]
                rxn_id = rxn.replace('__'+spc,'')

                fluxes[rxn] = fluxes_sol.loc[spc,rxn_id]
            else:
                fluxes[rxn] = fluxes_sol.loc['medium',rxn]

            # flux_search = rxn.split('__')
            # if len(flux_search) == 2:
            #     fluxes[rxn] = fluxes_sol.loc[flux_search[1],flux_search[0]]
            # elif len(flux_search) == 1:
            #     fluxes[rxn] = fluxes_sol.loc['medium',rxn]

        # growth_rates = {
        #     str(species_id):
        #         sol.members["growth_rate"][str(species_id)]
        #     for species_id in self.species_ids
        # }


        return {
            # 'growth_rates': growth_rates,
            # 'community_growth_rate': sol.growth_rate,
            'fluxes': fluxes
        }


class MediaUpdate(Process):
    defaults = {
        'patient_model': 'ERR260132',
        'v_max': 10.0,
        'k_m': 10.0,
        'timestep': 1.0,
    }

    def __init__(self,parameters=None):

        super().__init__(parameters)

        self.com = load_pickle('models/'+str(self.parameters['patient_model'])+'.pickle')
        self.media_molecules = list(self.com.medium.keys())

    def ports_schema(self):
        ports = {
            'media': {
                mol_id: {
                    '_default': 1000.0,
                    '_updater': 'accumulate',
                    '_emit': True,
                } for mol_id in self.media_molecules
            }
        }

        return ports

    def next_update(self, interval, states):

        media_input = states['media']

        media_update = media_input.copy()

        for mol_id in self.media_molecules:
            media_update[mol_id] = - (media_input[mol_id]*self.parameters['v_max']
                                    /(self.parameters['k_m']+media_input[mol_id])
                                    * self.parameters['timestep'])

        return {
            'media': media_update
        }

def run_process(total_time=5):

    # create a config
    config = {
        # 'species_files': ['models/ecoli.json',],
    }
    # create a MICOM process
    micom_process = MICOM(config)
    media_process = MediaUpdate({})

    # define the composite
    processes = {
        'micom': micom_process,
        'media': media_process,
    }
    topology = {
        'micom': {
            'fluxes': ('fluxes_store',),
            'media': ('media_store',),

            #     'media': ('media', 'micom'),
        #     'species_abundance': ('species_abundance', 'micom'),
        #     'community_growth_rate': ('community_growth_rate', 'micom'),
        },
        'media': {
            'media': ('media_store',),
        }
    }

    # make a vivarium simulation
    sim = Engine(processes=processes, topology=topology)

    # run the simulation
    sim.update(total_time)

    # get the data
    data = sim.emitter.get_data()

    print(data)

    return sim



if __name__ == '__main__':
    results = run_process(total_time=20)
    data = results.emitter.get_data()

#%%
# config = {
# }
# # create a MICOM process
# micom_process = MICOM(config)
#
# # define the composite
# processes = {
#     'micom': micom_process,
# }
# topology = {
#     'micom': {
#         'fluxes': ('fluxes_store',),
#         'media': ('media_store',),
#     }
# }
#
# # make a vivarium simulation
# sim = Engine(processes=processes, topology=topology)
#
# # run the simulation
# sim.update(5)
#%%
media_xmpl = np.array([data[tp]['media_store']['EX_nmn_m'] for tp in list(data.keys())])




#%%

import matplotlib.pyplot as plt

plt.plot(range(len(media_xmpl)),media_xmpl)

plt.show()

#%%

SCFAs = {
    "butyrate": 'EX_but\S*(eS*)',
    "acetate": 'EX_ac\S*(eS*)',
    "propionate": 'EX_ppa\S*(eS*)',
}
#%%

rxn_butyrate =  list(filter(re.compile(SCFAs["butyrate"]).match, list(data[0]['fluxes_store'].keys())))
rxn_acetate =  list(filter(re.compile(SCFAs["acetate"]).match, list(data[0]['fluxes_store'].keys())))
rxn_propionate =  list(filter(re.compile(SCFAs["propionate"]).match, list(data[0]['fluxes_store'].keys())))

#%%
def traj_group(rxns):
    plt.figure()
    for rxn in rxns:
        traj = np.array([data[tp]['fluxes_store'][rxn] for tp in list(data.keys())])
        plt.plot(range(len(traj)),traj,label=rxn)
    # plt.legend()
    plt.show()



#%%

traj_group(rxn_butyrate)
traj_group(rxn_acetate)
traj_group(rxn_propionate)
#%%




#%%