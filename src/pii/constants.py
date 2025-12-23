from typing import Final


ENTITY_PERSON: Final[str] = "PERSON"
ENTITY_PHONE: Final[str] = "PHONE"
ENTITY_EMAIL: Final[str] = "EMAIL"
ENTITY_ID: Final[str] = "ID"
ENTITY_ADDRESS: Final[str] = "ADDRESS"
ENTITY_BANK_ACCOUNT: Final[str] = "BANK_ACCOUNT"
ENTITY_PASSWORD: Final[str] = "PASSWORD"
ENTITY_CREDIT_CARD: Final[str] = "CREDIT_CARD"


SUPPORTED_ENTITY_TYPES: Final[list[str]] = [
    ENTITY_PERSON,
    ENTITY_PHONE,
    ENTITY_EMAIL,
    ENTITY_ID,
    ENTITY_ADDRESS,
    ENTITY_BANK_ACCOUNT,
    ENTITY_PASSWORD,
    ENTITY_CREDIT_CARD,
]

MASK_STYLE_FULL: Final[str] = "full"
MASK_STYLE_PARTIAL_LAST4: Final[str] = "partial_last4"

DEFAULT_MASK_CHAR: Final[str] = "X"
DEFAULT_MASK_STYLE: Final[str] = MASK_STYLE_FULL

SPAN_PRIORITY: Final[dict[str, int]] = {
    ENTITY_PHONE: 100,
    ENTITY_EMAIL: 100,
    ENTITY_ID: 100,
    ENTITY_BANK_ACCOUNT: 100,
    ENTITY_PASSWORD: 100,
    ENTITY_CREDIT_CARD: 100,
    ENTITY_PERSON: 50,
    ENTITY_ADDRESS: 10,
}

#（ISO 3166-1 alpha-2）
DEFAULT_PHONE_REGIONS: Final[list[str]] = [
    "HK",  # Hong Kong
    "CN",  # China
    "US",  # United States
    "GB",  # United Kingdom
    "FR",  # France
    "DE",  # Germany
]
