import numpy as np
import pandas as pd
import os

def get_datadir():
    return os.path.join(os.getenv('HOME'), 'Dropbox', 'C4SF-datasci-homeless', 'raw')

def encode_boolean(df, col):
    '''Encode values as booleans.
    If the string is 'Yes', the new value will be True. Otherwise it will be False.
    '''
    df.loc[df[col] == 'Yes', col] = True
    df.loc[df[col] == 'No', col] = False
    df.loc[df[col] == 'Not Applicable - Child', col] = False
    df.loc[df[col].isin(['Client refused',
                         "Client doesn't know",
                         'Data not collected',
                         '',
                         np.nan]), col] = False
    return df

def encode_unknown(df, col):
    '''Change non-informative values to 'Unknown'.
    '''
    df.loc[df[col].isin(['Client refused',
                         'Refused',
                         "Client doesn't know",
                         'Data not collected',
                         '',
                         np.nan]), col] = 'Unknown'
    return df

def process_data_client(sheet='Client', datadir=None):
    if datadir is None:
        datadir = get_datadir()
    
    cols = [
        'Personal ID',
        'Race',
        'Ethnicity',
        'Gender',
        'Veteran Status',
        ]

    infile = os.path.join(datadir, '{s}.csv'.format(s=sheet))

    df_client = pd.read_csv(infile, header=0, index_col=0, usecols=cols)
    df_client = df_client.dropna(how='all')
    df_client.index = df_client.index.astype(int)

    cols = ['Race', 'Ethnicity', 'Veteran Status']

    # fill in missing values
    for col in cols:
        df_client[col] = df_client[col].fillna(value='')

    # Remove "(HUD) from strings
    for col in cols:
        df_client[col] = df_client[col].apply(lambda x: x.replace(' (HUD)', ''))

    # and encode booleans
    df_client = encode_boolean(df_client, 'Veteran Status')

    # Some are unknown
    df_client = encode_unknown(df_client, 'Race')
    df_client = encode_unknown(df_client, 'Ethnicity')
    df_client = encode_unknown(df_client, 'Gender')
    
    return df_client

def process_data_enrollment(sheet='Enrollment', datadir=None):
    if datadir is None:
        datadir = get_datadir()
    
    cols = [
        'Personal ID',
        'Project Entry ID',
        'Client Age at Entry',
        'Last Permanent Zip',
        'Entry Date',
        'Exit Date',
        'Project ID',
        'Housing Status @ Project Start',
        'Living situation before program entry?',
        'Client Location',
        'Household ID',
        'Relationship to HoH',
        'Disabling Condition',
        'Continuously Homeless One Year',
        'Times Homeless Past Three Years',
        'Months Homeless This Time',
        'Chronic Homeless',
        'In Permanent Housing',
        'Residential Move In Date',
        'Domestic Violence Victim',
        'DV When Occurred',
        'DV Currently Fleeing',
        ]

    infile = os.path.join(datadir, '{s}.csv'.format(s=sheet))

    df_enroll = pd.read_csv(infile, header=0, index_col=0, usecols=cols,
                            parse_dates=['Entry Date', 'Exit Date', 'Residential Move In Date'],
                            infer_datetime_format=True)

    df_enroll = df_enroll.dropna(axis=0, how='all')
    df_enroll.index = df_enroll.index.astype(int)

    # drop anyone for whom we don't have age
    df_enroll = df_enroll.dropna(subset=['Client Age at Entry'])

    # turn these into integers
    cols = ['Project Entry ID', 'Client Age at Entry', 'Project ID', 'Household ID']
    for col in cols:
        df_enroll[col] = df_enroll[col].astype(int)

    # Remove "(HUD) from strings
    cols = ['Housing Status @ Project Start',
            'Living situation before program entry?',
            'Disabling Condition',
            'Continuously Homeless One Year',
            'Domestic Violence Victim',
            'DV When Occurred',
            'DV Currently Fleeing',
            ]
    for col in cols:
        df_enroll[col] = df_enroll[col].fillna(value='')
        df_enroll[col] = df_enroll[col].apply(lambda x: x.replace(' (HUD)', ''))
        # put the nans back
        df_enroll.loc[df_enroll[col] == '', col] = np.nan

    # encode booleans
    cols = [
        'Disabling Condition',
        'Continuously Homeless One Year',
        'Chronic Homeless',
        'In Permanent Housing',
        'Domestic Violence Victim',
        'DV Currently Fleeing', ]
    for col in cols:
        df_enroll = encode_boolean(df_enroll, col)
    
    # one person has a negative age. make it positive.
    col = 'Client Age at Entry'
    df_enroll.loc[df_enroll[col] < 0, col] = df_enroll.loc[df_enroll[col] < 0, col] * -1
    
    # Only keep rows with exit date
    df_enroll = df_enroll[df_enroll['Exit Date'].notnull()]
    
    # calculate the number of days that someone was enrolled
    df_enroll['Days Enrolled'] = ((df_enroll['Exit Date'] - df_enroll['Entry Date']) / np.timedelta64(1, 'D')).astype(int)
    
    # remove anyone with negative number of enrollment days
    df_enroll = df_enroll[df_enroll['Days Enrolled'] >= 0]
    
    return df_enroll

