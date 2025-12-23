from __future__ import annotations

from typing import List, Dict, Any, Optional
import re

import phonenumbers
from presidio_analyzer import AnalyzerEngine  # type: ignore
from presidio_analyzer.nlp_engine import NlpEngineProvider  # type: ignore

from .constants import (
    ENTITY_PERSON,
    ENTITY_PHONE,
    ENTITY_EMAIL,
    ENTITY_ID,
    ENTITY_ADDRESS,
    ENTITY_BANK_ACCOUNT,
    ENTITY_PASSWORD,
    ENTITY_CREDIT_CARD,
)


# ---- Presidio engine ----
_presidio_engine: Optional[AnalyzerEngine] = None


def _get_presidio_engine() -> Optional[AnalyzerEngine]:
    global _presidio_engine
    if _presidio_engine is not None:
        return _presidio_engine
    try:
        nlp_conf = {
            "nlp_engine_name": "spacy",
            "models": [
                {"lang_code": "en", "model_name": "en_core_web_sm"},
                {"lang_code": "zh", "model_name": "zh_core_web_sm"},
                {"lang_code": "xx", "model_name": "xx_ent_wiki_sm"},
            ],
        }
        provider = NlpEngineProvider(nlp_configuration=nlp_conf)
        nlp_engine = provider.create_engine()
        _presidio_engine = AnalyzerEngine(nlp_engine=nlp_engine)
        return _presidio_engine
    except Exception:
        return None


def _is_cjk(text: str) -> bool:
    return bool(re.search(r"[\u4e00-\u9fff]", text))


def _presidio_analyze(text: str, entities: list[str]):
    engine = _get_presidio_engine()
    if engine is None:
        print("Failed to get Presidio engine")
        return []
    try:
        # print("Presidio analyzing text: ", text)
        lang = "zh" if _is_cjk(text) else "en"
        return engine.analyze(text=text, entities=entities, language=lang)
    except Exception:
        # print("Error to analyze text: ", text)
        return []


# ---- utils ----

def _add_span(spans: List[Dict[str, Any]], start: int, end: int, label: str, meta: Optional[Dict[str, Any]] = None):
    if start < 0 or end <= start:
        return
    spans.append({
        "start": start,
        "end": end,
        "label": label,
        "meta": meta or {},
    })


# ---- regexes (fallback/augment) ----
EMAIL_REGEX = re.compile(r"""
    (?i)
    (?<![A-Z0-9._%+\-])
    [A-Z0-9._%+\-]+@(?:[A-Z0-9\-]+\.)+[A-Z]{2,}
    (?![A-Z0-9._%+\-])
""", re.VERBOSE)

SSN_REGEX = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
CN_ID_18_REGEX = re.compile(r"\b\d{17}[\dXx]\b")
CN_ID_15_REGEX = re.compile(r"\b\d{15}\b")
HKID_REGEX = re.compile(r"\b[A-Z]{1,2}\d{6}\(?[0-9A]\)?\b")

IBAN_REGEX = re.compile(r"\b[A-Z]{2}\d{2}[A-Z0-9]{11,30}\b", re.IGNORECASE)
LOCAL_BANK_HINT_REGEX = re.compile(r"(?i)(?:帳?號|賬?號|銀行|bank|acct|account|iban|swift)[:：\s]*([A-Z0-9\- ]{6,})")

PASSWORD_HINT_REGEX = re.compile(r"(?i)(?:password|密碼|密码|passcode|pwd)[:：\s]*([\S]{4,})")

CC_HINT_REGEX = re.compile(r"(?i)(?:信用卡|信用咭|credit\s*card|visa|mastercard|amex|discover|diners)[:：\s-]*")
CC_BODY_REGEX = re.compile(r"(?<!\d)(?:\d[ -]?){13,19}(?!\d)")


# ---- detectors ----

CH_ADDR_STRONG_RE = re.compile(r"(路|街|道|巷|弄|号|號|樓|楼|室|栋|幢|座|大厦|大廈)")
EN_ADDR_SUFFIX_RE = re.compile(r"\b(?:st|street|rd|road|ave|avenue|blvd|boulevard|ln|lane|dr|drive|ct|court|cir|circle|pkwy|parkway|pl|place|ter|terrace|hwy|highway|way|trail|trl|sq|square)\b", re.IGNORECASE)
EN_ADDR_APT_RE = re.compile(r"\b(?:apt|suite|ste|unit|po\s*box)\b", re.IGNORECASE)
EN_ADDR_DIGITS_PREFIX_RE = re.compile(r"\b\d{1,6}\s+[A-Za-z][A-Za-z\s]{1,30}\b")
LONG_PUNCT_RE = re.compile(r"[，,。\.\!\?；;]")


