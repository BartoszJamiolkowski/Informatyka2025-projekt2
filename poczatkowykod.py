# -*- coding: utf-8 -*-
"""
Created on Sun Jan 11 02:12:42 2026

@author: PC
"""

import sys
from PyQt5.QtWidgets import ( QApplication, QGraphicsView, QGraphicsScene,QGraphicsRectItem, QGraphicsTextItem)
from PyQt5.QtGui import QBrush, QPen
from PyQt5.QtCore import Qt

class Zbiornik:
    def __init__(self, nazwa, poziom):
        self.nazwa = nazwa  # nazwa zbiornika
        self.poziom = poziom  # poziom napełnienia w %

class Proces:
    def __init__(self):
        self.zbiorniki = [Zbiornik("Z1", 70),Zbiornik("Z2", 50),Zbiornik("Z3", 40),Zbiornik("Z4", 30)]

class ScenaInstalacji(QGraphicsScene):
    def __init__(self, proces):
        super().__init__(0, 0, 1000, 500) #rozmiar pola 

        self.proces = proces

        self.pozycje_zbiornikow = [(100, 250),(300, 300),(500, 350),(700, 400)]

        #rozmiar zbironikow 
        self.szerokosc_zbiornika = 60
        self.wysokosc_zbiornika = 120

        self.rysuj_wszystko()


    # punkt wyjścia rury od zbiornika
    def wyjscie_rury(self, x, y):
        return x + self.szerokosc_zbiornika, y - 8


    # punkt wejścia rury do zbiornika
    def wejscie(self, x, y):
        return x, y - 20


    def rysuj_wszystko(self):
        self.rysuj_zbiorniki()
        self.rysuj_rury()


    def rysuj_rury(self):
        pioro = QPen(Qt.black, 4)

        for i in range(len(self.pozycje_zbiornikow) - 1):
            x1, y1 = self.pozycje_zbiornikow[i]
            x2, y2 = self.pozycje_zbiornikow[i + 1]

            start_x, start_y = self.wyjscie_rury(x1, y1)
            koniec_x, koniec_y = self.wejscie(x2, y2)

            punkt_posredni_x = start_x + 40

            self.addLine(start_x, start_y, punkt_posredni_x, start_y, pioro)
            self.addLine(punkt_posredni_x, start_y, punkt_posredni_x, koniec_y, pioro)
            self.addLine(punkt_posredni_x, koniec_y, koniec_x, koniec_y, pioro)


    def rysuj_zbiornik(self, zbiornik, x, y):
        ramka = QGraphicsRectItem(
            x,
            y - self.wysokosc_zbiornika,
            self.szerokosc_zbiornika,
            self.wysokosc_zbiornika
        )
        ramka.setPen(QPen(Qt.black, 2))
        self.addItem(ramka)

        wysokosc_cieczy = zbiornik.poziom * 1.2
        ciecz = QGraphicsRectItem(
            x,
            y - wysokosc_cieczy,
            self.szerokosc_zbiornika,
            wysokosc_cieczy
        )
        ciecz.setBrush(QBrush(Qt.blue))
        self.addItem(ciecz)

        opis = QGraphicsTextItem(f"{zbiornik.nazwa}\n{zbiornik.poziom}%")
        opis.setPos(x - 5, y + 5)
        self.addItem(opis)


    def rysuj_zbiorniki(self):
        for zbiornik, (x, y) in zip(self.proces.zbiorniki, self.pozycje_zbiornikow):
            self.rysuj_zbiornik(zbiornik, x, y)


class WidokInstalacji(QGraphicsView):
    def __init__(self, proces):
        super().__init__()
        self.setScene(ScenaInstalacji(proces))


if __name__ == "__main__":
    aplikacja = QApplication(sys.argv)

    proces = Proces()
    widok = WidokInstalacji(proces)

    widok.resize(1050, 550)
    widok.show()

    sys.exit(aplikacja.exec_())


