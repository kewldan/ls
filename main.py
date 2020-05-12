#   Life Simulation  #
#   Симуляция жизни  #
# От Avenger/kewldan #
#     Version 1.2    #
#     11.05.2020     #

from tkinter import Tk, Canvas #Для визуализации
from random import randrange, random #Для случайных чисел
from math import floor, sqrt #Для математических действий
from time import time #Для времени
from os.path import exists #Для работы с File System

root = Tk() #Создаю окно
root.title("Life simulation")

#НАСТРОЙКИ
#НАЗВАНИЕ = ЗНАЧЕНИЕ #ЧТО МЕНЯЕТ # ЗНАЧЕНИЕ ПО УМОЛЧАНИЮ
SEG_SIZE = 6 #Размер клетки # 6
WIDTH = 128 #Ширина окна # 128
HEIGHT = 128 #Высота окна # 128
BACKGROUND = "#000" #Цвет фона # "#000"
FPS = 30 #Количество обновлений экрана в секунду #30
MutationChance = 25 #Шанс мутации # 25
NEnergy = 300 #Начальная энергия семечка # 300
CellEnergy = 13 #Количество потребляемой энергии на клетку # 13
criticalAge = 90 #Максимальный возраст дерева # 90
AllowLog = False #Включить логи (Не рекомендуется, снижает FPS) # False
#/////////

WIDTH *= SEG_SIZE
HEIGHT *= SEG_SIZE

#ГРАФИЧЕСКИЕ НАСТРОЙКИ
menuWidth = 32 #Ширина меню с информацией (В клетках) # 32
mainColor = "#55f" #Главный цвет # "#fff"
maxFPS = 60 #Максимальный FPS для slider
#/////////////////////

#ПРОДВИНУТЫЕ НАСТРОЙКИ (РЕДАКТИРОВАТЬ КРАЙНЕ НЕ РЕКОМЕНДУЕТСЯ)
CENTER = WIDTH / 2 // SEG_SIZE * SEG_SIZE #Формула для расчёта центра x
BOTTOM = HEIGHT // SEG_SIZE * SEG_SIZE - SEG_SIZE + 2 #Формула для расчёта низа/пола карты
LEFT = menuWidth #Формула для расчёта крайней левой стороны
GenLength = 16 #Длина генома
GenMax = 30 #Сумма пустых геномов (-1) + GenLength
saveFileName = "gen.txt" #Название файла для сохранения
record = [0, []] #Рекорд, в вторую клетку можно вписать свой стартовый геном
TotalMove = 0 #Счётчик ходов
#/////////////////////

menuWidth *= SEG_SIZE

c = Canvas(root, width = WIDTH + menuWidth, height = HEIGHT, bg = BACKGROUND)
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

if exists(saveFileName): #Если файл есть - загружаем данные из него
    record = load(saveFileName)

#top bottom left right
def generateGen(): #Генерация гена
    m = []
    for _ in range(GenLength):
        m.append([randrange(0, GenMax, 1), randrange(0, GenMax, 1), randrange(0, GenMax, 1), randrange(0, GenMax, 1)])
    return m

def generateColor(l = 3): #Генерация цвета
    rt = "#"
    m = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "a", "b", "c", "d", "e", "f"]
    for _ in range(l):
        rt += m[randrange(0, len(m) - 1, 1)]
    return rt

def Log(LogString):
    if AllowLog:
        print("[LOG]", LogString)

#TODO: Сделать свой randrange() через random() (Для оптимизации)
#TODO: Сделать просмотр дерева через геном P.S. В версии 2.0 это будет =)

class slider(object):
    def __init__(self, x, y, lineWidth, lineColor, ballColor, ballRadius, currentValue, maxValue):
        self.x = x
        self.y = y
        self.value = currentValue
        self.ballX = lineWidth / (maxValue / currentValue) + self.x
        self.ballR = ballRadius
        self.ballC = ballColor
        self.max = maxValue
        self.lw = lineWidth
        self.button = False
        self.this = {
            "main": c.create_line(x, y, x + lineWidth, y, fill = lineColor),
            "ball": c.create_oval(self.ballX - ballRadius, self.y - ballRadius, self.ballX + ballRadius, self.y + ballRadius, fill = ballColor, outline = ballColor)
        }
    def listener(self, event):
        if sqrt(((event.x - (self.ballX)) ** 2) + ((event.y - self.y) ** 2)) <= self.ballR:
            self.button = True
        else:
            self.button = False
    def listMove(self, event):
        x = event.x
        if self.button and x < self.x + self.lw and x > self.x:
            self.ballX = x
            self.value = round(self.max / ((self.lw) / (self.ballX - self.x)), 1)
            c.delete(self.this["ball"])
            self.this["ball"] = c.create_oval(self.ballX - self.ballR, self.y - self.ballR, self.ballX + self.ballR, self.y + self.ballR, fill = self.ballC, outline = self.ballC)
    def buttonRelease(self, event):
        self.button = False
    def allBind(self):
        root.bind("<Button-1>", self.listener)
        root.bind("<Motion>", self.listMove)
        root.bind("<ButtonRelease-1>", self.buttonRelease)