def _looks_like_address(txt: str) -> bool:
    t = (txt or "").strip()
    if not t or len(t) < 4:
        return False
    if len(t) > 64 and LONG_PUNCT_RE.search(t):
        return False
    if _is_cjk(t):
        if CH_ADDR_STRONG_RE.search(t):
            return True
        if re.search(r"[省市区縣县鎮镇鄉乡]", t) and (re.search(r"\d", t) or CH_ADDR_STRONG_RE.search(t)):
            return True
        return False
    if EN_ADDR_DIGITS_PREFIX_RE.search(t):
        return True
    if EN_ADDR_SUFFIX_RE.search(t) and re.search(r"\d", t):
        return True
    if EN_ADDR_APT_RE.search(t) and re.search(r"\d", t):
        return True
    return False


def detect_person_address(text: str, want_person: bool, want_address: bool) -> List[Dict[str, Any]]:
    spans: List[Dict[str, Any]] = []
    ents: list[str] = []
    if want_person:
        ents.append("PERSON")
    if want_address:
        ents.append("LOCATION")
    if not ents:
        return spans
    results = _presidio_analyze(text, ents)
    for r in results:
        etype = getattr(r, "entity_type", "")
        s = getattr(r, "start", None)
        e = getattr(r, "end", None)
        if s is None or e is None or e <= s:
            continue
        if etype == "PERSON" and want_person:
            _add_span(spans, s, e, ENTITY_PERSON)
        elif etype == "LOCATION" and want_address:
            _add_span(spans, s, e, ENTITY_ADDRESS)
    return spans


# --- Chinese address (zh/HK/TW) rule-based supplement ---
CN_ADDR_RE_1 = re.compile(
    r"(?:[\u4e00-\u9fff]{2,8}(?:省|自治区|特别行政区|市))+(?:[\u4e00-\u9fff]{2,8}(?:市|区|縣|县|旗))+[\u4e00-\u9fff0-9]{0,20}(?:路|街|道|巷|胡同)?(?:\d{1,5}(?:号|號))?(?:[\u4e00-\u9fff0-9]{0,8}(?:栋|幢|座))?(?:\d{1,3}(?:楼|樓|层))?(?:\d{1,5}(?:室|户))?"
)
CN_ADDR_RE_2 = re.compile(
    r"[\u4e00-\u9fffA-Za-z0-9]{2,20}(?:路|街|道|巷|胡同)\s*(?:\d{1,5}(?:号|號))?(?:[\u4e00-\u9fffA-Za-z0-9]{0,8}(?:栋|幢|座))?(?:\d{1,3}(?:楼|樓|层))?(?:\d{1,5}(?:室|户))?"
)
HK_ADDR_RE = re.compile(
    r"香港[\u4e00-\u9fff]{0,12}(?:區|区|市|縣|县)?[\u4e00-\u9fff0-9]{0,16}(?:道|路|街|巷)\s*\d{0,4}(?:号|號)?(?:[\u4e00-\u9fff0-9]{0,8}座)?(?:\d{1,3}(?:楼|樓))?(?:\d{1,4}室)?"
)
TW_ADDR_RE = re.compile(
    r"(?:台北|臺北|新北|桃園|桃园|台中|臺中|台南|臺南|高雄|基隆|新竹|嘉義|嘉义|台東|臺東|花蓮|花莲|宜蘭|宜兰|屏東|屏东|南投|雲林|云林|彰化|苗栗|連江|连江|金門|金门|澎湖)(?:市|縣|县)[\u4e00-\u9fff0-9]{0,12}(?:區|区|鄉|乡|鎮|镇)?[\u4e00-\u9fff0-9]{0,12}(?:路|街|道|巷|弄)(?:\d{1,3}段)?(?:\d{1,4}巷)?(?:\d{1,4}弄)?(?:\d{1,5}(?:號|号))(?:\d{1,3}(?:樓|楼))?(?:\d{1,4}室)?"
)


