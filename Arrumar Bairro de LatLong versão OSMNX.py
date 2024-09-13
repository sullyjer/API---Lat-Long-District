import pandas as pd
import osmnx as ox
import geopandas as gpd
from shapely.geometry import Point
import time

# Função para obter o bairro usando OSMnx e GeoPandas
def get_neighborhood_osmnx(lat, long, retries=3):
    attempt = 0
    while attempt < retries:
        try:
            time.sleep(2)  # Pausa de 2 segundos entre as requisições
            
            # Criar um ponto usando as coordenadas fornecidas
            point = Point(long, lat)
            
            # Obter features em um raio de 5000 metros usando OSMnx com tags mais amplas
            tags = {'place': ['neighbourhood', 'suburb', 'locality']}
            gdf = ox.features_from_point((lat, long), tags=tags, dist=5000)
            
            # Verificar se há dados
            if not gdf.empty:
                # Converter para GeoDataFrame para operações geoespaciais
                gdf = gpd.GeoDataFrame(gdf, geometry='geometry')
                
                # Reprojetar as geometrias para um CRS projetado (ex: UTM)
                gdf = gdf.to_crs(epsg=3857)
                
                # Reprojetar o ponto para o mesmo CRS
                point = gpd.GeoSeries([point], crs="EPSG:4326").to_crs(epsg=3857).iloc[0]
                
                # Encontrar a geometria mais próxima do ponto
                distances = gdf.distance(point)
                nearest_geom_idx = distances.idxmin()
                neighborhood = gdf.loc[nearest_geom_idx].get('name')
                
                if neighborhood:
                    print(f"Neighborhood found for ({lat}, {long}): {neighborhood}")
                    return neighborhood
                else:
                    print(f"No neighborhood found for ({lat}, {long})")
            else:
                print(f"No results for ({lat}, {long})")
        except Exception as e:
            print(f"Error getting neighborhood for ({lat}, {long}) on attempt {attempt + 1}: {e}")
        attempt += 1
        time.sleep(2)  # Espera um pouco antes de tentar novamente
    return None

# Carregar dados do Excel
input_file = 'Resultado Inicial.xlsx'
df = pd.read_excel(input_file)

# Verifique os nomes das colunas e ajuste se necessário
print(df.head())

# Adicionar coluna de bairro
df['Neighborhood'] = df.apply(lambda row: get_neighborhood_osmnx(row['LATITUDE'], row['LONGITUDE']), axis=1)

# Se a coluna do código da malha for chamada 'CODIGO_MALHA'
df['Codigo_Malha'] = df['CODIGO_MALHA']

# Salvar os resultados de volta no Excel
output_file = 'resultado.xlsx'
df.to_excel(output_file, index=False)

print("Dados processados e salvos com sucesso.")
