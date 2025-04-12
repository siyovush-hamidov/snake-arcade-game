import cv2
import numpy as np
import time

WIDTH, HEIGHT = 640, 480
CELL_SIZE = 20

directions = {
    "UP": (0, -CELL_SIZE),
    "DOWN": (0, CELL_SIZE),
    "LEFT": (-CELL_SIZE, 0),
    "RIGHT": (CELL_SIZE, 0)
}

class BlockadeGame:
    def __init__(self):
        self.players = {
            "RED": [(WIDTH // 4, HEIGHT // 2)],
            "BLUE": [(3 * WIDTH // 4, HEIGHT // 2)]
        }
        self.directions = {"RED": "RIGHT", "BLUE": "LEFT"}
        self.running = True
        self.scores = {"RED": 0, "BLUE": 0}
        self.paused = False
        self.red_player_img = cv2.imread('static/red_player.png')
        self.blue_player_img = cv2.imread('static/blue_player.png')
        if self.red_player_img is None or self.blue_player_img is None:
            print("Ошибка: Не удалось загрузить изображения игроков!")
            exit()
        self.red_player_img = cv2.resize(self.red_player_img, (CELL_SIZE, CELL_SIZE))
        self.blue_player_img = cv2.resize(self.blue_player_img, (CELL_SIZE, CELL_SIZE))
        self.background = cv2.imread('static/background.png')
        if self.background is None:
            print("Ошибка: Не удалось загрузить фоновое изображение!")
            exit()
        self.background = cv2.resize(self.background, (WIDTH, HEIGHT))
        self.trails = {"RED": [], "BLUE": []}
        self.last_update = time.time() 
        self.step_interval = 0.1

    def move(self, player):
        if self.paused:
            return
        head_x, head_y = self.players[player][-1]
        delta_x, delta_y = directions[self.directions[player]]
        new_head = (head_x + delta_x, head_y + delta_y)

        if (
            new_head in self.players["RED"] or 
            new_head in self.players["BLUE"] or 
            new_head[0] < 0 or new_head[0] >= WIDTH or 
            new_head[1] < 0 or new_head[1] >= HEIGHT
        ):
            self.scores["RED" if player == "BLUE" else "BLUE"] += 1
            self.reset_game()
            return
        
        self.players[player].append(new_head)
        if len(self.players[player]) > 1:
            self.trails[player].append((self.players[player][-2], self.players[player][-1]))

    def reset_game(self):
        self.players = {
            "RED": [(WIDTH // 4, HEIGHT // 2)],
            "BLUE": [(3 * WIDTH // 4, HEIGHT // 2)]
        }
        self.directions = {"RED": "RIGHT", "BLUE": "LEFT"}
        self.trails = {"RED": [], "BLUE": []}

    def change_direction(self, player, new_direction):
        opposite_directions = {"UP": "DOWN", "DOWN": "UP", "LEFT": "RIGHT", "RIGHT": "LEFT"}
        if new_direction != opposite_directions.get(self.directions[player], ""):
            self.directions[player] = new_direction

    def toggle_pause(self):
        self.paused = not self.paused

    def update(self):
        if self.paused:
            return
        current_time = time.time()
        if current_time - self.last_update >= self.step_interval:
            self.move("RED")
            self.move("BLUE")
            self.last_update = current_time

    def draw(self, frame):
        frame[:] = self.background.copy()
        
        for player, trail in self.trails.items():
            color = (0, 0, 255) if player == "RED" else (255, 0, 0)
            for start, end in trail:
                cv2.line(frame, start, end, color, 2)
        
        for player, segments in self.players.items():
            player_img = self.red_player_img if player == "RED" else self.blue_player_img
            for segment in segments:
                x, y = segment
                if x + CELL_SIZE <= WIDTH and y + CELL_SIZE <= HEIGHT:
                    frame[y:y+CELL_SIZE, x:x+CELL_SIZE] = player_img
        
        cv2.putText(frame, f"RED: {self.scores['RED']}", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        cv2.putText(frame, f"BLUE: {self.scores['BLUE']}", (WIDTH - 150, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
        
        cv2.circle(frame, (10, 10), 5, (255, 255, 255), -1)
        cv2.circle(frame, (WIDTH-10, 10), 5, (255, 255, 255), -1)
        cv2.circle(frame, (10, HEIGHT-10), 5, (255, 255, 255), -1)
        cv2.circle(frame, (WIDTH-10, HEIGHT-10), 5, (255, 255, 255), -1)
        
        if self.paused:
            cv2.putText(frame, "PAUSE", (WIDTH//2 - 50, HEIGHT//2), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 3)
        
        return frame

def show_start_screen():
    frame = cv2.imread('background.jpg')
    if frame is None:
        frame = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
    frame = cv2.resize(frame, (WIDTH, HEIGHT))
    text = [
        "THIS IS A SURVIVAL GAME FOR TWO PLAYERS",
        "STARTING WITH AN EMPTY SCREEN, PATHS ARE DRAWN",
        "BY THE TWO PLAYERS ONE RED AND THE OTHER BLUE",
        "THE OBJECT IS TO KEEP YOUR PATH FROM RUNNING",
        "INTO ANYTHING FOR AS LONG AS POSSIBLE",
        "THIS GAME TAKES PRACTICE SO DON'T GIVE UP!",
        "HIT ENTER TO BEGIN",
        "THE RED USER(ON THE LEFT) HAS WASD TO PLAY",
        "THE BLUE PLAYER CAN USE IJKL TO PLAY",
        "CLICK MOUSE TO PAUSE/UNPAUSE"
    ]
    y = 80
    for line in text:
        cv2.putText(frame, line, (50, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        y += 30
    cv2.imshow("Blockade Game", frame)
    while cv2.waitKey(0) != 13:
        pass

cv2.namedWindow("Blockade Game", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Blockade Game", WIDTH, HEIGHT)

def mouse_event(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN or event == cv2.EVENT_RBUTTONDOWN:
        game.toggle_pause()

show_start_screen()
game = BlockadeGame()
frame = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
cv2.imshow("Blockade Game", frame)

cv2.setMouseCallback("Blockade Game", mouse_event)

def key_event(event):
    if event == 27:
        game.running = False
    elif event == ord("w"):
        game.change_direction("RED", "UP")
    elif event == ord("s"):
        game.change_direction("RED", "DOWN")
    elif event == ord("a"):
        game.change_direction("RED", "LEFT")
    elif event == ord("d"):
        game.change_direction("RED", "RIGHT")
    elif event == ord("i"):
        game.change_direction("BLUE", "UP")
    elif event == ord("k"):
        game.change_direction("BLUE", "DOWN")
    elif event == ord("j"):
        game.change_direction("BLUE", "LEFT")
    elif event == ord("l"):
        game.change_direction("BLUE", "RIGHT")

while game.running:
    key = cv2.waitKey(1) 
    if key != -1:
        key_event(key)
    
    game.update()
    frame = game.draw(frame)
    cv2.imshow("Blockade Game", frame)

cv2.destroyAllWindows()