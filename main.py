#   Life Simulation  #
#   Симуляция жизни  #
# От Avenger/kewldan #
#     Version 1.3    #
#     15.05.2020     #

from tkinter import Tk, Canvas #Для визуализации
from random import randrange, random #Для случайных чисел
from math import floor, sqrt #Для математических действий
from time import time #Для времени
from os.path import exists #Для работы с File System

#НАСТРОЙКИ
#НАЗВАНИЕ = ЗНАЧЕНИЕ #ЧТО МЕНЯЕТ # ЗНАЧЕНИЕ ПО УМОЛЧАНИЮ
SEG_SIZE = 6 #Размер клетки # 6
WIDTH = 128 #Ширина окна # 128
HEIGHT = 128 #Высота окна # 128
BACKGROUND = "#000" #Цвет фона # "#000"
FPS = 30 #Количество обновлений экрана в секунду #30
MutationChance = 25 #Шанс мутации # 25
NEnergy = 300 #Начальная энергия семечка # 300
CellEnergy = 8 #Количество потребляемой энергии на клетку # 8
criticalAge = 90 #Максимальный возраст дерева # 90
AllowLog = False #Включить логи (Не рекомендуется, снижает FPS) # False
#/////////

WIDTH *= SEG_SIZE
HEIGHT *= SEG_SIZE

#ГРАФИЧЕСКИЕ НАСТРОЙКИ
menuWidth = 32 #Ширина меню с информацией (В клетках) # 32
mainColor = "#fff" #Главный цвет # "#fff"
maxFPS = 60 #Максимальный FPS для slider # 60
#/////////////////////

#ПРОДВИНУТЫЕ НАСТРОЙКИ (РЕДАКТИРОВАТЬ КРАЙНЕ НЕ РЕКОМЕНДУЕТСЯ!)
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

#TODO: Сделать просмотр дерева через геном P.S. В версии 1.3 это будет =)

class slider(object):
    def __init__(self, x, y, lineWidth, lineColor, ballColor, ballRadius, currentValue, maxValue):
        self.x = x
        self.y = y
        self.value = currentValue
        self.ballX = lineWidth / (maxValue / currentValue) + self.x
        self.lc = lineColor
        self.ballR = ballRadius
        self.ballC = ballColor
        self.max = maxValue
        self.lw = lineWidth
        self.button = False
    def listener(self, event):
        if sqrt(((event.x - (self.ballX)) ** 2) + ((event.y - self.y) ** 2)) <= self.ballR:
            self.button = True
        else:
            self.button = False
    def buttonRelease(self, event):
        self.button = False


# 0 - white, 1 - green
class life(object): #Жызн
    def __init__(self, gen, x, y, prog, color):
        self.type = 0 #Тип клетки
        self.x = x
        self.y = y
        self.gen = gen
        self.progress = prog
        self.color = color

class wood(object): #Дерево
    def __init__(self, energy, color, x, y, gen):
        self.energy = energy
        self.lifes = []
        self.color = color
        self.gen = gen
        self.time = TotalMove

