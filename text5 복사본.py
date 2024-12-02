import pygame
import sys
import random
from PIL import Image, ImageDraw, ImageFont

# 초기화
pygame.init()
current_time = 0

# 화면 크기 및 설정
SCREEN_WIDTH, SCREEN_HEIGHT = 240, 240
BACKGROUND_WIDTH, BACKGROUND_HEIGHT = 1000, 240
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Castle Defence")

# 폰트 설정
font = pygame.font.SysFont(None, 36)

# 체력 변수
castle_health = 500
enemy_mt_health = 700

# 배경 이미지 로드
background = Image.open('배경.png').convert('RGB')

# 배경 초기 위치 설정
x_offset = 240

# 캐릭터 아이콘 설정
character_icons = []
character_icons.append(Image.open("1렙멍_기본.png").convert('RGBA'))
character_icons.append(Image.open("2렙멍_기본.png").convert('RGBA'))
character_icons.append(Image.open("3렙멍_기본.png").convert('RGBA'))

# 각 아이콘 크기 조정 (필요 시)
for i in range(len(character_icons)):
    character_icons[i] = character_icons[i].resize((60, 60))
    #character_icons[i] = pygame.transform.scale(character_icons[i], (60, 60))

# 상태 변수
selected_tab = 'background'
selected_background = 0
selected_icon = 1
last_spawn_time = {
    "Dog1" : 0,
    "Dog2" : 0,
    "Dog3" : 0
}
last_spawn_time_all = 0
last_spawn_time_enemy = 0
SPAWN_COOLDOWN = 2000
SPAWN_COOLDOWN_ALL = 3000


# 생성 캐릭터 관리 리스트
characters = []

# 적 캐릭터 관리 변수
enemy_last_spawn_time = {
    "Enemy1": 0,
    "Enemy2": 0
}
enemy_spawn_intervals = {
    "Enemy1": random.randint(5000, 10000),  # 초기화
    "Enemy2": random.randint(5000, 10000)
}

