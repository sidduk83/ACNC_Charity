import pandas as pd
import xlsxwriter
import numpy as np
import urllib
import pyodbc
from sqlalchemy import create_engine
import re

# Disable chained assignments
pd.options.mode.chained_assignment = None

# Read the main data from the Excel file
df = pd.read_excel(r'C:\Users\Siddu Kori\Downloads\datadotgov_main.xlsx')

# Drop rows where ABN is missing
df = df.dropna(subset=['ABN'])

# Normalize State names
df['State'] = df['State'].replace(['Queensland (Qld)', 'Qld', 'qld'], 'QLD')
df['State'] = df['State'].replace(
    ['Australia', 'Australia Capital Territory', 'Bali', 'Australian Capital Territory', 'PINEWOOD', 'Au', '0'],
    'Other')
df['State'] = df['State'].replace(['VICTORIA & NSW', 'vic', 'Vic'], 'VIC')
df['State'] = df['State'].replace(['WA', 'WA ', 'Wa', 'wa'], 'WA')
df['State'] = df['State'].replace(['NSW', 'nsw', 'Nsw', 'NSW '], 'NSW')
df['State'] = df['State'].replace(['NT', 'nt ', 'NT '], 'NT')
df['State'] = df['State'].replace(['TAS', 'TAS ', 'Tas', 'tas'], 'TAS')

# Extract and rename operating states columns
df_operating_states = df[
    ['ABN', 'Operates_in_ACT', 'Operates_in_NSW', 'Operates_in_NT', 'Operates_in_QLD', 'Operates_in_SA',
     'Operates_in_TAS', 'Operates_in_VIC', 'Operates_in_WA']]
df_operating_states = df_operating_states.rename(columns={'Operates_in_ACT': 'ACT', 'Operates_in_NSW': 'NSW',
                                                          'Operates_in_NT': 'NT', 'Operates_in_QLD': 'QLD',
                                                          'Operates_in_SA': 'SA', 'Operates_in_TAS': 'TAS',
                                                          'Operates_in_VIC': 'VIC', 'Operates_in_WA': 'WA'})

# Reshape operating states dataframe
df_operating_states = pd.melt(df_operating_states, id_vars=['ABN'], var_name='State', value_name=r'Yes\No')
df_operating_states = df_operating_states.dropna(subset=[r'Yes\No'])
df_operating_states = df_operating_states[['ABN', 'State']]

# Merge with main data
df_operating_states_main = df[['ABN', 'State']]
df_merged = pd.concat([df_operating_states_main, df_operating_states])
df_merged.drop_duplicates(keep=False, inplace=True)
df_merged = df_merged.dropna(subset=['State'])

# Prepare address dataframe
df_Address = df[
    ['ABN', 'Charity_Legal_Name', 'Address_Line_1', 'Address_Line_2', 'Address_Line_3', 'Town_City', 'State']]
df_Address['Address_Line_1'] = df_Address['Address_Line_1'].replace(['0'], '')
df_Address['Address_Line_2'] = df_Address['Address_Line_2'].replace(['0'], '')
df_Address['Address_Line_3'] = df_Address['Address_Line_3'].replace(['0'], '')
df_Address['Town_City'] = df_Address['Town_City'].replace(['0'], '')
df_Address['Address'] = pd.Series(
    df_Address[['Address_Line_1', 'Address_Line_2', 'Address_Line_3']].fillna('').values.tolist()).str.join('')
df_Address = df_Address.loc[:, ['ABN', 'Charity_Legal_Name', 'Address', 'Town_City', 'State']]

# Prepare countries dataframe
df_countries = df[['ABN', 'Operating_Countries']]
df_countries = df_countries.dropna(subset=['Operating_Countries'])

# Read and filter main data from another Excel file
df_main_data = pd.read_excel(r'C:\Users\Siddu Kori\Downloads\datadotgov_ais22.xlsx')
df_main_data = df_main_data[df_main_data['registration status'] == 'Registered']
df_main_data = df_main_data[df_main_data['conducted activities'] == 'y']

# Select relevant columns
df_main_information = df_main_data[
    ['abn', 'Registration Date', 'charity name', 'charity website', 'charity size', 'date ais received',
     'financial report date received', 'staff - full time', 'staff - part time', 'staff - casual',
     'total full time equivalent staff', 'staff - volunteers', 'charity has related party transactions',
     'revenue from government', 'donations and bequests', 'revenue from goods and services',
     'revenue from investments', 'all other revenue', 'total revenue', 'other income', 'total gross income',
     'employee expenses', 'interest expenses', 'grants and donations made for use in Australia',
     'grants and donations made for use outside Australia', 'all other expenses', 'total expenses',
     'net surplus/deficit', 'other comprehensive income', 'total comprehensive income', 'total current assets',
     'non-current loans receivable', 'other non-current assets', 'total non-current assets', 'total assets',
     'total current liabilities', 'non-current loans payable', 'other non-current liabilities',
     'total non-current liabilities', 'total liabilities', 'net assets/liabilities',
     'Total paid to Key Management Personnel']]