class session(object): #Для игры
    def __init__(self, record):
        self.woods = []
        self.root = Tk() #Создаю окно
        self.root.title("Life simulation") #Называю окно
        self.c = Canvas(self.root, width = WIDTH + menuWidth, height = HEIGHT, bg = BACKGROUND) #Создаю канвас
        self.c.grid() #В центр окна
        self.c.focus_set() #Устанавливаю фокус
        self.objStatic = {
            "line": self.c.create_line(menuWidth, 0, menuWidth, HEIGHT, fill = mainColor)
        } #Статические объекты
        self.objDynamic = {
            "FPS": self.c.create_text(menuWidth / 2, SEG_SIZE * 3, text = "0 FPS", fill = mainColor),
            "MT": self.c.create_text(menuWidth / 2, SEG_SIZE * 6, text = "Время хода: n мс", fill = mainColor),
            "TS": self.c.create_text(menuWidth / 2, SEG_SIZE * 9, text = "Всего: n сек / n ходов", fill = mainColor),
            "TW": self.c.create_text(menuWidth / 2, SEG_SIZE * 12, text = "Всего n деревьев", fill = mainColor),
            "RL": self.c.create_text(menuWidth / 2, SEG_SIZE * 15, text = "Рекордное время: n ходов", fill = mainColor),
            "TFPS": self.c.create_text(menuWidth / 2, SEG_SIZE * 18, text = "Max FPS: n", fill = mainColor),
            "CFPS": slider(menuWidth / 2 - menuWidth / 4, SEG_SIZE * 21, menuWidth / 2, mainColor, "#f00", 5, FPS, maxFPS)
        } #Объекты которые могут менятся
        self.record = record
        self.objDynamic["CFPS"].this = {
            "main": self.c.create_line(self.objDynamic["CFPS"].x, self.objDynamic["CFPS"].y, self.objDynamic["CFPS"].x + self.objDynamic["CFPS"].lw, self.objDynamic["CFPS"].y, fill = self.objDynamic["CFPS"].lc),
            "ball": self.c.create_oval(self.objDynamic["CFPS"].ballX - self.objDynamic["CFPS"].ballR, self.objDynamic["CFPS"].y - self.objDynamic["CFPS"].ballR, self.objDynamic["CFPS"].ballX + self.objDynamic["CFPS"].ballR, self.objDynamic["CFPS"].y + self.objDynamic["CFPS"].ballR, fill = self.objDynamic["CFPS"].ballC, outline = self.objDynamic["CFPS"].ballC)
        }
        self.root.bind("<Button-1>", self.objDynamic["CFPS"].listener)
        self.root.bind("<Motion>", lambda event: self.sliderHandler(event, self.objDynamic["CFPS"]))
        self.root.bind("<ButtonRelease-1>", self.objDynamic["CFPS"].buttonRelease)
    def add_wood(self, color, x, y, gen): #Добавить дерево
        self.woods.append(wood(NEnergy, color, x, y, gen))
        self.woods[len(self.woods) - 1].lifes.append(life(gen[0], x, y, 0, color))
        self.woods[len(self.woods) - 1].lifes[len(self.woods[len(self.woods) - 1].lifes) - 1].this = self.c.create_rectangle(self.woods[len(self.woods) - 1].lifes[len(self.woods[len(self.woods) - 1].lifes) - 1].x + menuWidth, self.woods[len(self.woods) - 1].lifes[len(self.woods[len(self.woods) - 1].lifes) - 1].y, self.woods[len(self.woods) - 1].lifes[len(self.woods[len(self.woods) - 1].lifes) - 1].x + SEG_SIZE - 1 + menuWidth, self.woods[len(self.woods) - 1].lifes[len(self.woods[len(self.woods) - 1].lifes) - 1].y + SEG_SIZE - 1, fill = "#fff", outline = "#fff")
    def load(self, fileName): #Загрузить данные из файла
        if not exists(fileName):
            return
        _file = open(fileName, "r")
        text = _file.read()
        if text:
            self.record = [int(text.split()[0]), eval(text[len(str(text.split()[0])):])]
    def save(self, fileName): #Сохранить данные в файл
        _file = open(fileName, "w")
        _file.write(str(self.record[0]) +  " [" + ','.join(str(e) for e in self.record[1]) + "]")
        _file.close()
    def sliderHandler(self, event, object2):
        x = event.x
        if object2.button and x < object2.x + object2.lw and x > object2.x:
            object2.ballX = x
            object2.value = round(object2.max / ((object2.lw) / (object2.ballX - object2.x)), 1)
            self.c.delete(object2.this["ball"])
            object2.this["ball"] = self.c.create_oval(object2.ballX - object2.ballR, object2.y - object2.ballR, object2.ballX + object2.ballR, object2.y + object2.ballR, fill = object2.ballC, outline = object2.ballC)
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
                    self.c.delete(woody2.lifes[cell26].this)
                    cell26 += 1
                if record[0] < TotalMove - self.woods[l].time:
                    self.save(saveFileName)
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
                            full += (HEIGHT // SEG_SIZE - self.woods[b].lifes[v].y // SEG_SIZE) * minus
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
                        self.c.delete(woody2.lifes[cell26].this)
                        cell26 += 1
                    del self.woods[q]
            l += 1
        
        #Алгоритм - анти-вымирание
        if len(self.woods) == 0:
            self.add_wood(generateColor(3), CENTER, BOTTOM, generateGen()) #Добавляю дерево
            Log("Анти вымирание")
        #/////////////////////////
    def updateText(self, _fps, timeMove, tsS, tsM):
        self.c.delete(self.objDynamic["FPS"])
        self.objDynamic["FPS"] = self.c.create_text(menuWidth / 2, SEG_SIZE * 3, text = str(int(_fps)) + " FPS", fill = mainColor)
        self.c.delete(self.objDynamic["MT"])
        self.objDynamic["MT"] = self.c.create_text(menuWidth / 2, SEG_SIZE * 6, text = "Время хода: " + str(round(timeMove * 1000, 3)) + " мс", fill = mainColor)
        self.c.delete(self.objDynamic["TS"])
        self.objDynamic["TS"] = self.c.create_text(menuWidth / 2, SEG_SIZE * 9, text = "Всего: " + str(tsS) + " сек / " + str(tsM) + " ходов", fill = mainColor)
        self.c.delete(self.objDynamic["TW"])
        self.objDynamic["TW"] = self.c.create_text(menuWidth / 2, SEG_SIZE * 12, text = "Всего " + str(len(self.woods)) + " деревьев", fill = mainColor)
        self.c.delete(self.objDynamic["RL"])
        self.objDynamic["RL"] = self.c.create_text(menuWidth / 2, SEG_SIZE * 15, text = "Рекордное время: " + str(record[0]) + " ходов", fill = mainColor)
        self.c.delete(self.objDynamic["TFPS"])
        self.objDynamic["TFPS"] = self.c.create_text(menuWidth / 2, SEG_SIZE * 18, text = "Max FPS: " + str(int(self.objDynamic["CFPS"].value)), fill = mainColor)
    
    def sexAll(self): #Размножить всех
        for k in range(len(self.woods)): #Для каждого дерева
            for d in range(len(self.woods[k].lifes)): #Для каждой клетки дерева
                tf = self.woods[k].lifes[d] #Получаю клетку
                if tf.type == 0: #Если это стволовая клетка
                    Gen = tf.gen # Gen = [0, 1, 2, 3] # Выбираю ген
                    for g in range(len(Gen)): # G = 1 # Для каждой цифры в гене
                        if Gen[g] < GenLength: # Если ген не пустой
                            b = [[0, -1 * SEG_SIZE], [0, 1 * SEG_SIZE], [-1 * SEG_SIZE, 0], [1 * SEG_SIZE, 0]] # координаты ВВЕРХ, ВНИЗ, ЛЕВО, ПРАВО
                            nX = tf.x + b[g][0] # Получение X
                            nY = tf.y + b[g][1] # Получение Y
                            nL = 1 #Пока что можно размножатся
                            if nX < LEFT or nX + SEG_SIZE > WIDTH or nY < 0 or nY + SEG_SIZE - 3 > HEIGHT: #если клетка не за границей поля
                                nL = 0 #Уже нельзя
                            for a in range(len(self.woods)): # Для дерева
                                for b in range(len(self.woods[a].lifes)): # для каждой клетки
                                    if nX == self.woods[a].lifes[b].x and nY == self.woods[a].lifes[b].y: #Если на этой позиции уже есть клетка
                                        nL = 0 #Уже нельзя
                            if nL: #Если клетка свободна
                                self.woods[k].lifes.append(life(self.woods[k].gen[Gen[g]], nX, nY, Gen[g], self.woods[k].color)) #Добовляю клетку в массив дерева
                                self.woods[k].lifes[len(self.woods[k].lifes) - 1].this = self.c.create_rectangle(self.woods[len(self.woods) - 1].lifes[len(self.woods[len(self.woods) - 1].lifes) - 1].x + menuWidth, self.woods[len(self.woods) - 1].lifes[len(self.woods[len(self.woods) - 1].lifes) - 1].y, self.woods[len(self.woods) - 1].lifes[len(self.woods[len(self.woods) - 1].lifes) - 1].x + SEG_SIZE - 1 + menuWidth, self.woods[len(self.woods) - 1].lifes[len(self.woods[len(self.woods) - 1].lifes) - 1].y + SEG_SIZE - 1, fill = "#fff", outline = "#fff")
                        tf.type = 1 #Тип клетки - зелёная
                        self.c.delete(tf.this) #Убиваю клетку (На канвасе)
                        tf.this = self.c.create_rectangle(tf.x + menuWidth, tf.y, tf.x + SEG_SIZE - 1 + menuWidth, tf.y + SEG_SIZE - 1, fill = tf.color, outline = tf.color) #Перерисовываю клетку
        return True

game = session(record) #Новая сессия
game.load(saveFileName)
if exists(saveFileName):
    default = game.record[1]
else:
    default = generateGen()
game.add_wood("#00f", CENTER, BOTTOM, default) #Первое дерево
srtTime = time() #Время начала хода
allTime = time() #Время старта

def progress():
    global srtTime, TotalMove, FPS
    FPS = int(game.objDynamic["CFPS"].value) #Беру значение с слайдераы
    if FPS <= 0: #Если FPS = 0 -> Делаю его равным 1
        FPS = 1
    if game.sexAll():
        game.update() #Обновляю игру
        try:
            game.updateText(1 / (time() - srtTime), time() - srtTime, int(time() - allTime), TotalMove) #Обновляю данные на экране
            srtTime = time()
        except:
            game.updateText(0, 0, int(time() - allTime), TotalMove)
    TotalMove += 1
    game.root.after(1000 // FPS, progress) #Вызываю через n мс
progress()
game.root.mainloop()