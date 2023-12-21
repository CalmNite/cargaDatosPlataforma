import pandas as pd
import os

tabla_df = pd.read_csv(os.getenv('FILE'))
counts = tabla_df['REFCAT'].value_counts()
repeated_values = counts[counts > 1].index


tabla_df['REFCAT_Updated'] = tabla_df['REFCAT']
tabla_df['TYPE'] = 'REFERENCIA'
tabla_df['MUNICIPIO'] = 'SANT ANTONI DE PORTMANY'

for value in repeated_values:
    # Counter starting from 2 for the second occurrence
    counter = 2
    for index, row in tabla_df[tabla_df['REFCAT'] == value].iterrows():
        if tabla_df[tabla_df['REFCAT'] == value].index.get_loc(index) == 0:
            # Skip the first occurrence
            continue
        else:
            # Append a sequence number for subsequent occurrences
            tabla_df.at[index, 'REFCAT_Updated'] = row['REFCAT'] + str(counter)
            counter += 1

tabla_df['REFERENCIA_CATASTRAL'] = tabla_df['REFCAT_Updated']
tabla_df.to_csv(os.getenv('FILE'), index=False)