def _is_zh_locale(locale: str) -> bool:
    if not locale:
        return False
    l = locale.lower()
    return l in ("zh", "zh-cn", "zh-hk", "zh-tw")


def detect_cn_addresses(text: str, locale: str) -> List[Dict[str, Any]]:
    spans: List[Dict[str, Any]] = []
    if not (_is_cjk(text) or _is_zh_locale(locale)):
        return spans
    patterns = (CN_ADDR_RE_1, CN_ADDR_RE_2, HK_ADDR_RE, TW_ADDR_RE)
    seen: set[tuple[int, int]] = set()
    for pat in patterns:
        for m in pat.finditer(text):
            s, e = m.start(), m.end()
            if e - s < 4:
                continue
            frag = text[s:e]
            if not _looks_like_address(frag):
                continue
            if (s, e) in seen:
                continue
            seen.add((s, e))
            _add_span(spans, s, e, ENTITY_ADDRESS)
    return spans


HK_LOCALITY_RE = re.compile(
    r"(香港|香港島|香港岛|九龍|九龙|新界|中西區|中西区|東區|东区|南區|南区|灣仔區|湾仔区|油尖旺區|油尖旺区|深水埗區|深水埗区|九龍城區|九龙城区|黃大仙區|黄大仙区|觀塘區|观塘区|北區|北区|大埔區|大埔区|沙田區|沙田区|西貢區|西贡区|荃灣區|荃湾区|屯門區|屯门区|元朗區|元朗区|葵青區|葵青区|離島區|离岛区|葵芳|葵興|青衣|荃灣|將軍澳)"
)


def detect_hk_localities(text: str, locale: str) -> List[Dict[str, Any]]:
    spans: List[Dict[str, Any]] = []
    if not (_is_cjk(text) or _is_zh_locale(locale)):
        return spans
    for m in HK_LOCALITY_RE.finditer(text):
        s, e = m.start(), m.end()
        _add_span(spans, s, e, ENTITY_ADDRESS)
    return spans

def detect_emails(text: str) -> List[Dict[str, Any]]:
    spans: List[Dict[str, Any]] = []
    pres = _presidio_analyze(text, ["EMAIL_ADDRESS"])
    if pres:
        for r in pres:
            _add_span(spans, r.start, r.end, ENTITY_EMAIL)
        return spans
    for m in EMAIL_REGEX.finditer(text):
        _add_span(spans, m.start(), m.end(), ENTITY_EMAIL)
    return spans


def detect_ids(text: str) -> List[Dict[str, Any]]:
    spans: List[Dict[str, Any]] = []
    for r in _presidio_analyze(text, ["US_SSN"]):
        _add_span(spans, r.start, r.end, ENTITY_ID, {"subtype": "US_SSN"})
    for m in CN_ID_18_REGEX.finditer(text):
        _add_span(spans, m.start(), m.end(), ENTITY_ID, {"subtype": "CN_ID_18"})
    for m in CN_ID_15_REGEX.finditer(text):
        _add_span(spans, m.start(), m.end(), ENTITY_ID, {"subtype": "CN_ID_15"})
    for m in HKID_REGEX.finditer(text):
        _add_span(spans, m.start(), m.end(), ENTITY_ID, {"subtype": "HKID"})
    return spans


def detect_bank_accounts(text: str) -> List[Dict[str, Any]]:
    spans: List[Dict[str, Any]] = []
    for r in _presidio_analyze(text, ["IBAN_CODE"]):
        _add_span(spans, r.start, r.end, ENTITY_BANK_ACCOUNT, {"subtype": "IBAN"})
    for m in IBAN_REGEX.finditer(text):
        _add_span(spans, m.start(), m.end(), ENTITY_BANK_ACCOUNT, {"subtype": "IBAN"})
    for m in LOCAL_BANK_HINT_REGEX.finditer(text):
        group = m.group(1)
        if not group:
            continue
        s = m.start(1)
        e = m.end(1)
        cleaned = re.sub(r"[^A-Z0-9]", "", group, flags=re.IGNORECASE)
        if len(cleaned) >= 6:
            _add_span(spans, s, e, ENTITY_BANK_ACCOUNT, {"subtype": "LOCAL"})
    return spans


