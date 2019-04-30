# LG Remote

An `asyncio` based LG WebOS TV remote for Python 3.6+.

Remotes communicate with the LG WebOS TV using json messages over a websocket
connection on port 3000. [websockets](https://github.com/aaugustin/websockets)
is an `asyncio`-based websockets library for Python 3. This library extends
`websockets` to support the remote protocol and provides a command line tool
using that protocol.


## LGRemoteProtocol class

`LGRemoteProtocol` extends `websockets.WebsocketClientProtocol` with three
additional methods:
- `register(client_key)`: the remote must register with the tv before any
  additional messages can be sent. If `client_key` is not provided the tv will
  ask to pair. If pairing succeeds or if `client_key` was provided the
  `client_key` is returned. It should be saved for subsequent connections
  without pairing
- `request(ssap_uri, payload)` sends a payload to an `ssap_uri`. The payload
  should be a dictionary and is automatically serialized
- `response(ssap_uri, payload)` returns a deserialized payload as a dictionary.

### Example

From within an async function:
```
async with websockets.connect('ws://<tv ip address>:3000',
                              create_protocol=LGRemoteProtocol) as remote:
    # Register, and pair if no client_key is given
    client_key = await remote.register(<saved client_key or None>)

    # Save the client_key so we don't need to pair next time
    
    await remote.request('ssdp://audio/setVolume', { 'volume': 10 })
    response = await remote.response()

    # Do something with response
```

## lgremote command line tool

A command line tool `lgremote` is also provided. Commands are not hard-coded.
Instead, the `lgremote` command accepts an `ssdp` endpoint with an optional
json payload:
```
lgremote ssdp://audio/setVolume -p '{"volume": 10}'
```
For convenience, endpoint uris can be specified as space separated uri segments 
without the scheme. Here are some of the available endpoints in that format:
```
system turnOff
system.launcher open -p '{"target": <url>}'
system.notifications createToast -p '{"message": <message>}'
audio setMute -p '{"mute": <muted>}'
audio getStatus
audio getVolume
audio setVolume -p '{"volume": <level>}'
audio volumeUp
audio volumeDown
media.controls play
media.controls stop
media.controls pause
media.controls rewind
media.controls fastForward
tv channelUp
tv channelDown
tv openChannel -p '{"channelId": <channel>}'
tv getCurrentChannel
tv getChannelList
com.webos.service.tv.display set3DOn
com.webos.service.tv.display set3DOff
tv getExternalInputList
tv switchInput -p '{"inputId": <input_id>}'
com.webos.service.update getCurrentSWInformation
api getServiceList
com.webos.applicationManager listLaunchPoints
com.webos.applicationManager launch
system.launcher launch -p '{'id': <appid>}'
system.launcher close -p '{'id': <appid>}'
system.launcher launch -p '{"id": "youtube.leanback.v4", "params": {"contentTarget": url}}'
```

## Install

```
pip install -r requirements.txt
```

## Other libraries

There are many other libraries for communicating with LG WebOS TVs:

- [LGWebOSRemote](https://github.com/klattimer/LGWebOSRemote)
- [lgtv.js](https://github.com/msloth/lgtv.js)
- [lgtv2mqtt](https://github.com/hobbyquaker/lgtv2mqtt)
- [PyWebOSTV](https://github.com/supersaiyanmode/PyWebOSTV)
- [alexa-lgtv-remote](https://github.com/voydz/alexa-lgtv-remote)
- [harbour-lgremote-webos](https://github.com/CODeRUS/harbour-lgremote-webos)
