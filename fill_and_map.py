import pandas as pd
import numpy as np
from pathlib import Path

def map_econ_sdg(fpath):
    # map sdgs to economic expenses

    # load mapping data
    sdg_econ_map_in = pd.read_excel(fpath,
                                    sheet_name='SDG-DEA Economic',
                                    usecols='BN:BR',
                                    skiprows=[0,1,2,4],
                                    nrows=2,
                                    header=None
                                    )

    sdg_map = sdg_econ_map_in.copy()
    sdg_map.loc[1,:] = [jj.replace('&','').replace(',','').replace(' ','_') for jj in sdg_map.loc[1,:]] # remove special characters for gams later
    sdg_map_d = {}

    for ii in sdg_map.columns:
        sdgv = sdg_map.loc[0,ii]
        if (type(sdgv) == int) & (sdgv not in sdg_map_d): # if it's an integer and not mapped yet, map it
            # sdg_map_d[sdgv] = sdg_map.loc[1,ii]
            sdg_map_d[sdgv] = [sdg_map.loc[1,ii]]

        elif type(sdgv) == str: # if it's not an integer, split it
            split1 = sdgv.split(',')

            if len(split1) > 1: # if multiple values indicate a list of numbers as strings
                # sdgd2 = {int(vv):sdg_map.loc[1,ii] for vv in split1 if int(vv) not in sdg_map_d} # make a second dict with all new numbers and add them
                sdgd2 = {int(vv):[sdg_map.loc[1,ii]] for vv in split1 if int(vv) not in sdg_map_d} # make a second dict with all new numbers and add them
                sdg_map_d.update(sdgd2)
        else:
            print('something unexpected happened')

    for ii in range(1,18): # map the remaining sdgs to the final economic category
        if ii not in sdg_map_d:
            # sdg_map_d[ii] = sdg_map.iloc[1,-1]
            sdg_map_d[ii] = [sdg_map.iloc[1,-1]]

    return(sdg_map_d)


def sep_inds():
    # identify indicators to be skipped, or undesired
    use_inds_path = Path('data_raw/use_inds.xlsx')
    use_inds = pd.read_excel(use_inds_path, usecols='A:D')
    skip_inds = use_inds['ind_name'][use_inds['use']=='no']
    undes_inds = use_inds['ind_name'][use_inds['issue']=='undesired']
    return(skip_inds.tolist(), undes_inds.tolist(), use_inds)


def fill_econ(fpath):
    # load economic indicators and fill missing values

    # load economic indicators
    sdg_econ_in =  pd.read_excel(fpath,
                                sheet_name='SDG-DEA Economic',
                                usecols='B,BM:BR',
                                skiprows=[0,1,2],
                                header=2,
                                index_col=0
                                )

    sdg_econ = sdg_econ_in.copy()
    sdg_econ = sdg_econ.rename_axis(None, axis=1)

    # fix column names
    sdg_econ.columns = [c.split('.')[0] for c in sdg_econ.columns] 
    sdg_econ.columns = [sdg_econ.columns[0],*[jj.replace('&','').replace(',','').replace(' ','_') for jj in sdg_econ.columns[1:]]] # remove special characters

    # fill missing and zero values with income group averages
    sdg_econ.iloc[:,1:] = sdg_econ.iloc[:,1:].clip(lower=0) # treat negatives as zeros
    sdg_econ.replace(0, np.nan, inplace=True) # treat zeros as NaNs
    sdg_econ.fillna(sdg_econ.groupby(sdg_econ.columns[0])[sdg_econ.columns[1:]].transform('mean'), inplace=True)

    return(sdg_econ)


# def fill_inds(fpath):
#     # load sdg indicators and fill missing values
#     sdg_in = pd.read_excel(fpath,
#                         sheet_name='SDG-DEA FINAL',
#                         header=4,
#                         index_col=0,
#                         usecols='B,T:DQ',
#                         skiprows=[5])

#     # load economic indicators for income categories
#     sdg_econ = fill_econ(fpath)

#     # fill missing indicator data with income category means
#     inds = sdg_in.copy()
#     inc_cat = sdg_econ.iloc[:,0].unique() # income categories

#     for ii in inc_cat:
#         idx = sdg_econ[sdg_econ.iloc[:,0] == ii].index
#         inds.loc[idx,:] = inds.loc[idx,:].fillna(inds.loc[idx,:].mean())

#     inds = inds[inds.index.notnull()] # remove nan rows

#     return(inds)


def fill_inds_trans(fpath, report_skips=True):
    # load transformed sdg indicators and fill missing values
    inds_t = pd.read_excel(fpath,
                        engine='xlrd',
                        sheet_name='SDG-DEA FINAL transformed',
                        header=5,
                        index_col=0,
                        usecols='B,T:DQ',
                        skiprows=[6]
                        )

    skip, *_ = sep_inds()

    # add income categories
    sdg_econ = fill_econ(fpath)
    inc_cat = sdg_econ.iloc[:,0].unique() # income categories

    # remove countries with more than [cutoff] missing data
    cutoff = 0.2
    if report_skips == True:
        idx_c = inds_t[inds_t.isna().sum(axis=1)/inds_t.shape[1] >= cutoff].index
        print('Removing countries with >={0}% missing indicator values:\n'.format(str(100*cutoff)), (inds_t.isna().sum(axis=1)/inds_t.shape[1])[idx_c])

    inds_t = inds_t[inds_t.isna().sum(axis=1)/inds_t.shape[1] < cutoff]

    # do the same for indicators
    cutoff = 0.35
    flt = (inds_t.isna().sum(axis=0)/inds_t.shape[0] >= cutoff)
    if report_skips == True:
        print('\nRemoving indicators with >={0}% missing country values:\n'.format(str(100*cutoff)), (inds_t.isna().sum(axis=0)/inds_t.shape[0])[flt])
    inds_t = inds_t.drop(inds_t.loc[:,flt].columns, axis=1)

    # match econ index
    sdg_econ = sdg_econ.loc[inds_t.index,:]

    # fill nans with means of income categories
    for ii in inc_cat:
        idx = sdg_econ[sdg_econ.iloc[:,0] == ii].index
        inds_t.loc[idx,:] = inds_t.loc[idx,:].fillna(inds_t.loc[idx,:].mean())

    # use original column names without _inv
    inds_t.columns = [ii.replace('_inv','') for ii in inds_t.columns]
    
    # also skip indicators defined manually
    inds_t = inds_t.drop(skip, axis=1)
    
    return(inds_t)


def map_inds_sdg(fpath):
    # map sdgs to indicators
    sdg_map_in = pd.read_excel(fpath,
                            sheet_name='SDG-DEA FINAL',
                            usecols='T:DQ',
                            nrows=2,
                            skiprows=[0,1,2],
                            header=None
                            )

    sdg_map_in = sdg_map_in.fillna(method='ffill', axis=1)
    sdg_map = sdg_map_in.copy().transpose()

    inds_map = {}
    for sdg in sdg_map.iloc[:,0].unique():
        sdg_num = int(sdg.replace('SDG','').replace(' ','')) # get sdg number as integer
        inds_map[sdg_num] = sdg_map[sdg_map.iloc[:,0]==sdg].iloc[:,1].tolist() # list of indicators mapped to this sdg

    # remove indicators we skip because of missing data, or manually
    inds = fill_inds_trans(fpath, report_skips=False)
    inds_map = {k:[ii for ii in v if ii in inds.columns] for k, v in inds_map.items()}
    
    return(inds_map)