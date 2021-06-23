from tkinter import *
from tools.constituency import Constituency
from tools.party import Party
from tools.card import Card
from contextlib import suppress
import csv

DATA_FILE_PATH = 'data/elec15.csv'
BACKGROUND = '#383838'
LIST_COLOUR = '#BDC3C7'


class Visualiser:
    def __init__(self):
        self.window = Tk()
        self.window.geometry("1280x720")
        self.window.config(bg=BACKGROUND)
        self.window.title(f"Election Visualiser: {DATA_FILE_PATH}")

        self.total_votes = {}
        self.constituencies = []
        self.current_listings = []
        self.current_card = None
        self.share_percentage = 0.30
        self.share_party = None

        self.unmapped_parties = [
            Party('Conservative',       'con',          '#3498DB'),
            Party('Labour',             'lab',          '#E74C3C'),
            Party('Liberal Democrats',  'ld',           '#F39C12'),
            Party('Green',              'green',        '#2ECC71'),
            Party('Brexit',             'brexit',       '#1ABC9C'),
            Party('SNP',                'snp',          '#F1C40F'),
            Party('Plaid Cymru',        'pc',           '#27AE60'),
            Party('DUP',                'dup',          '#BDC3C7'),
            Party('Sinn Fein',          'sf',           '#16A085'),
            Party('SDLP',               'sdlp',         '#00B894'),
            Party('UUP',                'uup',          '#95A5A6'),
            Party('Alliance',           'alliance',     '#E67E22'),
            Party('Unknown',            'unknown',      'GREY'),
            Party('Other',              'other',        'GREY'),
            Party('UKIP',               'ukip',         '#9B59B6'),
            Party('Other Party',        'other_party',  'GREY'),
        ]

        self.parties = {}
        self.cards = {}

        for party in self.unmapped_parties:
            self.parties[party.get_id()] = party
            self.total_votes[party.get_id()] = 0
            self.cards[party.get_id()] = Card(self.window, self, party)

        self.constituencies_text = Text(self.window, width=40, height=25, font="Bahnschrift 10", bd=2, bg=BACKGROUND, relief="ridge")
        self.constituencies_text.place(relx=.52, rely=.34)

        self.parse()
        self.total = sum(self.total_votes[a] for a in self.total_votes)
        print(f"Total votes: {self.total:,}")

        self.turnout_label = Label(self.window, text="TURNOUT", font='Bahnschrift 42 bold', fg=BACKGROUND, bg="#ECF0F1", width=13)
        self.turnout_label.place(relx=.055, rely=.2)
        self.total_label = Label(self.window, text="{:,}".format(self.total), font='Bahnschrift 42 bold', fg=BACKGROUND, bg="#ECF0F1", width=15)
        self.total_label.place(relx=.375, rely=.2)
        self.select_inf = Label(self.window, text="Choose a party to highlight by clicking its name on the list to the right. This \nallows you to view the share of the total vote and seats won by the party."
                                                  "\nUse the slider at the bottom to transfer a percentage of votes from one \nparty to another - use the arrow to view the projected seats for all parties.",
                                bg=BACKGROUND, fg="#ECF0F1", font="Bahnschrift 13 bold", justify=LEFT)
        self.select_inf.place(relx=.053, rely=.325)

        for vote in self.total_votes:
            print(f"{vote}: {(self.total_votes[vote] / self.total) * 100:.2f}", end="\t")

        self.create()
        for party in self.unmapped_parties:
            self.cards[party.get_id()] = Card(self.window, self, party)

        del self.unmapped_parties

        self.show_details(self.parties[list(self.parties)[0]])
        self.draw_parties()
        self.window.mainloop()

    def parse(self):
        with open(DATA_FILE_PATH) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=",")
            row_labels = None
            for row in csv_reader:
                if row_labels is None:
                    row_labels = row
                    for column in row_labels:
                        if column in self.parties:
                            start_index = row_labels.index(column)
                            break
                else:
                    constituency = Constituency(row[2])
                    constituency.set_results(row_labels[start_index:len(row_labels)], row[start_index:len(row)])
                    self.constituencies.append(constituency)
                    self.constituencies_text.tag_config(self.parties[constituency.get_winner()].get_colour(), background=BACKGROUND, foreground=self.parties[constituency.get_winner()].get_colour(), underline=0)
                    self.constituencies_text.insert(END, f"{constituency.get_name()} ({self.parties[constituency.get_winner()].get_id().upper()})\n", self.parties[constituency.get_winner()].get_colour())

        for constituency in self.constituencies:
            self.parties[constituency.get_winner()].add_seat()
            for party in self.parties:
                self.total_votes[party] += constituency.get_votes(self.parties[party])

        self.temp_parties = sorted(self.parties.items(), key=lambda x: x[1].get_seats(), reverse=True)
        self.parties = {}

        for party in self.temp_parties:
            self.parties[party[0]] = party[1]

    def transfer(self, from_party, percentage, to_party):
        if from_party == to_party:
            return

        for constituency in self.constituencies:
            constituency.transfer_votes(from_party, percentage, to_party)

        for party_id in self.parties:
            party = self.parties[party_id]
            party.set_seats(0)
            self.total_votes[party.get_id()] = 0

        for constituency in self.constituencies:
            self.parties[constituency.get_winner()].add_seat()
            for party in self.parties:
                self.total_votes[party] += constituency.get_votes(self.parties[party])

        self.temp_parties = sorted(self.parties.items(), key=lambda x: x[1].get_seats(), reverse=True)
        self.parties = {}

        for party in self.temp_parties:
            self.parties[party[0]] = party[1]

        self.refresh()
        self.show_details(self.share_party, self.share_percentage, to_party)

    def create(self):
        SCALE = 0.75
        total_seats = len(self.constituencies)
        x = 0.055
        incrementer = 0.01
        # incrementer = ((1 - (x * 2)) / total_seats)

        for identifier in self.parties:
            party = self.parties[identifier]
            w = int(SCALE * (party.get_seats() / total_seats) * 1280)
            f = Frame(self.window, width=w, bg=party.get_colour(), height=50)
            f.place(relx=x, rely=.1)
            f.name = party.get_id()
            self.window.bind("<Motion>", lambda event: self.current_widget())
            self.window.bind("<Button-1>", lambda event: self.click_widget())
            if w / 1280 >= (0.1 / (11 / len(party.get_name()))):
                n = Label(f, text=party.get_name().upper(), font="Bahnschrift 10 bold", bg=party.get_colour(), fg=BACKGROUND)
                n.name = party.get_id()
                n.place(x=4, y=1)
            if w / 1280 >= 0.03:
                s = Label(f, text=party.get_seats(), font="Bahnschrift 10 bold", fg=party.get_colour(), bg=BACKGROUND)
                s.name = party.get_id()
                s.place(x=6, y=24)
            x += w / 1280 + incrementer
            self.current_listings.append(f)

    def draw_parties(self):
        x = 0.762
        y = 0.200
        for p in self.parties:
            party = self.parties[p]
            Button(self.window, bg=party.get_colour() if not LIST_COLOUR else LIST_COLOUR, bd=0, text=f'{party.get_name()} ({party.get_seats()})',
                   fg=BACKGROUND, width=25, font="Bahnschrift 12 bold",
                   command=lambda selected_party=party: self.show_details(selected_party)).place(relx=x, rely=y)
            y += 0.050

    def current_widget(self):
        x, y = self.window.winfo_pointerxy()
        widget = self.window.winfo_containing(x, y)
        x -= self.window.winfo_rootx()
        y -= self.window.winfo_rooty()
        with suppress(Exception):
            for card in self.cards:
                self.cards[card].place_forget()
            self.cards[widget.name].place(x=x + 15, y=y + 15)

    def click_widget(self):
        with suppress(Exception):
            x, y = self.window.winfo_pointerxy()
            widget = self.window.winfo_containing(x, y)
            x -= self.window.winfo_rootx()
            y -= self.window.winfo_rooty()
            party_id = widget.name
            print(self.parties[party_id].get_name())
            print("Vote share:", round((self.total_votes[party_id] / self.total) * 100, 2))
            print("Seat share:", round((self.parties[party_id].get_seats() / 650) * 100, 2), "\n")

    def show_details(self, party, share=0.3, to=None):
        wd = 1150
        party_transfer = StringVar()

        self.share_party = party
        to = self.parties["lab"] if not to else to

        frame = Frame(self.window, bg=party.get_colour(), width=wd / 2, height=300)
        frame.place(x=((1280-wd) / 2) + 6, y=350)
        Label(frame, text=party.get_name(), font="Bahnschrift 36 bold", fg=party.get_colour(), bg=BACKGROUND, width=19).place(relx=.05, rely=.04)
        Label(frame, text=party.get_seats(), font="Bahnschrift 42 bold", fg=party.get_colour(), bg=BACKGROUND, width=5).place(relx=.675, rely=.69)
        Label(frame, text="S H A R E   O F   V O T E", font="Bahnschrift 20 bold", bg=party.get_colour(), fg=BACKGROUND).place(relx=.045, rely=.3)
        Label(frame, text=f'{(self.total_votes[party.get_id()] / self.total) * 100:.2f}%', font="Bahnschrift 22", fg=party.get_colour(), bg=BACKGROUND, width=8).place(relx=.72, rely=.3)
        Label(frame, text="S H A R E   O F   S E A T S", font="Bahnschrift 20 bold", bg=party.get_colour(), fg=BACKGROUND).place(relx=.045, rely=.45)
        Label(frame, text=f'{(party.get_seats() / 650) * 100:.2f}%', font="Bahnschrift 22", fg=party.get_colour(), bg=BACKGROUND, width=8).place(relx=.72, rely=.45)
        Label(frame, text="T R A N S F E R   V O T E S", font="Bahnschrift 14 bold", bg=party.get_colour(), fg=BACKGROUND).place(relx=.045, rely=.59)
        Label(frame, text="P A R T Y", width=10, font="Bahnschrift 13 bold", fg=party.get_colour(), bg=BACKGROUND).place(relx=.05, rely=.8425)

        party_names = [self.parties[x].get_name() for x in self.parties]
        party_names.remove(to.get_name())

        party_list = OptionMenu(frame, party_transfer, to.get_name(), *party_names)
        party_list.config(width=17, bg=BACKGROUND, fg=party.get_colour(), font="Bahnschrift 12", bd=0)
        party_list.place(relx=.2275, rely=.8434)
        party_list["borderwidth"] = 0
        party_list["highlightthickness"] = 0

        party_transfer.set(to.get_name())

        COLOUR_HL = "#ECF0F1"
        COLOUR_BG = "#383838"
        COLOUR_FG = party.get_colour()

        self.s_len = Scale(frame, bg=COLOUR_BG, activebackground=COLOUR_HL, fg=COLOUR_BG, font='Bahnschrift 12 bold', bd=0,
                           highlightbackground=COLOUR_BG, highlightcolor=COLOUR_HL, orient=HORIZONTAL, sliderlength=24,
                           width=10, sliderrelief=FLAT, troughcolor=COLOUR_FG, length=350)
        self.s_len.bind('<Motion>', lambda event: self.update_text())
        self.s_len.set((share * 100))
        self.s_len.place(relx=.05, rely=.69)
        self.l_len = Label(frame, bg=COLOUR_BG, fg=COLOUR_FG, font='Bahnschrift 10 bold', width=7, text='30%')
        self.l_len.place(relx=.054, rely=.70)

        Button(frame, text="➝", width=5, bg=BACKGROUND, fg=party.get_colour(), font='Bahnschrift 12 bold',
               command=lambda: (self.transfer(party, int(self.s_len.get()) / 100, self.get_party(party_transfer.get()))), bd=0).place(relx=.574, rely=.84)

    def update_text(self):
        self.l_len.config(text=f'{self.s_len.get()}%')
        self.share_percentage = self.s_len.get() / 100

    def get_party(self, name):
        for p in self.parties:
            if self.parties[p].get_name() == name:
                return self.parties[p]

    def refresh(self):
        for listing in self.current_listings:
            listing.place_forget()
            
        print("\n")
        self.current_listings = []
        for vote in self.total_votes:
            print(f"{vote}: {(self.total_votes[vote] / self.total) * 100:.2f}", end="\t")

        self.create()
        self.draw_parties()
        self.constituencies_text.delete(0.0, END)

        for card in self.cards:
            self.cards[card].refresh()

        for constituency in self.constituencies:
            self.constituencies_text.tag_config(self.parties[constituency.get_winner()].get_colour(), foreground=BACKGROUND, background=self.parties[constituency.get_winner()].get_colour(), underline=0)
            self.constituencies_text.insert(END, f"{constituency.get_name()} ({self.parties[constituency.get_winner()].get_id().upper()})\n", self.parties[constituency.get_winner()].get_colour())


v = Visualiser()
