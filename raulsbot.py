import json
import random

class RaulsBot():
    def __init__(self, name):
        self.name = name
        self._bot = TemplateKitten(name)

    def request(self, data):
        payload = json.loads(data)
        action = payload['action']
        if action == 'START ':
            return self._bot.start_round(payload)
        elif action == 'PLAY':
            return self._bot.play()
        elif action == 'DRAW':
            return self._bot.add_card(payload['card'])
        elif action == 'INFORM':
            return self._bot.inform(payload['botname'], payload['event'], payload['data'])
        elif action == 'DEFUSE':
            return self._bot.handle_exploding_kitten(payload['decksize'])
        elif action == 'FUTURE':
            return self._bot.see_the_future(payload['cards'])
        return None

class TemplateKitten():
    def __init__(self, name):
        self.name = name
        self._hand = []
        self._future_cards = []

    def start_round(self, data):
        self._hand = []
        self._future_cards = []

    def add_card(self, cardname):
        self._hand.append(cardname)

    def inform(self, botname, action, response):
        pass

    def has_card(self, cardname):
        return cardname in self._hand

    def play(self):
        if self._future_cards:
            if self._future_cards[0] == "Exploding Kitten":
                if not self.has_card("DEFUSE"):
                    if self.has_card("Skip"):
                        self._hand.remove("Skip")
                        return "Skip"
                    elif self.has_card("Shuffle"):
                        self._hand.remove("Shuffle")
                        return "Shuffle"
        if not self._future_cards and self.has_card("See the Future"):
            self._hand.remove("See the Future")
            return "See the Future"
        if not self._future_cards and self.has_card("Shuffle"):
            self._hand.remove("Shuffle")
            return "Shuffle"
        return None

    def handle_exploding_kitten(self, deck_size):
        if deck_size <= 2:
            return 0  # ganz oben
        return random.randint(0, min(2, deck_size - 1))

    def see_the_future(self, top_three):
        self._future_cards = top_three
