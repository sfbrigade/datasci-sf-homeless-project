import numpy as np
import pandas as pd
import os
import re

from sklearn.feature_extraction import DictVectorizer

def get_datadir():
    return os.path.join(os.getenv('HOME'), 'Dropbox', 'C4SF-datasci-homeless', 'raw')

def encode_boolean(df, col, val=False):
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
                         np.nan]), col] = val
    return df

def encode_unknown(df, col, val='Unknown'):
    '''Change non-informative values to 'Unknown'.
    '''
    df.loc[df[col].isin(['Client refused',
                         'Refused',
                         "Client doesn't know",
                         'Data not collected',
                         '',
                         np.nan]), col] = val
    return df

def process_data_client(sheet='Client', datadir=None, simplify_strings=False):
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

    # remove any full duplicates
    df_client = df_client.reset_index().drop_duplicates().set_index('Personal ID')

    cols = ['Race', 'Ethnicity', 'Veteran Status']

    # fill in missing values
    for col in cols:
        df_client[col] = df_client[col].fillna(value='')

    # Remove "(HUD) from strings
    for col in cols:
        df_client[col] = df_client[col].apply(lambda x: x.replace('(HUD)', '').strip() if isinstance(x, str) else np.nan)

    # and encode booleans
    df_client = encode_boolean(df_client, 'Veteran Status')

    # Some are unknown
    df_client = encode_unknown(df_client, 'Race')
    df_client = encode_unknown(df_client, 'Ethnicity')
    df_client = encode_unknown(df_client, 'Gender')

    if simplify_strings:
        col = 'Race'
        df_client.loc[df_client[col] == 'Black or African American', col] = 'Black'
        df_client.loc[df_client[col] == 'American Indian or Alaska Native', col] = 'AmerIndian'
        df_client.loc[df_client[col] == 'Native Hawaiian or Other Pacific Islander', col] = 'PacificIsl'
        df_client[col] = df_client[col].apply(lambda x: x.lower())
        col = 'Ethnicity'
        df_client.loc[df_client[col] == 'Hispanic/Latino', col] = 'Latino'
        df_client.loc[df_client[col] == 'Non-Hispanic/Non-Latino', col] = 'NonLatino'
        df_client[col] = df_client[col].apply(lambda x: x.lower())
        col = 'Gender'
        df_client.loc[df_client[col] == 'Transgender male to female', col] = 'TransMtoF'
        df_client.loc[df_client[col] == 'Transgender female to male', col] = 'TransFtoM'
        df_client[col] = df_client[col].apply(lambda x: x.lower())

    return df_client

