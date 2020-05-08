#   Life Simulation  #
#   Симуляция жизни  #
# От Avenger/kewldan #
#     Version 1.1    #
#     08.05.2020     #

from tkinter import Tk, Canvas #Для визуализации
from random import randrange, random #Для случайных чисел
from math import floor #Для математических действий
from time import time #Для времени
from os.path import exists #Для работы с File System

root = Tk()
root.title("Life simulation")

#НАСТРОЙКИ
#НАЗВАНИЕ = ЗНАЧЕНИЕ #ЧТО МЕНЯЕТ # ЗНАЧЕНИЕ ПО УМОЛЧАНИЮ
SEG_SIZE = 5 #Размер клетки # 10
WIDTH = 128 #Ширина окна # 128
HEIGHT = 128 #Высота окна # 128
BACKGROUND = "#000" #Цвет фона # "#000"
FPS = 30 #Количество обновлений экрана в секунду #30
MutationChance = 25 #Шанс мутации # 25
NEnergy = 300 #Начальная энергия семечка # 300
MaxEnergy = 128 #Максимальная получаемая энергия # 128
CellEnergy = 13 #Количество потребляемой энергии на клетку # 13
AllowLog = False #Включить логи (Не рекомендуется, снижает FPS) # False
#/////////

WIDTH *= SEG_SIZE
HEIGHT *= SEG_SIZE

#ПРОДВИНУТЫЕ НАСТРОЙКИ (РЕДОКТИРОВАТЬ КРАЙНЕ НЕ РЕКОМЕНДУЕТСЯ)
CENTER = floor(WIDTH / 2 / SEG_SIZE) * SEG_SIZE #Формула для расчёта центра
BOTTOM = floor(HEIGHT / SEG_SIZE) * SEG_SIZE - SEG_SIZE + 2
CounterMax = 10 #Каждые n ходов писать статастику
GenLength = 16 #Длина генома
saveFileName = "gen.txt" #Название файла для сохранения
record = [0, []] #Рекорд
TotalMove = 0 #Ход
#/////////////////////

c = Canvas(root, width = WIDTH, height = HEIGHT, bg = BACKGROUND)
c.grid()
c.focus_set()

def load(fileName):
    _file = open(fileName, "r")
    text = _file.read()
    if text:
        return [int(text.split()[0]), eval(text[len(str(text.split()[0])):])]

def save(fileName, __record):
    _file = open(fileName, "w")
    _file.write(str(__record[0]) +  " [" + ','.join(str(e) for e in __record[1]) + "]")
    _file.close()

if exists(saveFileName):
    record = load(saveFileName)

#top bottom left right
def generateGen(n = 8): #Генерация гена
    global GenLength
    m = []
    for _ in range(n):
        m.append([randrange(-1, GenLength - 1, 1), randrange(-1, GenLength - 1, 1), randrange(-1, GenLength - 1, 1), randrange(-1, GenLength - 1, 1)])
    return m

def generateColor(l = 3): #Генерация цвета
    rt = "#"
    m = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "a", "b", "c", "d", "e", "f"]
    for _ in range(l):
        rt += m[randrange(0, len(m) - 1, 1)]
    return rt

def Log(LogString):
    global AllowLog
    if AllowLog:
        print("[LOG]", LogString)

#TODO: Сделать свой randrange() через random()
#TODO: Сделать просмотр дерева через геном P.S. В версии 2.0 это будет =)


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
        global c
        c.delete(self.this)

class wood(object): #Дерево
    def __init__(self, energy, color, x, y, gen):
        global TotalMove
        self.energy = energy
        self.lifes = []
        self.color = color
        self.gen = gen
        self.time = TotalMove
        self.lifes.append(life(gen, x, y, 0, color))
    def getMoveEnergy(self): # Получить энергию за ход
        full = 0
        for j in range(len(self.lifes)):
            try:
                if self.lifes[j].type == 1:
                    full += MaxEnergy / (HEIGHT / (HEIGHT - self.lifes[j].y))
                #TODO: Если клетку перекрывает другая клетка - уменьшаем получаемую энергию
            except:
                pass
        return full

