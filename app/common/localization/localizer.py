import json
from functools import wraps, partial
from os import listdir
from os.path import isfile, join
from typing import Union, Callable

from interactions.api.events import Component

from common.var import localization_path

from interactions import SlashContext, ComponentContext, LocalisedName, LocalisedDesc

locales = {}
default_locale = "en-US"  # 기본 로케일
used_keys = set()
_used_keys_cache = set()
_write_counter = 0
WRITE_EVERY = 20
USED_KEYS_LOG_PATH = "./used_translation_keys.json"

language_codes = {
    "bg": "bulgarian",
    "zh-CN": "chinese_china",
    "zh-TW": "chinese_taiwan",
    "hr": "croatian",
    "cs": "czech",
    "da": "danish",
    "nl": "dutch",
    "en-GB": "english_uk",
    "en-US": "english_us",
    "fi": "finnish",
    "fr": "french",
    "de": "german",
    "el": "greek",
    "hi": "hindi",
    "hu": "hungarian",
    "it": "italian",
    "ja": "japanese",
    "ko": "korean",
    "lt": "lithuanian",
    "no": "norwegian",
    "pl": "polish",
    "pt-BR": "portuguese_brazilian",
    "ro": "romanian_romania",
    "ru": "russian",
    "es-ES": "spanish",
    "sv-SE": "swedish",
    "th": "thai",
    "tr": "turkish",
    "uk": "ukrainian",
    "vi": "vietnamese",
}

language_utc_offsets = {
    "bg": 2,  # Bulgaria
    "zh-CN": 8,  # China
    "zh-TW": 8,  # Taiwan
    "hr": 1,  # Croatia
    "cs": 1,  # Czech
    "da": 1,  # Denmark
    "nl": 1,  # Netherlands
    "en-GB": 0,  # UK
    "en-US": -5,  # USA (EST 대표)
    "fi": 2,  # Finland
    "fr": 1,  # France
    "de": 1,  # Germany
    "el": 2,  # Greece
    "hi": 5.5,  # India
    "hu": 1,  # Hungary
    "it": 1,  # Italy
    "ja": 9,  # Japan
    "ko": 9,  # Korea
    "lt": 2,  # Lithuania
    "no": 1,  # Norway
    "pl": 1,  # Poland
    "pt-BR": -3,  # Brazil
    "ro": 2,  # Romania
    "ru": 3,  # Russia (Moscow 기준)
    "es-ES": 1,  # Spain
    "sv-SE": 1,  # Sweden
    "th": 7,  # Thailand
    "tr": 3,  # Turkey
    "uk": 2,  # Ukraine
    "vi": 7,  # Vietnam
}


for file in listdir(localization_path):
    if file.endswith(".json") and isfile(join(localization_path, file)):
        with open(join(localization_path, file), "r", encoding="utf-8") as f:
            locales[file[:-5]] = json.load(f)


def localize(server_only: bool = True):
    def decorator(func):
        @wraps(func)
        async def wrapped_func(
            self, ctx: Union[SlashContext, ComponentContext, Component], *args, **kwargs
        ):
            if isinstance(ctx, Component):
                ctx = ctx.ctx
            if server_only and not ctx.guild:
                _ = localizator(ctx.locale)
                await ctx.send(_("server_only_error"), ephemeral=True)
                return None

            locale = ctx.locale
            if locale not in locales:
                locale = ctx.guild.preferred_locale if ctx.guild else default_locale
            return await func(self, ctx, localizator(locale), *args, **kwargs)

        return wrapped_func

    return decorator


def localizator(locale) -> Callable[[str], str]:
    return partial(getlocale, locale=locale)


def getlocale(key_: str, locale: str) -> str:
    used_keys.add(key_)

    try:
        with open(USED_KEYS_LOG_PATH, "w", encoding="utf-8") as f:
            json.dump(sorted(used_keys), f, ensure_ascii=False, indent=2)
        # _write_counter = 0
    except Exception as e:
        print(f"⚠️ Failed to write used keys: {e}")

    if key_ in locales.get(locale, {}):
        return locales[locale][key_]
    if key_ in locales.get(default_locale, {}):
        return locales[default_locale][key_]
    return key_


def getname(name) -> LocalisedName:
    names = {}
    for locale in locales:
        if name in locales[locale]:
            names[language_codes[locale]] = (
                locales[locale][name].lower().replace(" ", "_")
            )
    if language_codes[default_locale] not in names:
        names[language_codes[default_locale]] = name
    return LocalisedName(**names)


def getdesc(name) -> LocalisedDesc:
    descs = {}
    for locale in locales:
        if name in locales[locale]:
            descs[language_codes[locale]] = locales[locale][name]
    if language_codes[default_locale] not in descs:
        descs[language_codes[default_locale]] = name
    return LocalisedDesc(**descs)
