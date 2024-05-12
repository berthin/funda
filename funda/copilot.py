import requests
import json

from funda.logging import logger

SERVICE_URL = "http://df89b4b26fdc:1337/v1/chat/completions"
BODY_TEMPLATE = {
    'model': '', 
    'provider': 'Bing', 
    'stream': True, 
    'messages': [
        {
            'role': 'assistant',
            'content': 'What can you do? Who are you?',
        }
    ]
}
#lines = requests.post(url, json=body, stream=True).iter_lines()

def ask_copilot(message: str) -> str:
    body = BODY_TEMPLATE.copy()
    body['messages'][0]['content'] = message

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