# Replace slashes in dates with hyphens
df_main_information['date ais received'] = df_main_information['date ais received'].str.replace('/', '-')
df_main_information['financial report date received'] = df_main_information[
    'financial report date received'].str.replace('/', '-')

# Read and filter program data
df_programs = pd.read_excel(r'C:\Users\Siddu Kori\Downloads\datadotgov_ais22_programs.xlsx')
df_programs = df_programs[df_programs['Registration Status'] == 'Registered']

# Prepare program classifications dataframe
df_programs_classifications = df_programs[
    ['ABN', 'Charity Name', 'Classification', 'Children - aged 6 to under 15', 'Environment', 'Families',
     'General community in Australia', 'Migrants, refugees or asylum seekers', 'Overseas communities or charities',
     'Aboriginal and Torres Strait Islander people', 'Adults - aged 65 and over', 'Early childhood - aged under 6',
     'Females', 'Gay, lesbian, bisexual, transgender or intersex persons', 'Males',
     'People at risk of homelessness/ people experiencing homelessness',
     'People with disabilities', 'Victims of crime (including family violence)', 'Animals',
     'Financially disadvantaged people',
     'People in rural/regional/remote communities', 'People with chronic illness (including terminal illness)',
     'Pre/post release offenders and/or their families', 'Veterans and/or their families', 'Youth - 15 to under 25',
     'Adults - aged 25 to under 65', 'Other charities',
     'People from a culturally and linguistically diverse background',
     'Unemployed persons', 'Victims of disaster', 'Other', 'other description', 'Operating online',
     'Operating overseas', ]]
df_programs_classifications = pd.melt(df_programs_classifications, id_vars=['ABN', 'Charity Name', 'Classification'],
                                      var_name='Purpose', value_name=r'Yes\No')
df_programs_classifications = df_programs_classifications[df_programs_classifications[r'Yes\No'] == 'Y']

# Prepare operating locations dataframe
df_operating_location = df_programs[
    ['ABN', 'Charity Name', 'Operating Location 1 lat/long', 'Operating Location 2 lat/long',
     'Operating Location 3 lat/long',
     'Operating Location 4 lat/long', 'Operating Location 5 lat/long', 'Operating Location 6 lat/long',
     'Operating Location 7 lat/long',
     'Operating Location 8 lat/long', 'Operating Location 9 lat/long', 'Operating Location 10 lat/long']]
df_operating_location = pd.melt(df_operating_location, id_vars=['ABN', 'Charity Name'], var_name='Operating_Location',
                                value_name=r'Lati_Long')
df_operating_location = df_operating_location.dropna(subset=['Lati_Long'])
df_operating_location[['Latitude', 'Longitude']] = df_operating_location['Lati_Long'].str.split('|', n=1, expand=True)
df_operating_location = df_operating_location[df_operating_location['Latitude'] != '0.0000000 ']
df_operating_location = df_operating_location[['ABN', 'Charity Name', 'Latitude', 'Longitude']]
df_operating_location['Latitude'] = pd.to_numeric(df_operating_location['Latitude']).astype('float')
df_operating_location['Longitude'] = pd.to_numeric(df_operating_location['Longitude']).astype('float')

print(df_operating_location.head())


# Function to insert records into SQL Server
def insert_records(df, table_name):
    # Database connection parameters
    params = urllib.parse.quote_plus(
        'Driver={ODBC Driver 17 for SQL Server};''Server=DESKTOP-4UM73JG\SQLEXPRESS;''Database=SK1259;''Trusted_Connection=yes;')
    engine = create_engine("mssql+pyodbc:///?odbc_connect=%s" % params)

    # Insert data into the specified table
    with engine.begin() as con:
        df.to_sql(table_name, schema='dbo', con=engine, index=False, if_exists='replace', index_label=None)
        print('table created')


# Insert data into SQL Server tables
insert_records(df_merged, 'Charity_State')
insert_records(df_Address, 'Charity_Address')
insert_records(df_countries, 'Charity_Countries')
insert_records(df_main_information, 'Charity_Operations')
insert_records(df_programs_classifications, 'Charity_Programs')
insert_records(df_operating_location, 'Charity_Geography')