import plyvel

lastScrappedURL = 'https://pt.surf-forecast.com/breaks/La-Herradura-Andalucia'

config = plyvel.DB('config', create_if_missing=True)
config.put(b'lastScrappedURL', lastScrappedURL.encode())
config.put(b'finished', b'T')