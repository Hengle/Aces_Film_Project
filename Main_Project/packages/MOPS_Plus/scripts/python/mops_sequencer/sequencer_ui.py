from PySide2.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsItem, QDialog, QVBoxLayout, \
    QHBoxLayout, QWidget, QStyle, QStyleOptionButton, QCheckBox, QLabel
from PySide2.QtGui import QPen, QColor, QPainter, QGradient, QLinearGradient, QDrag, QBrush
from PySide2.QtCore import Qt, QPointF, QRectF, QSize, QMimeData
import json
import traceback
import math
import hou

ROW_HEIGHT = 50
COL_WIDTH = 50
TIMELINE_WIDTH = 3

# TODO: copy/paste selection
# TODO: resizing beyond measure/track bounds leaves clips floating around.
# TODO: add trim function to remove clips outside working area

def clamp(num, minv, maxv):
    return max(min(num, maxv), minv)


def getScrollHeight():
    app = QApplication.instance()
    scroll_height = app.style().pixelMetric(QStyle.PM_ScrollBarExtent) + 5
    return scroll_height


class SequencerWindow(QDialog):
    """
    the parent window. holds stuff.
    """

    def __init__(self, parent=None):
        super(SequencerWindow, self).__init__(parent)
        self.setWindowTitle("MOPs Sequencer")
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.blocking = False  # block sync events if true
        # populate UI
        main_layout = QVBoxLayout()
        main_layout.setStretch(0, 0)
        main_layout.setStretch(0, 1)
        self.setLayout(main_layout)
        self.grid = GridView(self)
        self.palette = Palette()
        self.snap_chk = QCheckBox("Snap to Beats")
        self.snap_chk.setChecked(True)
        self.alwaysOnTop_chk = QCheckBox("Always on Top")
        self.alwaysOnTop_chk.setChecked(True)
        self.node = None  # the node i'm currently tracking
        self.clipdata = None  # stores previous state for undos
        label = QLabel("Instruments")
        main_layout.addWidget(label)
        main_layout.addWidget(self.palette)
        main_layout.addWidget(self.grid)
        options_layout = QHBoxLayout()
        options_layout.addWidget(self.snap_chk)
        options_layout.addWidget(self.alwaysOnTop_chk)
        main_layout.addLayout(options_layout)

        # main_layout.addStretch()
        self.snap_chk.stateChanged.connect(self.updateSnap)
        self.alwaysOnTop_chk.stateChanged.connect(self.updateAlwaysOnTop)
        self.show()

    def setNode(self, node):
        self.unsetNode()
        if node is None:
            return
        self.node = node
        self.node.addEventCallback((hou.nodeEventType.ParmTupleChanged,), self._onNodeChange)
        hou.playbar.addEventCallback(self.playbarEvent)
        self.sync_instruments()
        beats = self.node.evalParm("beats")
        measures = self.node.evalParm("measures")
        tracks = self.node.evalParm("tracks")
        self.snap_chk.setChecked(self.node.evalParm("snapping"))
        self.grid.set_size(beats, tracks, measures)
        self.sync_clips()

    def unsetNode(self):
        if self.node:
            try:
                self.node.removeEventCallback((hou.nodeEventType.ParmTupleChanged,), self._onNodeChange)
                hou.playbar.removeEventCallback(self.playbarEvent)
            except hou.ObjectWasDeleted:
                pass
        self.node = None

    def updateSnap(self):
        self.grid.snapping = self.snap_chk.isChecked()
        if self.node is not None:
            self.node.parm("snapping").set(self.grid.snapping)

    def updateAlwaysOnTop(self):
        if self.node is not None:
            value = self.alwaysOnTop_chk.isChecked()
            self.node.parm("alwaysOnTop").set(value)
        if value:
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(self.windowFlags() ^ Qt.WindowStaysOnTopHint)
        self.show()


    def onSceneChange(self):
        # update the parameters string
        if self.blocking:
            return

        if self.node:
            data = self.serialize_clips()
            if data != self.clipdata:
                # print("scene changed")
                # only update the parameter if something actually happened.
                # this prevents a bazillion updates from clogging the undo stack.
                prev_data = self.clipdata
                undo = GridUndo(self, self.node, prev_data)
                hou.undos.add(undo, "MOPs Sequencer Edit")
                with hou.undos.disabler():
                    self.node.parm("clipdata").set(data)
                self.clipdata = data

    def _onNodeChange(self, **kwargs):
        # this event fires when the linked node parameters are modified.
        # mostly we need this to sync instruments.
        if self.node is None:
            return
        if kwargs["event_type"] == hou.nodeEventType.ParmTupleChanged and kwargs["parm_tuple"] is not None:
            # print("node changed")
            for parm in kwargs["parm_tuple"]:
                # print(parm.name())
                if parm.name() == "instruments" or parm.name().startswith("instcolor"):
                    # this is the multiparm. we've added or removed an entry.
                    # resynchronize instruments.
                    self.sync_instruments()
                elif parm.name() == "beats" or parm.name() == "measures" or parm.name() == "tracks":
                    # we need to redraw the grid.
                    beats = self.node.evalParm("beats")
                    measures = self.node.evalParm("measures")
                    tracks = self.node.evalParm("tracks")
                    self.blocking = True
                    self.grid.set_size(beats, tracks, measures)
                    self.sync_clips()
                    self.blocking = False
                # elif parm.name() == "clipdata":
                #     # WHOOPS this completely fucks everything up
                #     self.blocking = True
                #     self.clipdata = self.node.evalParm("clipdata")
                #     self.sync_clips()
                #     self.blocking = False
                else:
                    return

    def closeEvent(self, event):
        if self.node:
            self.unsetNode()
            event.accept()

    def playbarEvent(self, event_type, frame):
        # print("current frame: {}".format(frame))
        if self.node:
            x = (self.node.evalParm("beat") + self.node.evalParm("beats") * self.node.evalParm("measure")) * COL_WIDTH
            # y = self.node.evalParm("measure") * ROW_HEIGHT
            y = 0
            height = self.node.evalParm("tracks") * ROW_HEIGHT
            self.grid.timeline.setPos(x, y)
            self.grid.timeline.setRect(0, 0, TIMELINE_WIDTH, height)
            self.grid.ensureVisible(self.grid.timeline, 100, 100)

    def serialize_clips(self):
        """
        Bundle all Clip data into a JSON string and return it.
        :return: a JSON object containing each Clip.
        """
        data = list()
        clips = self.grid.clips
        for c in clips:
            clipdata = dict()
            clipdata["instrument"] = c.instrument
            clipdata["measure"] = c.measure()
            clipdata["beat"] = c.beat()
            clipdata["duration"] = c.duration()
            clipdata["track"] = int(c.track())
            data.append(clipdata)
        return json.dumps(data, sort_keys=True, indent=4)

    def sync_instruments(self):
        """
        Rebuild the Palette. This happens anytime the Instruments multiparm is edited.
        :return: None
        """
        if self.node is None:
            return
        instrument_count = self.node.evalParm("instruments")
        instruments = list()
        for x in range(instrument_count):
            r = self.node.evalParm("instcolor{}r".format(x + 1))
            g = self.node.evalParm("instcolor{}g".format(x + 1))
            b = self.node.evalParm("instcolor{}b".format(x + 1))
            inst = {"color": (r, g, b)}
            instruments.append(inst)
        self.palette.populate_instruments(instruments)
        self.grid.update_clips(instruments)

    def sync_clips(self):
        """
        Rebuild the Clips view based on the JSON data provided by the clipdata parm.
        :return: None
        """
        if self.node is None:
            return
        clipstr = self.node.evalParm("clipdata")
        clipdata = list()
        if clipstr:
            try:
                clipdata = json.loads(clipstr)
            except:
                return
            # add color information to the data before passing it along.
            for x in range(len(clipdata)):

                instrument = int(clipdata[x]["instrument"])
                # print("getting data for node: {}".format(self.node.name()))
                # print("instrument parm name: instcolor{}r".format(instrument + 1))
                r = self.node.evalParm("instcolor{}r".format(instrument + 1))
                g = self.node.evalParm("instcolor{}g".format(instrument + 1))
                b = self.node.evalParm("instcolor{}b".format(instrument + 1))
                clipdata[x]["color"] = (r, g, b)
            self.grid.sync_clips(clipdata)
        self.clipdata = json.dumps(clipdata, sort_keys=True, indent=4)
        size = self.frameGeometry()
        w = size.width()
        h = (getScrollHeight() + self.grid.rows * ROW_HEIGHT) + 200
        # print("resizing: height {}".format(h))
        self.resize(w, h)


