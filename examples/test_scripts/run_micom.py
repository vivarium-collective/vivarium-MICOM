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
samples_subset = samples.run_accession.values
samples_subset.sort()
samples_subset = samples_subset[:5]

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

gcs.transpose().to_csv("data/growth_rates.csv")
media.transpose().to_csv("data/minimal_imports.csv")
fluxes.to_csv("data/minimal_fluxes.csv.gz", compression="gzip")


#%%
# results = workflow(media_and_gcs, samples.run_accession, max_procs)
# result = media_and_gcs('ERR260134_0')

#%%
#
# gcs_000 = result_000["gcs"]
# media_000 = result_000["medium"]
# fluxes_000 = result_000["fluxes"]


#%%
#
# gcs_paper = pd.read_csv("data/growth_rates.csv",sep=',',index_col=0,header=0)

#%%
#
# gcs_compare = pd.DataFrame(index=gcs_paper.columns)
#
# gcs_compare['paper'] = gcs_paper.loc['ERR260134'].values
#
# gcs_compare['reproduced'] = np.ones(len(gcs_compare['paper'].values))*np.nan
#
# for genus in gcs_000.index:
#     gcs_compare.loc[genus,'reproduced'] = gcs_000[genus]
#
# gcs_compare = gcs_compare.dropna(axis=0)
#
# gcs_compare['ratio'] = gcs_compare['reproduced'].values/gcs_compare['paper'].values

#%%

# for r in results:
#     gcs = gcs.append(r["gcs"])
#     media = media.append(r["medium"])
#     fluxes = fluxes.append(r["fluxes"])
#
# gcs.to_csv("data/growth_rates.csv")
# media.to_csv("data/minimal_imports.csv")
# fluxes.to_csv("data/minimal_fluxes.csv.gz", compression="gzip")
