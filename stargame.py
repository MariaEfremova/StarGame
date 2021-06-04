import random, sys, copy, os, pygame
from pygame.locals import *

FPS = 30  # кадров в секунду для обновления экрана
WINWIDTH = 800  # ширина окна в пикселях
WINHEIGHT = 600  # высота окна в пикселях
HALF_WINWIDTH = int(WINWIDTH / 2)
HALF_WINHEIGHT = int(WINHEIGHT / 2)
icon = pygame.image.load('Stars2.png')
pygame.display.set_icon(icon)

# ширина и высота каждой фигуры
TILEWIDTH = 50
TILEHEIGHT = 85
TILEFLOORHEIGHT = 43

CAM_MOVE_SPEED = 1  # кол-во пикселей, которые меняется при передвижении

# процент наружной декорации
OUTSIDE_DECORATION_PCT = 20

BLUE = (92, 204, 204)
DARKBLUE = (0, 99, 99)
BGCOLOR = BLUE
TEXTCOLOR = DARKBLUE

UP = 'вверх'
DOWN = 'вниз'
LEFT = 'лево'
RIGHT = 'право'


def main():
    global FPSCLOCK, DISPLAYSURF, IMAGES, TILEMAPPING, OUTSIDEDECOMAPPING, BASICFONT, PLAYERIMAGES, currentImage

    # инициализация Pygame и настройка глобальных переменных
    pygame.init()
    FPSCLOCK = pygame.time.Clock()

    # поскольку Surface object и хранится в DISPLAYSURF
    # из функции pygame.display.set_mode()
    # это поверзностный объект появляется на экране компьютера
    # при вызове pygame.display.update ()

    DISPLAYSURF = pygame.display.set_mode((WINWIDTH, WINHEIGHT))

    pygame.display.set_caption('Звездная головоломка')
    BASICFONT = pygame.font.Font('freesansbold.ttf', 20)

    # поверхностнтыне объекты, возвращаемые  pygame.image.load().
    IMAGES = {'uncovered goal': pygame.image.load('BlueSelector.png'),
                  'covered goal': pygame.image.load('Selector.png'),
                  'star': pygame.image.load('Star.png'),
                  'corner': pygame.image.load('Wall_Block_Tall.png'),
                  'wall': pygame.image.load('Wood_Block_Tall.png'),
                  'inside floor': pygame.image.load('Plain_Block.png'),
                  'outside floor': pygame.image.load('Grass_Block.png'),
                  'title': pygame.image.load('star_title.png'),
                  'solved': pygame.image.load('star_solved.png'),
                  'frog': pygame.image.load('frog.png'),
                  'cat': pygame.image.load('cat.png'),
                  'hamster': pygame.image.load('hamster.png'),
                  'pig': pygame.image.load('pig.png'),
                  'dog': pygame.image.load('dog.png'),
                  'rock': pygame.image.load('Rock.png'),
                  'short tree': pygame.image.load('Tree_Short.png'),
                  'tall tree': pygame.image.load('Tree_Tall.png'),
                  'ugly tree': pygame.image.load('Tree_Ugly.png')}

    # эти значения dict являются глобальными и отображают символы в текстовом файле

    TILEMAPPING = {'x': IMAGES['corner'],
                   '#': IMAGES['wall'],
                   'o': IMAGES['inside floor'],
                   ' ': IMAGES['outside floor']}
    OUTSIDEDECOMAPPING = {'1': IMAGES['rock'],
                          '2': IMAGES['short tree'],
                          '3': IMAGES['tall tree'],
                          '4': IMAGES['ugly tree']}

    # PLAYERIMAGES - все возможные персонажи, которыми может быть игрок.
    # currentImage - индекс текущего изображения игрока.
    currentImage = 0
    PLAYERIMAGES = [IMAGES['frog'],
                    IMAGES['cat'],
                    IMAGES['hamster'],
                    IMAGES['pig'],
                    IMAGES['dog']]

    startScreen()  # показывает начальный экран игры, пока игрок не нажмет клавишу для старта.

    # уровни из текстового файла readLevelsFile()

    levels = readLevelsFile('starPusherLevels.txt')
    currentLevelIndex = 0

    # основной игровой цикл. этот цикл выполняется.
    # когда пользователь завершает уровень, следующий/предыдущий цикл загружается.

    while True:  # основной игровой цикл
        # запуск уровня, для начала игры
        result = runLevel(levels, currentLevelIndex)

        if result in ('solved', 'next'):
            # перейти на следующий уровень
            currentLevelIndex += 1
            if currentLevelIndex >= len(levels):
                # если уровней больше нет, то вернется к первому уровню
                currentLevelIndex = 0
        elif result == 'back':
            # перейти на предыдущий уровень
            currentLevelIndex -= 1
            if currentLevelIndex < 0:
                # если предыдущих уровней нет, то перейдет к последнему.
                currentLevelIndex = len(levels) - 1
        elif result == 'reset':
            pass  # Loop повторно вызывает runLevel() для сброса уровня.


