import time
import pygame as pg
import sys
import random
from PIL import Image, ImageDraw, ImageFont

# 파이게임 초기화
pg.init()
clock = 0

ScreenSize = (240, 240)
BackGroundSize = (1000, 240)

screen = pg.display.set_mode(ScreenSize)

font = ImageFont.load_default(size=15)
fontBig = ImageFont.load_default(size=30)

backgroundImage = Image.open('배경.png').convert('RGB')

# 배경 초기 위치
x_offset = 240

# 캐릭터 아이콘
character_icons = [
    Image.open("1렙멍_기본.png").convert('RGBA'),
    Image.open("2렙멍_기본.png").convert('RGBA'),
    Image.open("3렙멍_기본.png").convert('RGBA'),
]

# 각 아이콘 크기 조정 (필요 시)
for i in range(len(character_icons)):
    character_icons[i] = character_icons[i].resize((60, 60))

# 상태 변수
selected_tab = 'background'
selected_icon = 1
last_spawn_time = [0, 0, 0]
last_spawn_time_all = 0
last_spawn_time_enemy = 0
SPAWN_COOLDOWN = 20
SPAWN_COOLDOWN_ALL = 5

# 적 캐릭터 관리 변수
enemy_last_spawn_time = [0, 0]
enemy_spawn_intervals = [
    random.randint(50, 120),
    random.randint(100, 150)
]

characters = []
gold = 0