def process_data_disability(sheet='Disability', datadir=None):
    if datadir is None:
        datadir = get_datadir()
    
    cols = [
        'Personal ID',
        'Disability Type',
        'Receiving Services For',
        'Disabilities ID',
        'Project Entry ID',
        ]

    infile = os.path.join(datadir, '{s}.csv'.format(s=sheet))

    df_disability = pd.read_csv(infile, header=0, index_col=0, usecols=cols)

    df_disability = df_disability.dropna(axis=0, how='all')
    df_disability.index = df_disability.index.astype(int)

    # turn these into integers
    cols = ['Disabilities ID', 'Project Entry ID']
    for col in cols:
        df_disability[col] = df_disability[col].astype(int)

    # Remove "(HUD) from strings
    cols = ['Disability Type',
            'Receiving Services For',
            ]
    for col in cols:
        df_disability[col] = df_disability[col].fillna(value='')
        df_disability[col] = df_disability[col].apply(lambda x: x.replace(' (HUD)', ''))
        # put the nans back
        df_disability.loc[df_disability[col] == '', col] = np.nan

    # encode booleans
    col = 'Receiving Services For'
    df_disability = encode_boolean(df_disability, col)
    
    return df_disability

def process_data_healthins(sheet='HealthInsurance', datadir=None):
    if datadir is None:
        datadir = get_datadir()
    
    cols = [
        'Personal ID',
        'Health Insurance Information Date',
        'Health Insurance',
        'Data Collection Stage',
        ]

    infile = os.path.join(datadir, '{s}.csv'.format(s=sheet))

    df_healthins = pd.read_csv(infile, header=0, index_col=0, usecols=cols,
                               parse_dates=['Health Insurance Information Date'],
                               infer_datetime_format=True)

    df_healthins = df_healthins.dropna(axis=0, how='all')
    df_healthins.index = df_healthins.index.astype(int)
    return df_healthins

def process_data_benefit(sheet = 'Benefit', datadir=None):
    if datadir is None:
        datadir = get_datadir()
    
    cols = [
        'Personal ID',
        'Project Entry ID',
        'Non-Cash Information Date',
        'Non-Cash Benefit',
        'Data Collection Stage',
        ]

    infile = os.path.join(datadir, '{s}.csv'.format(s=sheet))

    df_benefit = pd.read_csv(infile, header=0, index_col=0, usecols=cols,
                             parse_dates=['Non-Cash Information Date'],
                             infer_datetime_format=True)

    df_benefit = df_benefit.dropna(axis=0, how='all')
    df_benefit.index = df_benefit.index.astype(int)

    # Drop any project missing the code
    df_benefit = df_benefit.dropna(how='any', subset=['Non-Cash Benefit'])

    df_benefit['Project Entry ID'] = df_benefit['Project Entry ID'].astype(int)

    # Remove "(HUD) from strings
    cols = ['Non-Cash Benefit',
            ]
    for col in cols:
        df_benefit[col] = df_benefit[col].fillna(value='')
        df_benefit[col] = df_benefit[col].apply(lambda x: x.replace(' (HUD)', ''))
        # put the nans back
        df_benefit.loc[df_benefit[col] == '', col] = np.nan

    # shorten some column values
    col = 'Non-Cash Benefit'
    df_benefit.loc[df_benefit[col] == 'Supplemental Nutrition Assistance Program (Food Stamps)', col] = 'Food Stamps'
    df_benefit.loc[df_benefit[col] == 'Special Supplemental Nutrition Program for WIC', col] = 'WIC'
    df_benefit.loc[df_benefit[col] == 'Section 8, Public Housing, or other ongoing rental assistance', col] = 'Section 8, Public Housing'
    return df_benefit

def process_data_income(sheet='Income Entry & Exit', datadir=None):
    if datadir is None:
        datadir = get_datadir()
    
    cols = [
        'Personal ID',
        'Project Entry ID',
        'Entry Alimony',
        'Entry Child Support',
        'Entry Earned',
        'Entry GA',
        'Entry Other',
        'Entry Pension',
        'Entry Private Disability',
        'Entry Social Security Retirement',
        'Entry SSDI',
        'Entry SSI',
        'Entry TANF',
        'Entry Unemployment',
        'Entry VA Non-Service',
        'Entry VA Service Connected',
        "Entry Worker's Compensation",
        'Entry Total Income',
        'Exit Alimony',
        'Exit Child Support',
        'Exit Earned',
        'Exit GA',
        'Exit Other',
        'Exit Pension',
        'Exit Private Disability',
        'Exit Social Security Retirement',
        'Exit SSDI',
        'Exit SSI',
        'Exit TANF',
        'Exit Unemployment',
        'Exit VA Non-Service',
        'Exit VA Service Connected',
        "Exit Worker's Compensation",
        'Exit Total Income',
        'Income Change',
        ]

    infile = os.path.join(datadir, '{s}.csv'.format(s=sheet))

    df_income = pd.read_csv(infile, header=0, index_col=0, usecols=cols)

    df_income = df_income.dropna(axis=0, how='all')
    df_income.index = df_income.index.astype(int)

    # turn these into integers
    cols = ['Project Entry ID']
    for col in cols:
        df_income[col] = df_income[col].astype(int)

    # assume all nans are $0
    df_income = df_income.fillna(value='0')

    # turn the dollar strings into integers
    for col in df_income.columns:
        if col != 'Project Entry ID':
            df_income[col] = df_income[col].str.replace(',', '')
            df_income[col] = df_income[col].str.replace(r'[^-+\d.]', '').astype(int)

    return df_income