def runLevel(levels, levelNum):
    global currentImage
    levelObj = levels[levelNum]
    mapObj = decorateMap(levelObj['mapObj'], levelObj['startState']['player'])
    gameStateObj = copy.deepcopy(levelObj['startState'])
    mapNeedsRedraw = True  # установить значерие True для вызова drawMap()
    levelSurf = BASICFONT.render('Уровень %s из %s' % (levelNum + 1, len(levels)), 1, TEXTCOLOR)
    levelRect = levelSurf.get_rect()
    levelRect.bottomleft = (20, WINHEIGHT - 35)
    mapWidth = len(mapObj) * TILEWIDTH
    mapHeight = (len(mapObj[0]) - 1) * TILEFLOORHEIGHT + TILEHEIGHT
    MAX_CAM_X_PAN = abs(HALF_WINHEIGHT - int(mapHeight / 2)) + TILEWIDTH
    MAX_CAM_Y_PAN = abs(HALF_WINWIDTH - int(mapWidth / 2)) + TILEHEIGHT

    levelIsComplete = False

    # отслеживание, насколько перемещается камера:
    cameraOffsetX = 0
    cameraOffsetY = 0

    # отслеживание, удерживаются ли клавиши для перемещения камеры:
    cameraUp = False
    cameraDown = False
    cameraLeft = False
    cameraRight = False

    while True:  # основной игровой цикл
        # сброс переменных:
        playerMoveTo = None
        keyPressed = False

        for event in pygame.event.get():  # цикл обработки события
            if event.type == QUIT:
                # игрок нажал "X" в углу окна.
                terminate()

            elif event.type == KEYDOWN:
                # обработка нажатия клавиш
                keyPressed = True
                if event.key == K_LEFT:
                    playerMoveTo = LEFT
                elif event.key == K_RIGHT:
                    playerMoveTo = RIGHT
                elif event.key == K_UP:
                    playerMoveTo = UP
                elif event.key == K_DOWN:
                    playerMoveTo = DOWN

                # режим движения камеры
                elif event.key == K_a:
                    cameraLeft = True
                elif event.key == K_d:
                    cameraRight = True
                elif event.key == K_w:
                    cameraUp = True
                elif event.key == K_s:
                    cameraDown = True

                elif event.key == K_n:
                    return 'next'
                elif event.key == K_b:
                    return 'back'

                elif event.key == K_ESCAPE:
                    terminate()  # Esc - зевершение работы
                elif event.key == K_BACKSPACE:
                    return 'reset'  # сброс уровня
                elif event.key == K_p:
                    # сменить изображение персонажа на следующее
                    currentImage += 1
                    if currentImage >= len(PLAYERIMAGES):
                        # после последнего изображения персонажа переключаетмся на первого персонажа.
                        currentImage = 0
                    mapNeedsRedraw = True

            elif event.type == KEYUP:
                # отключить режим движения камеры.
                if event.key == K_a:
                    cameraLeft = False
                elif event.key == K_d:
                    cameraRight = False
                elif event.key == K_w:
                    cameraUp = False
                elif event.key == K_s:
                    cameraDown = False

        if playerMoveTo != None and not levelIsComplete:
            # если игрок нажал клавишу, чтобы переместиться, сделайте ход
            # и двигайте любые звезды.
            moved = makeMove(mapObj, gameStateObj, playerMoveTo)

            if moved:
                # счетчик шагов
                gameStateObj['stepCounter'] += 1
                mapNeedsRedraw = True

            if isLevelFinished(levelObj, gameStateObj):
                # уровень пройден, показывается изображение "уровень пройден"
                levelIsComplete = True
                keyPressed = False

        DISPLAYSURF.fill(BGCOLOR)

        if mapNeedsRedraw:
            mapSurf = drawMap(mapObj, gameStateObj, levelObj['goals'])
            mapNeedsRedraw = False

        if cameraUp and cameraOffsetY < MAX_CAM_X_PAN:
            cameraOffsetY += CAM_MOVE_SPEED
        elif cameraDown and cameraOffsetY > -MAX_CAM_X_PAN:
            cameraOffsetY -= CAM_MOVE_SPEED
        if cameraLeft and cameraOffsetX < MAX_CAM_Y_PAN:
            cameraOffsetX += CAM_MOVE_SPEED
        elif cameraRight and cameraOffsetX > -MAX_CAM_Y_PAN:
            cameraOffsetX -= CAM_MOVE_SPEED

        # настроить объект Rect в зависимости от движения камеры.
        mapSurfRect = mapSurf.get_rect()
        mapSurfRect.center = (HALF_WINWIDTH + cameraOffsetX, HALF_WINHEIGHT + cameraOffsetY)

        # рисуем mapSurf на DISPLAYSURF Surface.
        DISPLAYSURF.blit(mapSurf, mapSurfRect)

        DISPLAYSURF.blit(levelSurf, levelRect)
        stepSurf = BASICFONT.render('Шаги: %s' % (gameStateObj['stepCounter']), 1, TEXTCOLOR)
        stepRect = stepSurf.get_rect()
        stepRect.bottomleft = (20, WINHEIGHT - 10)
        DISPLAYSURF.blit(stepSurf, stepRect)

        if levelIsComplete:
            # уровень пройден. изображение "уровень пройден" остается
            # пока игрок не нажмет клавишу
            solvedRect = IMAGES['solved'].get_rect()
            solvedRect.center = (HALF_WINWIDTH, HALF_WINHEIGHT)
            DISPLAYSURF.blit(IMAGES['solved'], solvedRect)

            if keyPressed:
                return 'solved'

        pygame.display.update()  # draw DISPLAYSURF to the screen.
        FPSCLOCK.tick()