# 캐릭터 클래스
class Character:

    def __init__(self, img_walk, img_attack, img_death, pos, health):
        self.img = [
            img_walk,
            img_attack,
            img_death
        ]

        self.pos: list = pos
        self.health = health

        self.frame = 0 #random.randint(0, 10)

        self.speed = 0
        self.power = 0

        self.state = 0  # 0: walk, 1: attack, 2: death

        self.isEnemy = False

    def collide(self, other):
        next_x = self.pos[0] + self.speed
        self_left = next_x - self.img[0][0].width // 2
        self_right = next_x + self.img[0][0].width // 2
        other_left = other.pos[0] - other.img[0][0].width // 2
        other_right = other.pos[0] + other.img[0][0].width // 2

        if self_right > other_left and self_left < other_right:
            self.attack_ing = True
            return True
        else:
            self.attack_ing = False
            return False

    def draw(self, pallet: Image):
        tick = self.frame // 10 % len(self.img[self.state])
        img = self.img[self.state][tick]
        pallet.paste(
            img,
            (self.pos[0] - img.width // 2, self.pos[1] - img.height // 2),
            img
        )

    def update(self):
        global characters
        self.frame += 1
        if self.state == 2:
            """
            frame
            0-9: 사망1
            10-29: 사망2
            30-39: 사망3
            40-49: 사망4
            """
            #print(self.frame // 10, len(self.img[self.state]))

            if self.frame // 10 >= len(self.img[self.state]):
                characters.remove(self)

        elif self.health <= 0:
            self.frame = 0
            self.state = 2
            self.speed = 0
            self.pos = [self.pos[0], self.pos[1]]  # 왜 에러나지?
            self.pos[1] -= 20
        else:
            target = None
            for c in characters:
                if c.isEnemy == self.isEnemy:
                    continue

                if self.collide(c):
                    target = c

            if target:
                self.state = 1
                tick = self.frame // 10 % len(self.img[self.state])
                if tick == 6:
                    target.health -= self.power
            else:
                self.state = 0
                self.pos = [self.pos[0] + self.speed, self.pos[1]]


class Dog(Character):
    dogImage = [
        [
            [
                '1렙멍_걷기1.png',
                '1렙멍_걷기2.png',
                '1렙멍_걷기2.png',
                '1렙멍_걷기2.png',
                '1렙멍_걷기2.png',
                '1렙멍_걷기3.png',
                '1렙멍_걷기4.png',
                '1렙멍_걷기4.png',
                '1렙멍_걷기4.png',
                '1렙멍_걷기4.png',
            ],
            [
                '1렙멍_공격1.png',
                '1렙멍_공격2.png',
                '1렙멍_공격3.png',
                '1렙멍_공격3.png',
                '1렙멍_공격3.png',
                '1렙멍_공격3.png',
                '1렙멍_공격4.png',
                '1렙멍_공격5.png',
                '1렙멍_공격5.png',
                '1렙멍_공격5.png',
                '1렙멍_공격5.png',
                '1렙멍_공격5.png',
                '1렙멍_공격5.png',
            ],
            [
                '사망1.png',
                '사망2.png',
                '사망2.png',
                '사망3.png',
                '사망4.png',
            ]
        ],
        [
            [
                '2렙멍_걷기1.png',
                '2렙멍_걷기2.png',
                '2렙멍_걷기2.png',
                '2렙멍_걷기2.png',
                '2렙멍_걷기2.png',
                '2렙멍_걷기3.png',
                '2렙멍_걷기4.png',
                '2렙멍_걷기4.png',
                '2렙멍_걷기4.png',
                '2렙멍_걷기4.png',
            ],
            [
                '2렙멍_공격1.png',
                '2렙멍_공격2.png',
                '2렙멍_공격3.png',
                '2렙멍_공격3.png',
                '2렙멍_공격3.png',
                '2렙멍_공격4.png',
                '2렙멍_공격5.png',
                '2렙멍_공격6.png',
                '2렙멍_공격6.png',
                '2렙멍_공격6.png',
                '2렙멍_공격6.png',
                '2렙멍_공격6.png',
            ],
            [
                '사망1.png',
                '사망2.png',
                '사망2.png',
                '사망3.png',
                '사망4.png',
            ]
        ],
        [
            [
                '3렙멍_걷기1.png',
                '3렙멍_걷기2.png',
                '3렙멍_걷기2.png',
                '3렙멍_걷기2.png',
                '3렙멍_걷기2.png',
                '3렙멍_걷기3.png',
                '3렙멍_걷기4.png',
                '3렙멍_걷기4.png',
                '3렙멍_걷기4.png',
                '3렙멍_걷기4.png',
            ],
            [
                '3렙멍_공격1.png',
                '3렙멍_공격2.png',
                '3렙멍_공격3.png',
                '3렙멍_공격3.png',
                '3렙멍_공격3.png',
                '3렙멍_공격4.png',
                '3렙멍_공격5.png',
                '3렙멍_공격6.png',
                '3렙멍_공격6.png',
                '3렙멍_공격6.png',
                '3렙멍_공격6.png',
            ],
            [
                '사망1.png',
                '사망2.png',
                '사망2.png',
                '사망3.png',
                '사망4.png',
            ]
        ]
    ]

    dogHP_Power = [
        [22, 5],
        [35, 8],
        [100, 15]
    ]

    def __init__(self, dogType):
        w, a, d = self.dogImage[dogType]
        imgW = [Image.open(img).convert('RGBA') for img in w]
        imgA = [Image.open(img).convert('RGBA') for img in a]
        imgD = [Image.open(img).convert('RGBA') for img in d]

        super().__init__(imgW, imgA, imgD, (900, 120), self.dogHP_Power[dogType][0])
        self.power = self.dogHP_Power[dogType][1]
        self.speed = -2


class Enemy(Character):
    enemyImage = [
        [
            [
                '그라니_걷기1.png',
                '그라니_걷기2.png',
                '그라니_걷기2.png',
                '그라니_걷기2.png',
                '그라니_걷기2.png',
                '그라니_걷기3.png',
                '그라니_걷기4.png',
                '그라니_걷기4.png',
                '그라니_걷기4.png',
                '그라니_걷기4.png',
            ],
            [
                '그라니_공격1.png',
                '그라니_공격2.png',
                '그라니_공격3.png',
                '그라니_공격4.png',
                '그라니_공격5.png',
                '그라니_공격5.png',
                '그라니_공격5.png',
                '그라니_공격6.png',
                '그라니_공격7.png',
                '그라니_공격8.png',
                '그라니_공격8.png',
            ],
            [
                '사망1.png',
                '사망2.png',
                '사망2.png',
                '사망3.png',
                '사망4.png',
            ]
        ],
        [
            [
                '대지_걷기1.png',
                '대지_걷기2.png',
                '대지_걷기2.png',
                '대지_걷기2.png',
                '대지_걷기2.png',
                '대지_걷기3.png',
                '대지_걷기4.png',
                '대지_걷기4.png',
                '대지_걷기4.png',
                '대지_걷기4.png',
            ],
            [
                '대지_공격1.png',
                '대지_공격2.png',
                '대지_공격3.png',
                '대지_공격4.png',
                '대지_공격4.png',
                '대지_공격4.png',
                '대지_공격5.png',
                '대지_공격6.png',
                '대지_공격7.png',
                '대지_공격8.png',
                '대지_공격8.png',
                '대지_공격8.png',
                '대지_공격8.png',
            ],
            [
                '사망1.png',
                '사망2.png',
                '사망2.png',
                '사망3.png',
                '사망4.png',
            ],
        ],
        [
            [
                '사자자리1.jpg'
            ],
            [
                '사자자리1.jpg',
                '사자자리1.jpg',
                '사자자리1.jpg',
                '사자자리2.jpg',
                '사자자리1.jpg',
                '사자자리1.jpg',
                '사자자리1.jpg',
                '사자자리1.jpg',
                '사자자리1.jpg',
                '사자자리1.jpg',
                '사자자리1.jpg',
                '사자자리1.jpg',
                '사자자리1.jpg',
                '사자자리1.jpg',
                '사자자리1.jpg',
                '사자자리1.jpg',
                '사자자리1.jpg',
                '사자자리1.jpg',
                '사자자리1.jpg',
                '사자자리1.jpg',
                '사자자리1.jpg',
                '사자자리1.jpg',
                '사자자리1.jpg',
                '사자자리1.jpg',
            ],
            [
                '사망1.png',
                '사망2.png',
                '사망2.png',
                '사망3.png',
                '사망4.png'
            ]
        ]
    ]

    enemyHP_Power = [
        [33, 4],
        [61, 10],
        [2000, 30]
    ]

    def __init__(self, enemyType):
        w, a, d = self.enemyImage[enemyType]
        imgW = [Image.open(img).convert('RGBA') for img in w]
        imgA = [Image.open(img).convert('RGBA') for img in a]
        imgD = [Image.open(img).convert('RGBA') for img in d]

        super().__init__(imgW, imgA, imgD, (100, 120), self.enemyHP_Power[enemyType][0])
        self.power = self.enemyHP_Power[enemyType][1]
        self.speed = 2

        self.isEnemy = True

        self.isLion = enemyType == 2


    def update(self):
        global characters
        self.frame += 1
        if self.state == 2:
            """
            frame
            0-9: 사망1
            10-19: 사망2
            20-29: 사망3
            30-39: 사망4
            """
            #print(self.frame // 10, len(self.img[self.state]))

            if self.frame // 10 >= len(self.img[self.state]):
                characters.remove(self)

        elif self.health <= 0:
            self.frame = 0
            self.state = 2
            self.speed = 0
            self.pos = [self.pos[0], self.pos[1]]  # 왜 에러나지?
            self.pos[1] -= 20
        else:
            if self.isLion:
                target = []
                for c in characters:
                    if c.isEnemy == self.isEnemy:
                        continue

                    if self.collide(c):
                        target.append(c)
                if len(target)>0:
                    self.state = 1
                    tick = self.frame // 10 % len(self.img[self.state])
                    if tick == 0:
                        for t in target:
                            t.health -= self.power
                else:
                    self.state = 0
                    self.pos = [self.pos[0] + self.speed, self.pos[1]]
            else:
                target = None
                for c in characters:
                    if c.isEnemy == self.isEnemy:
                        continue

                    if self.collide(c):
                        target = c

                if target:
                    self.state = 1
                    tick = self.frame // 10 % len(self.img[self.state])
                    if tick == 4:
                        target.health -= self.power
                else:
                    self.state = 0
                    self.pos = [self.pos[0] + self.speed, self.pos[1]]


class Castle(Character):
    castleImage = [
        '아군_성.png',
        '적_산.png'
    ]

    castlePos = [
        [950, 130],
        [50, 130]
    ]

    def __init__(self, isEnemy):
        img = Image.open(self.castleImage[isEnemy]).convert('RGBA')
        super().__init__([img], [img], [img], self.castlePos[isEnemy], 5000)

        self.isEnemy = isEnemy

    def draw(self, pallet: Image):
        super().draw(pallet)
        draw = ImageDraw.Draw(pallet)
        draw.text((self.pos[0] - 50, self.pos[1] - 100), "HP: " + str(self.health), fill=(255, 0, 0), font=font)


def keyDown():
    global selected_tab
    selected_tab = 'background'


def keyUp():
    global selected_tab
    selected_tab = 'icon'


def keyLeft():
    global selected_tab, x_offset, selected_icon
    if selected_tab == 'background':
        x_offset += 20
    else:
        selected_icon = (selected_icon - 1) % 3


def keyRight():
    global selected_tab, x_offset, selected_icon
    if selected_tab == 'background':
        x_offset -= 20
    else:
        selected_icon = (selected_icon + 1) % 3


def keyP():
    global selected_tab, x_offset, selected_icon, clock, last_spawn_time_all, characters, gold
    needGold = [40, 80, 250]
    if clock - last_spawn_time_all > SPAWN_COOLDOWN_ALL:
        if gold >= needGold[selected_icon] and clock - last_spawn_time[selected_icon] > SPAWN_COOLDOWN:
            gold -= needGold[selected_icon]
            characters.append(Dog(selected_icon))
            last_spawn_time[selected_icon] = clock
        last_spawn_time_all = clock


startImage = Image.open('오프닝.jpg').convert('RGB')
startImage = startImage.resize((240, 240))
isStart = False
def startKey():
    global isStart
    isStart = True

while not isStart:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()
        if event.type == pg.KEYDOWN:
            startKey()

    screen.blit(pg.image.fromstring(startImage.tobytes(), startImage.size, startImage.mode), (0, 0))
    pg.display.flip()
    time.sleep(0.02)

c0 = Castle(0)
c1 = Castle(1)
characters.append(c0)
characters.append(c1)

lionSpawn = False

isGameOver = False
while True:

    if not c0 in characters:
        isGameOver = True
    if not c1 in characters:
        isGameOver = True
    if not isGameOver:
        clock += 1
        gold += random.randint(1, 3)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.KEYDOWN:
                # 키보드 입력 처리 눌렸을때
                if event.key == pg.K_s:
                    keyUp()
                if event.key == pg.K_w:
                    keyDown()
                if event.key == pg.K_a and selected_tab == 'icon':
                    keyLeft()
                if event.key == pg.K_d and selected_tab == 'icon':
                    keyRight()
                if event.key == pg.K_p:
                    keyP()

        keys = pg.key.get_pressed()
        if keys[pg.K_a] and selected_tab == 'background':
            keyLeft()
        if keys[pg.K_d] and selected_tab == 'background':
            keyRight()

        # 적 생성
        if clock - last_spawn_time_enemy > SPAWN_COOLDOWN_ALL:
            newE_type = random.randint(0, 1)
            newE = Enemy(newE_type)
            if clock - enemy_last_spawn_time[newE_type] > enemy_spawn_intervals[newE_type]:
                characters.append(newE)
                enemy_last_spawn_time[newE_type] = clock
                enemy_spawn_intervals[newE_type] = random.randint(100, 400)
                last_spawn_time_enemy = clock

        if c1.health <= 1000 and not lionSpawn:
            newE = Enemy(2)
            characters.append(newE)
            lionSpawn = True

    # 배경 이미지
    background = backgroundImage.copy()
    draw = ImageDraw.Draw(background)

    x_offset = max(min(x_offset, 0), ScreenSize[0] - BackGroundSize[0])

    # 캐릭터 그리기
    for c in characters:
        c.update()
        c.draw(background)

    # 배경 이미지 자르기
    background = background.crop((-x_offset, 0, -x_offset + ScreenSize[0], ScreenSize[1]))
    draw = ImageDraw.Draw(background)
    for i in range(3):
        rect = (i * 80, ScreenSize[1] - 60, i * 80 + 80, ScreenSize[1] - 60 + 80)
        background.paste(character_icons[i], rect[:2], character_icons[i])
        draw.rectangle((i * 80, ScreenSize[1] - 60, i * 80 + 80, ScreenSize[1]), outline=(255, 255, 255), width=1)

    if selected_tab == 'icon':
        rect = (selected_icon * 80, ScreenSize[1] - 60, selected_icon * 80 + 80, ScreenSize[1] - 60 + 80)
        draw.rectangle(rect, outline=(255, 0, 0), width=3)
    else:
        draw.rectangle((0, 0, 239, 240 - 60), outline=(255, 0, 0), width=1)
    draw.text((10, 10), "Gold: " + str(gold), fill=(153, 101, 21), font=font)

    if isGameOver:
        text = [
            "Game Over!",
            "You Win!"
        ][c0 in characters]

        # 가운데 정렬
        text_bbox = draw.textbbox((0, 0), text, font=fontBig)
        text_x = (240 - (text_bbox[2] - text_bbox[0])) // 2
        text_y = (240 - (text_bbox[3] - text_bbox[1])) // 2- 30
        draw.text((text_x, text_y), text, font=fontBig, fill=(255, 0, 0))

    # 화면에 그리기
    screen.blit(pg.image.fromstring(background.tobytes(), background.size, background.mode), (0, 0))
    pg.display.flip()

    time.sleep(0.01)