def process_data_enrollment(sheet='Enrollment', datadir=None, simplify_strings=False):
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

    # remove any full duplicates
    df_enroll = df_enroll.reset_index().drop_duplicates().set_index('Personal ID')

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
        df_enroll[col] = df_enroll[col].apply(lambda x: x.replace('(HUD)', '').strip() if isinstance(x, str) else np.nan)

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

    old_col = 'Residential Move In Date'
    new_col = 'Days To Residential Move In'
    dummy_date = pd.to_datetime('1970-01-01')
    df_enroll[old_col] = df_enroll[old_col].fillna(dummy_date)
    df_enroll[new_col] = ((df_enroll[old_col] - df_enroll['Entry Date']) / np.timedelta64(1, 'D')).astype(int)
    df_enroll.loc[df_enroll[new_col] <= 0, new_col] = np.nan
    df_enroll.loc[df_enroll[old_col] == dummy_date, old_col] = pd.NaT

    # remove anyone with negative number of enrollment days
    df_enroll = df_enroll[df_enroll['Days Enrolled'] >= 0]

    # turn DV When Occurred into numerical data
    col = 'DV When Occurred'
    df_enroll = encode_unknown(df_enroll, col)
    df_enroll.loc[df_enroll[col] == 'Unknown', col] = np.nan
    df_enroll.loc[df_enroll[col] == 'N/A - No Domestic Violence', col] = np.nan
    df_enroll.loc[df_enroll[col] == 'More than a year ago', col] = 24
    df_enroll.loc[df_enroll[col] == 'From six to twelve months ago', col] = 12
    df_enroll.loc[df_enroll[col] == 'Three to six months ago', col] = 6
    df_enroll.loc[df_enroll[col] == 'Within the past three months', col] = 3
    # and rename the column
    df_enroll = df_enroll.rename(columns={col: 'Months Ago DV Occurred'})

    # process head of household to be boolean
    old_col = 'Relationship to HoH'
    new_col = 'Head of Household'
    df_enroll[new_col] = False
    df_enroll.loc[df_enroll[old_col] == 'Self (head of household)', new_col] = True
    df_enroll = df_enroll.drop(old_col, axis=1)

    # turn Months Homeless This Time into numerical data
    col = 'Months Homeless This Time'
    df_enroll = encode_unknown(df_enroll, col)
    values = df_enroll[col].unique().tolist()
    df_enroll.loc[df_enroll[col] == 'More than 12 months', col] = '24'
    df_enroll[col] = df_enroll[col].apply(lambda x: int(x) if isinstance(x, str) & x.isdigit() else x)
    df_enroll.loc[df_enroll[col] == 'Unknown', col] = np.nan

    # turn Times Homeless Past Three Years into numerical data
    col = 'Times Homeless Past Three Years'
    df_enroll = encode_unknown(df_enroll, col)
    df_enroll.loc[df_enroll[col] == '4 or more', col] = '4'
    df_enroll[col] = df_enroll[col].apply(lambda x: int(x) if isinstance(x, str) & x.isdigit() else x)
    df_enroll.loc[df_enroll[col] == 'Unknown', col] = np.nan

    col = 'Housing Status @ Project Start'
    df_enroll = encode_unknown(df_enroll, col)
    col = 'Living situation before program entry?'
    df_enroll = encode_unknown(df_enroll, col)

    if simplify_strings:
        col = 'Housing Status @ Project Start'
        df_enroll.loc[df_enroll[col] == 'Stably housed', col] = 'Housed'
        df_enroll.loc[df_enroll[col] == 'At-risk of homelessness', col] = 'AtRisk'
        df_enroll.loc[df_enroll[col] == 'Category 1 - Homeless', col] = 'Cat1Homeless'
        df_enroll.loc[df_enroll[col] == 'Category 2 - At imminent risk of losing housing', col] = 'Cat2RiskLosing'
        df_enroll.loc[df_enroll[col] == 'Category 3 - Homeless only under other federal statutes', col] = 'Cat3HomelessFedStatutes'
        df_enroll.loc[df_enroll[col] == 'Category 4 - Fleeing domestic violence', col] = 'Cat4FleeingDV'
        df_enroll[col] = df_enroll[col].apply(lambda x: x.lower())

        col = 'Living situation before program entry?'
        df_enroll.loc[df_enroll[col] == 'Place not meant for habitation', col] = 'Streets'
        df_enroll.loc[df_enroll[col] == 'Emergency shelter, including hotel or motel paid for with emergency shelter voucher', col] = 'EmerShelter'
        df_enroll.loc[df_enroll[col] == 'Hotel or motel paid for without emergency shelter voucher', col] = 'Hotel'
        df_enroll.loc[df_enroll[col] == "Staying or living in a friend's room, apartment or house", col] = 'Friend'
        df_enroll.loc[df_enroll[col] == "Staying or living in a family member's room, apartment or house", col] = 'Family'
        df_enroll.loc[df_enroll[col] == 'Hospital or other residential non-psychiatric medical facility', col] = 'Hospital'
        df_enroll.loc[df_enroll[col] == 'Psychiatric hospital or other psychiatric facility', col] = 'HospitalPsych'
        df_enroll.loc[df_enroll[col] == 'Substance abuse treatment facility or detox center', col] = 'DetoxCenter'
        df_enroll.loc[df_enroll[col] == 'Long-term care facility or nursing home', col] = 'LongTermCare'
        df_enroll.loc[df_enroll[col] == 'Foster care home or foster care group home', col] = 'Foster'
        df_enroll.loc[df_enroll[col] == 'Safe Haven', col] = 'SafeHaven'
        df_enroll.loc[df_enroll[col] == 'Jail, prison or juvenile detention facility', col] = 'Jail'
        df_enroll.loc[df_enroll[col] == 'Transitional housing for homeless persons (including homeless youth)', col] = 'TransitionalHousing'
        df_enroll.loc[df_enroll[col] == 'Residential project or halfway house with no homeless criteria', col] = 'HalfwayHouse'
        df_enroll.loc[df_enroll[col] == 'Permanent housing for formerly homeless persons', col] = 'PermanentHousing'
        df_enroll.loc[df_enroll[col] == 'Rental by client, no ongoing housing subsidy', col] = 'Rental'
        df_enroll.loc[df_enroll[col] == 'Rental by client, with VASH subsidy', col] = 'RentalVASH'
        df_enroll.loc[df_enroll[col] == 'Rental by client, with GPD TIP subsidy', col] = 'RentalGDPTIP'
        df_enroll.loc[df_enroll[col] == 'Rental by client, with other ongoing housing subsidy', col] = 'RentalOther'
        df_enroll.loc[df_enroll[col] == 'Owned by client, no ongoing housing subsidy', col] = 'Owned'
        df_enroll.loc[df_enroll[col] == 'Owned by client, with ongoing housing subsidy', col] = 'OwnedSubsidy'
        df_enroll[col] = df_enroll[col].apply(lambda x: x.lower())
    return df_enroll