class Palette(QWidget):
    """
    holds color swatches used to create new clips via drag/drop.
    """

    def __init__(self, parent=None):
        super(Palette, self).__init__(parent)
        # self.setAttribute(Qt.WA_StyledBackground, True)
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 10, 0, 10)
        self.layout.setSpacing(6)
        self.setLayout(self.layout)
        self.instruments = list()
        # self.populate_instruments()
        # self.setStyleSheet("background-color: rgb(240, 240, 240);")

    def add_instrument(self, instrument=0, color=(0.2, 0.9, 0.9)):
        # add an instrument to the palette.
        inst = Swatch(instrument, color)
        self.instruments.append(inst)
        self.layout.addWidget(inst)

    def clearLayout(self):
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def populate_instruments(self, instruments):
        """
        Given the instruments list passed from the main window, populate the palette.
        :param instruments: a list of dict items with any necessary attributes for building the swatches.
        :return: None
        """
        self.clearLayout()
        self.instruments = list()
        # parse instruments data.
        for i in instruments:
            self.add_instrument(len(self.instruments), (i["color"][0], i["color"][1], i["color"][2]))
        self.layout.addStretch()


class Swatch(QWidget):
    """
    a single color swatch representing an instrument. can be dragged onto clip view.
    """

    def __init__(self, instrument=0, color=(0.2, 0.9, 0.9)):
        super(Swatch, self).__init__()
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.color = QColor.fromRgbF(color[0], color[1], color[2])
        self.instrument = instrument
        self.setGeometry(0, 0, 30, 30)
        self.setMaximumSize(30, 30)
        self.setCursor(Qt.SizeAllCursor)

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.setPen(QPen(Qt.NoPen))
        color = self.color
        painter.setBrush(color)
        painter.fillRect(0, 0, self.size().width(), self.size().height(), color)
        painter.end()

    def minimumSizeHint(self):
        return QSize(30, 30)

    def mouseMoveEvent(self, event):
        if event.buttons() != Qt.LeftButton:
            return

        mimeData = QMimeData()
        data = {"instrument": self.instrument, "color": (self.color.red(), self.color.green(), self.color.blue())}
        datajs = json.dumps(data)
        mimeData.setText(datajs)
        drag = QDrag(self)
        drag.setMimeData(mimeData)
        drag.setHotSpot(event.pos() - self.rect().topLeft())
        dropAction = drag.start(Qt.MoveAction)




