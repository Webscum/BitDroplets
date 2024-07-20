import time
import random as r
from machine import UART, Pin, I2C, Timer, ADC
from ssd1306 import SSD1306_I2C
from fifo import Fifo

class Encoder:
    def __init__(self, rot_a, rot_b):
        self.a = Pin(rot_a, mode = Pin.IN, pull = Pin.PULL_UP)
        self.b = Pin(rot_b, mode = Pin.IN, pull = Pin.PULL_UP)
        self.fifo = Fifo(30, typecode = 'i')
        self.a.irq(handler = self.handler, trigger = Pin.IRQ_RISING, hard = True)
    
    def handler(self, pin):
        if self.b():
            self.fifo.put(-1)
        else:
            self.fifo.put(1)

ROT_Push = Pin(12, Pin.IN, Pin.PULL_UP)

i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)

oled_width = 128
oled_height = 64
oled = SSD1306_I2C(oled_width, oled_height, i2c)
oled.fill(0)

rot = Encoder(10, 11)

def MenuScreen(name, options):
    chosenIndex = 0
    
    while True:
        
        if rot.fifo.has_data():
            chosenIndex = (chosenIndex + rot.fifo.get()) % len(options)
            chosenIndex += len(options)*int(chosenIndex < 0)
            
        oled.fill(0)
        
        oled.text(name, 64-(4*len(name)), 15, 1)
        optionIndex = 0
        for option in options:
            isChosen = int(optionIndex == chosenIndex)
            oled.text( (">" * isChosen) + option + ("<" * isChosen), 63-(4*(len(option)+isChosen*2)), 23+(optionIndex*8))
            optionIndex += 1
            
        if not ROT_Push():
            oled.fill(0)
            return chosenIndex
            
        oled.show()
        
def exitGame():
    oled.fill(0)
    oled.text("BYE!", 63-4*4, 23)
    oled.show()
    oled.fill(0)
    time.sleep(1/2)
    oled.show()
    
def playGame():
    
    playerpos = [64, 63]

    droplets = []
    dropamount = 40
    dropspeed = 1

    gameover = 0

    for iter in range(dropamount):
        droplets.append([r.randrange(0,127),r.randrange(-63, 0)])
        

    while True:
        oled.fill(0)
        
        if rot.fifo.has_data():
            rotVal = rot.fifo.get()
            playerpos[0] += rotVal
            playerpos[0] -= int(playerpos[0] < 0 or playerpos[0] > 127) * rotVal
            print(rotVal) 
        
        for h in range(4):
            oled.pixel(playerpos[0], playerpos[1] - int(h), 1)
        
        for drop in droplets:
            if drop[0] == playerpos[0] and drop[1] >= (playerpos[1] - 3):
                gameover = True
                
            drop[1] += 1 * dropspeed
            drop[0] += int(drop[1] >= 63) * r.randrange(0, 63)
            drop[0] %= 128
            drop[1] -= int(drop[1] >= 63) * (r.randrange(0, 24) + 63)
            oled.pixel(drop[0], drop[1], 1)
            
        
        if gameover:
            oled.fill(0)
            if MenuScreen("GAME OVER", ["Replay", "Exit"]):
                exitGame()
                return
            else:
                playGame()
                return
        
        oled.show()
        
        time.sleep(1/180)
        
firstMenuChoice = MenuScreen("DROPLETS", ["Play", "Exit"])

if firstMenuChoice:
    exitGame()
else:
    playGame() # The game goes to game over and restart or exit in this function, it is reclusive
    
        
        
    


