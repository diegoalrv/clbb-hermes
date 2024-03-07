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
        self.request_data_endpoint = os.getenv('request_data_endpoint', '/api')
        self.id_network = os.getenv('id_roadnetwork', 1)
        self.base_url = f'{self.server_address}/{self.request_data_endpoint}'
        self.roadnetwork_url = f'{self.base_url}/roadnetwork'
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
    
    def load_amenities(self):
        amenities = None
        endpoint = f'{self.base_url}/amenity/'
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
        endpoint = f'{self.base_url}/areaofinterest/{id}/'
        response = requests.get(endpoint)
        data = response.json()
        geometries= [wkt.loads(data['geometry'].split(';')[-1])]
        properties= [data['properties']]

        area_of_interest = gpd.GeoDataFrame(properties, geometry=geometries)
        area_of_interest = area_of_interest.set_crs(4326)
        return area_of_interest

    def load_network(self, id_network):
        endpoint = f'{self.roadnetwork_url}/{id_network}/serve_h5_file/'
        filename = f'/app/tmp/net_{id_network}.h5'
        if not os.path.exists(filename):
            response = requests.get(endpoint)
            if response.status_code == 200:
                with open(filename, 'wb') as f:
                    f.write(response.content)
                print("¡Archivo h5 descargado exitosamente!")
            else:
                print("Error al descargar el archivo h5:", response.text)
        return pdna.Network.from_hdf5(filename)