class session(object): #Для игры
    def __init__(self):
        self.woods = []
    def add_wood(self, color, x, y, gen): #Добавить дерево
        self.woods.append(wood(NEnergy, color, x, y, gen))
    def update(self): #Обновить
        global GenLength, saveFileName
        l = 0
        while l < len(self.woods):
            woody2 = self.woods[l]
            woody2.energy -= (len(woody2.lifes) * CellEnergy)
            if woody2.energy <= 0:
                cell26 = 0
                while cell26 < len(woody2.lifes):
                    cell = woody2.lifes[cell26]
                    if cell.type == 0:
                        Ngen = woody2.gen
                        if random() < MutationChance / 100: # Семечко мутирует
                            Ngen[randrange(0, GenLength - 1, 1)] = [randrange(-1, GenLength - 1, 1), randrange(-1, GenLength - 1, 1), randrange(-1, GenLength - 1, 1), randrange(-1, GenLength - 1, 1)]
                        free = True
                        for w in range(len(self.woods)):
                            woody3 = self.woods[w]
                            if w == l:
                                continue
                            for c in range(len(woody3.lifes)):
                                cell22 = woody3.lifes[c]
                                if cell22.x == cell.x and cell22.y == BOTTOM:
                                    free = False
                        if free:
                            self.add_wood(generateColor(3), cell.x, BOTTOM, Ngen)
                    woody2.lifes[cell26].kill()
                    cell26 += 1
                if record[0] < TotalMove - self.woods[l].time:
                    save(saveFileName, [TotalMove - self.woods[l].time, self.woods[l].gen])
                    record[0] = TotalMove - self.woods[l].time
                    record[1] = self.woods[l].gen
                del self.woods[l]
            else:
                self.woods[l].energy += woody2.getMoveEnergy()

            l += 1
        
        #Алгоритм - анти-вымирание
        if len(self.woods) == 0:
            self.add_wood(generateColor(3), CENTER, BOTTOM, generateGen(GenLength))
            Log("Анти вымирание")
        #/////////////////////////
    
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
                            if nX < 0 or nX + SEG_SIZE > WIDTH or nY < 0 or nY + SEG_SIZE - 3 > HEIGHT: #если клетка не за границей поля
                                nL = 0
                            for a in range(len(self.woods)): # Для дерева
                                for b in range(len(self.woods[a].lifes)): # для каждой клетки
                                    if nX == self.woods[a].lifes[b].x and nY == self.woods[a].lifes[b].y:
                                        nL = 0
                            if nL: #Если клетка свободна
                                self.woods[k].lifes.append(life(tf.gen, nX, nY, Gen[g], self.woods[k].color))
                        if Gen != [-1, -1, -1, -1]:
                            tf.type = 1
                            tf.kill()
                            tf.this = c.create_rectangle(tf.x, tf.y, tf.x + SEG_SIZE - 1, tf.y + SEG_SIZE - 1, fill = tf.color, outline = tf.color)
        return True

default = [] #Ген по умолчанию
if exists(saveFileName):
    default = load(saveFileName)[1]
else:
    default = generateGen(GenLength)

game = session()
game.add_wood("#00f", CENTER, BOTTOM, default) #Первое дерево

srtTime = time()
allTime = time()
counter = 0

def progress():
    global FPS, allTime, srtTime, CounterMax, counter, record, TotalMove
    if game.sexAll():
        game.update()
    if counter == CounterMax:
        print("Время хода", round((time() - srtTime) / CounterMax, 3), "секунд")
        print("FPS:", 1 / ((time() - srtTime) / CounterMax))
        srtTime = time()
        print("Время симуляции", round(time() - allTime, 3), "секунд", "/", TotalMove, "ходов")
        print("Количество деревьев", len(game.woods))
        print("Рекорд жизни", round(record[0], 1), "ходов")
        print("Лучший ген", record[1])
        print(" ")
        counter = 0
    else:
        counter += 1
    TotalMove += 1

    root.after(int(1000/FPS), progress)

progress()

root.mainloop()
