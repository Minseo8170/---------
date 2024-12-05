import time
import random
from colorsys import hsv_to_rgb
import board
from gpiozero import Button
from digitalio import DigitalInOut
from PIL import Image, ImageDraw, ImageFont
from adafruit_rgb_display import st7789

# 디스플레이 생성
cs_pin = DigitalInOut(board.CE0)
dc_pin = DigitalInOut(board.D25)
reset_pin = DigitalInOut(board.D24)
BAUDRATE = 24000000  # SPI 통신 속도

spi = board.SPI()
disp = st7789.ST7789(
    spi,
    height=240,
    y_offset=80,
    rotation=180,
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    baudrate=BAUDRATE,
)

# 입력 핀:
button_A = Button(5)
button_B = Button(6)
button_L = Button(27)
button_R = Button(23)
button_U = Button(17)
button_D = Button(22)
button_C = Button(4)

# 백라이트 켜기
backlight = DigitalInOut(board.D26)
backlight.switch_to_output()
backlight.value = True


clock = 0

ScreenSize = (240, 240)
BackGroundSize = (1000, 240)

font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 15)
fontBig = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 30)

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
    random.randint(90, 150)
]

characters = []
gold = 0
needGold = [40, 80, 250]


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
        tick = self.frame // 5 % len(self.img[self.state])
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

            if self.frame // 5 >= len(self.img[self.state]):
                characters.remove(self)

        elif self.health <= 0:
            self.frame = 0
            self.state = 2
            self.speed = 0
            self.pos = [self.pos[0], self.pos[1]] 
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
        [22, 8],
        [45, 12],
        [105, 30]
    ]

    def __init__(self, dogType):
        w, a, d = self.dogImage[dogType]
        imgW = [Image.open(img).convert('RGBA') for img in w]
        imgA = [Image.open(img).convert('RGBA') for img in a]
        imgD = [Image.open(img).convert('RGBA') for img in d]

        super().__init__(imgW, imgA, imgD, (900, 120), self.dogHP_Power[dogType][0])
        self.power = self.dogHP_Power[dogType][1]
        self.speed = -3


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
        [600, 45]
    ]

    def __init__(self, enemyType):
        w, a, d = self.enemyImage[enemyType]
        imgW = [Image.open(img).convert('RGBA') for img in w]
        imgA = [Image.open(img).convert('RGBA') for img in a]
        imgD = [Image.open(img).convert('RGBA') for img in d]

        super().__init__(imgW, imgA, imgD, (100, 120), self.enemyHP_Power[enemyType][0])
        self.power = self.enemyHP_Power[enemyType][1]
        self.speed = 3

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

            if self.frame // 4 >= len(self.img[self.state]):
                characters.remove(self)

        elif self.health <= 0:
            self.frame = 0
            self.state = 2
            self.speed = 0
            self.pos = [self.pos[0], self.pos[1]] 
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
        super().__init__([img], [img], [img], self.castlePos[isEnemy], 2000)

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
    if clock - last_spawn_time_all > SPAWN_COOLDOWN_ALL:
        if gold >= needGold[selected_icon] and clock - last_spawn_time[selected_icon] > SPAWN_COOLDOWN:
            gold -= needGold[selected_icon]
            characters.append(Dog(selected_icon))
            last_spawn_time[selected_icon] = clock
        last_spawn_time_all = clock

def reset_game():
    global characters, c0, c1, clock, gold, lionSpawn, enemy_last_spawn_time, last_spawn_time_all, last_spawn_time_enemy
    characters = []  # 캐릭터 리스트 초기화
    c0 = Castle(0) # 아군 성 초기화
    c1 = Castle(1) # 적 성 초기화
    characters.append(c0)
    characters.append(c1)
    clock = 0        # 게임 시간 초기화
    gold = 0         # 골드 초기화
    lionSpawn = False  # 특정 적 스폰 여부 초기화
    enemy_last_spawn_time = [0, 0]  # 적 스폰 시간 초기화
    last_spawn_time_all = 0 # 아군 스폰 시간 초기화
    last_spawn_time_enemy = 0  # 전체 적 스폰 시간 초기화


startImage = Image.open('오프닝.jpg').convert('RGB')
startImage = startImage.resize((240, 240))
isStart = False
def startKey():
    global isStart
    isStart = True

c0 = Castle(0)
c1 = Castle(1)
characters.append(c0)
characters.append(c1)

lionSpawn = False

button_D.when_pressed = keyUp
button_U.when_pressed = keyDown
button_L.when_pressed = keyLeft
button_R.when_pressed = keyRight

button_A.when_pressed = keyP

isGameOver = False
while True:

    while not isStart:
        if button_A.is_pressed or button_B.is_pressed:
            startKey()
            reset_game()
            
        disp.image(startImage)
        time.sleep(0.02)


    if not c0 in characters:
        isGameOver = True
    if not c1 in characters:
        isGameOver = True
    if not isGameOver:
        clock += 1
        gold += random.randint(1, 3)
        if button_L.is_pressed and selected_tab == 'background':
            keyLeft()
        if button_R.is_pressed and selected_tab == 'background':
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

        if c1.health <= 500 and not lionSpawn:
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
        draw.text((i * 80 + 53, ScreenSize[1] - 60), str(needGold[i]), fill=(160, 255, 186), font=font)

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
        draw.text((text_x, text_y - 40), "Press any key to restart", font=font, fill=(255, 0, 0))
        if button_A.is_pressed or button_B.is_pressed:
            isStart = False

    # 화면에 그리기
    disp.image(background)

    time.sleep(0.01)
