#kivy imports
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.uix.image import Image as kvImage

#Screen capture imports, with goal of platform independance + multimonitor support
from functools import partial
from PIL import Image
from kivy.core.image import Image as CoreImage
from pynput import mouse
import mss
import mss.tools
import numpy as np
from kivy.graphics import texture
import io
import cv2 

memoryBuffer = io.BytesIO() 
temp = Image.open("board.png")
temp.save(memoryBuffer, format='png')

class ToolBar(BoxLayout):
    pass


class BoardScreen(Screen):
    lastCapture = CoreImage("Board.png")
    def __init__(self, **kwargs):
        super(BoardScreen, self).__init__(**kwargs)
    def on_kv_post(self, base_widget): #event fires once kv has loaded
        Clock.schedule_interval(partial(BoardScreen.board_update, self.ids['boardImage']), 0.25)
        memoryBuffer.seek(0)
        capture = CoreImage(io.BytesIO(memoryBuffer.read()), ext='png')
        self.ids['boardImage'].texture = capture.texture
    def board_update(object, dt):
        global memoryBuffer
        # memoryBuffer.seek(0)
        # captureCV2 = np.frombuffer(memoryBuffer.read(), dtype=np.uint8)
        # captureCV2 = cv2.imdecode(captureCV2, cv2.IMREAD_ANYCOLOR)
        # processedCapture = BoardScreen.draw_grid(captureCV2, (8,8))
        # capture = BoardScreen.openCVtoCoreImage(processedCapture)
        memoryBuffer.seek(0)
        capture = CoreImage(io.BytesIO(memoryBuffer.read()), ext='png')
        
        # if not(capture.texture == BoardScreen.lastCapture.texture): #implement equals image check
        #     processedCapture = BoardScreen.board_processing(capture)
        object.texture = capture.texture #processedcapture is a coreimage !!!!
            # BoardScreen.lastCapture = capture
        # else:
        #     pass #do nothing if board has not changed
    def board_processing(boardImage):
        processedImage = 1
        return processedImage
            
    def openCVtoCoreImage(anOpenCV):
        is_success, buffer = cv2.imencode(".png", anOpenCV)
        tempBuffer = io.BytesIO(buffer)
        tempBuffer.seek(0)
        aCoreImage = CoreImage(io.BytesIO(tempBuffer.read()), ext='png')
        tempBuffer.close()
        return aCoreImage
    
    def draw_grid(img, grid_shape, color=(0, 255, 0), thickness=1):
        h, w, _ = img.shape
        rows, cols = grid_shape
        dy, dx = h / rows, w / cols
        # draw vertical lines
        for x in np.linspace(start=dx, stop=w-dx, num=cols-1):
            x = int(round(x))
            cv2.line(img, (x, 0), (x, h), color=color, thickness=thickness)
        # draw horizontal lines
        for y in np.linspace(start=dy, stop=h-dy, num=rows-1):
            y = int(round(y))
            cv2.line(img, (0, y), (w, y), color=color, thickness=thickness)
        return img
    
    def slice_board(board, nslices):
        h, w, channels = board.shape
        print(h , w, channels)
        slicesY = [(h//nslices)*n for n in range(1,nslices+1)]
        slicesX = [(w//nslices)*n for n in range(1,nslices+1)]
        print(len(slicesX), slicesY)
        tiles = []
        prevX = 0 
        for x in slicesX:
            prevY = 0
            col = board[:, prevX:x]
            prevX = x
            for y in slicesY:
                tile = col[prevY:y, :]
                tiles.append(tile)
                prevY = y
        return tiles

class SettingsScreen(Screen):
    pass

class BoardView(App):
    topLeft = (0,0)
    botRight = (100,100)
    def update_capture(*args):
        global memoryBuffer
        topLeft = BoardView.topLeft
        botRight = BoardView.botRight
        sct = mss.mss()
        width = abs(topLeft[0] - botRight[0]) #subtract x values
        height = abs(topLeft[1] - botRight[1]) #subtract y values
        bounding_box = {'top': topLeft[1], 'left': topLeft[0], 'width': width, 'height': height}
        image = sct.grab(bounding_box)
        image = Image.frombytes("RGB", image.size, image.bgra, "raw", "BGRX") #convert to PIL, no intermediate format
        image.save(memoryBuffer, format='png')
    def on_click(x, y, button, pressed):
        if pressed:
            BoardView.topLeft = (x, y)
        print('{0} at {1}'.format('Pressed' if pressed else 'Released', (x, y)))
        if not pressed:
            BoardView.botRight = (x,y)
            BoardView.update_capture()
            return False
    def start_listener(null): 
        # Collect events until released
        with mouse.Listener(on_click=BoardView.on_click) as listener:
            listener.join() 
    def build(self):
        Clock.schedule_interval(BoardView.update_capture, 0.25)
        pass
    
if __name__ == '__main__':
    BoardView().run()