def detect_passwords(text: str) -> List[Dict[str, Any]]:
    spans: List[Dict[str, Any]] = []
    for m in PASSWORD_HINT_REGEX.finditer(text):
        group = m.group(1)
        if not group:
            continue
        s = m.start(1)
        e = m.end(1)
        if len(group) >= 4:
            _add_span(spans, s, e, ENTITY_PASSWORD)
    return spans


def _luhn_valid(digits: str) -> bool:
    total = 0
    parity = len(digits) % 2
    for i, ch in enumerate(digits):
        d = ord(ch) - 48
        if (i % 2) == parity:
            d = d * 2
            if d > 9:
                d -= 9
        total += d
    return total % 10 == 0


def detect_credit_cards(text: str) -> List[Dict[str, Any]]:
    spans: List[Dict[str, Any]] = []
    for r in _presidio_analyze(text, ["CREDIT_CARD"]):
        _add_span(spans, r.start, r.end, ENTITY_CREDIT_CARD)
    for m in CC_BODY_REGEX.finditer(text):
        s, e = m.start(), m.end()
        raw = text[s:e]
        digits = re.sub(r"\D", "", raw)
        if len(digits) < 13 or len(digits) > 19:
            continue
        has_hint = bool(CC_HINT_REGEX.search(text[max(0, s - 24):min(len(text), e + 24)]))
        if has_hint or _luhn_valid(digits):
            _add_span(spans, s, e, ENTITY_CREDIT_CARD)
    return spans


def detect_phones(text: str, phone_regions: List[str]) -> List[Dict[str, Any]]:
    spans: List[Dict[str, Any]] = []
    seen: set[tuple[int, int]] = set()
    for r in _presidio_analyze(text, ["PHONE_NUMBER"]):
        s, e = r.start, r.end
        if (s, e) in seen:
            continue
        seen.add((s, e))
        frag = text[s:e]
        region_meta: Optional[str] = None
        try:
            num = phonenumbers.parse(frag, None)
            region_meta = phonenumbers.region_code_for_number(num)
        except Exception:
            region_meta = None
        _add_span(spans, s, e, ENTITY_PHONE, {"region": region_meta})
    # fallback/augment via phonenumbers across requested regions
    regions: List[Optional[str]] = list(dict.fromkeys(phone_regions or []))
    if re.search(r"(?<!\d)1[3-9]\d{9}(?!\d)", text) and "CN" not in regions:
        regions.append("CN")
    tried_regions = list(dict.fromkeys([*regions, None]))
    for region in tried_regions:
        try:
            matcher = phonenumbers.PhoneNumberMatcher(text, region)  # type: ignore[arg-type]
        except Exception:
            continue
        for match in matcher:
            s, e = match.start, match.end
            if (s, e) in seen:
                continue
            seen.add((s, e))
            try:
                num = match.number
                reg = phonenumbers.region_code_for_number(num)
            except Exception:
                reg = None
            _add_span(spans, s, e, ENTITY_PHONE, {"region": reg})
    return spans


def detect_all(text: str, locale: str, entity_types: List[str], phone_regions: List[str]) -> List[Dict[str, Any]]:
    want_person = ENTITY_PERSON in entity_types
    want_address = ENTITY_ADDRESS in entity_types
    want_email = ENTITY_EMAIL in entity_types
    want_phone = ENTITY_PHONE in entity_types
    want_id = ENTITY_ID in entity_types
    want_bank = ENTITY_BANK_ACCOUNT in entity_types
    want_pwd = ENTITY_PASSWORD in entity_types
    want_cc = ENTITY_CREDIT_CARD in entity_types

    spans: List[Dict[str, Any]] = []

    if want_person or want_address:
        spans.extend(detect_person_address(text, want_person, want_address))
        # if want_address and (_is_cjk(text) or _is_zh_locale(locale)):
        #     spans.extend(detect_cn_addresses(text, locale))
        #     spans.extend(detect_hk_localities(text, locale))
    if want_email:
        spans.extend(detect_emails(text))
    if want_id:
        spans.extend(detect_ids(text))
    if want_bank:
        spans.extend(detect_bank_accounts(text))
    if want_pwd:
        spans.extend(detect_passwords(text))
    if want_cc:
        spans.extend(detect_credit_cards(text))
    if want_phone:
        spans.extend(detect_phones(text, phone_regions))

    return spans
