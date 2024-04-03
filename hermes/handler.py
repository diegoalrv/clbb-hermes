import os
import requests
import hashlib
import json
import geopandas as gpd
import pandas as pd
import pandana as pdna
from shapely import wkt
from shapely.geometry import Point, LineString, Polygon


class Handler:
    def __init__(self):
        self.server_address = os.getenv('server_address', 'http://localhost:8000')
        self.request_data_endpoint = os.getenv('request_data_endpoint', 'api')
        self.id_network = os.getenv('id_roadnetwork', 1)
        self.project_name = os.getenv('project_name', '')
    
    @staticmethod
    def generate_unique_code(strings):
        text = ''.join(strings)
        return hashlib.sha256(text.encode()).hexdigest()

    def post_data(self, endpoint='', data=None, headers={'Content-Type': 'application/json'}):
        endpoint = endpoint if endpoint else f'{self.server_address}/urban-indicators/indicatordata/upload_to_table/'

        json_data = json.dumps(data)

        response = requests.post(endpoint, headers=headers, data=json_data)
        if response.status_code == 200:
            print('Datos guardados exitosamente')
        else:
            print('Error al guardar los datos:', response.text)
        pass

    def get_data(self,endpoint, params, as_dataframe):
        response = requests.get(endpoint, params=params)
        if response.status_code == 200:
            data = response.json()
            # return data
            if as_dataframe:
                try:
                    return gpd.GeoDataFrame.from_features(data, crs='EPSG:4326')
                except:
                    return pd.DataFrame(response.json())
            else:
                return data
        else:
            print("Error al hacer la solicitud:", response.status_code)
            return None

    # Methods to load indicator data from API

    def load_indicator_data(self, indicator_name, indicator_hash=None, as_dataframe=True):
        endpoint = f'{self.server_address}/urban-indicators/indicatordata/get_table_data'
        indicator_hash = self.indicator_hash if indicator_hash is None else indicator_hash

        params = {
            "indicator_name": indicator_name,
            "indicator_hash": indicator_hash,
        }
        data = self.get_data(endpoint, params, as_dataframe)
        data.drop(columns=['hash'], inplace=True)
        return data

    # Methods to load data from API
    
    def load_amenities(self):
        amenities = None
        endpoint = f'{self.server_address}/{self.request_data_endpoint}/amenity/'
        response = requests.get(endpoint)
        data = response.json()
        
        geometries = []
        properties = []
        for feature in data['features']:
            geometries.append(wkt.loads(feature['geometry'].split(';')[-1]))
            properties.append(feature['properties'])

        amenities = gpd.GeoDataFrame(properties, geometry=geometries)
        amenities.drop(columns=['tags'], inplace=True)
        return amenities

    def load_area_of_interest(self, id=2):
        area_of_interest = None
        endpoint = f'{self.server_address}/{self.request_data_endpoint}/areaofinterest/{id}/'
        response = requests.get(endpoint)
        data = response.json()
        geometries= [wkt.loads(data['geometry'].split(';')[-1])]
        properties= [data['properties']]

        area_of_interest = gpd.GeoDataFrame(properties, geometry=geometries)
        area_of_interest = area_of_interest.set_crs(4326)
        return area_of_interest

    def load_network(self, id_network=None):
        if id_network is None:
            id_network = self.id_network
        filename = f'/app/tmp/net_{id_network}.h5'
        if not os.path.exists(filename):
            endpoint = f'{self.server_address}/{self.request_data_endpoint}/roadnetwork/{id_network}/serve_h5_file/'
            print(endpoint)
            response = requests.get(endpoint)
            if response.status_code == 200:
                with open(filename, 'wb') as f:
                    f.write(response.content)
                print("¡Archivo h5 descargado exitosamente!")
            else:
                print("Error al descargar el archivo h5:", response.text)
                return response.status_code
        return pdna.Network.from_hdf5(filename)