class GridView(QGraphicsView):
    """
    the graphics view for the sequencer grid.
    """

    def __init__(self, mainui):
        super(GridView, self).__init__()
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setAcceptDrops(True)
        self.rows = 1
        self.cols = 8
        self.beats = 8
        self.snapping = True
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.dragbox = None  # placeholder for grid highlight when dragging
        self.timeline = None
        self.clips = list()
        self.mainui = mainui # this is the SequencerWindow parent instance
        self.draw_grid()

    def set_size(self, beats, tracks, measures):
        self.rows = tracks
        self.cols = beats * measures
        self.beats = beats
        # need to include scrollbar height in calculation.
        scroll_height = getScrollHeight()
        # self.setMinimumSize(COL_WIDTH, ROW_HEIGHT*self.rows)
        # self.setMaximumSize(9000, scroll_height + ROW_HEIGHT*self.rows)
        self.resize(self.cols * COL_WIDTH, self.rows * ROW_HEIGHT)
        self.draw_grid()

    def sizeHint(self):
        return QSize(self.cols * COL_WIDTH, self.rows * ROW_HEIGHT)

    def draw_grid(self):
        # draw grid lines for measures (rows)
        self.scene.clear()
        y_offset = 0
        x_offset = 0
        grid_pen = QPen(Qt.SolidLine)
        grid_pen.setColor(QColor(200, 200, 200, 255))
        for y in range(self.rows + 1):
            # draw horizontal line
            self.scene.addLine(0, y_offset, COL_WIDTH * self.cols, y_offset, grid_pen)
            y_offset += ROW_HEIGHT
        for x in range(self.cols + 1):
            # draw vertical line
            # print("drawing col {}".format(x))
            # print(x / self.beats)
            if (x / self.beats) % 1.0 == 0:
                grid_pen.setColor(QColor(250, 250, 250, 255))
                grid_pen.setWidth(2)
                grid_pen.setStyle(Qt.SolidLine)
            else:
                grid_pen.setColor(QColor(200, 200, 200, 255))
                grid_pen.setWidth(1)
                grid_pen.setStyle(Qt.DashLine)
            self.scene.addLine(x_offset, 0, x_offset, ROW_HEIGHT * self.rows, grid_pen)
            x_offset += COL_WIDTH
        # fit the scene to the window
        self.scene.setSceneRect(0, 0, COL_WIDTH * self.cols, ROW_HEIGHT * self.rows)
        # rect = self.scene.sceneRect()
        self.timeline = Timeline()
        self.scene.addItem(self.timeline)
        # self.fitInView(rect)

    def sync_clips(self, clipdata):
        """
        given a clipdata dictionary, rebuild the clips view.
        :param clipdata: a dictionary loaded from the clipdata JSON parameter.
        :return: None
        """
        if not clipdata:
            return
        if self.clips:
            for i in self.clips:
                try:
                    self.remove_clip(i)
                except:
                    pass
        self.clips = list()
        for data in clipdata:
            self.add_new_clip(data["track"], data["beat"] + (data["measure"] * self.beats), data["duration"], data["instrument"], data["color"])
        # self.mainui.adjustSize()

    def add_clip(self, clip):
        # add the given Clip object to the scene.
        self.scene.addItem(clip)
        self.clips.append(clip)

    def add_new_clip(self, row, col, duration=1.0, instrument=0, color=(1.0, 0.0, 0.0)):
        # create a new Clip object and add it.
        clip = Clip(row, col, duration, instrument, color)
        self.scene.addItem(clip)
        self.clips.append(clip)
        return clip

    def remove_clip(self, clip):
        index = self.clips.index(clip)
        self.clips.pop(index)
        self.scene.removeItem(clip)

    def update_clip(self, clip, instrument, color):
        # update the clip to a new instrument.
        clip.instrument = instrument
        clip.setColor(color)

    def update_clips(self, instruments):
        """
        Given a list of instrument dictionary objects, update clips to match any changes.
        :param instruments: a list of dict objects describing dictionary parameters.
        :return: None
        """
        for x in range(len(instruments)):
            # get all clips with this instrument index and update their colors.
            color = QColor.fromRgbF(instruments[x]["color"][0], instruments[x]["color"][1], instruments[x]["color"][2])
            for i in self.clips:
                if i.instrument == x:
                    i.setColor(color)
                elif i.instrument >= len(instruments):
                    # this instrument no longer exists.
                    self.remove_clip(i)

    # def resizeEvent(self, event):
    #     rect = self.scene.sceneRect()
    #     self.fitInView(rect)

    def dragEnterEvent(self, event):
        # if the mime data is valid, create the drag target box.
        mimedata = event.mimeData()
        data = dict()
        try:
            data = json.loads(mimedata.text())
            if "instrument" not in data.keys():
                return
            scene_pos = self.mapToScene(event.pos())
            self.dragbox = Dragbox(scene_pos.x(), scene_pos.y())
            self.scene.addItem(self.dragbox)
            event.accept()
        except:
            print(traceback.format_exc())

    def dragMoveEvent(self, event):
        if self.dragbox:
            scene_pos = self.mapToScene(event.pos())
            # for some reason it's mapping the event position to be +width/2, +height/2. why?
            # print(scene_pos)
            # snap scene pos like a Clip
            tx = scene_pos.x() - (COL_WIDTH * 0.5)
            ty = scene_pos.y() - (ROW_HEIGHT * 0.5)
            if self.snapping:
                tx = round(tx / COL_WIDTH) * COL_WIDTH
            ty = round(ty / ROW_HEIGHT) * ROW_HEIGHT
            # clamp to grid.
            tx = clamp(tx, 0, (self.cols - 1.0) * COL_WIDTH)
            ty = clamp(ty, 0, (self.rows - 1) * ROW_HEIGHT)
            new_pos = QPointF(tx + self.dragbox.borderSize, ty + self.dragbox.borderSize)
            self.dragbox.setPos(new_pos)

        event.accept()

    def dragLeaveEvent(self, event):
        if self.dragbox:
            self.scene.removeItem(self.dragbox)
            self.dragbox = None
            event.accept()

    def dropEvent(self, event):
        # print("drop")
        # get mime data from event
        # event positions are in world space relative to the QGraphicsView
        # and don't account for scaling within the view.
        mimedata = event.mimeData()
        data = dict()
        try:
            data = json.loads(mimedata.text())
            # print(data)
            if "instrument" not in data.keys():
                return
            scene_pos = self.mapToScene(event.pos())
            scene_pos = self.dragbox.pos()
            # print(scene_pos)
            self.scene.removeItem(self.dragbox)
            self.dragbox = None
            # now add the new Clip. if we're dropping onto an existing Clip, we'll want to swap it.
            item = self.itemAt(event.pos().x(), event.pos().y())
            if item:
                if isinstance(item, Clip):
                    qcol = QColor.fromRgb(data["color"][0], data["color"][1], data["color"][2])
                    self.update_clip(item, data["instrument"], qcol)
            else:
                # based on the position, get the row and column and generate a new clip.
                row = math.floor(scene_pos.y() / ROW_HEIGHT)
                col = scene_pos.x() / COL_WIDTH
                if self.snapping:
                    col = math.floor(col)
                qcol = QColor.fromRgb(data["color"][0], data["color"][1], data["color"][2])
                self.add_new_clip(row, col, 1.0, data["instrument"], (qcol.redF(), qcol.greenF(), qcol.blueF()))
            self.mainui.onSceneChange()
            event.accept()
        except:
            print(traceback.format_exc())

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete or event.key() == Qt.Key_Backspace:
            # print("poop")
            # remove selected clips
            sel = self.scene.selectedItems()
            # print(sel)
            if sel:
                for i in sel:
                    self.remove_clip(i)
                self.mainui.onSceneChange()
        super(GridView, self).keyPressEvent(event)

    def mouseReleaseEvent(self, event):
        # print("bloop")
        self.mainui.onSceneChange()
        super(GridView, self).mouseReleaseEvent(event)


