from staticmap import StaticMap, CircleMarker, Line
from pathlib import Path
from geopy.geocoders import Nominatim

from PIL import Image, ImageDraw, ImageFont

geolocator = Nominatim(user_agent="my_app")
reference_point = (5.466646, 51.4400568) # get_coordinates('hoog gagel 56, eindhoven')

def get_coordinates(address: str) -> tuple[float, float]:
    location = geolocator.geocode(address)
    return (location.longitude, location.latitude)


def add_title(image: Image, title: str) -> None:
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default(size=20)
    draw.text((10, 10), title, fill='blue', font=font)


def take_screenshot(address: str, screenshot_path: Path) -> None:
    # Define the map boundaries
    m = StaticMap(800, 600, url_template="http://a.tile.osm.org/{z}/{x}/{y}.png")

    # Add a marker at the address location
    m.add_marker(CircleMarker(get_coordinates(address), 'red', 8))
    m.add_marker(CircleMarker(reference_point, 'blue', 8))

    # Save the map screenshot
    image = m.render()
    add_title(image, address)
    image.save(screenshot_path)

    return image


take_screenshot("Jan van de Capellelaan 41, Eindhoven", Path("data/test.png"))