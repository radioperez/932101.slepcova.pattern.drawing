import sys
from PyQt6.QtCore import Qt, QSize, QPoint
from PyQt6.QtWidgets import ( 
    QApplication,
    QMainWindow,
    QWidget,
    QLabel,
    QToolBar,
    QColorDialog,
)
from PyQt6.QtGui import (
    QAction,
    QIcon,
    QPixmap,
    QPainter,
    QPen,
    QColor,
)

class Memento:
    def __init__(self, state):
        self.state = state

class Canvas:
    def __init__(self, width, height):
        self.state = QPixmap(width, height)
        self.state.fill(QColor("white"))
    def save_state(self):
        return Memento(self.state.copy())
    def restore_state(self, memento: 'Memento'):
        self.state = memento.state.copy()

class Caretaker:
    HISTORY_LEN = 20
    def __init__(self):
        self.history = []
    def add(self, memento):
        if len(self.history) == self.HISTORY_LEN: self.history = self.history[1:]
        self.history.append(memento)
    def get_last(self):
        return self.history.pop()

class Canvas_widget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFixedSize(680, 480)
        self.canvas = Canvas(500,500)
        self.caretaker = Caretaker()
        
        self.last_pos = None
        self.painter = QPainter()
        self.pen = QPen(QColor("black"),1)
        self.eraser = QPen(QColor("white"),1)
    def paintEvent(self, e):
        with QPainter(self) as painter:
            painter.drawPixmap(0,0,self.canvas.state)
    def mousePressEvent(self, e):
        savestate = self.canvas.save_state()
        self.caretaker.add(savestate)

        self.last_pos = e.pos()
        QWidget.mousePressEvent(self, e)
    def mouseMoveEvent(self, e):
        self.painter.begin(self.canvas.state)
        if e.buttons() == Qt.MouseButton.RightButton:
            self.painter.setPen(self.eraser)
        elif e.buttons() == Qt.MouseButton.LeftButton:
            self.painter.setPen(self.pen)
        self.painter.drawLine(self.last_pos, e.pos())
        self.painter.end()

        self.last_pos = e.pos()
        self.update()
        QWidget.mouseMoveEvent(self, e)
    def mouseReleaseEvent(self, e):
        self.last_pos = None
        QWidget.mouseReleaseEvent(self,e)

class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        self.setGeometry(100, 100, 800, 600)

        self.setWindowTitle("Drawing app")

        # Toolbar
        toolbar = QToolBar("Tools")
        self.addToolBar(toolbar)
        undo = QAction("Undo", self)
        toolbar.addAction(undo)
        self.get_color = QAction("Color #000000", self)
        self.color = QColor("black")
        toolbar.addAction(self.get_color)
        self.show_size = QAction("Size 1", self)
        inc_size = QAction("+", self)
        dec_size = QAction("-", self)
        self.pen_size = 1
        toolbar.addAction(self.show_size)
        toolbar.addAction(inc_size)
        toolbar.addAction(dec_size)

        # Canvas
        self.canvas_widget = Canvas_widget()
        undo.triggered.connect(self.undo)
        self.get_color.triggered.connect(self.set_color)
        inc_size.triggered.connect(self.inc_size)
        dec_size.triggered.connect(self.dec_size)

        self.setCentralWidget(self.canvas_widget)
    def undo(self):
        savestate = self.canvas_widget.caretaker.get_last()
        if savestate: 
            self.canvas_widget.canvas.restore_state(savestate)
            self.canvas_widget.update()

    def set_color(self):
        color = QColorDialog.getColor(self.color, self)
        if color:
            self.color = color
            self.canvas_widget.pen.setColor(color)
            self.get_color.setText("Color "+QColor(self.color).name())
    def inc_size(self):
        self.pen_size = abs(self.pen_size + 1) % 100
        self.canvas_widget.pen.setWidth(self.pen_size)
        self.canvas_widget.eraser.setWidth(self.pen_size)
        self.show_size.setText("Size "+str(self.pen_size)) 
    def dec_size(self):
        self.pen_size = abs(self.pen_size - 1) % 100
        self.canvas_widget.pen.setWidth(self.pen_size)
        self.canvas_widget.eraser.setWidth(self.pen_size)
        self.show_size.setText("Size "+str(self.pen_size)) 

app = QApplication(sys.argv)
main = MainWindow()
main.show()
app.exec()