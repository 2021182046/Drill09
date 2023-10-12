# 이것은 각 상태들을 객체로 구현한 것임.
import math

from pico2d import load_image, get_time
from sdl2 import SDL_KEYDOWN, SDLK_SPACE, SDLK_RIGHT, SDLK_LEFT, SDL_KEYUP


def space_down(e):
    return e[0]== 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_SPACE


def time_out(e):
    return e[0]== 'TIME_OUT'


def right_down(e):
    return e[0]== 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_RIGHT

def right_up(e):
    return e[0]== 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_RIGHT

def left_down(e):
    return e[0]== 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_LEFT

def left_up(e):
    return e[0]== 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_LEFT

def autorun_down(e):
    # AutoRun 이벤트를 위한 키가 눌렸다는 것을 확인
    return e[0]== 'INPUT' and e[1].type == SDL_KEYDOWN



class Idle:

    @staticmethod
    def enter(boy, e):
        if boy.action == 0:
            boy.action = 2
        elif boy.action == 1:
            boy.action = 3
        boy.dir =0
        boy.frame=0
        boy.start_time = get_time()
        print('Idle Enter')

    @staticmethod
    def exit(boy, e):
        print('Idle Exit')

    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + 1) % 8
        if get_time() - boy.start_time > 3.0:
            boy.state_machine.handle_event(('TIME_OUT', 0))
        print('Idle Do')

    @staticmethod
    def draw(boy):
        boy.image.clip_draw(boy.frame*100, boy.action*100, 100, 100, boy.x, boy.y)
        pass


class Sleep:

    @staticmethod
    def enter(boy, e):
        boy.frame=0
        print('고개 숙이기')

    @staticmethod
    def exit(boy, e):
        print('고개 들기')

    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + 1) % 8
        print('드르렁')

    @staticmethod
    def draw(boy):
        if boy.action == 2:
            boy.image.clip_composite_draw(boy.frame * 100, 200, 100, 100, -math.pi/2, '', boy.x-25, boy.y-25, 100, 100)
        else:
            boy.image.clip_composite_draw(boy.frame * 100, 200, 100, 100, math.pi/2, '', boy.x - 25, boy.y - 25, 100, 100)

        #boy.image.clip_composite_draw(boy.frame*100, boy.action*100, 100, 100, math.pi/2, '', boy.x-25, boy.y-25, 100, 100) #''은 상하반전
        pass


class Run:

    @staticmethod
    def enter(boy, e):
        if right_down(e) or left_up(e): #오른쪽 run
            boy.dir, boy.action = 1, 1
        elif left_down(e) or right_up(e): #왼쪽 run
            boy.dir, boy.action = -1, 0

    @staticmethod
    def exit(boy, e):
        print('달리기 멈춤')
        pass

    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + 1) % 8
        boy.x += boy.dir * 5 #이동 확인 및 속도
        pass

    @staticmethod
    def draw(boy):
        boy.image.clip_draw(boy.frame * 100, boy.action * 100, 100, 100, boy.x, boy.y)


class AutoRun:

    @staticmethod
    def enter(boy, e):
        if right_down(e) or left_up(e): #오른쪽 run
            boy.dir, boy.action = 1, 1
        elif left_down(e) or right_up(e): #왼쪽 run
            boy.dir, boy.action = -1, 0

    @staticmethod
    def exit(boy, e):
        print('달리기 멈춤')
        pass

    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + 1) % 8
        boy.x += boy.dir * 5 #이동 확인 및 속도
        pass

    @staticmethod
    def draw(boy):
        boy.image.clip_draw(boy.frame * 100, boy.action * 100, 100, 100, boy.x, boy.y)


class StateMachine:
    def __init__(self, boy): #2 boy가 자신을 StateMachine에게 전달
        self.boy = boy #3 전달 저장
        self.transitions = {
            Idle: {right_down: Run, left_down: Run, left_up: Run, right_up: Run, time_out: Sleep},
            Run: {right_down: Idle, left_down: Idle, left_up: Idle, right_up: Idle},
            Sleep: {right_down: Run, left_down: Run, left_up: Run, right_up: Run, space_down: Idle}
        }
        self.cur_state = Idle
        self.table = {
            Sleep: {space_down: Idle},
            Idle: {time_out: Sleep}
        }

    def start(self):
        self.cur_state.enter(self.boy, ('NONE', 0)) # 소년 정보 넘겨주기

    def update(self):
        self.cur_state.do(self.boy) # 소년 정보 넘겨주기

    def handle_event(self, e):
        for check_event, next_state in self.transitions[self.cur_state].items():
            if check_event(e):
                self.cur_state.exit(self.boy, e)
                self.cur_state = next_state
                self.cur_state.enter(self.boy, e)
                return True #성공적으로 이벤트 변환
        return False #이벤트를 소모하지 못함

        pass

    def draw(self):
        self.cur_state.draw(self.boy) #4 자신이 가지고 있는 소년 정보





class Boy:
    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.action = 3
        self.image = load_image('animation_sheet.png')
        self.state_machine = StateMachine(self) #2 자신의 정보 넘기기
        self.state_machine.start()

    def update(self):
        self.state_machine.update()

    def handle_event(self, event):
        #pico2d event -> statemachine 상태로 변환
        self.state_machine.handle_event(('INPUT', event))
        pass

    def draw(self):
        self.state_machine.draw()