# 캐릭터 클래스
class Character:
    def collide(self, other):
        next_x = self.x + self.speed
        self_left = next_x - self.images_walk[0].width//2
        self_right = next_x + self.images_walk[0].width//2
        other_left = other.x - other.images_walk[0].width//2
        other_right = other.x + other.images_walk[0].width//2

        if self_right > other_left and self_left < other_right:
            self.attack_ing = True
            return True
        else:
            self.attack_ing = False
            return False

    # 캐릭터 그리기
    def draw(self, pallet:Image):
        if self.die:
            if self.death_frame_index < len(self.images_death):
                img = self.images_death[self.death_frame_index]
                pallet.paste(img,(self.x-img.width//2, self.y-100),img)
        elif self.attack_ing:
            img = self.images_attack[self.attack_frame_index]
            pallet.paste(img,(self.x-img.width//2, self.y),img)
        else:
            # 캐릭터를 중심 좌표에 맞게 보정
            img = self.images_walk[self.walk_frame_index]
            pallet.paste(img,(self.x-img.width//2, self.y),img)

class Dog(Character):
    def __init__(self, x, y):
        self.images_walk = [Image.open(img).convert('RGBA') for img in self.image_file_dog_walk]
        self.images_attack = [Image.open(img).convert('RGBA') for img in self.image_file_dog_attack]
        self.images_death = []
        self.images_death.append(Image.open("사망1.png").convert('RGBA'))
        self.images_death.append(Image.open("사망2.png").convert('RGBA'))
        self.images_death.append(Image.open("사망3.png").convert('RGBA'))
        self.images_death.append(Image.open("사망4.png").convert('RGBA'))
        self.x = x
        self.y = y
        self.walk_frame_index = 0
        self.attack_frame_index = 0
        self.death_frame_index = 0
        self.speed = -2
        self.animation_time = 0
        self.health = 100
        self.power = 0

        self.attack_ing = False
        self.die = False
        self.dead_animation_complete = False

    # 캐릭터 이동 및 애니메이션 업데이트
    def update(self, dt, characters):
        if self.die:
            self.death()
            return
        target = None
        for character in characters:
            if type(character) in [Enemy1, Enemy2]:
                if self.collide(character):
                    target = character
        if target is None:
            self.move()
        else:
            self.attact(target)
            print('공격',target)

    def move(self):
        self.x += self.speed
        self.animation_time += dt
        repeated_frames = []
        if self.animation_time > 100: # 100ms마다 프레임 전환
            if self.walk_frame_index == 1 or self.walk_frame_index == 3:
                repeated_frames.extend([self.walk_frame_index] * 7)
            self.walk_frame_index = (self.walk_frame_index + 1) % len(self.images_walk)
            self.animation_time = 0

    def attact(self, target):
        self.animation_time += dt
        repeated_frames = []
        if self.animation_time > 100: # 100ms마다 프레임 전환
            if Dog1 or Dog2:
                if self.attack_frame_index == 3:
                    repeated_frames.extend([self.attack_frame_index] * 3)
                if self.attack_frame_index == 4:
                    target.health -= self.power
                    if target.health <= 0:
                        target.die = True
                if self.attack_frame_index == 5:
                    repeated_frames.extend([self.attack_frame_index] * 9)
            if Dog3:
                if self.attack_frame_index == 3:
                    repeated_frames.extend([self.attack_frame_index] * 2)
                if self.attack_frame_index == 4:
                    target.health -= self.power
                    if target.health <= 0:
                        target.die = True
                if self.attack_frame_index == 6:
                    repeated_frames.extend([self.attack_frame_index] * 7)
            self.attack_frame_index = (self.attack_frame_index + 1) % len(self.images_attack)
            self.animation_time = 0

    def death(self):
        if self.health <= 0:
            self.die = True
            # 죽음 애니메이션 처리
            repeated_frames = []
            self.animation_time += dt
            if self.animation_time > 500:  # 500ms마다 프레임 전환
                if self.death_frame_index == 4:
                    self.dead_animation_complete = True
                    return
                if self.death_frame_index == 1:
                    repeated_frames.extend([self.death_frame_index] * 3)
                self.animation_time = 0
            if self.dead_animation_complete:
                if self in characters:  # 리스트에서 제거하기 전에 존재 여부 확인
                    characters.remove(self)
            

class Dog1(Dog):
    image_file_dog_walk = [
        '1렙멍_걷기1.png',
        '1렙멍_걷기2.png',
        '1렙멍_걷기3.png',
        '1렙멍_걷기4.png',
    ]

    image_file_dog_attack = [
        '1렙멍_공격1.png',
        '1렙멍_공격2.png',
        '1렙멍_공격3.png',
        '1렙멍_공격4.png',
        '1렙멍_공격5.png',
        '1렙멍_기본.png',
    ]

    def __init__(self, x, y):
        super().__init__(x, y)
        self.power = 5
        self.health = 22

class Dog2(Dog):
    image_file_dog_walk = [
        '2렙멍_걷기1.png',
        '2렙멍_걷기2.png',
        '2렙멍_걷기3.png',
        '2렙멍_걷기4.png',
    ]

    image_file_dog_attack =[
        '2렙멍_공격1.png',
        '2렙멍_공격2.png',
        '2렙멍_공격3.png',
        '2렙멍_공격4.png',
        '2렙멍_공격5.png',
        '2렙멍_공격6.png',
        '2렙멍_기본.png',
    ]

    def __init__(self, x, y):
        super().__init__(x, y)
        self.power = 8
        self.health = 40

class Dog3(Dog):
    image_file_dog_walk = [
        '3렙멍_걷기1.png',
        '3렙멍_걷기2.png',
        '3렙멍_걷기3.png',
        '3렙멍_걷기4.png',
    ]

    image_file_dog_attack = [
        '3렙멍_공격1.png',
        '3렙멍_공격2.png',
        '3렙멍_공격3.png',
        '3렙멍_공격4.png',
        '3렙멍_공격5.png',
        '3렙멍_공격6.png',
        '3렙멍_기본.png',
    ]

    def __init__(self, x, y):
        super().__init__(x, y)
        self.power = 15
        self.health = 60

class Enemy(Character):
    def __init__(self, x, y):
        self.images_walk = [Image.open(img).convert("RGBA") for img in self.image_file_enemy_walk]
        self.images_attack = [Image.open(img).convert('RGBA') for img in self.image_file_enemy_attack]
        self.images_death = []
        self.images_death.append(Image.open("사망1.png").convert('RGBA'))
        self.images_death.append(Image.open("사망2.png").convert('RGBA'))
        self.images_death.append(Image.open("사망3.png").convert('RGBA'))
        self.images_death.append(Image.open("사망4.png").convert('RGBA'))
        self.x = x
        self.y = y
        self.walk_frame_index = 0
        self.attack_frame_index = 0
        self.death_frame_index = 0
        self.speed = 2
        self.animation_time = 0
        self.power = 0
        self.health = 100

        self.attack_ing = False
        self.die = False
        self.dead_animation_complete = False

    # 캐릭터 이동 및 애니메이션 업데이트
    def update(self, dt, characters):
        if self.die:
            self.death()
            return
        target = None
        for character in characters:
            if type(character) in [Dog1,Dog2,Dog3]:
                if self.collide(character):
                    target = character
        if target is None:
            self.move()
        else:
            self.attact(target)
            print('공격',target)

    def move(self):
        self.x += self.speed
        self.animation_time += dt
        repeated_frames = []
        if self.animation_time > 100: # 100ms마다 프레임 전환
            if self.walk_frame_index == 1 or self.walk_frame_index == 3:
                repeated_frames.extend([self.walk_frame_index] * 7)
            self.walk_frame_index = (self.walk_frame_index + 1) % len(self.images_walk)
            self.animation_time = 0

    def attact(self, target):
        self.animation_time += dt
        repeated_frames = []
        if self.animation_time > 100: # 100ms마다 프레임 전환
            if Enemy1:
                if self.attack_frame_index == 4:
                    target.health -= self.power
                    if self.health <= 0:
                        target.die = True
                if self.attack_frame_index == 5:
                    repeated_frames.extend([self.attack_frame_index] * 3)    
                if self.attack_frame_index == 8:
                    repeated_frames.extend([self.attack_frame_index] * 4)
            if Enemy2:
                if self.attack_frame_index == 4:
                    repeated_frames.extend([self.attack_frame_index] * 3)  
                if self.attack_frame_index == 5:
                    target.health -= self.power  
                    if self.health <= 0:
                        target.die = True
                if self.attack_frame_index == 8:
                    repeated_frames.extend([self.attack_frame_index] * 7)
            self.attack_frame_index = (self.attack_frame_index + 1) % len(self.images_attack)
            self.animation_time = 0

    def death(self):
        if self.health <= 0:
            self.die = True
            # 죽음 애니메이션 처리
            repeated_frames = []
            self.animation_time += dt
            if self.animation_time > 500:  # 500ms마다 프레임 전환
                if self.death_frame_index == 4:
                    self.dead_animation_complete = True
                    return
                if self.death_frame_index == 1:
                    repeated_frames.extend([self.death_frame_index] * 3)
                self.animation_time = 0
            if self.dead_animation_complete:
                if self in characters:  # 리스트에서 제거하기 전에 존재 여부 확인
                    characters.remove(self)

class Enemy1(Enemy):
    image_file_enemy_walk = [
        '그라니_걷기1.png',
        '그라니_걷기2.png',
        '그라니_걷기3.png',
        '그라니_걷기4.png',
    ]

    image_file_enemy_attack = [
        '그라니_공격1.png',
        '그라니_공격2.png',
        '그라니_공격3.png',
        '그라니_공격4.png',
        '그라니_공격5.png',
        '그라니_공격6.png',
        '그라니_공격7.png',
        '그라니_공격8.png',
        '그라니_기본.png',
    ]

    def __init__(self, x, y):
        super().__init__(x, y)
        self.power = 4
        self.health = 33

class Enemy2(Enemy):
    image_file_enemy_walk = [
        '대지_걷기1.png',
        '대지_걷기2.png',
        '대지_걷기3.png',
        '대지_걷기4.png',
    ]

    image_file_enemy_attack = [
        '대지_공격1.png',
        '대지_공격2.png',
        '대지_공격3.png',
        '대지_공격4.png',
        '대지_공격5.png',
        '대지_공격6.png',
        '대지_공격7.png',
        '대지_공격8.png',
        '대지_기본.png',
    ]

    def __init__(self, x, y):
        super().__init__(x, y)
        self.power = 10
        self.health = 50
        
class Enemy3:
    image_file_enemy3 = [
        '사자자리.jpg'
    ]

class castle_hp:
    # 함수: 체력 텍스트 렌더링
    def draw_health():
        # 아군 성 체력
        player_text = font.render(f"Player Health: {castle_health}", True, (255, 255, 255))
        screen.blit(player_text, (900, 100))

        # 적 성 체력
        enemy_text = font.render(f"Enemy Health: {enemy_mt_health}", True, (255, 255, 255))
        screen.blit(enemy_text, (100, 10))

    # 함수: 체력바 그리기
    def draw_health_bar(x, y, health, max_health, color):
        bar_width = 200
        bar_height = 20
        fill = (health / max_health) * bar_width
        pygame.draw.rect(screen, (0, 0, 0), (x, y, bar_width, bar_height))  # 바 테두리
        pygame.draw.rect(screen, color, (x, y, fill, bar_height))  # 현재 체력


class Castle:
    castle = Image.open('아군_성.png').convert('RGBA')

class Enemy_mt:
    enemy_mt = Image.open('적_산.png').convert('RGBA')

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
    global selected_tab, x_offset, selected_icon, current_time, last_spawn_time_all
    if current_time - last_spawn_time_all > SPAWN_COOLDOWN_ALL:
        if selected_icon == 0 and current_time - last_spawn_time["Dog1"] > SPAWN_COOLDOWN:  # 첫 번째 아이콘에 해당하는 Dog1 생성
            character_spawn_x = 900
            character_spawn_y = 90  # Y축 정중앙 (240x240 캐릭터 기준으로 보정)                 
            characters.append(Dog1(character_spawn_x, character_spawn_y))
            last_spawn_time["Dog1"] = current_time
        if selected_icon == 1 and current_time - last_spawn_time["Dog2"] > SPAWN_COOLDOWN:  # 두 번째 아이콘에 해당하는 Dog2 생성
            character_spawn_x = 900
            character_spawn_y = 90  # Y축 정중앙 (240x240 캐릭터 기준으로 보정) 
            characters.append(Dog2(character_spawn_x, character_spawn_y))
            last_spawn_time["Dog2"] = current_time
        if selected_icon == 2 and current_time - last_spawn_time["Dog3"] > SPAWN_COOLDOWN:  # 세 번째 아이콘에 해당하는 Dog3 생성
            character_spawn_x = 900
            character_spawn_y = 90  # Y축 정중앙 (240x240 캐릭터 기준으로 보정) 
            characters.append(Dog3(character_spawn_x, character_spawn_y))
            last_spawn_time["Dog3"] = current_time
        last_spawn_time_all = current_time



# 메인 루프
clock = pygame.time.Clock()
while True:
    current_time = pygame.time.get_ticks()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            # 키보드 입력 처리 눌렸을때
            if event.key == pygame.K_s:
                keyUp()
            if event.key == pygame.K_w:
                keyDown()
            if event.key == pygame.K_a and selected_tab == 'icon':
                keyLeft()
            if event.key == pygame.K_d and selected_tab == 'icon':
                keyRight()
            if event.key == pygame.K_p:
                keyP()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_a] and selected_tab == 'background':
        keyLeft()
    if keys[pygame.K_d] and selected_tab == 'background':
        keyRight()

    # 적 생성 로직
    enemy_types = ["Enemy1", "Enemy2"]
    chosen_enemies = random.sample(enemy_types, 1)
    for enemy_type in chosen_enemies:
        if current_time - last_spawn_time_enemy > SPAWN_COOLDOWN_ALL:
            if current_time - enemy_last_spawn_time[enemy_type] > enemy_spawn_intervals[enemy_type]:
                spawn_x = 100
                spawn_y = 90
                if enemy_type == "Enemy1":
                    characters.append(Enemy1(spawn_x, spawn_y))
                elif enemy_type == "Enemy2":
                    characters.append(Enemy2(spawn_x, spawn_y))
            
                # 스폰 시간 및 다음 간격 갱신
                enemy_last_spawn_time[enemy_type] = current_time
                enemy_spawn_intervals[enemy_type] = random.randint(5000, 10000)
            last_spawn_time_enemy = current_time

    # 배경 위치 조정
    x_offset = max(min(x_offset, 0), SCREEN_WIDTH - background.width)
    
    # 배경 그리기
    bg = background.copy()

        # 체력 텍스트와 체력바 렌더링
    castle_hp.draw_health()
    castle_hp.draw_health_bar(900, 100, castle_health, 500, (0, 255, 0))  # 아군 성 체력바
    castle_hp.draw_health_bar(100, 100, enemy_mt_health, 700, (255, 0, 0))  # 적 성 체력바

    #아군 성, 적 산 그리기
    """
    screen.blit(Castle.castle, (x_offset + 900, 15))
    screen.blit(Enemy_mt.enemy_mt, (x_offset, 15))
    """
    bg.paste(Castle.castle, (900, 15), Castle.castle)
    bg.paste(Enemy_mt.enemy_mt, (0, 15), Enemy_mt.enemy_mt)

    # 캐릭터 업데이트 및 그리기
    for character in characters:
        character.update(dt, characters)
        character.draw(bg)

    bg = bg.crop((-x_offset, 0, -x_offset + SCREEN_WIDTH, SCREEN_HEIGHT))
    draw = ImageDraw.Draw(bg)

    # 캐릭터 아이콘 영역 그리기
    for i in range(3):
        rect = (i * 80, SCREEN_HEIGHT - 60, i*80+80,SCREEN_HEIGHT - 60 + 80)
        if i == selected_icon:
            draw.rectangle(rect, outline=(255, 0, 0), width=3)
        else:
            draw.rectangle(rect, outline=(255, 255, 255), width=1)
        #screen.blit(character_icons[i], rect.topleft)
        bg.paste(character_icons[i], rect[:2], character_icons[i])

    # 배경 이미지를 화면에 표시
    screen.blit(pygame.image.fromstring(bg.tobytes(), bg.size, "RGB"), (0, 0))
    pygame.display.flip()
    dt = clock.tick(15)