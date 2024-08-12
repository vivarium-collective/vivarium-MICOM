"""Extract minimal growth media and growth rates."""

import pandas as pd
import micom
from micom import load_pickle
from micom.media import minimal_medium
from micom.workflows import workflow
from micom.logger import logger


logger = micom.logger.logger
try:
    max_procs = snakemake.threads
except NameError:
    max_procs = 20

@profile
def media_and_gcs(sam):
    com = load_pickle("data/models/" + sam + ".pickle")

    # Get growth rates
    try:
        sol = com.cooperative_tradeoff(fraction=0.5)
        rates = sol.members["growth_rate"].copy()
        rates["community"] = sol.growth_rate
        rates.name = sam
    except Exception:
        logger.warning("Could not solve cooperative tradeoff for %s." % sam)
        return None

    # Get the minimal medium
    med = minimal_medium(com, 0.95 * sol.growth_rate, exports=True)
    med.name = sam

    # Apply medium and reoptimize
    com.medium = med[med > 0]
    sol = com.cooperative_tradeoff(fraction=0.5, fluxes=True, pfba=False)
    fluxes = sol.fluxes
    fluxes["sample"] = sam
    return {"medium": med, "gcs": rates, "fluxes": fluxes}


# samples = pd.read_csv("data/recent.csv")
# gcs = pd.DataFrame()
# media = pd.DataFrame()
# fluxes = pd.DataFrame()
#%%
# results = workflow(media_and_gcs, samples.run_accession, max_procs)
result_000 = media_and_gcs('ERR260134')

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