# 0 - white, 1 - green
class life(object): #Жызн
    def __init__(self, gen, x, y, prog, color):
        self.type = 0 #Тип клетки
        self.x = x
        self.y = y
        self.gen = gen
        self.progress = prog
        self.color = color
        self.this = c.create_rectangle(x + menuWidth, y, x + SEG_SIZE - 1 + menuWidth, y + SEG_SIZE - 1, fill = "#fff", outline = "#fff")
    def kill(self): #Удаление с поля
        c.delete(self.this)

class wood(object): #Дерево
    def __init__(self, energy, color, x, y, gen):
        self.energy = energy
        self.lifes = []
        self.color = color
        self.gen = gen
        self.time = TotalMove
        self.lifes.append(life(gen[0], x, y, 0, color))

class session(object): #Для игры
    def __init__(self):
        self.woods = []
        self.objStatic = {
            "line": c.create_line(menuWidth, 0, menuWidth, HEIGHT, fill = mainColor)
        } #Статические объекты
        self.objDynamic = {
            "FPS": c.create_text(menuWidth / 2, SEG_SIZE * 3, text = "0 FPS", fill = mainColor),
            "MT": c.create_text(menuWidth / 2, SEG_SIZE * 6, text = "Время хода: n мс", fill = mainColor),
            "TS": c.create_text(menuWidth / 2, SEG_SIZE * 9, text = "Всего: n сек / n ходов", fill = mainColor),
            "TW": c.create_text(menuWidth / 2, SEG_SIZE * 12, text = "Всего n деревьев", fill = mainColor),
            "RL": c.create_text(menuWidth / 2, SEG_SIZE * 15, text = "Рекордное время: n ходов", fill = mainColor),
            "TFPS": c.create_text(menuWidth / 2, SEG_SIZE * 18, text = "Max FPS: n", fill = mainColor),
            "CFPS": slider(menuWidth / 2 - menuWidth / 4, SEG_SIZE * 21, menuWidth / 2, mainColor, "#f00", 5, FPS, maxFPS)
        } #Объекты которые могут менятся
        self.objDynamic["CFPS"].allBind()
    def add_wood(self, color, x, y, gen): #Добавить дерево
        self.woods.append(wood(NEnergy, color, x, y, gen))
    def update(self): #Обновить
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
                            Ngen[randrange(0, GenLength - 1, 1)][randrange(0, 3, 1)] = randrange(0, GenMax, 1)
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
                full = 0
                for j in range(len(self.woods[l].lifes)):
                    try:
                        if self.lifes[j].type == 1:
                            minus = 3
                            for b in range(len(self.woods)): #Для каждого дерева
                                for v in range(len(self.woods[b].lifes)): #Для каждой клетки дерева
                                    if self.woods[b].lifes[v].x == self.woods[l].lifes[j].x and self.woods[b].lifes[v].y < self.woods[l].lifes[j].y: #Если клетка надо мной то
                                        if minus:
                                            minus -= 1
                            full += (WIDTH // SEG_SIZE - self.woods[b].lifes[v].y * SEG_SIZE) * minus
                    except:
                        pass
                self.woods[l].energy += full
            
            for q in range(len(self.woods)):
                if TotalMove - self.woods[q].time >= criticalAge:
                    cell26 = 0
                    while cell26 < len(woody2.lifes):
                        cell = woody2.lifes[cell26]
                        if cell.type == 0:
                            Ngen = woody2.gen
                            if random() < MutationChance / 100: # Семечко мутирует
                                Ngen[randrange(0, GenLength - 1, 1)][randrange(0, 3, 1)] = randrange(-1, GenMax, 1)
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
                    del self.woods[q]
            l += 1
        
        #Алгоритм - анти-вымирание
        if len(self.woods) == 0:
            self.add_wood(generateColor(3), CENTER, BOTTOM, generateGen())
            Log("Анти вымирание")
        #/////////////////////////
    def updateText(self, _fps, timeMove, tsS, tsM):
        c.delete(self.objDynamic["FPS"])
        self.objDynamic["FPS"] = c.create_text(menuWidth / 2, SEG_SIZE * 3, text = str(int(_fps)) + " FPS", fill = mainColor)
        c.delete(self.objDynamic["MT"])
        self.objDynamic["MT"] = c.create_text(menuWidth / 2, SEG_SIZE * 6, text = "Время хода: " + str(round(timeMove * 1000, 3)) + " мс", fill = mainColor)
        c.delete(self.objDynamic["TS"])
        self.objDynamic["TS"] = c.create_text(menuWidth / 2, SEG_SIZE * 9, text = "Всего: " + str(tsS) + " сек / " + str(tsM) + " ходов", fill = mainColor)
        c.delete(self.objDynamic["TW"])
        self.objDynamic["TW"] = c.create_text(menuWidth / 2, SEG_SIZE * 12, text = "Всего " + str(len(self.woods)) + " деревьев", fill = mainColor)
        c.delete(self.objDynamic["RL"])
        self.objDynamic["RL"] = c.create_text(menuWidth / 2, SEG_SIZE * 15, text = "Рекордное время: " + str(record[0]) + " ходов", fill = mainColor)
        c.delete(self.objDynamic["TFPS"])
        self.objDynamic["TFPS"] = c.create_text(menuWidth / 2, SEG_SIZE * 18, text = "Max FPS: " + str(int(self.objDynamic["CFPS"].value)), fill = mainColor)
    
    def sexAll(self): #Размножить всех
        for k in range(len(self.woods)): #Для каждого дерева
            for d in range(len(self.woods[k].lifes)): #Для каждой клетки дерева
                tf = self.woods[k].lifes[d]
                if tf.type == 0: #Если это стволовая клетка
                    Gen = tf.gen # Gen = [0, 1, 2, 3] # Выбираю ген
                    for g in range(len(Gen)): # G = 1 # Для каждой цифры в гене
                        if Gen[g] < GenLength: # Если ген не пустой
                            b = [[0, -1 * SEG_SIZE], [0, 1 * SEG_SIZE], [-1 * SEG_SIZE, 0], [1 * SEG_SIZE, 0]] # координаты ВВЕРХ, ВНИЗ, ЛЕВО, ПРАВО
                            nX = tf.x + b[g][0] # Получение X
                            nY = tf.y + b[g][1] # Получение Y
                            nL = 1
                            if nX < LEFT or nX + SEG_SIZE > WIDTH or nY < 0 or nY + SEG_SIZE - 3 > HEIGHT: #если клетка не за границей поля
                                nL = 0
                            for a in range(len(self.woods)): # Для дерева
                                for b in range(len(self.woods[a].lifes)): # для каждой клетки
                                    if nX == self.woods[a].lifes[b].x and nY == self.woods[a].lifes[b].y:
                                        nL = 0
                            if nL: #Если клетка свободна
                                self.woods[k].lifes.append(life(self.woods[k].gen[Gen[g]], nX, nY, Gen[g], self.woods[k].color))
                        tf.type = 1
                        tf.kill()
                        tf.this = c.create_rectangle(tf.x + menuWidth, tf.y, tf.x + SEG_SIZE - 1 + menuWidth, tf.y + SEG_SIZE - 1, fill = tf.color, outline = tf.color)
        return True

if exists(saveFileName):
    default = record[1]
else:
    default = generateGen()

game = session()
game.add_wood("#00f", CENTER, BOTTOM, default) #Первое дерево

srtTime = time() #Время начала хода
allTime = time() #Время старта

def progress():
    global srtTime, TotalMove, FPS
    FPS = int(game.objDynamic["CFPS"].value)
    if FPS <= 0:
        FPS = 1
    if game.sexAll():
        game.update()
        try:
            game.updateText(1 / (time() - srtTime), time() - srtTime, int(time() - allTime), TotalMove)
            srtTime = time()
        except:
            game.updateText(0, 0, int(time() - allTime), TotalMove)
    TotalMove += 1
    root.after(1000 // FPS, progress) #Вызываю через n мс

progress()

root.mainloop()