def process_data_disability(sheet='Disability', datadir=None, simplify_strings=False):
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

    # remove any full duplicates
    df_disability = df_disability.reset_index().drop_duplicates().set_index('Personal ID')

    # turn these into integers
    cols = ['Disabilities ID', 'Project Entry ID']
    for col in cols:
        df_disability[col] = df_disability[col].astype(int)

    # Remove "(HUD) from strings
    cols = ['Disability Type',
            'Receiving Services For',
            ]
    for col in cols:
        df_disability[col] = df_disability[col].apply(lambda x: x.replace('(HUD)', '').strip() if isinstance(x, str) else np.nan)

    # encode booleans
    col = 'Receiving Services For'
    df_disability = encode_boolean(df_disability, col)

    if simplify_strings:
        col = 'Disability Type'
        df_disability.loc[df_disability[col] == 'Mental Health Problem', col] = 'MentalHealth'
        df_disability.loc[df_disability[col] == 'Chronic Health Condition', col] = 'ChronicHealth'
        df_disability.loc[df_disability[col] == 'Both Alcohol and Drug Abuse', col] = 'AlcoholDrug'
        df_disability.loc[df_disability[col] == 'Alcohol Abuse', col] = 'Alcohol'
        df_disability.loc[df_disability[col] == 'Drug Abuse', col] = 'Drug'
        df_disability.loc[df_disability[col] == 'HIV/AIDS', col] = 'HIVAIDS'
        df_disability.loc[df_disability[col] == 'Substance Abuse', col] = 'Substance'
        df_disability.loc[df_disability[col] == 'Dual Diagnosis', col] = 'DualDiagnosis'
        df_disability.loc[df_disability[col] == 'Vision Impaired', col] = 'Vision'
        df_disability.loc[df_disability[col] == 'Hearing Impaired', col] = 'Hearing'
        df_disability[col] = df_disability[col].apply(lambda x: x.lower() if isinstance(x, str) else np.nan)

    return df_disability

