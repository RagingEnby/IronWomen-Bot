from typing import Optional
import disnake
from modules import asyncreqs, utils


class MojangPlayer:
    def __init__(self, uuid: str, name: str):
        self.uuid = uuid
        self.name = name

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"MojangPlayer(uuid={self.uuid}, name={self.name})"

    @property
    def avatar(self) -> str:
        return f"https://mc-heads.net/avatar/{self.uuid}"

    def set_author(self, embed: disnake.Embed, text: Optional[str] = None) -> disnake.Embed:
        return embed.set_author(
            name=self.name + (' ' + text if text else ""),
            icon_url=self.avatar
        )

    @classmethod
    def from_dict(cls, data: dict[str, str]):
        return cls(data['id'], data['name'])


CACHE: dict[str, MojangPlayer] = {}


async def get(identifier: str) -> MojangPlayer:
    identifier = utils.remove_color_codes(identifier.lower()).strip().replace('-', '')
    if identifier in CACHE:
        return CACHE[identifier]
    print(identifier, 'not in mojang cache')
    url = "https://api.ragingenby.dev/player/" + identifier
    response = await asyncreqs.get(url)
    data = await response.json()
    CACHE[identifier] = MojangPlayer.from_dict(data)
    return CACHE[identifier]
    