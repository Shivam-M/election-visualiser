

class Constituency:
    def __init__(self, name, winner=None):
        self._name = name
        self._winner = winner
        self._rankings = {}
        self._turnout = 0

    def transfer_votes(self, from_party, percentage, to_party):
        self._rankings[to_party.get_id()] += percentage * self._rankings[from_party.get_id()]
        self._rankings[from_party.get_id()] = (1 - percentage) * self._rankings[from_party.get_id()]
        self.sort_results()

    def sort_results(self):
        temp_rankings = sorted(self._rankings.items(), key=lambda x: x[1], reverse=True)
        self._rankings = {}
        for party_votes in temp_rankings:
            self._rankings[party_votes[0]] = party_votes[1]
        self._winner = list(self._rankings)[0]

    def set_results(self, labels, values):
        if len(labels) != len(values):
            raise Exception("Labels do not match values.")
        for label in labels:
            self._rankings[label] = int(values[labels.index(label)])
        self.sort_results()

    def get_winner(self):
        return self._winner

    def get_votes(self, party):
        for p in self._rankings:
            if p == party.get_id():
                return self._rankings[p]
        return 0

    def get_turnout(self):
        if self._turnout == 0:
            for party_votes in self._rankings:
                self._turnout += party_votes
        return self._turnout

    def get_name(self):
        return self._name

