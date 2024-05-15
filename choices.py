import argparse

class Request:

    def __init__(self, name, content=None, choices=None):
        self.name = name
        self.content = content
        if choices is None:
            choices = set()
        self.choices = choices


class Game:

    def __init__(self):
        self.g = {}
        self.endpoints = {}

    def endpoint(self, name):
        def handler(func):
            self.endpoints[name] = func
        return handler

    def __call__(self, request):
        handler = self.endpoints[request.name]
        return handler(request)


class Client:
    """
    Handle responses from game/server and take input from user/player.
    """

    def __init__(self, prompt=None):
        if prompt is None:
            prompt = '> '
        self.prompt = prompt

    def __call__(self, response, prompt=None):
        if response.content:
            print(response.content)
        answer = input(prompt or self.prompt)
        if answer in response.choices:
            request = Request(
                name = response.choices[answer],
            )
            return request
        else:
            # request ourself again
            return response


# - thinking here is to make this a lot like a web app only we have to
#   implement the client/browser
# - so we'll just use the console and `input`
# - client will need to parse or accept some object as a response
# - server/game will need to parse or accept some object as a request

game = Game()

@game.endpoint('/start')
def start(request):
    raise NotImplementedError

@game.endpoint('/')
def init(request):
    choices = {
        '1': '1. start',
        '2': '2. resume',
    }
    # response is what the client will take and then send another request
    request = Request(
        name = '/',
        choices = choices,
        content = '\n'.join(choices.values()),
    )
    return request

def main(argv=None):
    parser = argparse.ArgumentParser()
    args = parser.parse_args(argv)

    client = Client()
    request = Request(name='/')
    while True:
        response = game(request)
        request = client(response)

if __name__ == '__main__':
    main()
