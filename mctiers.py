from typing import Any, Dict, List, Optional

import httpx
import re

from models import Gamemode, OverallPlayer, GamemodePlayer, Player, Test


def match_uuid(string: str) -> bool:
    return bool(
        re.match(
            r"/([0-9a-f]{8})(?:-|)([0-9a-f]{4})(?:-|)(4[0-9a-f]{3})(?:-|)([89ab][0-9a-f]{3})(?:-|)([0-9a-f]{12})/",
            string,
        )
    )


def match_discord_id(string: str):
    return bool(re.match(r"\d{17,20}", string))


class ResponseBadRequest(Exception):
    pass


class ResponseInvalidGamemode(Exception):
    pass


class ResponseInternalError(Exception):
    pass


class MCTiersAPI:
    """
    The MCTiersAPI class used for calling all functions related to the API.
    """

    client: httpx.Client

    def __init__(self) -> None:
        """
        Initalises the `MCTiersAPI` class
        """

        self.client = httpx.Client(base_url="https://mctiers.com/api/v2", timeout=10)

    def get(self, endpoint: str, params: Optional[Any] = None) -> Any:
        """
        Perform a GET request against the MCTiers API and return parsed JSON.

        Args:
            endpoint: The API endpoint path (relative to the client's `base_url`).
            params: Optional query parameters to send with the request. This
                may be a dict, list or other value accepted by `httpx`.

        Returns:
            The parsed JSON body of the response.

        Raises:
            ResponseBadRequest: When the API returns a bad request error.
            ResponseInvalidGamemode: When an invalid gamemode is supplied.
            ResponseInternalError: When the API reports an internal error.
            Exception: For any unknown error codes returned by the API.
        """

        resp = self.client.get(endpoint, params=params)

        data = resp.json()

        if resp.is_error:
            code = data.get("code")
            message = data.get("message")

            match code:
                case "error.bad_request":
                    raise ResponseBadRequest(message)
                case "error.invalid_gamemode":
                    raise ResponseInvalidGamemode(message)
                case "error.internal":
                    raise ResponseInternalError(message)
                case _:
                    raise Exception(f"Unknown error code: {code} | message: {message}")

        return data

    def get_all_gamemodes(
        self, rank_count: int = 1, *, rank_from: int = 0
    ) -> Dict[str, Gamemode]:
        """
        Retrieve all available gamemodes from the API and return them as a
        mapping from gamemode key to `Gamemode` model.

        Args:
            rank_count: Number of player ranks to request per tier (API
                parameter `count`).
            rank_from: Pagination offset for ranks (API parameter `from`).

        Returns:
            A dictionary mapping gamemode keys to `Gamemode` instances.
        """

        gamemodes: Dict[str, Gamemode] = {}

        data: Dict[str, Any] = self.get(
            "/mode/list", {"count": str(rank_count), "from": str(rank_from)}
        )

        for key, obj in data.items():
            gamemodes[key] = Gamemode.model_validate(obj)

        return gamemodes

    def list_all_gamemodes(
        self, rank_count: int = 1, *, rank_from: int = 0
    ) -> List[Gamemode]:
        """
        Return all available gamemodes as a list.

        This is a convenience wrapper around `get_all_gamemodes()`
        that discards the dictionary keys and returns only the
        `Gamemode` objects.
        """

        return list(self.get_all_gamemodes(rank_count, rank_from=rank_from).values())

    def list_overall_rankings(
        self, rank_count: int = 1, *, rank_from: int = 0
    ) -> List[OverallPlayer]:
        """
        Retrieve the overall player rankings from the API.

        Args:
            rank_count: Number of players to return.
            rank_from: Pagination offset.

        Returns:
            A list of `OverallPlayer` objects sorted by `points`.
        """

        rankings: List[OverallPlayer] = []

        objs: List[Any] = self.get(
            "/mode/overall", {"count": str(rank_count), "from": str(rank_from)}
        )

        for obj in objs:
            rankings.append(OverallPlayer.model_validate(obj))

        return sorted(rankings, key=lambda player: player.points)

    def get_gamemodes_rankings(
        self,
        gamemode: str,
        rank_count: int = 1,
        *,
        rank_from: int = 0,
        retired: bool = False,
    ) -> Dict[int, List[GamemodePlayer]]:
        """
        Retrieve rankings for a specific gamemode.

        Args:
            gamemode: The gamemode key to query (e.g. "bedwars").
            rank_count: Number of players to request per tier.
            rank_from: Pagination offset for the returned ranks.
            retired: If True, query the retired leaderboard endpoint.

        Returns:
            A dict mapping tier numbers (int) to lists of `GamemodePlayer`
            instances. The returned dict is sorted by tier.
        """

        rankings: Dict[int, List[GamemodePlayer]] = {}

        endpoint: str = f"/mode/{gamemode}{"/retired" if retired else ""}"

        data: Dict[str, List[Any]] = self.get(
            endpoint, {"count": str(rank_count), "from": str(rank_from)}
        )

        for key, objs in data.items():
            ranking = rankings[int(key)] = []
            for obj in objs:
                ranking.append(GamemodePlayer.model_validate(obj))

        return dict(sorted(rankings.items()))

    def get_player_profile(
        self,
        identifier: str,
        *,
        tests: bool = False,
        badges: bool = False,
    ) -> Player:
        """
        Retrieve a player's profile using a UUID, username, or Discord ID.

        Args:
            identifier: The player's UUID, in-game username, or Discord ID.
            tests: Whether to include test match data in the response.
            badges: Whether to include badge information in the response.

        Returns:
            Player: The validated player profile object.
        """

        params: List[str] = []
        endpoint: str = f"/profile/by-name/{identifier}"

        if match_uuid(identifier):
            endpoint = f"/profile/{identifier}"

        if match_discord_id(identifier):
            endpoint = f"/profile/by-discord/{identifier}"

        if tests:
            params.append("tests")

        if badges:
            params.append("badges")

        obj = self.get(endpoint, params)

        return Player.model_validate(obj)

    def get_tester_history(
        self,
        uuid: str,
        test_count: int = 1,
        *,
        gamemode: Optional[str] = None,
        test_from: int = 0,
    ) -> List[Test]:
        """
        Retrieve a paginated list of tests performed by a tester (by UUID).

        Args:
            uuid: UUID of the tester whose history to retrieve.
            test_count: Number of test entries to request.
            gamemode: Optional gamemode filter to limit results.
            test_from: Pagination offset.

        Returns:
            A list of `Test` objects sorted by their `at` timestamp.
        """

        testers: List[Test] = []
        params: Dict[str, Any] = {"count": test_count, "from": test_from}

        if gamemode:
            params["gamemode"] = gamemode

        objs: List[Any] = self.get(f"/tests/{uuid}", params)

        for obj in objs:
            print(obj)
            testers.append(Test.model_validate(obj))

        return sorted(testers, key=lambda test: test.at)

    def get_recent_high_test(
        self, test_count: int = 1, *, gamemode: Optional[str] = None
    ) -> List[Test]:
        """
        Retrieve the most recent high-tier tests.

        This returns recent tests that resulted in high tiers (typically tier
        1 or 2). Optionally filter by a specific gamemode.

        Args:
            test_count: Number of tests to request.
            gamemode: Optional gamemode to filter results.

        Returns:
            A list of `Test` objects sorted by their `at` timestamp.
        """

        testers: List[Test] = []
        params: Dict[str, Any] = {"count": test_count}

        if gamemode:
            params["gamemode"] = gamemode

        objs: List[Any] = self.get(f"/tests/recent/high", params)

        for obj in objs:
            testers.append(Test.model_validate(obj))

        return sorted(testers, key=lambda test: test.at)