def process_data_healthins(sheet='HealthInsurance', datadir=None, simplify_strings=False):
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

    # remove any full duplicates
    df_healthins = df_healthins.reset_index().drop_duplicates().set_index('Personal ID')

    col = 'Health Insurance'
    df_healthins = encode_unknown(df_healthins, col)

    if simplify_strings:
        col = 'Health Insurance'
        df_healthins.loc[df_healthins[col] == 'State Health Insurance for Adults', col] = 'StateAdult'
        df_healthins.loc[df_healthins[col] == "Veteran's Administration (VA) Medical Services", col] = 'Veteran'
        df_healthins.loc[df_healthins[col] == "State Children's Health Insurance Program", col] = 'StateChild'
        df_healthins.loc[df_healthins[col] == 'Employer - Provided Health Insurance', col] = 'Employer'
        df_healthins.loc[df_healthins[col] == 'Private Pay Health Insurance', col] = 'Pirvate'
        df_healthins.loc[df_healthins[col] == 'Health Insurance obtained through COBRA', col] = 'COBRA'
        df_healthins[col] = df_healthins[col].apply(lambda x: x.lower())

    return df_healthins

def process_data_benefit(sheet='Benefit', datadir=None, simplify_strings=False):
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

    # remove any full duplicates
    df_benefit = df_benefit.reset_index().drop_duplicates().set_index('Personal ID')

    # Drop any project missing the code
    df_benefit = df_benefit.dropna(how='any', subset=['Non-Cash Benefit'])

    df_benefit['Project Entry ID'] = df_benefit['Project Entry ID'].astype(int)

    # Remove "(HUD) from strings
    cols = ['Non-Cash Benefit',
            ]
    for col in cols:
        df_benefit[col] = df_benefit[col].apply(lambda x: x.replace('(HUD)', '').strip() if isinstance(x, str) else np.nan)

    if simplify_strings:
        col = 'Non-Cash Benefit'
        df_benefit.loc[df_benefit[col] == 'Supplemental Nutrition Assistance Program (Food Stamps)', col] = 'FoodStamps'
        df_benefit.loc[df_benefit[col] == 'Special Supplemental Nutrition Program for WIC', col] = 'WIC'
        df_benefit.loc[df_benefit[col] == 'Other Source', col] = 'Other'
        df_benefit.loc[df_benefit[col] == 'Section 8, Public Housing, or other ongoing rental assistance', col] = 'PublicHousing'
        df_benefit.loc[df_benefit[col] == 'Other TANF-Funded Services', col] = 'TANFOther'
        df_benefit.loc[df_benefit[col] == 'TANF Transportation Services', col] = 'TANFTransportation'
        df_benefit.loc[df_benefit[col] == 'TANF Child Care Services', col] = 'TANFChildCare'
        df_benefit.loc[df_benefit[col] == 'Temporary rental assistance', col] = 'TempRental'
        df_benefit[col] = df_benefit[col].apply(lambda x: x.lower())

    return df_benefit

def process_data_income(sheet='Income Entry & Exit', datadir=None, simplify_strings=False):
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

    # remove any full duplicates
    df_income = df_income.reset_index().drop_duplicates().set_index('Personal ID')

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

