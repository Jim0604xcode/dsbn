from datetime import datetime
from typing import TypedDict
class PassAwayMappingDict(TypedDict):
    death_certificate: str
    id_card_copy: str
    relationship_proof:str
    inheritor_id_proof:str

class FavoriteHeadshotMappingDict(TypedDict):
    picture:str
class GoodsDonorMappingDict(TypedDict):
    image_url_1:str
    image_url_2:str
    image_url_3:str