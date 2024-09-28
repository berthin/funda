import requests
import json
import httpx
import aiohttp
from os import environ

from funda.logging import logger

SERVICE_URL = "http://df89b4b26fdc:1337/v1/chat/completions"
BODY_TEMPLATE = {
    'model': '', 
    'provider': 'Bing', 
    'stream': True, 
    'messages': [
        {
            'role': 'system', 
            'content': '''
            You are a helpful footbal assistant AI.
            You will be asked only football related questions and you are not allowed to talk about any other topics, In case the topic is not football
            related, you must reply "Sorry, I'm a football AI. Please, restrain the content to football only.".
            All of your responses must start with: "[Yo AI]: "
            ''',
        },
        {
            'role': 'user', 
            'content': 'What is the best football team and why?',
        }
    ]
}
# response = client.chat.completions.create(
#   model="gpt-3.5-turbo",
#   messages=[
#     {"role": "system", "content": "You are a helpful assistant."},
#     {"role": "user", "content": "Who won the world series in 2020?"},
#     {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
#     {"role": "user", "content": "Where was it played?"}
#   ]
# )
#lines = requests.post(url, json=body, stream=True).iter_lines()


def test_cookie(message: str) -> str:
    import uuid
    import socket
    take_ip_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    take_ip_socket.connect(("8.8.8.8", 80))
    FORWARDED_IP: str = take_ip_socket.getsockname()[0]
    HEADERS_INIT_CONVER = {
        "authority": "www.bing.com",
        "accept": "application/json",
        "accept-language": "en-US;q=0.9",
        "cache-control": "max-age=0",
        "sec-ch-ua": '"Not/A)Brand";v="99", "Microsoft Edge";v="115", "Chromium";v="115"',
        "sec-ch-ua-arch": '"x86"',
        "sec-ch-ua-bitness": '"64"',
        "sec-ch-ua-full-version": '"115.0.1901.188"',
        "sec-ch-ua-full-version-list": '"Not/A)Brand";v="99.0.0.0", "Microsoft Edge";v="115.0.1901.188", "Chromium";v="115.0.5790.114"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-model": '""',
        "sec-ch-ua-platform": '"Windows"',
        "sec-ch-ua-platform-version": '"15.0.0"',
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.188",
        "x-edge-shopping-flag": "1",
        "x-forwarded-for": FORWARDED_IP,
    }
    headers = HEADERS_INIT_CONVER.copy()
    _u_cookie = environ.get('COPILOT_TOKEN')
    assert _u_cookie, 'You need to define your "_U" cookie in the envvars as "COPILOT_TOKEN".'
    headers['Cookie'] = f'SUID=A; _U={_u_cookie}'
    session = httpx.AsyncClient(
        proxies=None,
        timeout=900,
        headers=HEADERS_INIT_CONVER,
    )

    cookies = {'_U': _u_cookie}
    aio_session = aiohttp.ClientSession(cookies=cookies)


def ask_copilot(message: str) -> str:
    body = BODY_TEMPLATE.copy()
    #body['messages'][1]['content'] = message

    try:
        logger.info(f'Trying to ask copilot: {message}')
        lines = requests.post(SERVICE_URL, json=body, stream=True).iter_lines()

        response_chunks = []
        for line in lines:
            if line.startswith(b'data: '):
                try:
                    response_chunks += json.loads(line[6:]).get("choices", [{"delta": {}}])[0]["delta"].get("content", "")
                except json.JSONDecodeError:
                    pass
        
        response = ''.join(response_chunks)
        logger.info(f'Replied: {response}')
        return response
    except Exception as error:
        logger.error(error)
        return 'Error'


if __name__ == '__main__':
    reply = ask_copilot('''
        Give me a summary in english of the following text, but be consice, I only want the summary and nothing else:
        Lekker rustig wonen,  4  ruime slaapkamers  en een  diepe tuin op zonzijde?   Deze ruime gezinswoning heeft het allemaal! Bijzonderheden? Heel  veel daglicht, 4  Ruime slaapkamers, een  open keuken,  een uitgebouwde  woonkamer  en een lekkere 20 meter diepe achtertuin op het zuid-westen waar je tot in de late uurtjes geniet van de zon.  Ligging? Op 10 minuten fietsen van het bruisende stadscentrum, maar ook dichtbij natuur, Geldrop en uitvalswegen richting Nuenen en Helmond.    Je bent van harte welkom!  Begane grond  ENTREE Hal met tegelvloer, trapkast met groepenkast, trapopgang, toiletruimte en toegang tot de keuken/woonkamer.  TOILET Betegelde toiletruimte met staand closet.  KEUKEN Open keuken met tegelvloer, deur naar de tuin en keukeninrichting in lengte opstelling.  WOONKAMER Ruime uitgebouwde doorzon woonkamer (ca. 25 m2) voorzien van laminaatvloer en aluminium schuifpui naar de tuin.  TUIN Zonnige en goed onderhouden tuin, gesitueerd op het zuid-westen en voorzien van terras, borders, grasgazon en een ruime tuinberging (ca. 8 m2). Er is een achterom.  1e Verdieping Overloop met laminaatvloer, bergkast, trapopgang en toegang tot de slaapkamers en badkamer.  SLAAPKAMER I Slaapkamer (ca. 4 m2), gelegen aan de achterzijde, voorzien van laminaatvloer en deur naar balkon.  SLAAPKAMER II Slaapkamer (ca. 12 m2), gelegen aan de achterzijde, voorzien van tapijtvloer en inbouwkast.  BADKAMER Geheel betegelde badkamer met douche (thermostaatkraan) en wastafelmeubel.  SLAAPKAMER III Slaapkamer (ca. 10 m2), gelegen aan de voorzijde, voorzien van laminaatvloer en inbouwkast.  2e Verdieping Overloop met toegang tot bergruimte, wasruimte en slaapkamer.   SLAAPKAMER IV Zolderkamer (ca. 14 m2) met inbouwkast en laminaatvloer.   WASRUIMTE Aan de voorzijde gelegen wasruimte met de witgoedaansluiting.  BERGKAST Onder schuine kap gelegen bergkast met de C.V.-opstelling.  Bijzonderheden: Verrassend ruime gezinswoning; 4 slaapkamers; Gelegen op 10 fietsminuten van het centrum; Dichtbij diverse voorzieningen, zoals supermarkt, basisschool en kinderopvang, gezondheidscentrum, winkels Haagdijk (Tongelresestraat), tennispark en uitvalswegen; Grotendeels voorzien van kunststof kozijnen met op begane grond en eerste verdieping: HR++, tweede verdieping: enkel glas en dakraam: HR++); 2 Zonnepanelen (2018); Energieblabel B; Glasvezelaansluiting; Verwarming en warmwater via Remeha Calenta uit 2009.
    ''')

    print(reply)