

class Party:
    def __init__(self, name, identifier, colour="GREY"):
        self._name = name
        self._identifier = identifier
        self._colour = colour
        self._seats = 0

    def add_seat(self):
        self._seats += 1

    def set_seats(self, num):
        self._seats = num

    def get_seats(self):
        return self._seats

    def get_name(self):
        return self._name

    def get_colour(self):
        return self._colour

    def get_id(self):
        return self._identifier