def process_data_project(sheet='Project', datadir=None, simplify_strings=False):
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

    # remove any full duplicates
    df_project = df_project.reset_index().drop_duplicates().set_index('Project ID')

    # Drop any project missing the code
    df_project = df_project.dropna(how='any', subset=['Project Type Code'])

    # Remove "(HUD) from strings
    cols = ['Project Type Code',
            ]
    for col in cols:
        df_project[col] = df_project[col].apply(lambda x: x.replace('(HUD)', '').strip() if isinstance(x, str) else np.nan)

    # convert postal code to integer; 0 if postal code is missing
    df_project['Address Postal Code'] = df_project['Address Postal Code'].fillna(value='0')
    df_project['Address Postal Code'] = df_project['Address Postal Code'].apply(lambda x: x[:5])
    df_project['Address Postal Code'] = df_project['Address Postal Code'].astype(int)

    if simplify_strings:
        col = 'Project Type Code'
        df_project.loc[df_project[col] == 'Transitional housing', col] = 'TransitionalHousing'
        df_project.loc[df_project[col] == 'Emergency Shelter', col] = 'EmergencyShelter'
        df_project.loc[df_project[col] == 'Homelessness Prevention', col] = 'HomelessnessPrevention'
        df_project.loc[df_project[col] == 'Street Outreach', col] = 'StreetOutreach'
        df_project.loc[df_project[col] == 'Services Only', col] = 'ServicesOnly'
        df_project.loc[df_project[col] == 'PH - Permanent Supportive Housing (disability required for entry)', col] = 'PermanentSupportiveHousing'
        df_project.loc[df_project[col] == 'PH - Rapid Re-Housing', col] = 'RapidReHousing'
        df_project[col] = df_project[col].apply(lambda x: x.lower())

    return df_project

def process_data_service(sheet='Service', datadir=None, simplify_strings=False):
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

    # remove any full duplicates
    df_service = df_service.reset_index().drop_duplicates().set_index('Personal ID')

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

    if simplify_strings:
        col = 'Description'
        df_service.loc[df_service[col] == 'Emergency Shelter', col] = 'EmergencyShelter'
        df_service[col] = df_service[col].apply(lambda x: x.lower())

    return df_service

def process_data_bedinventory(sheet='BedInventory', datadir=None, simplify_strings=False):
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

    # remove any full duplicates
    df_bedinv = df_bedinv.reset_index().drop_duplicates().set_index('Project ID')

    # turn these into integers, assume zero if NaN
    cols = ['Inventory ID', 'HMIS Participating Beds', 'Unit Inventory', 'Bed Inventory', 'Vet Bed Inventory', 'Youth Bed Inventory']
    for col in cols:
        # df_bedinv[col] = df_bedinv.loc[~df_bedinv[col].isnull(), col].apply(lambda x: int(x))
        df_bedinv[col] = df_bedinv[col].fillna(value=0)
        df_bedinv[col] = df_bedinv[col].astype(int)

    return df_bedinv

def rename_columns(df):
    '''Rename columns to be lowercase alphanumeric characters,
    and turn spaces into underscores.
    '''

    rename_dict = {}
    columns = df.columns.tolist()
    for col in columns:
        rename_dict[col] = re.sub(r'([^\s\w]|_)+', '', col).lower().strip().replace('  ', ' ').replace(' ', '_')

    df = df.rename(columns=rename_dict)
    return df

def encode_categorical_features(df, features, astype='int', method='records', reference_vals=None):
    # magnitude_list=None, magnitude_field=None

    if not isinstance(features, list):
        features = [features]

    if reference_vals is None:
        reference_vals = [None] * len(features)

    cols_all = []
    for i, feature in enumerate(features):
        prefix = '{}_'.format(feature)
        df[feature] = df[feature].fillna('unknown')
        df, cols = myOneHotEncoder(df, feature, prefix=prefix, astype=astype, method=method)

        # if magnitude_list is not None and magnitude_field is not None:
        #     # encode magnitude of feature; since the above is binary, assign units per feature
        #     if feature in magnitude_list:
        #         for col in cols:
        #             df.loc[:, col] = df[col] * df[magnitude_field]

        cols_all += cols
    return (df, cols_all)

def myOneHotEncoder(df, column, prefix='', astype='int', method='records'):
    cols = []
    vec = DictVectorizer()
    assignment = vec.fit_transform(df[[column]].to_dict(method)).toarray()
    for assign, ind in iter(vec.vocabulary_.items()):
        name = prefix + assign.split(vec.separator)[1].lower().replace('-', '').replace('  ', ' ').replace(' ', '_')
        df.loc[:, name] = assignment[:,ind]
        df[name] = df[name].astype(astype)
        cols.append(name)
    return (df, cols)
