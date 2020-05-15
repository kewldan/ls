#     Gen viewer     #
#   Просмотр генома  #
# От Avenger/kewldan #
#     Version 1.3    #
#     15.05.2020     #

from math import floor
from tkinter import Tk, Canvas

root = Tk()
root.title("Gen viewer")
gen = eval(input("Введите геном: "))

#НАСТРОЙКИ
WIDTH = 1280 #Ширина экрана в пикселях # 1280
HEIGHT = 720 #Высота экрана в пикселях # 720
SEG_SIZE = 10 #Размер одной клетки # 10
BACKGROUND = "#000" #Цвет фона # "#000"
Nenergy = 300 #Начальная энергия # 300
MustEnergy = 8 #Сколько клетка сжигает энергии за ход # 8
#/////////

#ФОРМУЛЫ
CENTER = WIDTH / 2 // SEG_SIZE * SEG_SIZE #Формула для расчёта центра x
BOTTOM = HEIGHT // SEG_SIZE * SEG_SIZE - SEG_SIZE + 2 #Формула для расчёта пола симуляции
#///////

c = Canvas(root, width = WIDTH, height = HEIGHT, bg = BACKGROUND)
c.grid()
c.focus_set()
GenLength = len(gen)
class life(object): #Жызн
    def __init__(self, gen, x, y, prog, color):
        self.type = 0
        self.x = x
        self.y = y
        self.gen = gen
        self.progress = prog
        self.color = color
        self.this = c.create_rectangle(x, y, x + SEG_SIZE - 1, y + SEG_SIZE - 1, fill = "#fff", outline = "#fff")
    def kill(self): #Удаление с поля
        c.delete(self.this)
class wood(object): #Дерево
    def __init__(self, color, x, y, gen):
        self.lifes = []
        self.color = color
        self.gen = gen
        self.energy = Nenergy
        self.status = True
        self.lifes.append(life(gen[0], x, y, 0, color))
    def update(self):
        if self.status == False:
            return
        for d in range(len(self.lifes)): #Для каждой клетки дерева
            tf = self.lifes[d]
            if tf.type == 0: #Если это стволовая клетка
                Gen = tf.gen # Gen = [0, 1, 2, 3] # Выбираю ген
                for g in range(len(Gen)): # G = 1 # Для каждой цифры в гене
                    if Gen[g] < GenLength: # Если ген не пустой
                        b = [[0, -1 * SEG_SIZE], [0, 1 * SEG_SIZE], [-1 * SEG_SIZE, 0], [1 * SEG_SIZE, 0]] # координаты ВВЕРХ, ВНИЗ, ЛЕВО, ПРАВО
                        nX = tf.x + b[g][0] # Получение X
                        nY = tf.y + b[g][1] # Получение Y
                        nL = 1
                        if nX < 0 or nX + SEG_SIZE > WIDTH or nY < 0 or nY + SEG_SIZE - 3 > HEIGHT: #если клетка не за границей поля
                            nL = 0
                        for b in range(len(self.lifes)): # для каждой клетки
                            if nX == self.lifes[b].x and nY == self.lifes[b].y:
                                nL = 0
                        if nL: #Если клетка свободна
                            self.lifes.append(life(self.gen[Gen[g]], nX, nY, Gen[g], self.color))
                    tf.type = 1
                    tf.kill()
                    tf.this = c.create_rectangle(tf.x, tf.y, tf.x + SEG_SIZE - 1, tf.y + SEG_SIZE - 1, fill = tf.color, outline = tf.color)
        full = 0
        for j in range(len(self.lifes)):
            try:
               if self.lifes[j].type == 1:
                    minus = 3
                    for v in range(len(self.lifes)): #Для каждой клетки дерева
                        if self.lifes[v].x == self.lifes[j].x and self.lifes[v].y < self.lifes[j].y: #Если клетка надо мной то
                            if minus:
                                minus -= 1
                    full += (HEIGHT // SEG_SIZE - self.lifes[v].y // SEG_SIZE) * minus
            except:
                pass
        self.energy += full
        print(self.energy)
        self.energy -= len(self.lifes) * MustEnergy
        return True
woody = wood("#0f0", CENTER, BOTTOM, gen)
def main():
    global woody
    if woody.update():
        if woody.energy >= 0:
            root.after(10, main)
        else:
            woody.status = False
            print("Симуляция завершена")
main()
root.mainloop()