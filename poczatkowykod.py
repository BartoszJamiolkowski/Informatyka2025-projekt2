import sys
from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsRectItem
from PyQt5.QtGui import QBrush, QPen
from PyQt5.QtCore import Qt, QTimer


# ===== KLASY LOGICZNE =====
class Zbiornik:
    def __init__(self, nazwa, poziom):
        self.nazwa = nazwa  # nazwa zbiornika
        self.poziom = poziom # poziom zbiornika (0-100)


class Proces:
    def __init__(self):
        # Inicjalizacja zbiorników: Z1, Z2, Z3, Z4
        self.zbiorniki = [
            Zbiornik("Z1", 80),
            Zbiornik("Z2", 60),
            Zbiornik("Z3", 0),
            Zbiornik("Z4", 0)
        ]


# ===== SCENA GRAFICZNA =====
class ScenaInstalacji(QGraphicsScene):
    def __init__(self, proces):
        super().__init__(0, 0, 1000, 600)

        self.proces = proces

        # Pozycje zbiorników (x, y dolnej krawędzi)
        self.pozycje_zbiornikow = [
            (100, 120),   # Z1
            (250, 260),   # Z2
            (420, 480),   # Z3
            (570, 480)    # Z4
        ]

        self.szerokosc_zbiornika = 100
        self.wysokosc_zbiornika = 120

        self.ciecze_items = []  # lista prostokątów wody

        self.rysuj_wszystko()

        # Timer animacji wody
        self.timer = QTimer()
        self.timer.timeout.connect(self.animuj_wode)
        self.timer.start(50)  # 50 ms = 20 FPS

    # ===== POMOCNICZE =====
    def wyjscie_rury(self, x, y):
        return x + self.szerokosc_zbiornika, y - 10

    def wejscie_od_gory(self, x, y):
        return x + self.szerokosc_zbiornika / 2, y - self.wysokosc_zbiornika

    def wejscie_z_boku_dol(self, x, y):
        return x, y - 20

    # ===== RYSOWANIE =====
    def rysuj_wszystko(self):
        self.rysuj_zbiorniki()
        self.rysuj_rury()

    # ===== RURY =====
    def rura_boczna_dol(self, i1, i2, pioro):
        x1, y1 = self.pozycje_zbiornikow[i1]
        x2, y2 = self.pozycje_zbiornikow[i2]

        sx, sy = self.wyjscie_rury(x1, y1)
        ex, ey = self.wejscie_z_boku_dol(x2, y2)
        mx = (sx + ex) / 2

        self.addLine(sx, sy, mx, sy, pioro)
        self.addLine(mx, sy, mx, ey, pioro)
        self.addLine(mx, ey, ex, ey, pioro)

    def rysuj_rure_schodkowa(self, i1, i2, pioro):
        x1, y1 = self.pozycje_zbiornikow[i1]
        x2, y2 = self.pozycje_zbiornikow[i2]

        sx, sy = self.wyjscie_rury(x1, y1)
        ex, ey = self.wejscie_od_gory(x2, y2)
        mx = sx + 20

        self.addLine(sx, sy, mx, sy, pioro)
        self.addLine(mx, sy, mx, ey - 20, pioro)
        self.addLine(mx, ey - 20, ex, ey - 20, pioro)
        self.addLine(ex, ey - 20, ex, ey, pioro)

    def rysuj_rury(self):
        pioro = QPen(Qt.black, 4)

        # Z1 -> Z2 (boczna dół)
        self.rura_boczna_dol(0, 1, pioro)

        # Z2 -> rozgałęzienie w prawo do Z3 i Z4
        x2, y2 = self.pozycje_zbiornikow[1]
        sx, sy = self.wyjscie_rury(x2, y2)
        px, py = sx + 200, sy
        self.addLine(sx, sy, px, py, pioro)

        # Z3
        x3, y3 = self.pozycje_zbiornikow[2]
        ex3, ey3 = self.wejscie_od_gory(x3, y3)
        self.addLine(px, py, px, ey3 - 20, pioro)
        self.addLine(px, ey3 - 20, ex3, ey3 - 20, pioro)
        self.addLine(ex3, ey3 - 20, ex3, ey3, pioro)

        # Z4
        x4, y4 = self.pozycje_zbiornikow[3]
        ex4, ey4 = self.wejscie_od_gory(x4, y4)
        self.addLine(px, py, px, ey4 - 20, pioro)
        self.addLine(px, ey4 - 20, ex4, ey4 - 20, pioro)
        self.addLine(ex4, ey4 - 20, ex4, ey4, pioro)

    # ===== ZBIORNIKI =====
    def rysuj_zbiornik(self, zbiornik, x, y):
        # Ramka zbiornika
        ramka = QGraphicsRectItem(x, y - self.wysokosc_zbiornika, self.szerokosc_zbiornika, self.wysokosc_zbiornika)
        ramka.setPen(QPen(Qt.black, 2))
        self.addItem(ramka)

        # Ciecz wewnątrz zbiornika
        wysokosc_cieczy = zbiornik.poziom * 1.2
        ciecz = QGraphicsRectItem(x, y - wysokosc_cieczy, self.szerokosc_zbiornika, wysokosc_cieczy)
        ciecz.setBrush(QBrush(Qt.blue))
        self.addItem(ciecz)

        self.ciecze_items.append((zbiornik, ciecz, y))

    def rysuj_zbiorniki(self):
        for zbiornik, (x, y) in zip(self.proces.zbiorniki, self.pozycje_zbiornikow):
            self.rysuj_zbiornik(zbiornik, x, y)

    # ===== ANIMACJA WODY =====
    def animuj_wode(self):
        zbiorniki = self.proces.zbiorniki

        # Prosty przepływ Z1 -> Z2
        if zbiorniki[0].poziom > 0 and zbiorniki[1].poziom < 100:
            przeplyw = min(1, zbiorniki[0].poziom)
            zbiorniki[0].poziom -= przeplyw
            zbiorniki[1].poziom += przeplyw

        # Z2 -> Z3 i Z4 po połowie
        if zbiorniki[1].poziom > 0:
            przeplyw = min(0.5, zbiorniki[1].poziom)
            zbiorniki[1].poziom -= 2 * przeplyw
            zbiorniki[2].poziom += przeplyw
            zbiorniki[3].poziom += przeplyw

        # Aktualizacja prostokątów wody
        for zbiornik, ciecz, y in self.ciecze_items:
            wysokosc_cieczy = zbiornik.poziom * 1.2
            ciecz.setRect(ciecz.rect().x(), y - wysokosc_cieczy, ciecz.rect().width(), wysokosc_cieczy)


# ===== WIDOK =====
class WidokInstalacji(QGraphicsView):
    def __init__(self, proces):
        super().__init__()
        self.setScene(ScenaInstalacji(proces))


# ===== PROGRAM GŁÓWNY =====
if __name__ == "__main__":
    app = QApplication(sys.argv)

    proces = Proces()
    widok = WidokInstalacji(proces)

    widok.resize(1050, 650)
    widok.show()

    sys.exit(app.exec_())

