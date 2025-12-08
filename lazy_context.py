import argparse
import os

class Need(Exception):

    def __init__(self, key):
        self.key = key


class LazyContext:

    def __init__(self, providers):
        # dict: key -> Provider()
        self.providers = providers
        self.cache = {}

    def __getitem__(self, key):
        if key in self.cache:
            return self.cache[key]

        if key not in self.providers:
            raise KeyError(key)

        try:
            value = self.providers[key](self)
        except Need as e:
            # resolve dependency first
            self[e.key]
            # then retry this provider
            return self[key]

        self.cache[key] = value
        return value

class Provider:

    def __call__(self, context):
        raise NotImplementedError


class StringProvider(Provider):

    def __init__(self, envkey, prompt, default=None):
        self.envkey = envkey
        self.prompt = prompt
        self.default = default

    def __call__(self, context):
        value = os.getenv(self.envkey)
        if value:
            return value
        return input(self.prompt) or self.default


def main(argv=None):
    parser = argparse.ArgumentParser()
    args = parser.parse_args(argv)

    context = LazyContext({
        'username': StringProvider('USERNAME', 'Enter username: '),
    })

    print(context['username'])

if __name__ == '__main__':
    main()
