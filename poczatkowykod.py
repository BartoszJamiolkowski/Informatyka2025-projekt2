import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QStackedWidget
from PyQt5.QtCore import Qt, QTimer, QPointF
from PyQt5.QtGui import QPainter, QColor, QPen, QPainterPath

# ===================== RURA =====================
class Rura:
    def __init__(self, punkty, grubosc=8, kolor=Qt.black):
        self.punkty = [QPointF(float(p[0]), float(p[1])) for p in punkty]
        self.grubosc = grubosc
        self.kolor_rury = kolor
        self.kolor_cieczy = QColor(0, 180, 255)
        self.czy_plynie = False

    def ustaw_przeplyw(self, plynie):
        self.czy_plynie = plynie

    def draw(self, painter):
        if len(self.punkty) < 2: return
        path = QPainterPath()
        path.moveTo(self.punkty[0])
        for p in self.punkty[1:]: path.lineTo(p)

        pen_rura = QPen(self.kolor_rury, self.grubosc, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        painter.setPen(pen_rura)
        painter.drawPath(path)

        if self.czy_plynie:
            pen_ciecz = QPen(self.kolor_cieczy, self.grubosc - 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
            painter.setPen(pen_ciecz)
            painter.drawPath(path)

# ===================== ZBIORNIK =====================
class Zbiornik:
    def __init__(self, x, y, width=100, height=140, nazwa=""):
        self.x, self.y, self.width, self.height, self.nazwa = x, y, width, height, nazwa
        self.pojemnosc, self.aktualna_ilosc, self.poziom = 100.0, 0.0, 0.0

    def dodaj_ciecz(self, ilosc):
        wolne = self.pojemnosc - self.aktualna_ilosc
        dodano = min(ilosc, wolne)
        self.aktualna_ilosc += dodano
        self.aktualizuj_poziom()
        return dodano

    def usun_ciecz(self, ilosc):
        usunieto = min(ilosc, self.aktualna_ilosc)
        self.aktualna_ilosc -= usunieto
        self.aktualizuj_poziom()
        return usunieto

    def aktualizuj_poziom(self):
        self.poziom = self.aktualna_ilosc / self.pojemnosc

    def czy_pusty(self): return self.aktualna_ilosc <= 0.01
    def czy_pelny(self): return self.aktualna_ilosc >= self.pojemnosc - 0.01

    def punkt_gora_srodek(self): return (self.x + self.width / 2, self.y)
    def punkt_dol_srodek(self): return (self.x + self.width / 2, self.y + self.height)
    def punkt_gora_wejscie(self): return (self.x + self.width * 0.8, self.y)

    def draw(self, painter):
        if self.poziom > 0:
            h_cieczy = self.height * self.poziom
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(0, 120, 255, 200))
            painter.drawRect(int(self.x + 3), int(self.y + self.height - h_cieczy), int(self.width - 6), int(h_cieczy - 2))
        pen = QPen(Qt.black, 4)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(int(self.x), int(self.y), int(self.width), int(self.height))
        painter.setPen(Qt.black)
        painter.drawText(int(self.x), int(self.y - 10), self.nazwa)

# ===================== WIDOK SYMULACJI =====================
class WidokSymulacji(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.main_app = parent
        self.z1 = Zbiornik(100, 120, nazwa="Zbiornik 1")
        self.z2 = Zbiornik(250, 260, nazwa="Zbiornik 2")
        self.z3 = Zbiornik(420, 480, nazwa="Zbiornik 3")
        self.z4 = Zbiornik(570, 480, nazwa="Zbiornik 4")
        self.z1.aktualna_ilosc = 100.0
        self.z2.aktualna_ilosc = 0.0
        self.z3.aktualna_ilosc = 30.0
        self.z4.aktualna_ilosc = 20.0
        
        self.zbiorniki = [self.z1, self.z2, self.z3, self.z4]
        for z in self.zbiorniki: z.aktualizuj_poziom()

        self.tryb_powrotu = False
        self.odblokowany_odplyw_z2 = False

        # Rury
        p1_start, p1_end = self.z1.punkt_dol_srodek(), self.z2.punkt_gora_srodek()
        self.rura1 = Rura([p1_start, (p1_start[0], (p1_start[1]+p1_end[1])/2), (p1_end[0], (p1_start[1]+p1_end[1])/2), p1_end])
        p2_start = self.z2.punkt_dol_srodek()
        self.rura2 = Rura([p2_start, (p2_start[0], 440), (self.z3.punkt_gora_srodek()[0], 440), self.z3.punkt_gora_srodek()])
        self.rura3 = Rura([p2_start, (p2_start[0], 440), (self.z4.punkt_gora_srodek()[0], 440), self.z4.punkt_gora_srodek()])
        
        # Powrót
        b_y, r_x, t_y, p_in = 720, 900, 60, self.z1.punkt_gora_wejscie()
        self.rura_powrot_z4 = Rura([self.z4.punkt_dol_srodek(), (self.z4.punkt_dol_srodek()[0], b_y), (r_x, b_y), (r_x, t_y), (p_in[0], t_y), p_in])
        self.rura_powrot_z3 = Rura([self.z3.punkt_dol_srodek(), (self.z3.punkt_dol_srodek()[0], b_y), (self.z4.punkt_dol_srodek()[0], b_y)])
        self.rury = [self.rura1, self.rura2, self.rura3, self.rura_powrot_z4, self.rura_powrot_z3]

        self.flow_speed = 0.8
        self.pump_speed = 0.2 # WOLNIEJSZE WYPOMPOWYWANIE
        self.slow_flow = 0.1

        self.timer = QTimer()
        self.timer.timeout.connect(self.logika)
        self.timer.start(20)

        # Przycisk Raportu
        self.btn_raport = QPushButton("RAPORT", self)
        self.btn_raport.setGeometry(500, 740, 200, 40)
        self.btn_raport.clicked.connect(lambda: self.main_app.setCurrentIndex(1))

    def logika(self):
        if self.z3.aktualna_ilosc >= 70.0 and self.z4.aktualna_ilosc >= 70.0:
            self.tryb_powrotu = True
            self.odblokowany_odplyw_z2 = True
        if self.tryb_powrotu and self.z1.aktualna_ilosc >= 50.0: # Stop przy 50%
            self.tryb_powrotu = False
            self.odblokowany_odplyw_z2 = False

        p1 = p2 = p3 = p_powrot = False
        if self.tryb_powrotu:
            if not self.z1.czy_pelny():
                v3 = self.z3.usun_ciecz(self.pump_speed * 0.5)
                v4 = self.z4.usun_ciecz(self.pump_speed * 0.5)
                self.z1.dodaj_ciecz(v3 + v4)
                p_powrot = True
            if self.z2.aktualna_ilosc > 0.05:
                il = min(self.slow_flow, self.z2.aktualna_ilosc)
                s = (self.z3.pojemnosc - self.z3.aktualna_ilosc) + (self.z4.pojemnosc - self.z4.aktualna_ilosc)
                if s > 0:
                    self.z2.usun_ciecz(il)
                    self.z3.dodaj_ciecz(il * ((self.z3.pojemnosc - self.z3.aktualna_ilosc)/s))
                    self.z4.dodaj_ciecz(il * ((self.z4.pojemnosc - self.z4.aktualna_ilosc)/s))
                    p2 = p3 = True
        else:
            if not self.z1.czy_pusty() and not self.z2.czy_pelny():
                self.z2.dodaj_ciecz(self.z1.usun_ciecz(self.flow_speed))
                p1 = True
            if self.z2.aktualna_ilosc >= 20.0: self.odblokowany_odplyw_z2 = True
            if self.odblokowany_odplyw_z2 and self.z2.aktualna_ilosc > 0.05:
                il = min(self.flow_speed, self.z2.aktualna_ilosc)
                s = (self.z3.pojemnosc - self.z3.aktualna_ilosc) + (self.z4.pojemnosc - self.z4.aktualna_ilosc)
                if s > 0:
                    self.z2.usun_ciecz(il)
                    self.z3.dodaj_ciecz(il * ((self.z3.pojemnosc - self.z3.aktualna_ilosc)/s))
                    self.z4.dodaj_ciecz(il * ((self.z4.pojemnosc - self.z4.aktualna_ilosc)/s))
                    p2 = p3 = True
            elif self.z2.aktualna_ilosc <= 0.05: self.odblokowany_odplyw_z2 = False

        self.rura1.ustaw_przeplyw(p1); self.rura2.ustaw_przeplyw(p2); self.rura3.ustaw_przeplyw(p3)
        self.rura_powrot_z3.ustaw_przeplyw(p_powrot); self.rura_powrot_z4.ustaw_przeplyw(p_powrot)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        for r in self.rury: r.draw(painter)
        for z in self.zbiorniki: z.draw(painter)

# ===================== STRONA RAPORTU =====================
class StronaRaportu(QWidget):
    def __init__(self, parent, symulacja):
        super().__init__()
        self.main_app = parent
        self.sym = symulacja
        self.layout = QVBoxLayout()
        self.labels = []

        self.title = QLabel("RAPORT NAPEŁNIENIA ZBIORNIKÓW")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        self.layout.addWidget(self.title)

        for z in self.sym.zbiorniki:
            lbl = QLabel(f"{z.nazwa}: 0%")
            lbl.setStyleSheet("font-size: 18px; margin: 10px;")
            self.layout.addWidget(lbl)
            self.labels.append((z, lbl))

        self.btn_powrot = QPushButton("POWRÓT DO SYMULACJI")
        self.btn_powrot.setFixedSize(250, 50)
        self.btn_powrot.clicked.connect(lambda: self.main_app.setCurrentIndex(0))
        self.layout.addWidget(self.btn_powrot, alignment=Qt.AlignCenter)
        self.setLayout(self.layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.aktualizuj)
        self.timer.start(100)

    def aktualizuj(self):
        for z, lbl in self.labels:
            lbl.setText(f"{z.nazwa}: {int(z.poziom * 100)}%")

# ===================== GŁÓWNA APLIKACJA =====================
class AplikacjaKaskada(QStackedWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Symulacja Kaskady z Raportem")
        self.setFixedSize(1200, 800)
        self.setStyleSheet("background-color: white;")
        
        self.widok_sym = WidokSymulacji(self)
        self.widok_raport = StronaRaportu(self, self.widok_sym)
        
        self.addWidget(self.widok_sym)
        self.addWidget(self.widok_raport)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AplikacjaKaskada()
    window.show()
    sys.exit(app.exec_())
