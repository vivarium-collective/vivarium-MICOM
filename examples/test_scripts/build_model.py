"""Builds micom community models using patient input data from Micom 2020 paper"""

from os.path import isfile
import micom
from micom import Community
import pandas as pd

import os

#%%
wd_default = os.path.dirname(os.getcwd())

os.chdir(wd_default)
print(wd_default)
print(os.getcwd())

# define path to input data for patients and agora models
# git repo micom-dev/paper was cloned 'micom_validation' directory
# make sure that agora models database is downloaded and placed in the data/agora folder after extraction

path_data = os.path.join(os.getenv("HOME"),'projects','micom_validation','paper','data')


# define output path for build community models

path_model = os.path.join(os.getcwd(),'models')

#%%

logger = micom.logger.logger

# load patient taxonomy data (micom 2020 input data)

taxonomy = pd.read_csv(os.path.join(path_data,"genera.csv")).query("relative > 1e-3")
taxonomy["file"] = taxonomy.file.apply(
    lambda ids: [os.path.join(path_data,"agora")+"/" + i for i in ids.split("|")]
)
taxonomy["name"] = taxonomy.genus
assert not taxonomy.name.str.contains(" ").any()
taxonomy = taxonomy.rename(columns={"name": "id", "reads": "abundance"})

# western diet data (micom 2020 input data)

diet = pd.read_csv(os.path.join(path_data,"western_diet.csv"))
diet.index = diet.reaction = diet.reaction.str.replace("_e", "_m")
diet = diet.flux * diet.dilution


def build_and_save(args):

    # builds micom community models using patient input data and agora models

    s, tax = args
    filename = "models/" + s + ".pickle"
    if isfile(filename):
        return
    com = Community(tax, id=s, progress=False)
    ex_ids = [r.id for r in com.exchanges]
    logger.info(
        "%d/%d import reactions found in model.",
        diet.index.isin(ex_ids).sum(),
        len(diet),
    )
    com.medium = diet[diet.index.isin(ex_ids)]
    com.to_pickle(filename)



samples = taxonomy.samples.unique()
samples.sort()

# gathers model builder input argoments for all patients

args = [(s, taxonomy[taxonomy.samples == s]) for s in samples]



#%% load the first patient sample

for sam_idx in range(5):
    sample_0 = samples[sam_idx]

    # creates a shortened version of community models for first 5 patients
    # iterate through the entire "args" list to build models for all patients
    # define input to build function with fist 5 genera of first patient sample
    # delete ".iloc[:5,:] from the next line to include all genera in the community model

    args_0 = (str(sample_0), taxonomy[taxonomy.samples == sample_0].iloc[:5,:])

    # build micom toy model

    build_and_save(args_0)
#%%