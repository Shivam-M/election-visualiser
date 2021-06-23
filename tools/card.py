from tkinter import *


class Card(Label):
    def __init__(self, master, main, party):
        self._main = main
        self._party = party
        super().__init__(master, text=f'{party.get_name()} ({party.get_seats()})', font="Bahnschrift 8", fg=party.get_colour(), bg="#282828")

    def refresh(self):
        self.config(text=f'{self._party.get_name()} ({self._party.get_seats()})')

