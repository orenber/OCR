import matplotlib.pyplot as plt
import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QApplication
from matplotlib.patches import Rectangle

from Algo.Utilities import blob_select


class AxesEvent:

    def __init__(self, *args, **kwargs):

        self.ax = plt.axes(*args, **kwargs)
        self.figure = self.ax.get_figure()
        self.__in_axes = False
        self.callback = {'on_press': '',
                         'on_release': '',
                         'on_motion': '',
                         'on_scroll': '',
                         'enter_axes': '',
                         'leave_axes': ''}

    def connect(self):
        # connect to all the events we need
        self.cidpress = self.figure.canvas.mpl_connect(
            'button_press_event', self.on_press)
        self.enter_axes = self.figure.canvas.mpl_connect(
            'axes_enter_event', self.enter_axes)
        self.leave_axes = self.figure.canvas.mpl_connect(
            'axes_leave_event', self.leave_axes)

    def mouse_motion(self, state: bool = False):
        if state:
            self.cidrelease = self.figure.canvas.mpl_connect(
                'button_release_event', self.on_release)
            self.cidmotion = self.figure.canvas.mpl_connect(
                'motion_notify_event', self.on_motion)
            self.scroll = self.figure.canvas.mpl_connect(
                'scroll_event', self.on_scroll)
        elif state == False:
            self.figure.canvas.mpl_disconnect(self.cidrelease)
            self.figure.canvas.mpl_disconnect(self.cidmotion)
            self.figure.canvas.mpl_disconnect(self.scroll)

    def on_press(self, event):
        # on button press we will see if the mouse is over us and store some data
        if self.__in_axes and id(self.ax) == id(event.inaxes):
            self.mouse_motion(True)

            callback = self.callback['on_press']
            if callable(callback):
                callback(event)

            pass

    def on_scroll(self, event):

        callback = self.callback['on_scroll']
        if callable(callback):
            callback(event)

    def on_motion(self, event):

        if self.__in_axes and id(self.ax) == id(event.inaxes):

            callback = self.callback['on_motion']
            if callable(callback):
                callback(event)

        pass

    def on_release(self, event):
        self.__in_axes = True
        if id(self.ax) == id(event.inaxes):

            self.mouse_motion(False)

            callback = self.callback['on_release']
            if callable(callback):
                callback(event)
        pass

    def enter_axes(self, event):

        QApplication.setOverrideCursor(QCursor(Qt.ArrowCursor))
        self.__in_axes = True
        if id(self.ax) == id(event.inaxes):

            callback = self.callback['enter_axes']
            if callable(callback):
                callback(event)

        pass

    def leave_axes(self, event):
        QApplication.restoreOverrideCursor()
        self.__in_axes = False
        if id(self.ax) == id(event.inaxes):

            callback = self.callback['leave_axes']
            if callable(callback):
                callback(event)

        pass

    def disconnect(self):
        self.figure.canvas.mpl_disconnect(self.cidpress)
        self.figure.canvas.mpl_disconnect(self.cidrelease)
        self.figure.canvas.mpl_disconnect(self.cidmotion)