class Dragbox(QGraphicsRectItem):
    """
    a graphics item representing an empty space the user is dragging a swatch to.
    """

    borderSize = 2

    def __init__(self, x, y):
        x = x + self.borderSize
        y = y + self.borderSize
        w = COL_WIDTH - (self.borderSize * 2)
        h = ROW_HEIGHT - (self.borderSize * 2)
        super(Dragbox, self).__init__(0, 0, w, h)

        self.setPos(x, y)
        col = QColor.fromRgbF(0.9, 0.9, 0.9)
        pen = QPen(col)
        pen.setWidth(self.borderSize)
        pen.setStyle(Qt.DashLine)
        self.setPen(pen)
        self.setZValue(999)  # draw on top


class Timeline(QGraphicsRectItem):
    """
    a graphics item representing the timeline indicator.
    """

    width = TIMELINE_WIDTH

    def __init__(self):
        w = self.width
        h = ROW_HEIGHT
        super(Timeline, self).__init__(0, 0, w, h)
        pen = QPen(Qt.NoPen)
        col = QColor.fromRgbF(1.0, 0, 0)
        self.setBrush(QBrush(col))
        self.setPen(pen)
        self.setZValue(1000)


class Clip(QGraphicsRectItem):
    """
    a graphics item representing a single instance of an instrument.
    has an instrument index, measure, beat, and duration.
    """
    handleSize = 8
    borderSize = 2

    def __init__(self, row=0, col=0, duration=1.0, instrument=0, color=(1.0, 0.0, 0.0)):
        # calculate x/y/w/h based on row and col
        x = (col * COL_WIDTH) + self.borderSize
        y = (row * ROW_HEIGHT) + self.borderSize
        w = (COL_WIDTH * duration) - (self.borderSize * 2)
        h = ROW_HEIGHT - (self.borderSize * 2)
        qcol = QColor.fromRgbF(color[0], color[1], color[2])
        grad = QLinearGradient(0, 0.7, 0, 1)
        grad.setCoordinateMode(QGradient.ObjectMode)
        grad.setColorAt(0, qcol)
        grad.setColorAt(1, qcol.darker(140))
        super(Clip, self).__init__(0, 0, w, h)
        self.setPos(x, y)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)  # allow dragging/dropping
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)  # send events when modified
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsFocusable, True)
        self.setCursor(Qt.SizeAllCursor)
        self.setBrush(grad)
        pen = QPen()
        pen.setWidth(self.borderSize)
        pen.setJoinStyle(Qt.MiterJoin)
        self.setPen(pen)
        self.setZValue(-1)  # draw this behind the grid
        self.setAcceptHoverEvents(True)
        self.instrument = instrument
        self.handles = dict()  # stores resize handles. these change dynamically.
        self.currentHandle = None  # stores currently activated handle, if any.
        self.pressPos = None  # stores position of last mouse press
        self.lastRect = None  # stores last rect before resize event
        self.updateHandles()

    def measure(self):
        # return the measure (row) this clip belongs to.
        beat = (self.pos().x() - self.borderSize) / COL_WIDTH
        view = self.scene().views()[0]
        beats = float(view.beats)
        m = math.floor(beat / beats)
        return m

    def beat(self):
        # return the beat (col) this clip belongs to.
        col = (self.pos().x() - self.borderSize) / COL_WIDTH
        view = self.scene().views()[0]
        beats = float(view.beats)
        col = col % beats
        return col

    def track(self):
        row = round(self.pos().y() / ROW_HEIGHT)
        return row

    def duration(self):
        # return the duration of this clip, in beats.
        w = (self.rect().width() + self.borderSize * 2) / COL_WIDTH
        return w

    def setColor(self, qcol):
        grad = QLinearGradient(0, 0.7, 0, 1)
        grad.setCoordinateMode(QGradient.ObjectMode)
        grad.setColorAt(0, qcol)
        grad.setColorAt(1, qcol.darker(140))
        self.setBrush(grad)

    def updateHandles(self):
        # update resize handle bounds on this object. this needs to happen anytime the object is adjusted.
        me = self.rect()
        # self.handles["left"] = QRectF(me.left(), me.top(), self.handleSize, me.height())
        self.handles["right"] = QRectF(me.right() - self.handleSize, me.top(), me.right(), me.height())

    def handleAt(self, point):
        # return the resize handle at the given point, if any.
        for k, v in self.handles.items():
            if v.contains(point):
                return k
        return None

    def interactiveResize(self, point):
        # resize this object horizontally, based on the delta between the mouse position
        # and self.pressPos.
        rect = QRectF(self.lastRect)
        temp_rect = QRectF(self.rect())
        view = self.scene().views()[0]
        # print("last rect right: {}".format(rect.right()))
        if self.currentHandle == "right":
            dx = point.x() - self.pressPos.x()
            if view.snapping:
                dx = round(dx / COL_WIDTH) * COL_WIDTH
            # print(dx)
            rect.setRight(rect.right() + dx)
            min_size = self.handleSize
            if view.snapping:
                min_size = COL_WIDTH - self.borderSize * 2
            max_size = view.cols * COL_WIDTH - self.pos().x() - self.borderSize
            rect.setWidth(clamp(rect.width(), min_size, max_size))
            self.setRect(rect)

        # check for collisions
        for other in view.clips:
            if other is not self:
                if self.collidesWithItem(other):
                    self.setRect(temp_rect)
        self.updateHandles()

    def debug(self):
        print("Measure: {}".format(self.measure()))
        print("Beat: {}".format(self.beat()))
        print("Duration: {}".format(self.duration()))
        print("Position: {},{}".format(self.pos().x(), self.pos().y()))

    ################################
    #### re-implemented Qt functions
    ################################

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            orig = self.pos()
            view = self.scene().views()[0]
            # snap to nearest grid cell by returning the new position.
            tx = value.x()
            ty = value.y()
            # print("original coords: {},{}".format(tx, ty))
            if view.snapping:
                tx = round(tx / COL_WIDTH) * COL_WIDTH
            ty = round(ty / ROW_HEIGHT) * ROW_HEIGHT
            # clamp to grid.
            tx = clamp(tx, 0, (view.cols - self.duration()) * COL_WIDTH)
            ty = clamp(ty, 0, (view.rows - 1) * ROW_HEIGHT)
            new_pos = QPointF(tx + self.borderSize, ty + self.borderSize)
            # print(new_pos)
            # check to see if this position is inside any other item.
            for other in view.clips:
                if other is not self:
                    this = QRectF(tx, ty, self.rect().width(), self.rect().height())
                    test = QRectF(other.pos().x(), other.pos().y(), other.rect().width() - 1, other.rect().height() - 1)
                    # if test.contains(new_pos):
                    # print("collision")
                    # return orig
                    if this.intersects(test):
                        return orig
            return new_pos
        return value

    def hoverMoveEvent(self, event):
        handle = self.handleAt(event.pos())
        cursor = Qt.SizeAllCursor
        if handle:
            cursor = Qt.SizeHorCursor
        self.setCursor(cursor)
        super(Clip, self).hoverMoveEvent(event)

    def mousePressEvent(self, event):
        # fires when mouse is first pressed on this item.
        self.currentHandle = self.handleAt(event.pos())
        if self.currentHandle:
            self.pressPos = event.pos()
            self.lastRect = self.rect()
        super(Clip, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        # fires when the mouse is moving over the clip.
        if self.currentHandle:
            self.interactiveResize(event.pos())
        else:
            super(Clip, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        super(Clip, self).mouseReleaseEvent(event)
        self.currentHandle = None
        self.lastRect = None

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete or event.key() == Qt.Key_Backspace:
            view = self.scene().views()[0]
            view.remove_clip(self)
        super(Clip, self).keyPressEvent(event)

    def contextMenuEvent(self, event):
        pass
        # self.debug()


class GridUndo(object):
    """
    This contains instructions for how to undo or redo operations in the GridView.
    """

    def __init__(self, ui, node, data):
        self.ui = ui
        self.node = node
        self.data = data
        # print("undo created with data: {}".format(data))

    def undo(self):
        if self.node:
            self.node.parm("clipdata").set(self.data)
            self.ui.sync_clips()

    def redo(self):
        if self.node:
            self.node.parm("clipdata").set(self.data)
            self.ui.sync_clips()


"""
In loving memory of Zuul.
Until we meet again.

              __..--''``---....___   _..._    __
    /// //_.-'    .-/";  `        ``<._  ``.''_ `. / // /
   ///_.-' _..--.'_    \                    `( ) ) // //
   / (_..-' // (< _     ;_..__               ; `' / ///
    / // // //  `-._,_)' // / ``--...____..-' /// / //

"""