def process_data_project(sheet='Project', datadir=None):
    if datadir is None:
        datadir = get_datadir()
    
    cols = [
        'Project ID',
        'Project Name',
        'Project Type Code',
        'Address City',
        'Address Postal Code',
        ]

    infile = os.path.join(datadir, '{s}.csv'.format(s=sheet))

    df_project = pd.read_csv(infile, header=0, index_col=1, usecols=cols)

    df_project.head()

    df_project = df_project.dropna(axis=0, how='all')
    df_project.index = df_project.index.astype(int)

    # Drop any project missing the code
    df_project = df_project.dropna(how='any', subset=['Project Type Code'])

    # Remove "(HUD) from strings
    cols = ['Project Type Code',
            ]
    for col in cols:
        df_project[col] = df_project[col].fillna(value='')
        df_project[col] = df_project[col].apply(lambda x: x.replace(' (HUD)', ''))
        # put the nans back
        df_project.loc[df_project[col] == '', col] = np.nan

    # convert postal code to integer; 0 if postal code is missing
    df_project['Address Postal Code'] = df_project['Address Postal Code'].fillna(value='0')
    df_project['Address Postal Code'] = df_project['Address Postal Code'].apply(lambda x: x[:5])
    df_project['Address Postal Code'] = df_project['Address Postal Code'].astype(int)

    return df_project

def process_data_service(sheet='Service', datadir=None):
    if datadir is None:
        datadir = get_datadir()
    
    cols =  [
        'Personal ID',
        'Services ID',
        'Date Provided',
        'Date Ended',
        'Service Code',
        'Description',
        'Project ID',
        'Record Type',
        'Project Entry ID',
        ]

    infile = os.path.join(datadir, '{s}.csv'.format(s=sheet))

    df_service = pd.read_csv(infile, header=0, index_col=0, usecols=cols,
                             parse_dates=['Date Provided', 'Date Ended'],
                             infer_datetime_format=True)

    df_service = df_service.dropna(axis=0, how='all')
    df_service.index = df_service.index.astype(int)

    # Drop anyone missing these IDs
    df_service = df_service.dropna(how='any', subset=['Project ID', 'Project Entry ID'])

    # turn these into integers
    cols = ['Project ID', 'Project Entry ID']
    for col in cols:
        df_service[col] = df_service[col].astype(int)

    # drop any null dates
    df_service = df_service.dropna(subset=['Date Provided', 'Date Ended'])
    
    # calculate the number of days service was given
    df_service['Days'] = ((df_service['Date Ended'] - df_service['Date Provided']) / np.timedelta64(1, 'D')).astype(int)
    
    return df_service

def process_data_bedinventory(sheet='BedInventory', datadir=None):
    if datadir is None:
        datadir = get_datadir()
    
    cols = [
        'Project ID',
        'Inventory ID',
        'Inventory Household Type',
        'HMIS Participating Beds',
        'Inventory Start Date',
        'Inventory End Date',
        'Unit Inventory',
        'Bed Inventory',
        'Vet Bed Inventory',
        'Youth Bed Inventory',
        'Youth Bed Age Group',
        ]

    infile = os.path.join(datadir, '{s}.csv'.format(s=sheet))

    df_bedinv = pd.read_csv(infile, header=0, index_col=0, usecols=cols,
                            parse_dates=['Inventory Start Date', 'Inventory End Date'],
                            infer_datetime_format=True)

    df_bedinv = df_bedinv.dropna(axis=0, how='all')
    df_bedinv.index = df_bedinv.index.astype(int)

    # turn these into integers, assume zero if NaN
    cols = ['Inventory ID', 'HMIS Participating Beds', 'Unit Inventory', 'Bed Inventory', 'Vet Bed Inventory', 'Youth Bed Inventory']
    for col in cols:
        # df_bedinv[col] = df_bedinv.loc[~df_bedinv[col].isnull(), col].apply(lambda x: int(x))
        df_bedinv[col] = df_bedinv[col].fillna(value=0)
        df_bedinv[col] = df_bedinv[col].astype(int)
    
    return df_bedinv
