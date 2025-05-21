import re
import json
from typing import Optional, Literal
from httpx import Response
from json import JSONDecodeError

from TikTokLive.client.errors import UserNotFoundError
from TikTokLive.client.web.web_settings import WebDefaults
from TikTokLive.client.web.web_base import ClientRoute, TikTokHTTPClient
from TikTokLive.client.web.routes.fetch_room_id_api import FetchRoomIdAPIRoute
from TikTokLive.client.errors import UserOfflineError, UserNotFoundError, TikTokLiveError
from TikTokLive.client.web.routes.fetch_room_id_live_html import FailedParseRoomIdError, FetchRoomIdLiveHTMLRoute


class FailedParseRoomTitleAPIError(TikTokLiveError):
    """ Thrown when the Room Title cannot be parsed """


class FailedParseRoomTitleHTMLError(TikTokLiveError):
    """ Thrown when the Room Title cannot be parsed """


class FetchRoomTitleRoute(ClientRoute):
    """
    Route to retrieve the room title from cached response on FetchRoomId route

    """

    async def __call__(self, client: Literal["html", "api"]) -> str:
        """
        Fetch the Room ID for a given unique_id from the TikTok API

        :param unique_id: The user's uniqueId
        :return: The room ID string

        """
        if (client == "html"):
            response = FetchRoomIdLiveHTMLRoute.response.text
            return self.parse_room_title_from_html(response)
        else:
            response = FetchRoomIdAPIRoute.response.json()
            return self.parse_room_title_from_api(response)

        return ""

    @classmethod
    def parse_room_title_from_html(cls, html: str) -> str:
        """
        Parse the room ID from livestream API response

        :param data: The data to parse
        :return: The user's room id
        :raises: UserOfflineError if the user is offline
        :raises: FailedParseRoomIdError if the user data does not exist

        """
        match: Optional[re.Match[str]
                        ] = FetchRoomIdLiveHTMLRoute.SIGI_PATTERN.search(html)

        if match is None:
            raise FailedParseRoomIdError(
                "Failed to extract the SIGI_STATE HTML tag, you might be blocked by TikTok.")

        # Load SIGI_STATE JSON
        try:
            sigi_state: dict = json.loads(match.group(1))
        except JSONDecodeError:
            raise FailedParseRoomIdError(
                "Failed to parse SIGI_STATE into JSON. Are you captcha-blocked by TikTok?")

        # LiveRoom is missing for users that have never been live
        if sigi_state.get('LiveRoom') is None:
            raise UserNotFoundError(
                "The requested user is not capable of going LIVE on TikTok, "
                "has never gone live on TikTok, or does not exist.."
            )

        # Method 1) Parse the room ID from liveRoomUserInfo/user#roomId
        room_data: dict = sigi_state["LiveRoom"]["liveRoomUserInfo"]
        username_str: str = f" '@{room_data['uniqueId']}' " if room_data.get(
            'uniqueId') else " "

        # User is offline
        if room_data.get('status') == 4:
            raise UserOfflineError(
                f"The requested TikTok LIVE user{username_str}is offline.")

        return room_data['liveRoom'].get('title')

    @classmethod
    def parse_room_title_from_api(cls, data: dict) -> str:
        """
        Parse the room ID from livestream API response

        :param data: The data to parse
        :return: The user's room id
        :raises: UserOfflineError if the user is offline
        :raises: FailedParseRoomIdError if the user data does not exist

        """
        try:
            return data['data']['liveRoom']['title']
        except KeyError:
            raise FailedParseRoomTitleAPIError(
                "That user can't stream, or you might be blocked by TikTok.")
