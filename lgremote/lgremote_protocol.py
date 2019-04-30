import json
from websockets import WebSocketClientProtocol
from os.path import join, dirname

class LGRemoteProtocol(WebSocketClientProtocol):
    async def register(self, client_key=None):
        with open(join(dirname(__file__), 'register_request.json')) as f:
            request = json.load(f)
        
        if client_key:
            request['payload']['client-key'] = client_key

        await self.send(json.dumps(request))
        response = json.loads(await self.recv())

        if 'pairingType' in response.get('payload', {}):
            print("Please accept the pairing request on your TV")
            response = json.loads(await self.recv())
         
        if 'client-key' in response.get('payload', {}):
            client_key = response['payload']['client-key']
        
        return client_key
    
    async def request(self, uri, payload):
        request = {
            'type': 'request',
            'id': 0,
            'uri': uri,
            'payload': payload
        }
        await self.send(json.dumps(request))

    async def response(self):
        response = json.loads(await self.recv())

        if response['type'] == 'response':
            return response['payload']
        elif response['type'] == 'error':
            return response['error']
        else:
            # TODO: warn if unseen response type
            return response.get('payload', {})
