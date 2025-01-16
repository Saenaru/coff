import json
import requests
import folium
import os
import logging
from geopy import distance
from dotenv import load_dotenv


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        logging.warning('Координаты не найдены.')
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lat, lon


def main():
    load_dotenv("apikey.env")
    apikey = os.getenv('APIKEY')
    if apikey is None:
        logging.error('API ключ не найден. Проверьте "apikey.env" файл.')
        return

    address = input('Где вы находитесь? ')
    coordinates_personal = fetch_coordinates(apikey, address)
    mymap = folium.Map(location=coordinates_personal, zoom_start=14)

    folium.Marker(
        location=coordinates_personal,
        popup='Ваше местоположение',
        tooltip='Вы здесь',
        icon=folium.Icon(color='red')
    ).add_to(mymap)

    coffee_shops_info = []

    with open("coffee.json", "r", encoding="cp1251") as my_file:
        coffee_json = my_file.read()

    coffee_list = json.loads(coffee_json)

    if isinstance(coffee_list, list):
        for coffee in coffee_list:
            name = coffee.get('Name', 'Название отсутствует')
            coordinates_coffee = coffee.get(
                'geoData', {}
            ).get('coordinates', [None, None])
            if len(coordinates_coffee) > 0:
                longitude = coordinates_coffee[0]
            else:
                longitude = None

            if len(coordinates_coffee) > 1:
                latitude = coordinates_coffee[1]
            else:
                latitude = None

            distance_km = distance.distance(
                coordinates_personal, (latitude, longitude)
            ).km
            coffee_shops_info.append({
                'title': name,
                'distance': distance_km,
                'latitude': latitude,
                'longitude': longitude
            })

        coffee_shops_info = sorted(
            coffee_shops_info, key=lambda x: x['distance']
        )

        for shop in coffee_shops_info[:5]:
            folium.Marker(
                location=[shop['latitude'], shop['longitude']],
                popup=f"{shop['title']} ({shop['distance']:.2f} км)",
                tooltip=shop['title']
            ).add_to(mymap)

    mymap.save("index.html")


if __name__ == "__main__":
    main()
