# PSP Streamer for Home Assistant

Native Home Assistant **custom integration**, installable through **HACS**.
Control a PSP running [PSPStreamer](https://github.com/dreimer1986/PSPStreamer)
and view its confirmed playback state, title and position.

This repository contains only the integration. The server app/add-on, Docker
image and PSP application remain in the
[PSPStreamer repository](https://github.com/dreimer1986/PSPStreamer).

## Install with HACS

1. Open **HACS → menu → Custom repositories**.
2. Add `https://github.com/dreimer1986/PSPStreamerHA` with type **Integration**.
3. Download **PSP Streamer** and restart Home Assistant.
4. Open **Settings → Devices & services → Add integration → PSP Streamer**.
5. Enter the PSP Streamer server URL and its shared password.

Requires Home Assistant **2026.3+**, PSP Streamer server **0.1.44+** and the
matching PSP application with playback telemetry. The PSP may be offline during
setup; the entity becomes available once the application connects.

This repository does not need a GitHub Release: HACS can install its default
branch. Releases of the PSP application in the other repository are independent.
Do not add this repository to Home Assistant's app/add-on store.

## Features

- Confirmed playing, paused, buffering and idle state, with available metadata.
- Play/resume, pause, stop, seek and previous/next item.
- Media browser for enabled Files, Plex, Jellyfin, DLNA and Radio sources.
  DLNA and Plex/Jellyfin original-version folders require server 0.1.51+.
  Register DLNA servers in the server web UI; they then appear here automatically.
  Selected versions retain their identity when played from HA. External subtitles
  use the server's track indices via `extra.subtitle`, like embedded tracks.
- Current Plex/Jellyfin episode thumbnails and album covers in the media-player
  entity and dashboard. Requires PSPStreamer server/add-on 0.1.46 or newer.
  Home Assistant fetches images with the configured server password and serves
  them through its own image proxy; credentials are never embedded in image URLs.
- URL/password configuration, reconfiguration and German/English setup texts.
- No MQTT, extra PSP polling thread or changes to A/V synchronization.

See the [complete setup guide and limitations](docs/HOME_ASSISTANT.md).

Integration 0.1.2 also accepts authenticated cover images for version-specific
media IDs. When updating the HA server app to host networking, keep using its
host IP/domain and configured port; change any former container-only DNS address
through this integration's **Reconfigure** menu. No new entity is needed.

Integration **0.1.3** also accepts DLNA cover identifiers from server **0.1.52**.
When the DLNA source supplies `albumArtURI`, its current-media cover appears
through the same authenticated image proxy. Missing covers stay empty; this
does not imply DLNA backdrop or watched-state support. PSP-side timers,
bookmarks, favorites and connection profiles do not require new HA entities.

## Development

The integration is self-contained at runtime. The existing integration checks
use a real local PSP Streamer test server, so development requires a checkout of
that repository too. In a separate Python environment with Home Assistant
installed, run from this repository:

```bash
PYTHONPATH=../PSPStreamer python -m unittest tests.ha_integration_checks -v
```

No server code is bundled into the integration. GitHub Actions contains HACS
and hassfest packaging checks. The imported integration retains the source
project's GPL-2.0-or-later license; see [LICENSE](LICENSE).