def isWall(mapObj, x, y):
    ""
    if x < 0 or x >= len(mapObj) or y < 0 or y >= len(mapObj[x]):
        return False  # x and y aren't actually on the map.
    elif mapObj[x][y] in ('#', 'x'):
        return True  # wall is blocking
    return False


def decorateMap(mapObj, startxy):
    startx, starty = startxy

    # копия карты, чтоб не менялся оригинал
    mapObjCopy = copy.deepcopy(mapObj)

    # удаление символов, которые не являются стенами карты
    for x in range(len(mapObjCopy)):
        for y in range(len(mapObjCopy[0])):
            if mapObjCopy[x][y] in ('$', '.', '@'):
                mapObjCopy[x][y] = ' '

    # Заливка для определения внутренней или внешней плитки пола
    floodFill(mapObjCopy, startx, starty, ' ', 'o')

    # преобразовывает стены в плитку
    for x in range(len(mapObjCopy)):
        for y in range(len(mapObjCopy[0])):

            if mapObjCopy[x][y] == '#':
                if (isWall(mapObjCopy, x, y - 1) and isWall(mapObjCopy, x + 1, y)) or \
                        (isWall(mapObjCopy, x + 1, y) and isWall(mapObjCopy, x, y + 1)) or \
                        (isWall(mapObjCopy, x, y + 1) and isWall(mapObjCopy, x - 1, y)) or \
                        (isWall(mapObjCopy, x - 1, y) and isWall(mapObjCopy, x, y - 1)):
                    mapObjCopy[x][y] = 'x'

            elif mapObjCopy[x][y] == ' ' and random.randint(0, 99) < OUTSIDE_DECORATION_PCT:
                mapObjCopy[x][y] = random.choice(list(OUTSIDEDECOMAPPING.keys()))

    return mapObjCopy


def isBlocked(mapObj, gameStateObj, x, y):
    """Возвращает True если положение (x, y) на карте заблокировано стеноц или звездой."""

    if isWall(mapObj, x, y):
        return True

    elif x < 0 or x >= len(mapObj) or y < 0 or y >= len(mapObj[x]):
        return True  # x and y aren't actually on the map.

    elif (x, y) in gameStateObj['stars']:
        return True  # a star is blocking

    return False


