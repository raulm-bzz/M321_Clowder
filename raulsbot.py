import json
import random

class RaulsBot():
    def __init__(self, name):
        self.name = name
        self._bot = TemplateKitten(name)

    def request(self, data):
        payload = json.loads(data)
        action = payload['action']
        if action == 'START':
            return self._bot.start_round(payload)
        elif action == 'PLAY':
            return self._bot.play(payload)
        elif action == 'DRAW':
            return self._bot.add_card(payload['card'])
        elif action == 'INFORM':
            return self._bot.inform(payload['botname'], payload['event'], payload['data'])
        elif action == 'DEFUSE':
            return self._bot.handle_exploding_kitten(payload['decksize'])
        elif action == 'SEE_THE_FUTURE':
            return self._bot.see_the_future(payload['cards'])
        elif action == 'EXPLODE':
            return 'ACK'
        elif action == 'GAMEOVER':
            return 'ACK'
        return None

class TemplateKitten():
    def __init__(self, name):
        self.name = name
        self._hand = []
        self._future_cards = []
        self._deck_size = 0
        self._exploding_kittens_left = 1
        self._bots_alive = []
        self._initial_card_counts = {}

    def start_round(self, data):
        self._hand = []
        self._future_cards = []
        self._bots_alive = data['bots']
        for card in data['card_counts']:
            if card['name'] == 'EXPLODING_KITTEN':
                self._exploding_kittens_left = card['count']
            self._initial_card_counts[card['name']] = card['count']
        return 'ACK'

    def add_card(self, cardname):
        self._hand.append(cardname)
        return 'ACK'

    def inform(self, botname, action, cardname):
        if action == 'DRAW' and cardname == 'null':
            self._deck_size -= 1
        return 'ACK'

    def play(self, payload):
        self._deck_size = payload.get('deck', self._deck_size)
        self._bots_alive = payload.get('bots', self._bots_alive)

        danger_probability = self._exploding_kittens_left / max(1, self._deck_size)

        if not self._future_cards and self.has_card('SEE_THE_FUTURE') and danger_probability > 0.10:
            self._hand.remove('SEE_THE_FUTURE')
            return {'card': 'SEE_THE_FUTURE'}

        if self._future_cards:
            if self._future_cards[0] == 'EXPLODING_KITTEN':
                if not self.has_card('DEFUSE'):
                    if self.has_card('SKIP'):
                        self._hand.remove('SKIP')
                        return {'card': 'SKIP'}
                    elif self.has_card('SHUFFLE'):
                        self._hand.remove('SHUFFLE')
                        return {'card': 'SHUFFLE'}

        if danger_probability > 0.20 and self.has_card('SHUFFLE'):
            self._hand.remove('SHUFFLE')
            return {'card': 'SHUFFLE'}

        return {'card': 'NONE'}

    def handle_exploding_kitten(self, deck_size):
        self._exploding_kittens_left = max(0, self._exploding_kittens_left - 1)
        if len(self._bots_alive) <= 2:
            return 0
        return min(2, deck_size - 1)

    def see_the_future(self, top_three):
        self._future_cards = top_three
        return 'ACK'

    def has_card(self, name):
        return name in self._hand
