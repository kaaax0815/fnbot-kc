"""
“Commons Clause” License Condition v1.0
Copyright Oli 2020

The Software is provided to you by the Licensor under the
License, as defined below, subject to the following condition.
Without limiting other conditions in the License, the grant
of rights under the License will not include, and the License
does not grant to you, the right to Sell the Software.
For purposes of the foregoing, “Sell” means practicing any or
all of the rights granted to you under the License to provide
to third parties, for a fee or other consideration (including
without limitation fees for hosting or consulting/ support
services related to the Software), a product or service whose
value derives, entirely or substantially, from the functionality
of the Software. Any license notice or attribution required by
the License must also include this Commons Clause License
Condition notice.

Software: BenBotAsync
License: Apache 2.0
"""

from typing import Tuple, Union, Any

from .enums import *
from .cosmetics import BRCosmetic
from .exceptions import InvalidParameters, NotFound
from .api import BenBot

import aiohttp
import base64
import codecs
import fortnitepy
import traceback
import functools
import asyncio
import json
import datetime

__name__ = 'BenBotAsyncNoAds'
__version__ = '2.6.0'
__author__ = 'kaaaxcreators'

try:
    import fortnitepy

    if fortnitepy.__version__ == '1.7.1':
        raise ValueError('Please update your fortnitepy to 2.0.0+.')
except ImportError:
    pass

BEN_BOT_BASE = 'https://benbotfn.tk/api/v1'

# # IOS_TOKEN_TEMPLATE = (b'SnJ5cGJ6ciAlZiwgVid6IG4geWJvb2wgb2JnIHpucXIgb2wga1p2ZmdnL3p2Zmdr'
# #                       b'Ynl2ISBTYmUgdXJ5YywgeXZmZyBicyBwYnp6bmFxZiBiZSB2cyBsYmggam5hYW4g'
# #                       b'dWJmZyBsYmhlIGJqYSBvYmcsIHdidmEgZ3VyIHF2ZnBiZXE6IHVnZ2NmOi8vcXZm'
# #                       b'cGJlcS50dC84dXJORUVPLg==')
#
# IOS_TOKEN_TEMPLATE = (b'SGZyIFBicXIgVW52eXJsLUdGSCAjbnEhXGFKcnlwYnpyICVmLCB2cyBsYmggam5hZyBsYm'
#                       b'hlIGJqYSBvYmcgYmUgdXJ5Yywgd2J2YTogdWdnY2Y6Ly9xdmZwYmVxLnR0Lzh1ck5FRU8==')


def time() -> str:
    return datetime.datetime.now().strftime('%H:%M:%S')


# Credit to Terbau for this function.
async def json_or_text(response: aiohttp.ClientResponse) -> Union[str, dict]:
    text = await response.text(encoding='utf-8')
    if 'application/json' in response.headers.get('content-type', ''):
        return json.loads(text)
    return text


async def set_default_loadout(client: fortnitepy.Client, config: dict, member: fortnitepy.PartyMember) -> None:
    """Function which can be used with fortnitepy to set the default loadout."""

    party_update_meta = client.party  # Saves direct route to the party_update_meta object.

    if (party_update_meta.id == client.party.id
            and client.default_party_member_config.cls is not fortnitepy.party.JustChattingClientPartyMember):
        await party_update_meta.me.edit_and_keep(  # Sets default loadout.
            functools.partial(
                party_update_meta.me.set_outfit,
                config['cid']
            ),
            functools.partial(
                party_update_meta.me.set_backpack,
                config['bid']
            ),
            functools.partial(
                party_update_meta.me.set_pickaxe,
                config['pickaxe_id']
            ),
            functools.partial(
                party_update_meta.me.set_banner,
                icon=config['banner'],
                color=config['banner_colour'],
                season_level=config['level']
            ),
            functools.partial(
                party_update_meta.me.set_battlepass_info,
                has_purchased=True,
                level=config['bp_tier']
            )
        )

    await asyncio.sleep(1)  # Waits 1 second after submitting iOS token before emoting to avoid rate limits.

    if (party_update_meta.id == client.party.id
            and client.default_party_member_config.cls is not fortnitepy.party.JustChattingClientPartyMember):
        await party_update_meta.me.clear_emote()  # Clears emote to allow the next emote to play.
        await party_update_meta.me.set_emote(asset=config['eid'])  # Plays the emote from config.

        if client.user.display_name != member.display_name:  # Welcomes the member who just joined.
            print(f"[PartyBot] [{time()}] {member.display_name} has joined the lobby.")