class BoardFreeHand:

    def __init__(self, *args, **kwargs):

        self.ax = plt.axes(*args, **kwargs)
        self.figure = self.ax.get_figure()
        self.press = None
        self.penColor = 'blue'
        self.background = None
        self.__in_axes = False
        self._xdata = [np.nan]
        self._ydata = [np.nan]
        self.erse_color = self.ax.get_facecolor()
        self.erse_size = 1
        self.__erse_size = 1

    @property
    def draw(self) -> bool:
        return self.__draw

    @draw.setter
    def draw(self, state: bool):
        self.__draw = state

        if self.__draw:
            self.mouse_motion(True)
        else:
            self.mouse_motion(False)

    @property
    def erse_size(self) -> int:
        return self.__erse_size

    @erse_size.setter
    def erse_size(self, size: int):
        if size < 1:
            self.__erse_size = 1
        else:
            self.__erse_size = size

    def connect(self):
        # connect to all the events we need
        self.cidpress = self.figure.canvas.mpl_connect(
            'button_press_event', self.on_press)

        self.enter_axes = self.figure.canvas.mpl_connect(
            'axes_enter_event', self.enter_axes)
        self.leave_axes = self.figure.canvas.mpl_connect(
            'axes_leave_event', self.leave_axes)

    def mouse_motion(self, state: bool = False):
        if state:
            self.cidrelease = self.figure.canvas.mpl_connect(
                'button_release_event', self.on_release)
            self.cidmotion = self.figure.canvas.mpl_connect(
                'motion_notify_event', self.on_motion)
            self.scroll = self.figure.canvas.mpl_connect(
                'scroll_event', self.on_scroll)
        elif state == False:
            self.figure.canvas.mpl_disconnect(self.cidrelease)
            self.figure.canvas.mpl_disconnect(self.cidmotion)
            self.figure.canvas.mpl_disconnect(self.scroll)

    def on_press(self, event):
        # on button press we will see if the mouse is over us and store some data
        if self.__in_axes and id(self.ax) == id(event.inaxes):
            self.draw = True

    def on_scroll(self, event):

        scroll_direction = event.button
        print('scroll dirction' + scroll_direction)
        if scroll_direction == 'down':
            self.erse_size -= 1
            pass

        elif scroll_direction == 'up':

            self.erse_size += 1
            pass

    def on_motion(self, event):

        if self.__in_axes:

            if event.button == 1:
                self.draw_on( event.xdata, event.ydata, self.penColor)
                pass
            elif event.button == 3:
                self.draw_on(event.xdata, event.ydata, self.erse_color, self.erse_size)
                pass

    def draw_on(self, x0: float, y0: float, draw_color='black', size=1):

        # LIFO
        self._xdata.append(x0)
        self._ydata.append(y0)
        if len(self._xdata) > 2:
            self._xdata.pop(0)
            self._ydata.pop(0)

        self.ax.plot(self._xdata, self._ydata, color=draw_color, linewidth=size)

        self.figure.canvas.draw()

        pass

    def on_release(self, event):
        self.draw = False
        self._xdata = []
        self._ydata = []

    def enter_axes(self, event):
        self.__in_axes = True
        QApplication.setOverrideCursor(QCursor(Qt.ArrowCursor))
        pass

    def leave_axes(self, event):
        self.__in_axes = False
        QApplication.restoreOverrideCursor()

    def disconnect(self):
        self.figure.canvas.mpl_disconnect(self.cidpress)
        self.figure.canvas.mpl_disconnect(self.cidrelease)
        self.figure.canvas.mpl_disconnect(self.cidmotion)
        if self.draw:
            self.mouse_motion(False)


class BoaredImage(BoardFreeHand):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.image_size = [45, 45]
        self.image = self.st()

    def create_binary_image(self):

        black_image = np.zeros([self.image_size[0], self.image_size[0]], dtype=np.bool)
        self.ax.cla()
        self.ax.imshow( black_image, cmap=plt.cm.gray)
        return black_image

    def draw_on(self, x0: int, y0: int, drawcolor='black', size=1):

        self.image[int(y0), int(x0)] = True
        self.ax.cla()
        self.ax.imshow(self.image, cmap=plt.cm.gray)
        self.figure.canvas.draw()


class AxesSelectBlobImage(BoardFreeHand):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.binary_image = []
        self.rectangle = Rectangle((np.nan, np.nan), np.nan, np.nan,
                                   linewidth=1, edgecolor='g', facecolor='none')
        self.ax.add_patch(self.rectangle)
        # protected
        self._command = []

    @property
    def command(self):
        return self.__command

    def command(self, command):
        # check if the command is lambda expression
        if callable(command):

            self._command = command

    def set_binary_image(self, binary_image: np.array):
        self.binary_image = binary_image
        self.ax.imshow(binary_image)
        pass



    def draw_on(self, x0: int, y0: int, drawcolor='black', size=1):

        if callable(self.command):
            self.command(x0, y0, self.binary_image)
        else:

            blob = blob_select(self.binary_image, x0, y0)
            ROI = blob['ROI']
            self.rectangle.set_x(ROI['x'])
            self.rectangle.set_y(ROI['y'])
            self.rectangle.set_width(ROI['width'])
            self.rectangle.set_height(ROI['height'])
        # Add the patch to the Axes

        pass


def main():

    plt.figure()
    ax1 = AxesEvent([0.1, 0.1, 0.4, 0.8])
    ax2 = AxesEvent([0.55, 0.1, 0.4, 0.8])

    ax1.connect()
    ax2.connect()
    plt.show()


if __name__ == "__main__":
    main()
