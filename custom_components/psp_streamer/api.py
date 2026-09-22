"""Authenticated, asynchronous server API; never poll the command mailbox."""
import asyncio
import base64
import re
from urllib.parse import urlsplit

import aiohttp


class ApiError(Exception):
    """Unavailable, incompatible or failed request."""


class AuthError(ApiError):
    """Password rejected."""


def normalize_url(value):
    value = value.strip().rstrip('/')
    parsed = urlsplit(value)
    if (parsed.scheme not in {'http', 'https'} or not parsed.hostname or
            parsed.username or parsed.password or parsed.query or parsed.fragment):
        raise ValueError('Invalid server URL')
    _ = parsed.port  # Reject invalid ports before saving a config entry.
    return value


class Api:
    def __init__(self, session, url, password):
        self.session = session
        self.url = normalize_url(url)
        self.headers = {'Authorization': 'Basic ' + base64.b64encode(('psp:'+password).encode()).decode('ascii')}

    async def request(self, path, *, params=None, command=None, timeout=30):
        try:
            async with self.session.request('POST' if command is not None else 'GET',
                    self.url + path, params=params, json=command, headers=self.headers,
                    allow_redirects=False, timeout=aiohttp.ClientTimeout(total=timeout)) as response:
                if response.status in (401, 403):
                    raise AuthError('Authentication failed')
                if response.status != 200:
                    raise ApiError(f'Server returned HTTP {response.status}')
                result = await response.json()
                if not isinstance(result, dict):
                    raise ApiError('Invalid server response')
                return result
        except (aiohttp.ClientError, asyncio.TimeoutError, ValueError) as err:
            # Do not expose URLs, credentials or server response bodies in logs.
            raise ApiError('Could not communicate with PSP Streamer') from err

    async def status(self):
        data = await self.request('/api/player', timeout=10)
        if (data.get('api') != 1 or not isinstance(data.get('server_id'), str) or
                not isinstance(data.get('online'), bool) or
                data.get('state') not in {'idle', 'playing', 'paused', 'buffering'}):
            raise ApiError('Update the PSP Streamer server')
        return data

    async def image(self, path):
        # Only our server's image route; never forward the password to a URL
        # from an upstream metadata field or an HTTP redirect.
        if not isinstance(path, str) or not re.fullmatch(r'/api/artwork/[a-zA-Z0-9.]+/(?:cover|backdrop)(?:\?v=[0-9a-f]+)?', path):
            return None, None
        try:
            async with self.session.get(self.url+path, headers=self.headers, allow_redirects=False,
                    timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status != 200 or response.content_type not in {'image/jpeg','image/png','image/webp'}:
                    return None, None
                data = bytearray()
                async for chunk in response.content.iter_chunked(65536):
                    data.extend(chunk)
                    if len(data)>8*1024*1024:
                        return None, None
                return bytes(data), response.content_type
        except (aiohttp.ClientError, asyncio.TimeoutError):
            return None, None

    async def command(self, action, **fields):
        return await self.request('/api/remote/command', command={'action': action, **fields}, timeout=60)
