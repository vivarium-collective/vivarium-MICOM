import pandas as pd
import os
from plotnine import *
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
from adjustText import adjust_text
from scipy.stats import ttest_ind
import numpy as np
from itertools import combinations
from scipy.spatial.distance import pdist
from skbio.stats.distance import DistanceMatrix, permanova

sample_keep = ["run_accession", "subset", "status", "type"]
SCFAs = {
    "butyrate": "EX_but\\(e\\)",
    "acetate": "EX_ac\\(e\\)",
    "propionate": "EX_ppa\\(e\\)",
}
theme_set(theme_minimal())

#%%

path_data = os.path.join(os.getenv("HOME"),'projects','micom_validation','paper','data')

path_model = os.path.join(os.getcwd(),'models')

path_output = os.path.join(os.getcwd(),'data')

samples_subset = ['ERR260134','ERR260138','ERR260165','ERR260172','ERR260180']

#%%
fluxes = pd.read_csv("data/minimal_fluxes.csv.gz", compression="gzip")

#%%

fluxes_default = fluxes

fluxes = fluxes.melt(
    id_vars=["sample", "compartment"], var_name="reaction", value_name="flux"
)

#%%
fluxes = fluxes[
    fluxes.reaction.str.startswith("EX_")
    & (fluxes.compartment != "medium")
    & fluxes.reaction.str.endswith("(e)")
].fillna(0)
fluxes["taxa"] = fluxes.compartment + "_" + fluxes["sample"]
fluxes["name"] = fluxes.compartment.str.replace("_", " ")

#%%
samples = pd.read_csv(os.path.join(path_data,"recent.csv"))[
    ["run_accession", "status", "subset", "type"]
]
samples = samples.rename(columns={"run_accession": "sample"})
samples.index = samples["sample"]
samples = samples.loc[samples_subset]

#%%
sample_keep = ["run_accession", "subset", "status", "type"]
SCFAs = {
    "butyrate": "EX_but\\(e\\)",
    "acetate": "EX_ac\\(e\\)",
    "propionate": "EX_ppa\\(e\\)",
}

#%%

species = pd.read_csv(os.path.join(path_data,"genera.csv"))[["samples", "genus", "reads"]]
species["name"] = species.genus
totals = species.groupby("samples").reads.sum()
species["relative"] = species.reads / totals[species.samples].values
fluxes = pd.merge(
    fluxes, species, left_on=["sample", "name"], right_on=["samples", "name"]
)
fluxes["tot_flux"] = fluxes.flux * fluxes.relative

#%% production

groups = SCFAs

fluxes_p = fluxes[fluxes.tot_flux > 0]

dfs = []
for name, filt in groups.items():
    df = fluxes_p[fluxes_p.reaction.str.contains(filt)].copy()
    res = samples.copy()
    df = df.groupby(["sample", "compartment"]).tot_flux.sum().reset_index()
    res["flux"] = df.groupby("sample").tot_flux.sum().abs()
    res["metabolite"] = name
    dfs.append(res)

#%% consumption

print("Consumption rates:")


fluxes_c = fluxes[fluxes.tot_flux < 0]

dfs_c = []
for name, filt in groups.items():
    df_c = fluxes_c[fluxes_c.reaction.str.contains(filt)].copy()
    res = samples.copy()
    df_c = df_c.groupby(["sample", "compartment"]).tot_flux.sum().reset_index()
    res["flux"] = df_c.groupby("sample").tot_flux.sum().abs()
    res["metabolite"] = name
    dfs_c.append(res)

#%%