async def get_cosmetic(**params: Any) -> BRCosmetic:
    """|coro|

    Fetches first cosmetic matching parameters. All parameters are optional but at least 1 is required.

    Parameters
    ----------
    backendRarity: Optional[:class:`str`]
        The backend rarity of the cosmetic.
    backendType: Optional[:class:`str`]
        The backend type of the cosmetic.
    description: Optional[:class:`str`]
        The description of the cosmetic (this is based on your searchLang and your matchMethod).
    hasFeaturedIcon: Optional[:class:`bool`]
        Whether the cosmetic needs a featured icon.
    hasIcon: Optional[:class:`bool`]
        Whether the cosmetic needs a normal icon.
    hasSeries: Optional[:class:`str`]
        Whether the cosmetic needs to have a series.
    hasVariants: Optional[:class:`str`]
        Whether the cosmetic needs to have variants.
    lang: Optional[:class:`str`]
        The language code that should be used for **results**, defaults to 'en'.
    matchMethod: Optional[:class:`str`]
        The match method (full, contains, starts, ends) that should be used for filtering the files
    name: Optional[:class:`str`]
        The display name of the cosmetic (this is based on your searchLang and your matchMethod).
    rarity: Optional[:class:`str`]
        The rarity of the cosmetic (this is based on your searchLang and your matchMethod).
    searchLang: Optional[:class:`str`]
        The language code that should be used for searching, defaults to 'en'.
    series: Optional[:class:`str`]
        The series of the cosmetic (this is based on your searchLang and your matchMethod).
    set: Optional[:class:`str`]
        The set of the cosmetic (this is based on your searchLang and your matchMethod).
    shortDescription: Optional[:class:`str`]
        The short description of the cosmetic (this is based on your searchLang and your matchMethod).


    Raises
    ------
    InvalidParameters
        If none or more than 1 parameters are provided.
    NotFound
        If no cosmetics are found matching parameters.

    Returns
    -------
    :class:`BRCosmetic`:
        BRCosmetic object containing the cosmetics information.
    """
    async with aiohttp.ClientSession() as session:
        async with session.request(method='GET', url=f'{BEN_BOT_BASE}/cosmetics/br/search', params=params) as r:
            data = await json_or_text(r)

            if 'At least one search parameter is required' in str(data):
                raise InvalidParameters('At least one valid search parameter is required.')

            if 'Could not find any cosmetic matching parameters' in str(data):
                raise NotFound('Could not find any cosmetic matching parameters.')

            return BRCosmetic(data)


async def get_cosmetics(**params: Any) -> list:
    """|coro|

    Fetches first cosmetic matching parameters. All parameters are optional but at least 1 is required.

    Parameters
    ----------
    backendRarity: Optional[:class:`str`]
        The backend rarity of the cosmetic.
    backendType: Optional[:class:`str`]
        The backend type of the cosmetic.
    description: Optional[:class:`str`]
        The description of the cosmetic (this is based on your searchLang and your matchMethod).
    hasFeaturedIcon: Optional[:class:`bool`]
        Whether the cosmetic needs a featured icon.
    hasIcon: Optional[:class:`bool`]
        Whether the cosmetic needs a normal icon.
    hasSeries: Optional[:class:`str`]
        Whether the cosmetic needs to have a series.
    hasVariants: Optional[:class:`str`]
        Whether the cosmetic needs to have variants.
    lang: Optional[:class:`str`]
        The language code that should be used for **results**, defaults to 'en'.
    matchMethod: Optional[:class:`str`]
        The match method (full, contains, starts, ends) that should be used for filtering the files
    name: Optional[:class:`str`]
        The display name of the cosmetic (this is based on your searchLang and your matchMethod).
    rarity: Optional[:class:`str`]
        The rarity of the cosmetic (this is based on your searchLang and your matchMethod).
    searchLang: Optional[:class:`str`]
        The language code that should be used for searching, defaults to 'en'.
    series: Optional[:class:`str`]
        The series of the cosmetic (this is based on your searchLang and your matchMethod).
    set: Optional[:class:`str`]
        The set of the cosmetic (this is based on your searchLang and your matchMethod).
    shortDescription: Optional[:class:`str`]
        The short description of the cosmetic (this is based on your searchLang and your matchMethod).


    Raises
    ------
    InvalidParameters
        If none or more than 1 parameters are provided.
    NotFound
        If no cosmetics are found matching parameters.

    Returns
    -------
    :class:`list`:
        List containing BRCosmetic objects which contain the cosmetics information.
    """
    async with aiohttp.ClientSession() as session:
        async with session.request(method='GET', url=f'{BEN_BOT_BASE}/cosmetics/br/search/all', params=params) as r:
            data = await json_or_text(r)

            if 'At least one search parameter is required' in str(data):
                raise InvalidParameters('At least one valid search parameter is required.')

            if 'Could not find any cosmetic matching parameters' in str(data):
                raise NotFound('Could not find any cosmetic matching parameters.')

            return [BRCosmetic(cosmetic) for cosmetic in data]


async def get_cosmetic_from_id(cosmetic_id: str) -> BRCosmetic:
    """|coro|

    Fetches first cosmetic matching parameters. All parameters are optional but at least 1 is required.

    Parameters
    ----------
    cosmetic_id: :class:`str`
        The id of the cosmetic.


    Raises
    ------
    NotFound
        If no cosmetics are found matching parameters.

    Returns
    -------
    :class:`BRCosmetic`:
        BRCosmetic object containing the cosmetics information.
    """
    async with aiohttp.ClientSession() as session:
        async with session.request(method='GET', url=f'{BEN_BOT_BASE}/cosmetics/br/{cosmetic_id}') as r:
            data = await json_or_text(r)

            if 'Invalid ID' in str(data):
                raise NotFound('Invalid ID.')

            return BRCosmetic(data)
