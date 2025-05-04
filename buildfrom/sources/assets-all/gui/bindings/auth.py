import time
from typing import Union, cast
from .. import common
import minecraft_launcher_lib
import json

offical_mc_auth = {
    "redirectUrl": "https://login.live.com/oauth20_desktop.srf",
    "clientId": "00000000402b5328",
}


class CompleteLoginResponse(
    minecraft_launcher_lib.microsoft_types.CompleteLoginResponse
):
    access_token: minecraft_launcher_lib.microsoft_types.MinecraftAuthenticateResponse


def get_authorization_token(
    client_id: str,
    client_secret: str | None,
    redirect_uri: str,
    auth_code: str,
    code_verifier: str | None = None,
) -> minecraft_launcher_lib.microsoft_account.AuthorizationTokenResponse:
    """
    Get the authorization token. This function is called during :func:`complete_login`, so you need to use this function ony if :func:`complete_login` doesn't work for you.

    :param client_id: The Client ID of your Azure App
    :param client_secret: The Client Secret of your Azure App. This is deprecated and should not been used anymore.
    :param redirect_uri: The Redirect URI of your Azure App
    :param auth_code: The Code you get from :func:`parse_auth_code_url`
    :param code_verifier: The 3rd entry in the Tuple you get from :func:`get_secure_login_data`
    """
    parameters = {
        "client_id": client_id,
        "scope": minecraft_launcher_lib.microsoft_account.__SCOPE__,
        "code": auth_code,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
    }

    if client_secret is not None:
        parameters["client_secret"] = client_secret

    if code_verifier is not None:
        parameters["code_verifier"] = code_verifier

    header = {
        "Content-Type": "application/x-www-form-urlencoded",
        "user-agent": minecraft_launcher_lib.microsoft_account.get_user_agent(),
    }
    r = minecraft_launcher_lib.microsoft_account.requests.post(
        "https://login.live.com/oauth20_token.srf", data=parameters, headers=header
    )
    return r.json()


def complete_login(
    client_id: str,
    client_secret: str | None,
    redirect_uri: str,
    auth_code: str,
    code_verifier: str | None = None,
) -> CompleteLoginResponse:
    """
    Do the complete login process.

    :param client_id: The Client ID of your Azure App
    :param client_secret: The Client Secret of your Azure App. This is deprecated and should not been used anymore.
    :param redirect_uri: The Redirect URI of your Azure App
    :param auth_code: The Code you get from :func:`parse_auth_code_url`
    :param code_verifier: The 3rd entry in the Tuple you get from :func:`get_secure_login_data`
    :raises AzureAppNotPermitted: Your Azure App don't have the Permission to use the Minecraft API
    :raises AccountNotOwnMinecraft: The Account does not own Minecraft

    It returns the following:

    .. code:: json

        {
            "id" : "The uuid",
            "name" : "The username",
            "access_token": MinecraftAuthenticateResponse,
            "refresh_token": "The refresh token",
            "skins" : [{
                "id" : "6a6e65e5-76dd-4c3c-a625-162924514568",
                "state" : "ACTIVE",
                "url" : "http://textures.minecraft.net/texture/1a4af718455d4aab528e7a61f86fa25e6a369d1768dcb13f7df319a713eb810b",
                "variant" : "CLASSIC",
                "alias" : "STEVE"
            } ],
            "capes" : []
        }
    """
    token_request = get_authorization_token(
        client_id, client_secret, redirect_uri, auth_code, code_verifier
    )
    token = token_request["access_token"]

    xbl_request = minecraft_launcher_lib.microsoft_account.authenticate_with_xbl(token)
    xbl_token = xbl_request["Token"]
    userhash = xbl_request["DisplayClaims"]["xui"][0]["uhs"]

    xsts_request = minecraft_launcher_lib.microsoft_account.authenticate_with_xsts(
        xbl_token
    )
    xsts_token = xsts_request["Token"]

    account_request = (
        minecraft_launcher_lib.microsoft_account.authenticate_with_minecraft(
            userhash, xsts_token
        )
    )

    if "access_token" not in account_request:
        raise minecraft_launcher_lib.microsoft_account.AzureAppNotPermitted()

    access_token = account_request["access_token"]

    profile = minecraft_launcher_lib.microsoft_account.get_profile(access_token)

    if "error" in profile and profile["error"] == "NOT_FOUND":
        raise minecraft_launcher_lib.microsoft_account.AccountNotOwnMinecraft()

    profile = cast(
        minecraft_launcher_lib.microsoft_account.CompleteLoginResponse, profile
    )

    profile["access_token"] = account_request
    profile["refresh_token"] = token_request["refresh_token"]

    return profile


