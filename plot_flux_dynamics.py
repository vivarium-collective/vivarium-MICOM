import os
import re
import matplotlib.pyplot as plt
import matplotlib as mpl
import pickle
import numpy as np

mpl.rcParams['figure.dpi'] = 300


# define regex patterns for exchange reaction IDs with SCFAs

SCFAs = {
    "butyrate": 'EX_but\S*(eS*)',
    "acetate": 'EX_ac\S*(eS*)',
    "propionate": 'EX_ppa\S*(eS*)',
}
#%% load test simulation data and retrieve SCFAs

data = pickle.load(open(os.path.join('out','test_output.pickle')))
rxn_butyrate =  list(filter(re.compile(SCFAs["butyrate"]).match, list(data[0]['fluxes_store'].keys())))
rxn_acetate =  list(filter(re.compile(SCFAs["acetate"]).match, list(data[0]['fluxes_store'].keys())))
rxn_propionate =  list(filter(re.compile(SCFAs["propionate"]).match, list(data[0]['fluxes_store'].keys())))

#%% plot flux dynamics for SCFA groups
def traj_group(rxns,grp):
    plt.figure()
    for rxn in rxns:
        traj = np.array([data[tp]['fluxes_store'][rxn] for tp in list(data.keys())])
        plt.plot(range(len(traj)),traj,label=rxn)
    plt.xlabel('Time step')
    plt.ylabel('Fluxes: '+grp)
    plt.savefig(os.path.join('out','dynamics_'+grp+'.png'))

#%%

traj_group(rxns=rxn_butyrate,grp='butyrates')
traj_group(rxns=rxn_acetate,grp='acetates')
traj_group(rxns=rxn_propionate,grp='propionates')

