import pandas as pd
import numpy as np

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
            sdg_map_d[sdgv] = sdg_map.loc[1,ii]

        elif type(sdgv) == str: # if it's not an integer, split it
            split1 = sdgv.split(',')

            if len(split1) > 1: # if multiple values indicate a list of numbers as strings
                sdgd2 = {int(vv):sdg_map.loc[1,ii] for vv in split1 if int(vv) not in sdg_map_d} # make a second dict with all new numbers and add them
                sdg_map_d.update(sdgd2)
        else:
            print('something unexpected happened')

    for ii in range(1,18): # map the remaining sdgs to the final economic category
        if ii not in sdg_map_d:
            sdg_map_d[ii] = sdg_map.iloc[1,-1]

    return(sdg_map_d)


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

    sdg_map_d = {}
    for sdg in sdg_map.iloc[:,0].unique():
        sdg_num = int(sdg.replace('SDG','').replace(' ','')) # get sdg number as integer
        sdg_map_d[sdg_num] = sdg_map[sdg_map.iloc[:,0]==sdg].iloc[:,1].tolist() # list of indicators mapped to this sdg
    
    return(sdg_map_d)


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
    del sdg_econ.index.name # remove index column name for gams later

    # fix column names
    sdg_econ.columns = [c.split('.')[0] for c in sdg_econ.columns] 
    sdg_econ.columns = [sdg_econ.columns[0],*[jj.replace('&','').replace(',','').replace(' ','_') for jj in sdg_econ.columns[1:]]] # remove special characters

    # fill missing and zero values with income group averages
    sdg_econ.replace(0, np.nan, inplace=True)
    sdg_econ.fillna(sdg_econ.groupby(sdg_econ.columns[0])[sdg_econ.columns[1:]].transform('mean'), inplace=True)

    return(sdg_econ)


def fill_inds(fpath):
    # load sdg indicators and fill missing values
    sdg_in = pd.read_excel(fpath,
                        sheet_name='SDG-DEA FINAL',
                        header=4,
                        index_col=0,
                        usecols='B,T:DQ',
                        skiprows=[5])

    # load economic indicators for income categories
    sdg_econ = fill_econ(fpath)

    # fill missing indicator data with income category means
    inds = sdg_in.copy()
    inc_cat = sdg_econ.iloc[:,0].unique() # income categories

    for ii in inc_cat:
        idx = sdg_econ[sdg_econ.iloc[:,0] == ii].index
        inds.loc[idx,:] = inds.loc[idx,:].fillna(inds.loc[idx,:].mean())

    inds = inds[inds.index.notnull()] # remove nan rows

    return(inds)


def fill_inds_trans(fpath):
    # load transformed sdg indicators and fill missing values
    sdg_in_trans = pd.read_excel(fpath,
                        sheet_name='SDG-DEA FINAL transformed',
                        header=5,
                        index_col=0,
                        usecols='B,T:DQ',
                        skiprows=[6]
                        )    

    # load economic indicators for income categories
    sdg_econ = fill_econ(fpath)

    # fill missing indicator data with income category means
    inds_t = sdg_in_trans.copy()
    inc_cat = sdg_econ.iloc[:,0].unique() # income categories

    # fill nans with means of income categories
    for ii in inc_cat:
        idx = sdg_econ[sdg_econ.iloc[:,0] == ii].index
        inds_t.loc[idx,:] = inds_t.loc[idx,:].fillna(inds_t.loc[idx,:].mean())

    inds_t = inds_t[inds_t.index.notnull()] # remove nan rows

    # use original column names without _inv
    inds_t.columns = [ii.replace('_inv','') for ii in inds_t.columns]
    
    return(inds_t)
