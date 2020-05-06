from tkinter import *
from random import randrange, random
from math import floor
from time import time
from os.path import exists
from numpy import load, save

root = Tk()
root.title("Жызн")

#НАСТРОЙКИ
SEG_SIZE = 10 #Размер клетки # 10
WIDTH = 1280 #Ширина окна # 1280
HEIGHT = 720 #Высота окна # 720
BACKGROUND = "#000" #Цвет фона # "#000"
MutationChance = 100 #Шанс мутации # 25
NEnergy = 300 #Начальная энергия семечка # 300
MaxEnergy = 48 #Максимальная получаемая энергия # 32
CellEnergy = 13 #Количество потребляемой энергии на клетку # 13
#/////////

#ПРОДВИНУТЫЕ НАСТРОЙКИ
CENTER = floor(WIDTH / 2 / SEG_SIZE) * SEG_SIZE #Формула для расчёта центра
FPS = 8 #Количество обновлений экрана в секунду
CounterMax = 10 #Каждые n ходов писать статастику
GenLength = 16 #Длина гена
saveFileName = "gen.npy"
record = [0]
#/////////////////////

c = Canvas(root, width = WIDTH, height = HEIGHT, bg = BACKGROUND)
c.grid()
c.focus_set()

if exists(saveFileName):
    record = load(saveFileName, allow_pickle = True)

#top bottom left right
def generateGen(n = 8): #Генирация гена
    global GenLength
    m = []
    for _ in range(n):
        m.append([randrange(-1, GenLength - 1, 1), randrange(-1, GenLength - 1, 1), randrange(-1, GenLength - 1, 1), randrange(-1, GenLength - 1, 1)])
    return m

def generateColor(l = 3): #Генирация цвета
    rt = "#"
    m = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "a", "b", "c", "d", "e", "f"]
    for _ in range(l):
        rt += m[randrange(0, len(m) - 1, 1)]
    return rt


# 0 - white, 1 - green
class life(object): #Жызн
    def __init__(self, gen, x, y, prog, color):
        global SEG_SIZE
        self.type = 0
        self.x = x
        self.y = y
        self.gen = gen #TODO: Нафига хранить весь геном? Почему нельзя хранить только ген?!
        self.progress = prog
        self.color = color
        self.this = c.create_rectangle(x, y, x + SEG_SIZE - 1, y + SEG_SIZE - 1, fill = "#fff", outline = "#fff")
    def kill(self): #Удаление с поля
        c.delete(self.this)

class wood(object):
    def __init__(self, energy, color, x, y, gen):
        self.energy = energy
        self.lifes = []
        self.color = color
        self.gen = gen
        self.time = time()
        self.lifes.append(life(gen, x, y, 1, color))
    def getMoveEnergy(self): # Получить энергию за ход
        full = 0
        for j in range(len(self.lifes)):
            if self.lifes[j].type == 1:
                continue
            try:
                full += MaxEnergy / (HEIGHT / (HEIGHT - self.lifes[j].y))
            except:
                pass
        return full

class session(object): #Для игры
    def __init__(self):
        self.woods = []
    def add_wood(self, color, x, y, gen): #Добавить дерево
        self.woods.append(wood(NEnergy, color, x, y, gen))
    def del_wood(self, index): #Удалить дерево по индексу
        del self.woods[index]
    def update(self): #Обновить
        global GenLength, saveFileName
        l = 0
        while l < len(self.woods):
            woody = self.woods[l]
            woody.energy -= (len(woody.lifes) * CellEnergy)
            if woody.energy <= 0:
                for cell2 in range(len(woody.lifes)):
                    cell = woody.lifes[cell2]
                    if cell.type == 0:
                        Ngen = woody.gen
                        if random() < MutationChance / 100: # Семечко мутирует
                            Ngen[randrange(0, GenLength - 1, 1)] = [randrange(-1, GenLength - 1, 1), randrange(-1, GenLength - 1, 1), randrange(-1, GenLength - 1, 1), randrange(-1, GenLength - 1, 1)]
                        self.add_wood(generateColor(3), cell.x, HEIGHT - SEG_SIZE, Ngen)
                    cell.kill()
                if record[0] < time() - self.woods[l].time:
                    save(saveFileName, [time() - self.woods[l].time, self.woods[l].gen])
                    record[0] = time() - self.woods[l].time
                    record[1] = self.woods[l].gen
                del self.woods[l]
            else:
                self.woods[l].energy += woody.getMoveEnergy()

            l += 1
    def sexAll(self): #Размножить всех
        for k in range(len(self.woods)): #Для каждого дерева
            for d in range(len(self.woods[k].lifes)): #Для каждой клетки дерева
                tf = self.woods[k].lifes[d]
                if tf.type == 0: #Если это стволовая клетка
                    Gen = tf.gen[tf.progress] # Gen = [0, 1, 2, 3] # Выбираю ген
                    for g in range(len(Gen)): # G = 1 # Для каждой цифры в гене
                        if Gen[g] != -1: # Если ген не пустой
                            b = [[0, -1 * SEG_SIZE], [0, 1 * SEG_SIZE], [-1 * SEG_SIZE, 0], [1 * SEG_SIZE, 0]] # координаты ВВЕРХ, ВНИЗ, ЛЕВО, ПРАВО
                            nX = tf.x + b[g][0] # Получение X
                            nY = tf.y + b[g][1] # Получение Y
                            nL = 1
                            if nX < 0 or nX > WIDTH or nY < 0 or nY > HEIGHT: #если клетка не за границей поля
                                nL = 0
                            for a in range(len(self.woods)): # Для дерева
                                for b in range(len(self.woods[a].lifes)): # для каждой клетки
                                    if nX == self.woods[a].lifes[b].x and nY == self.woods[a].lifes[b].y:
                                        nL = 0
                            if nL: #Если клетка свободна
                                self.woods[k].lifes.append(life(tf.gen, nX, nY, Gen[g], self.woods[k].color))
                        tf.type = 1
                        tf.kill()
                        tf.this = c.create_rectangle(tf.x, tf.y, tf.x + SEG_SIZE - 1, tf.y + SEG_SIZE - 1, fill = tf.color, outline = tf.color)
        return True

default = [] #Ген по умолчанию
if exists(saveFileName):
    default = load(saveFileName, allow_pickle = True)[1]
else:
    default = generateGen(GenLength)

game = session()
game.add_wood("#00f", CENTER, HEIGHT - SEG_SIZE, default) #Первое дерево

srtTime = time()
allTime = time()
counter = 0

def progress():
    global FPS, allTime, srtTime, CounterMax, counter, record
    if game.sexAll():
        game.update()
    if counter == CounterMax:
        print("Время хода", round((time() - srtTime) / CounterMax, 3), "секунд")
        print("FPS:", 1 / ((time() - srtTime) / CounterMax))
        srtTime = time()
        print("Время симуляции", round(time() - allTime, 3), "секунд")
        print("Количество деревьев", len(game.woods))
        print("Рекорд жизни", round(record[0], 1), "секунд")
        print("Лучший ген", record[1])
        print(" ")
        counter = 0
    else:
        counter += 1

    root.after(int(1000/FPS), progress)

progress()

root.mainloop()