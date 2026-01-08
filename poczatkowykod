import sys
from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem
from PyQt5.QtGui import QBrush, QPen
from PyQt5.QtCore import Qt

# ===================== MODEL =====================
class Tank:
    def __init__(self, name, level):
        self.name = name
        self.level = level  # % napełnienia

class Process:
    def __init__(self):
        #poczatkowy poziom i zbioniki
        self.tanks = [Tank("T1", 70),Tank("T2", 50),Tank("T3", 40),Tank("T4", 30)]

# ===================== SCENA =====================
class PlantScene(QGraphicsScene):
    def __init__(self, process):
        super().__init__(0, 0, 1000, 500)
        self.p = process
        self.tank_pos = [(100, 250), (300, 300), (500, 350), (700, 400)]
        self.tank_w = 60
        self.tank_h = 120
        self.draw_all()

    def outlet(self, x, y):
        return x + self.tank_w, y

    def inlet(self, x, y):
        return x, y - 20

    def draw_all(self):
        self.draw_tanks()
        self.draw_pipes()

    def draw_pipes(self):
        pen = QPen(Qt.black, 4)
        for i in range(3):
            x1, y1 = self.tank_pos[i]
            x2, y2 = self.tank_pos[i + 1]
            sx, sy = self.outlet(x1, y1)
            ex, ey = self.inlet(x2, y2)
            self.addLine(sx, sy, sx, ey, pen)  # pionowa część
            self.addLine(sx, ey, ex, ey, pen)  # pozioma część

    def draw_tank(self, tank, x, y):
        # ramka zbiornika
        frame = QGraphicsRectItem(x, y - self.tank_h, self.tank_w, self.tank_h)
        frame.setPen(QPen(Qt.black, 2))
        self.addItem(frame)

        # ciecz
        h = max(0, tank.level * 1.2)
        liquid = QGraphicsRectItem(x, y - h, self.tank_w, h)
        liquid.setBrush(QBrush(Qt.blue))
        self.addItem(liquid)

        # tekst
        txt = QGraphicsTextItem(f"{tank.name}\n{tank.level:.0f}%")
        txt.setPos(x - 5, y + 5)
        self.addItem(txt)

    def draw_tanks(self):
        for tank, (x, y) in zip(self.p.tanks, self.tank_pos):
            self.draw_tank(tank, x, y)

# ===================== WIDOK =====================
class PlantView(QGraphicsView):
    def __init__(self, process):
        super().__init__()
        self.scene = PlantScene(process)
        self.setScene(self.scene)

# ===================== OKNO GŁÓWNE =====================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    process = Process()
    view = PlantView(process)
    view.resize(1050, 550)
    view.show()
    sys.exit(app.exec_())