def makeMove(mapObj, gameStateObj, playerMoveTo):
    # игрок двигается в нужном направлении
    playerx, playery = gameStateObj['player']

    stars = gameStateObj['stars']

    # используем переменные xOffset и yOffset для направления персонажа
    if playerMoveTo == UP:
        xOffset = 0
        yOffset = -1
    elif playerMoveTo == RIGHT:
        xOffset = 1
        yOffset = 0
    elif playerMoveTo == DOWN:
        xOffset = 0
        yOffset = 1
    elif playerMoveTo == LEFT:
        xOffset = -1
        yOffset = 0

    # проверяем, может ли персонаж двигаться в нужном направлении
    if isWall(mapObj, playerx + xOffset, playery + yOffset):
        return False
    else:
        if (playerx + xOffset, playery + yOffset) in stars:
            # проверка, сможет ли игрок толкнуть звезду
            if not isBlocked(mapObj, gameStateObj, playerx + (xOffset * 2), playery + (yOffset * 2)):
                # перемещение звезды
                ind = stars.index((playerx + xOffset, playery + yOffset))
                stars[ind] = (stars[ind][0] + xOffset, stars[ind][1] + yOffset)
            else:
                return False

        gameStateObj['player'] = (playerx + xOffset, playery + yOffset)
        return True


def startScreen():
    """Отображется начальный экран."""

    # размещение изображения заголовка
    titleRect = IMAGES['title'].get_rect()
    topCoord = 20  # положение верхней части текста
    titleRect.top = topCoord
    titleRect.centerx = HALF_WINWIDTH
    topCoord += titleRect.height

    instructionText = ['Нажмите любую клавишу для старта.',
                       'Для прохождения уровня двигайте звездочку на нужное место.',
                       'Используйте клавиши со стрелками для перемещения фигур.',
                       'P - смена персонажа.',
                       'N - следующий уровень.',
                       'B - вернуться на предыдущий уровень.',
                       'Backspace - сброса уровня. Esc - выход из игры.', ]

    # Start with drawing a blank color to the entire window:
    DISPLAYSURF.fill(BGCOLOR)

    DISPLAYSURF.blit(IMAGES['title'], titleRect)

    for i in range(len(instructionText)):
        instSurf = BASICFONT.render(instructionText[i], 1, TEXTCOLOR)
        instRect = instSurf.get_rect()
        topCoord += 20  # расстояние между строчками в заголовке
        instRect.top = topCoord
        instRect.centerx = HALF_WINWIDTH
        topCoord += instRect.height
        DISPLAYSURF.blit(instSurf, instRect)

    while True:  # основной цикл начального экрана
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    terminate()
                return

        # отображение DISPLAYSURF на реальном экране
        pygame.display.update()
        FPSCLOCK.tick()


def readLevelsFile(filename):
    assert os.path.exists(filename), 'Cannot find the level file: %s' % (filename)
    mapFile = open(filename, 'r')
    content = mapFile.readlines() + ['\r\n']
    mapFile.close()

    levels = []  # сожержит список объектов уровня
    levelNum = 0
    mapTextLines = []  # содержит линии для карты одного уровня
    mapObj = []  # объекты карты, созданные из данных mapTextLines
    for lineNum in range(len(content)):
        # обработка каждый строки, которая была в файле уровня
        line = content[lineNum].rstrip('\r\n')

        if ';' in line:
            # игнорировать ; в текстовом файле с уровнями
            line = line[:line.find(';')]

        if line != '':
            mapTextLines.append(line)
        elif line == '' and len(mapTextLines) > 0:
            # пустая строка означает конец карты в файле
            # преобразование текста в mapTextLines в объект уровня

            maxWidth = -1
            for i in range(len(mapTextLines)):
                if len(mapTextLines[i]) > maxWidth:
                    maxWidth = len(mapTextLines[i])
            # если добавить пробелы в конце коротких строк, карты будет более прямоугольной.
            for i in range(len(mapTextLines)):
                mapTextLines[i] += ' ' * (maxWidth - len(mapTextLines[i]))

            # преобразование mapTextLines в объекты карты
            for x in range(len(mapTextLines[0])):
                mapObj.append([])
            for y in range(len(mapTextLines)):
                for x in range(maxWidth):
                    mapObj[x].append(mapTextLines[y][x])

            startx = None  # x и y для начальной позиции игрока
            starty = None
            goals = []
            stars = []
            for x in range(maxWidth):
                for y in range(len(mapObj[x])):
                    if mapObj[x][y] in ('@', '+'):
                        startx = x
                        starty = y
                    if mapObj[x][y] in ('.', '+', '*'):
                        goals.append((x, y))
                    if mapObj[x][y] in ('$', '*'):
                        stars.append((x, y))

            # проверка работочпособности уровней
            assert startx != None and starty != None, 'Level %s (around line %s) in %s is missing a "@" or "+" to mark the start point.' % (
                levelNum + 1, lineNum, filename)
            # если отсутствует @ или +, игра не запускается
            assert len(goals) > 0, 'Level %s (around line %s) in %s must have at least one goal.' % (
                levelNum + 1, lineNum, filename)
            # уровень должен иметь хоть одну цель для завершения
            assert len(stars) >= len(
                goals), 'Level %s (around line %s) in %s is impossible to solve. It has %s goals but only %s stars.' % (
                levelNum + 1, lineNum, filename, len(goals), len(stars))
            # уровень нельзя пройти, если нет конечной точки

            # создать объект уровня и объект состояния запуска игры
            gameStateObj = {'player': (startx, starty),
                            'stepCounter': 0,
                            'stars': stars}
            levelObj = {'width': maxWidth,
                        'height': len(mapObj),
                        'mapObj': mapObj,
                        'goals': goals,
                        'startState': gameStateObj}

            levels.append(levelObj)

            # сбросить переменные для чтения следующей карты
            mapTextLines = []
            mapObj = []
            gameStateObj = {}
            levelNum += 1
    return levels


