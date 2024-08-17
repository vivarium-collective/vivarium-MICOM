"""Extract minimal growth media and growth rates."""
import os
import pandas as pd
import micom
from micom import load_pickle
from micom.media import minimal_medium
from micom.logger import logger

#%%

path_data = os.path.join(os.getenv("HOME"),'projects','micom_validation','paper','data')

path_model = os.path.join(os.getcwd(),'models')

path_output = os.path.join(os.getcwd(),'data')

if not os.path.exists(path_output):
    os.mkdir(path_output)

#%%

# @profile
def media_and_gcs(sample_id):
    com = load_pickle("models/" + sample_id + ".pickle")

    # Get growth rates
    try:
        sol = com.cooperative_tradeoff(fraction=0.5)
        rates = sol.members["growth_rate"].copy()
        rates["community"] = sol.growth_rate
        rates.name = sample_id
    except Exception:
        logger.warning("Could not solve cooperative tradeoff for %s." % sample_id)
        return None

    # Get the minimal medium
    med = minimal_medium(com, 0.95 * sol.growth_rate, exports=True)
    med.name = sample_id

    # Apply medium and reoptimize
    com.medium = med[med > 0]
    sol = com.cooperative_tradeoff(fraction=0.5, fluxes=True, pfba=False)
    fluxes = sol.fluxes
    fluxes["sample"] = sample_id
    return {"medium": med, "gcs": rates, "fluxes": fluxes}


# samples = pd.read_csv("data/recent.csv")
# gcs = pd.DataFrame()
# media = pd.DataFrame()
# fluxes = pd.DataFrame()

#%%

samples = pd.read_csv(os.path.join(path_data,"recent.csv"))
samples_subset = ['ERR260134','ERR260138','ERR260165','ERR260172','ERR260180']


#%%

results = []

for sample in samples_subset:
    result_sample = media_and_gcs(sample)
    results.append(result_sample)

#%%
gcs = pd.DataFrame()
media = pd.DataFrame()
fluxes = pd.DataFrame()
for r in results:
    # gcs = gcs.concat(r["gcs"])
    gcs = pd.concat([gcs, r["gcs"]], axis=1)
    # media = media.concat(r["medium"])
    media = pd.concat([media, r["medium"]], axis=1)
    # fluxes = fluxes.concat(r["fluxes"])
    fluxes = pd.concat([fluxes, r["fluxes"]], axis=0)

# fluxes = fluxes.transpose()
fluxes["compartment"] = list(fluxes.index)

#%%

gcs.transpose().to_csv(os.path.join(path_output,"growth_rates.csv"))
media.transpose().to_csv(os.path.join(path_output,"minimal_imports.csv"))
fluxes.to_csv(os.path.join(path_output,"minimal_fluxes.csv.gz"), compression="gzip")

