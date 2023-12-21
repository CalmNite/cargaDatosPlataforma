import pandas as pd
import requests
import json
import base64
import os


def login_api():
    url = f'{base_url}/api/auth/login'
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    json_data = json.dumps({"username": os.getenv("USERNAME"), "password": os.getenv("PASSWORD")})
    x = requests.post(url, headers=headers, data=json_data)
    return_data = json.loads(x.text)
    token = f'Bearer {return_data["token"]}'
    return token

def find_by_name(i, token_tenant):
    url = f'{base_url}/api/tenant/assets?assetName={i}'
    headers = {"Content-Type": "application/json", "Accept": "application/json", "X-Authorization": token_tenant}
    x = requests.get(url, headers=headers)
    if x.status_code == 200:
        return_data = x.json()['id']['id']
        return return_data
    else:
        return None

def update_asset_attributes(id, token_tenant, data):
    url = f'{base_url}/api/plugins/telemetry/ASSET/{id}/attributes/SERVER_SCOPE'
    headers = {"Content-Type": "application/json", "Accept": "application/json", "X-Authorization": token_tenant}
    json_data = json.dumps(data)
    x = requests.post(url, headers=headers, data=json_data)
    return x

token = login_api()

FOLDER_NAME = os.getenv('FOLDER_NAME')

base_url = os.getenv("URL")
file_names = [os.getenv("FILE_NAME") + str(i) + '.xlsx' for i in range(1, 23)]
tabla_df = pd.read_csv(os.getenv('FILE'))
tabla_foto = pd.read_json('json_data.json')


tabla_foto['codigo'] = tabla_foto['codigo'].str.replace("'", "")
tabla_foto['codigo'] = pd.to_numeric(tabla_foto['codigo'], downcast='integer')

i1 = 0
for file_name in file_names:
    
    i1 += 1
    try:
        # Load the Excel file into a pandas DataFrame
        excel_df = pd.read_excel(file_name)
        excel_df['CODIGOEMERGENCIA'] = excel_df['CODIGOEMERGENCIA'].str.replace("'", "")
        excel_df['CODIGOEMERGENCIA'] = pd.to_numeric(excel_df['CODIGOEMERGENCIA'], downcast='integer')
        
        # Extract the emergency code column from the Excel file
        emergency_code_column = excel_df['CODIGOEMERGENCIA']
        
        # Compare the emergency code column with the values in tabla_df
        matched_rows = tabla_df[tabla_df['CODIGOEMERGENCIA'].isin(emergency_code_column) & (tabla_df['CODIGO'] == i1)]
        
        
        # Do something with the matched rows if needed
        if not matched_rows.empty:
            # Process the matched rows
            print(f"Matching rows in {file_name}:")
            df_row = pd.merge(matched_rows, excel_df, left_on="CODIGOEMERGENCIA", right_on= "CODIGOEMERGENCIA")
            df_last = pd.merge(df_row, tabla_foto,  left_on="CODIGOEMERGENCIA", right_on= "codigo")
            
            for i in df_last[["REFCAT", "CODIGOEMERGENCIA", "REFCAT_Updated", 'imagen']].values:
                id = find_by_name(i[2], token)
                file_path = os.path.join(FOLDER_NAME, i[0] + ".png")
                try:
                    with open(file_path, "rb") as image_file:
                        encoded_string = base64.b64encode(image_file.read())
                        encoded_string = bytes("data:image/jpeg;base64,", encoding='utf-8') + encoded_string
                        encoded_string = encoded_string.decode("utf-8")
                except FileNotFoundError:
                    encoded_string = None

                json_data = { "foto_inst": i[3], "fachada": encoded_string}
            
                update_asset_attributes(id, token, json_data)
                    
        
    except FileNotFoundError:
        print(f"File {file_name} not found.")
    except Exception as e:
        print(f"An error occurred while processing {file_name}: {e}")