def floodFill(mapObj, x, y, oldCharacter, newCharacter):
    if mapObj[x][y] == oldCharacter:
        mapObj[x][y] = newCharacter

    if x < len(mapObj) - 1 and mapObj[x + 1][y] == oldCharacter:
        floodFill(mapObj, x + 1, y, oldCharacter, newCharacter)  # вызов справа
    if x > 0 and mapObj[x - 1][y] == oldCharacter:
        floodFill(mapObj, x - 1, y, oldCharacter, newCharacter)  # вызов слева
    if y < len(mapObj[x]) - 1 and mapObj[x][y + 1] == oldCharacter:
        floodFill(mapObj, x, y + 1, oldCharacter, newCharacter)  # вызов вниз
    if y > 0 and mapObj[x][y - 1] == oldCharacter:
        floodFill(mapObj, x, y - 1, oldCharacter, newCharacter)  # вызов вверх


def drawMap(mapObj, gameStateObj, goals):
    # mapSurf будет единственным объеком Surface на котором рисуются плитки.
    # вся карта размещается на DISPLAYSURF
    # сначала необходимо рассчитать ширину и высоту
    mapSurfWidth = len(mapObj) * TILEWIDTH
    mapSurfHeight = (len(mapObj[0]) - 1) * TILEFLOORHEIGHT + TILEHEIGHT
    mapSurf = pygame.Surface((mapSurfWidth, mapSurfHeight))
    mapSurf.fill(BGCOLOR)  # начать с пустого цвета на поверхности

    for x in range(len(mapObj)):
        for y in range(len(mapObj[x])):
            spaceRect = pygame.Rect((x * TILEWIDTH, y * TILEFLOORHEIGHT, TILEWIDTH, TILEHEIGHT))
            if mapObj[x][y] in TILEMAPPING:
                baseTile = TILEMAPPING[mapObj[x][y]]
            elif mapObj[x][y] in OUTSIDEDECOMAPPING:
                baseTile = TILEMAPPING[' ']

            # сначала рисуется основная плитка пола/стены
            mapSurf.blit(baseTile, spaceRect)

            if mapObj[x][y] in OUTSIDEDECOMAPPING:
                # рисуются урашения, которые есть на этой плитке
                mapSurf.blit(OUTSIDEDECOMAPPING[mapObj[x][y]], spaceRect)
            elif (x, y) in gameStateObj['stars']:
                if (x, y) in goals:
                    # A goal AND star are on this space, draw goal first.
                    mapSurf.blit(IMAGES['covered goal'], spaceRect)
                mapSurf.blit(IMAGES['star'], spaceRect)
            elif (x, y) in goals:
                mapSurf.blit(IMAGES['uncovered goal'], spaceRect)

            # последний выход игрока
            if (x, y) == gameStateObj['player']:
                mapSurf.blit(PLAYERIMAGES[currentImage], spaceRect)

    return mapSurf


def isLevelFinished(levelObj, gameStateObj):
    # возвращается изначальное значение, если все цели отмечены звездами.
    for goal in levelObj['goals']:
        if goal not in gameStateObj['stars']:
            # нашли пространство с целью,он без звезды
            return False
    return True


def terminate():
    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