def complete_refresh(
    client_id: str,
    client_secret: str | None,
    redirect_uri: str | None,
    refresh_token: str,
) -> CompleteLoginResponse:
    """
    Do the complete login process with a refresh token. It returns the same as :func:`complete_login`.

    :param client_id: The Client ID of your Azure App
    :param client_secret: The Client Secret of your Azure App. This is deprecated and should not been used anymore.
    :param redirect_uri: The Redirect URI of Azure App. This Parameter only exists for backwards compatibility and is not used anymore.
    :param refresh_token: Your refresh token
    :raises InvalidRefreshToken: Your refresh token is not valid
    :raises AccountNotOwnMinecraft: The Account does not own Minecraft
    """
    token_request = (
        minecraft_launcher_lib.microsoft_account.refresh_authorization_token(
            client_id, client_secret, redirect_uri, refresh_token
        )
    )

    if "error" in token_request:
        raise minecraft_launcher_lib.microsoft_account.InvalidRefreshToken()

    token = token_request["access_token"]

    xbl_request = minecraft_launcher_lib.microsoft_account.authenticate_with_xbl(token)
    xbl_token = xbl_request["Token"]
    userhash = xbl_request["DisplayClaims"]["xui"][0]["uhs"]

    xsts_request = minecraft_launcher_lib.microsoft_account.authenticate_with_xsts(
        xbl_token
    )
    xsts_token = xsts_request["Token"]

    account_request = (
        minecraft_launcher_lib.microsoft_account.authenticate_with_minecraft(
            userhash, xsts_token
        )
    )
    access_token = account_request["access_token"]

    profile = minecraft_launcher_lib.microsoft_account.get_profile(access_token)

    if "error" in profile and profile["error"] == "NOT_FOUND":
        raise minecraft_launcher_lib.microsoft_account.AccountNotOwnMinecraft()

    profile = cast(CompleteLoginResponse, profile)

    profile["access_token"] = account_request
    profile["refresh_token"] = token_request["refresh_token"]

    return profile


def isNotLoggedIn():
    common.settings.beginGroup("account")
    res = not common.settings.value("loggedIn") or (
        common.settings.value("authRes") == None
        or common.settings.value("authRes") == ""
    )
    common.settings.endGroup()
    return res

def do_refresh_from_token(auth,refresh_token) -> Union[tuple[bool, CompleteLoginResponse], tuple[bool, int]]:
    try:
        refresh = complete_refresh(
            client_id=auth["clientId"],
            client_secret=None,
            redirect_uri=auth["redirectUrl"],
            refresh_token=refresh_token,
        )
        print("Auth has been refreshed")
    except minecraft_launcher_lib.exceptions.InvalidRefreshToken:
        common.settings.endGroup()
        return (False, 1)
    except minecraft_launcher_lib.exceptions.AccountNotOwnMinecraft:
        common.settings.endGroup()
        return (False, 2)
    except Exception as e:
        common.settings.endGroup()
        print(e)
        return (False, 0)
    common.settings.setValue("authRes", json.dumps(refresh))
    common.settings.setValue("authObtainedAt", time.time())
    common.settings.setValue("loggedIn", True)
    common.settings.endGroup()
    return (True, refresh)
def refresh_auth(auth) -> Union[tuple[bool, CompleteLoginResponse], tuple[bool, int]]:
    common.settings.beginGroup("account")
    info = json.loads(common.settings.value("authRes"))
    margin = 60
    if (
        info["access_token"]["expires_in"]
        + common.settings.value("authObtainedAt", type=float)
        + margin
    ) < time.time():
        return do_refresh_from_token(auth,info["refresh_token"])
    else:
        common.settings.endGroup()
        return (True, info)


def authFlow(auth) -> Union[tuple[bool, CompleteLoginResponse], tuple[bool, int]]:
    print(not isNotLoggedIn())
    if not isNotLoggedIn():
        info = refresh_auth(auth)
        if info[0]:
            return (True, info[1])
        else:
            if info[1] == 0:
                print("Auth error, aborting")
            elif info[1] == 1 or info[1] == 2:
                print("account invalid, logging out")
                common.settings.beginGroup("account")
                common.settings.setValue("loggedIn", False)
                common.settings.setValue("authRes", "{}")
                common.settings.setValue("authObtainedAt", 0)
                common.settings.endGroup()
            return (False, info[1])
    else:
        return (False, 0)
