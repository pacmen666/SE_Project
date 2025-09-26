#test版本调整：每50分->每20分考一个单词（修改部分已用断点标出）
import pygame
import sys
import random
import os
import json

# 初始化pygame
pygame.init()
pygame.font.init()

# -------------------------- 常量定义 --------------------------
GRID_SIZE = 80
WIDTH, HEIGHT = 1200, 960
GRID_WIDTH, GRID_HEIGHT = WIDTH // GRID_SIZE, HEIGHT // GRID_SIZE

# 颜色（新增黄金果实颜色）
BLACK, WHITE, RED, BLUE, GOLD = (0, 0, 0), (255, 255, 255), (255, 0, 0), (0, 0, 255), (255, 215, 0)
GREEN = (0, 255, 0)

# 方向
UP, DOWN, LEFT, RIGHT = (0, -1), (0, 1), (-1, 0), (1, 0)

# 初始化窗口和字体
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("单词学习贪吃蛇游戏")


pygame.font.init()
# 思源黑体相对路径（字体文件与代码文件在同一文件夹下，直接写文件名即可）
SOURCE_HAN_FONT = "SourceHanSansCN-Normal.ttf"

# 检查字体文件是否存在（可选但建议保留，方便排查问题）
if not os.path.exists(SOURCE_HAN_FONT):
    print(f"⚠️  未找到思源黑体文件：{SOURCE_HAN_FONT}，请确认字体文件与代码文件在同一文件夹！")
    # 若字体缺失，用pygame默认字体兜底（避免游戏崩溃）
    font = pygame.font.Font(None, 36)
    small_font = pygame.font.Font(None, 24)
    large_font = pygame.font.Font(None, 72)
else:
    # 加载思源黑体（相对路径直接生效）
    font = pygame.font.Font(SOURCE_HAN_FONT, 36)
    small_font = pygame.font.Font(SOURCE_HAN_FONT, 24)
    large_font = pygame.font.Font(SOURCE_HAN_FONT, 72)
    print("✅ 思源黑体加载完成")

# -------------------------- 工具函数 --------------------------
def load_asset(filename, asset_type="image", size=None):
    """通用资源加载函数"""
    path = os.path.join(os.path.dirname(__file__), filename)

    if not os.path.exists(path):
        print(f"⚠️  未找到{asset_type}文件：{filename}")
        return None

    try:
        if asset_type == "image" and size:
            image = pygame.image.load(path).convert_alpha()
            return pygame.transform.scale(image, size)
        elif asset_type == "sound":
            return pygame.mixer.Sound(path)
    except Exception as e:
        print(f"❌ 加载{asset_type} {filename} 失败：{e}")

    return None


def load_words(filename="words.json"):
    """加载单词数据"""
    path = os.path.join(os.path.dirname(__file__), filename)

    if not os.path.exists(path):
        print(f"⚠️ 未找到单词文件：{filename}")
        # 创建默认单词列表
        default_words = {
            "words": [
                {"english": "abandon", "chinese": "抛弃，放弃"},
                {"english": "ability", "chinese": "能力，才能"},
                {"english": "abroad", "chinese": "在国外，海外"},
                {"english": "academic", "chinese": "学术的，教学的"},
                {"english": "accommodate", "chinese": "容纳，提供住宿"},
                {"english": "accompany", "chinese": "陪伴，伴随"},
                {"english": "accomplish", "chinese": "完成，实现"},
                {"english": "account", "chinese": "账户，解释"},
                {"english": "accurate", "chinese": "准确的，精确的"},
                {"english": "achieve", "chinese": "达到，完成"}
            ]
        }
        return default_words["words"]

    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data["words"]
    except Exception as e:
        print(f"❌ 加载单词文件失败：{e}")
        return []


# -------------------------- 蛇类 --------------------------
class Snake:
    def __init__(self):
        # 在__init__中正确定义所有实例属性
        self.length = 1  # length=1时只有蛇头，无身体；length>1时才存在蛇身
        center_x = WIDTH // 2 - (WIDTH // 2 % GRID_SIZE)
        center_y = HEIGHT // 2 - (HEIGHT // 2 % GRID_SIZE)
        self.positions = [(center_x, center_y)]
        self.direction = RIGHT
        self.next_direction = None
        self.head_image = load_asset("snake_head.webp", "image", (GRID_SIZE, GRID_SIZE))
        self.body_image = load_asset("../eatting_snake/body.jpg", "image", (GRID_SIZE, GRID_SIZE))

    def reset(self):
        """重置蛇的状态，只修改属性值，不定义新属性"""
        self.length = 1
        center_x = WIDTH // 2 - (WIDTH // 2 % GRID_SIZE)
        center_y = HEIGHT // 2 - (HEIGHT // 2 % GRID_SIZE)
        self.positions = [(center_x, center_y)]
        self.direction = RIGHT
        self.next_direction = None

    def update_direction(self):
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        head_x, head_y = self.positions[0]
        dir_x, dir_y = self.direction

        new_head_x = (head_x + dir_x * GRID_SIZE) % WIDTH
        new_head_y = (head_y + dir_y * GRID_SIZE) % HEIGHT
        new_head_x -= new_head_x % GRID_SIZE
        new_head_y -= new_head_y % GRID_SIZE

        self.positions.insert(0, (new_head_x, new_head_y))
        if len(self.positions) > self.length:
            self.positions.pop()

    def get_head_position(self):
        return self.positions[0]

    def turn(self, point):
        if (point[0] * -1, point[1] * -1) != self.direction:
            self.next_direction = point

    def draw(self, surface):
        # 绘制头部
        head_x, head_y = self.positions[0]
        if self.head_image:
            rotations = {UP: 90, DOWN: -90, LEFT: 180, RIGHT: 0}
            rotated_head = pygame.transform.rotate(self.head_image, rotations[self.direction])
            surface.blit(rotated_head, (head_x, head_y))
        else:
            pygame.draw.rect(surface, BLUE, (head_x, head_y, GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(surface, BLACK, (head_x, head_y, GRID_SIZE, GRID_SIZE), 1)

        # 绘制身体
        for body_x, body_y in self.positions[1:]:
            if self.body_image:
                surface.blit(self.body_image, (body_x, body_y))
            else:
                pygame.draw.rect(surface, WHITE, (body_x, body_y, GRID_SIZE, GRID_SIZE))
                pygame.draw.rect(surface, BLACK, (body_x, body_y, GRID_SIZE, GRID_SIZE), 1)

    def check_collision(self):
        return self.positions[0] in self.positions[1:]

    def reduce_length(self, reduce_amount):
        """新增：削减蛇身长度（保留蛇头）"""
        # 蛇身长度 = 总长度 - 1（蛇头），只有蛇身≥削减量时才生效
        body_length = self.length - 1
        if body_length >= reduce_amount:
            self.length -= reduce_amount
            # 同步削减positions列表（保留头部，删除末尾指定数量的身体段）
            self.positions = self.positions[:-reduce_amount]
            return True  # 削减成功
        return False  # 蛇身不足，削减无效


# -------------------------- 普通果实类（原有） --------------------------
class Food:
    def __init__(self):
        self.position = (0, 0)
        self.food_image = load_asset("../eatting_snake/fruit.png", "image", (GRID_SIZE, GRID_SIZE))
        self.randomize_position()

    def randomize_position(self):
        self.position = (
            random.randint(0, GRID_WIDTH - 1) * GRID_SIZE,
            random.randint(0, GRID_HEIGHT - 1) * GRID_SIZE
        )

    def draw(self, surface):
        x, y = self.position
        if self.food_image:
            surface.blit(self.food_image, (x, y))
        else:
            pygame.draw.rect(surface, RED, (x, y, GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(surface, BLACK, (x, y, GRID_SIZE, GRID_SIZE), 1)


# -------------------------- 黄金果实类（新增） --------------------------
class GoldFood:
    def __init__(self):
        self.position = (0, 0)
        self.exists = False  # 黄金果实是否在场上（控制生成频率）
        self.gold_image = load_asset("../eatting_snake/gold_fruit.png", "image", (GRID_SIZE, GRID_SIZE))  # 可替换为黄金果实图片
        self.spawn_timer = 0  # 生成计时器（控制多久生成一次）
        self.spawn_interval = 50  # 生成间隔（单位：游戏帧，约30-40秒生成一次，可调整）
        self.despawn_timer = 0  # 消失计时器（生成后一段时间不被吃则消失）
        self.despawn_interval = 25  # 消失间隔（单位：游戏帧，约15-20秒消失，可调整）

    def update(self, snake_positions):
        """更新黄金果实状态：控制生成、消失逻辑"""
        if not self.exists:
            # 不在场上时，累加计时器，到间隔后生成
            self.spawn_timer += 1
            if self.spawn_timer >= self.spawn_interval:
                self.randomize_position(snake_positions)
                self.exists = True
                self.spawn_timer = 0  # 重置生成计时器
                self.despawn_timer = 0  # 重置消失计时器
        else:
            # 在场上时，累加消失计时器，到间隔后消失
            self.despawn_timer += 1
            if self.despawn_timer >= self.despawn_interval:
                self.exists = False

    def randomize_position(self, snake_positions):
        """随机生成位置（避免与蛇身重叠）"""
        while True:
            self.position = (
                random.randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                random.randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            )
            # 确保黄金果实不生成在蛇身上
            if self.position not in snake_positions:
                break

    def draw(self, surface):
        """绘制黄金果实（只在存在时绘制）"""
        if self.exists:
            x, y = self.position
            if self.gold_image:
                surface.blit(self.gold_image, (x, y))
            else:
                # 无图片时用金色矩形替代
                pygame.draw.rect(surface, GOLD, (x, y, GRID_SIZE, GRID_SIZE))
                pygame.draw.rect(surface, BLACK, (x, y, GRID_SIZE, GRID_SIZE), 2)  # 加粗边框区分普通果实


# -------------------------- 单词测试类（新增） --------------------------
class WordQuiz:
    def __init__(self, words, snake):  # 新增参数：snake（蛇对象）
        self.words = words
        self.snake = snake  # 保存蛇对象，用于后续修改蛇身
        self.quiz_active = False
        self.current_word = None
        self.user_input = ""
        self.correct_answer = ""
        self.answered_words = set()
        self.correct_sound = load_asset("correct.mp3", "sound")
        self.wrong_sound = load_asset("wrong.mp3", "sound")

    def start_quiz(self, score):
        """每20分触发一次单词测试"""
        if score > 0 and score % 20 == 0 and not self.quiz_active and len(self.answered_words) < len(self.words):
            # 选择一个未测试的单词
            available_words = [word for word in self.words if word["english"] not in self.answered_words]
            if available_words:
                self.current_word = random.choice(available_words)
                self.user_input = ""
                self.correct_answer = self.current_word["chinese"]
                self.quiz_active = True
                return True
        return False

    def handle_input(self, event):
        if not self.quiz_active:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                # 提交答案
                self.check_answer()
                return True
            elif event.key == pygame.K_BACKSPACE:
                # 删除最后一个字符
                self.user_input = self.user_input[:-1]
                return True
        elif event.type == pygame.TEXTINPUT:
            # 处理中文输入，将输入的字符添加到user_input中
            self.user_input += event.text
            return True
        return False

    def check_answer(self):
        """检查答案是否正确"""
        if self.user_input.strip() == self.correct_answer:
            # 答案正确（原有逻辑不变）
            if self.correct_sound:
                self.correct_sound.play()
            self.answered_words.add(self.current_word["english"])
            self.quiz_active = False
            return True
        else:
            # 答案错误（新增：蛇身加长10个单位的惩罚）
            self.snake.length += 10  # 核心惩罚代码：蛇身直接加长10
            print(f"答案错误！惩罚：蛇身加长10个单位，当前蛇长：{self.snake.length}")  # 可选：控制台提示
            if self.wrong_sound:
                self.wrong_sound.play()
            self.quiz_active = False
            return False

    def draw(self, surface):
        """绘制单词测试界面"""
        if not self.quiz_active:
            return

        # 绘制半透明背景
        s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 200))
        surface.blit(s, (0, 0))

        # 绘制测试框
        quiz_rect = pygame.Rect(WIDTH // 4, HEIGHT // 4, WIDTH // 2, HEIGHT // 2)
        pygame.draw.rect(surface, WHITE, quiz_rect)
        pygame.draw.rect(surface, BLACK, quiz_rect, 3)

        # 绘制单词和输入框
        word_text = large_font.render(f"单词: {self.current_word['english']}", True, BLACK)
        surface.blit(word_text, (quiz_rect.centerx - word_text.get_width() // 2, quiz_rect.y + 50))

        prompt_text = font.render("请输入中文意思:", True, BLACK)
        surface.blit(prompt_text, (quiz_rect.centerx - prompt_text.get_width() // 2, quiz_rect.y + 120))

        input_rect = pygame.Rect(quiz_rect.centerx - 200, quiz_rect.y + 160, 400, 50)
        pygame.draw.rect(surface, BLACK, input_rect, 2)
        input_text = font.render(self.user_input, True, BLACK)
        surface.blit(input_text, (input_rect.x + 10, input_rect.y + 10))

        # 绘制提示
        hint_text = small_font.render("按Enter提交答案", True, BLACK)
        surface.blit(hint_text, (quiz_rect.centerx - hint_text.get_width() // 2, quiz_rect.y + 230))


# -------------------------- 单词学习页面（新增） --------------------------
class WordLearningPage:
    def __init__(self, words):
        self.words = words
        self.active = True

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                # 按任意键开始游戏
                self.active = False
                return True
        return False

    def draw(self, surface):
        if not self.active:
            return

        surface.fill(BLACK)

        # 绘制标题
        title_text = large_font.render("雅思单词学习", True, WHITE)
        surface.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 50))

        # 绘制提示
        hint_text = font.render("请记住以下单词，按任意键开始游戏", True, WHITE)
        surface.blit(hint_text, (WIDTH // 2 - hint_text.get_width() // 2, 120))

        # 绘制单词列表
        y_pos = 180
        for i, word in enumerate(self.words):
            word_text = font.render(f"{i + 1}. {word['english']} - {word['chinese']}", True, WHITE)
            surface.blit(word_text, (WIDTH // 2 - word_text.get_width() // 2, y_pos))
            y_pos += 40

        pygame.display.update()


# -------------------------- 通关页面（新增） --------------------------
class VictoryPage:
    def __init__(self):
        self.active = False
        self.victory_sound = load_asset("victory.mp3", "sound")

    def activate(self):
        self.active = True
        if self.victory_sound:
            self.victory_sound.play()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    # 按R键重新开始游戏
                    self.active = False
                    return "restart"
                elif event.key == pygame.K_q:
                    # 按Q键退出游戏
                    pygame.quit()
                    sys.exit()
        return None

    def draw(self, surface, score):
        if not self.active:
            return

        surface.fill(BLACK)

        # 绘制通关信息
        victory_text = large_font.render("恭喜通关！", True, GREEN)
        surface.blit(victory_text, (WIDTH // 2 - victory_text.get_width() // 2, HEIGHT // 2 - 100))

        score_text = font.render(f"最终得分: {score}", True, WHITE)
        surface.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2))

        restart_text = font.render("按R键重新开始游戏，按Q键退出", True, WHITE)
        surface.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 100))

        pygame.display.update()


# -------------------------- 游戏主类 --------------------------
class Game:
    def __init__(self):
        # 加载单词数据
        self.words = load_words()
        self.snake = Snake()  # 先创建蛇对象
        self.food = Food()
        self.gold_food = GoldFood()
        # 关键修改：创建WordQuiz时传入self.snake（蛇对象）
        self.word_quiz = WordQuiz(self.words, self.snake)  # 新增参数：self.snake
        self.learning_page = WordLearningPage(self.words)
        self.victory_page = VictoryPage()
        self.score = 0
        self.clock = pygame.time.Clock()
        self.speed = 2.5
        self.game_over = False
        self.last_quiz_score = -20  # 确保第一次吃到20分时触发测试

        # 加载音效（原有逻辑不变）
        self.bgm = load_asset("bgm.mp3", "sound")
        self.eat_sound = load_asset("eat.mp3", "sound")
        self.die_sound = load_asset("die.mp3", "sound")
        self.eat_gold_sound = load_asset("gold_fruit.mp3", "sound")

        if self.bgm:
            self.bgm.play(-1)

    def handle_events(self):
        # 处理单词学习页面事件
        if self.learning_page.active:
            if self.learning_page.handle_events():
                return

        # 处理通关页面事件
        if self.victory_page.active:
            result = self.victory_page.handle_events()
            if result == "restart":
                self.reset()
            return

        # 处理单词测试事件
        if self.word_quiz.quiz_active:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                self.word_quiz.handle_input(event)
            return

        # 处理游戏事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if self.game_over:
                    self.reset()
                    return

                key_actions = {
                    pygame.K_UP: UP,
                    pygame.K_DOWN: DOWN,
                    pygame.K_LEFT: LEFT,
                    pygame.K_RIGHT: RIGHT,
                    pygame.K_ESCAPE: "quit"
                }

                if event.key in key_actions:
                    action = key_actions[event.key]
                    if action == "quit":
                        pygame.quit()
                        sys.exit()
                    else:
                        self.snake.turn(action)

    def update(self):
        # 检查是否通关
        if len(self.word_quiz.answered_words) >= len(self.words) and not self.victory_page.active:
            self.victory_page.activate()
            return

        # 如果正在学习单词或通关，不更新游戏状态
        if self.learning_page.active or self.victory_page.active:
            return

        # 如果正在单词测试，不更新游戏状态
        if self.word_quiz.quiz_active:
            return

        if self.game_over:
            return

        # 更新蛇方向和移动
        self.snake.update_direction()
        self.snake.move()

        # 检测普通果实碰撞
        if self.snake.get_head_position() == self.food.position:
            self.snake.length += 1
            self.score += 10
            if self.eat_sound:
                self.eat_sound.play()
            # 重新生成普通果实（避免与蛇身重叠）
            while self.food.position in self.snake.positions:
                self.food.randomize_position()
            # 提升游戏速度
            self.speed = 2.5 + (self.score // 200)

            # 检查是否触发单词测试
            if self.score - self.last_quiz_score >= 20:
                if self.word_quiz.start_quiz(self.score):
                    self.last_quiz_score = self.score

        # 检测黄金果实碰撞
        if self.gold_food.exists and self.snake.get_head_position() == self.gold_food.position:
            # 尝试削减4节蛇身（不算蛇头）
            reduce_success = self.snake.reduce_length(4)
            if reduce_success:
                # 削减成功：播放音效，加分
                if self.eat_gold_sound:
                    self.eat_gold_sound.play()
                self.score += 20
            else:
                # 蛇身不足4节：播放普通音效（提示无效）
                if self.eat_sound:
                    self.eat_sound.play()
            # 无论是否削减成功，黄金果实都消失
            self.gold_food.exists = False

        # 更新黄金果实状态（生成/消失逻辑）
        self.gold_food.update(self.snake.positions)

        # 检测蛇身碰撞
        if self.snake.check_collision():
            if self.die_sound:
                self.die_sound.play()
            self.game_over = True

    def draw(self):
        screen.fill(BLACK)

        # 绘制学习页面
        if self.learning_page.active:
            self.learning_page.draw(screen)
            return

        # 绘制通关页面
        if self.victory_page.active:
            self.victory_page.draw(screen, self.score)
            return

        # 绘制游戏元素
        self.snake.draw(screen)
        self.food.draw(screen)
        self.gold_food.draw(screen)

        # 绘制分数
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        # 绘制已掌握单词进度
        progress_text = font.render(f"已掌握: {len(self.word_quiz.answered_words)}/{len(self.words)}", True, WHITE)
        screen.blit(progress_text, (10, 50))

        # 绘制单词测试界面
        self.word_quiz.draw(screen)

        # 绘制游戏结束界面
        if self.game_over:
            texts = [
                ("Game Over!", RED, -50),
                ("Press any key to restart", WHITE, 10)
            ]

            for text, color, offset in texts:
                rendered = font.render(text, True, color)
                x = WIDTH // 2 - rendered.get_width() // 2
                y = HEIGHT // 2 + offset
                screen.blit(rendered, (x, y))

        pygame.display.update()

    def reset(self):
        """重置游戏状态"""
        self.snake.reset()
        self.food.randomize_position()
        self.gold_food = GoldFood()
        self.word_quiz = WordQuiz(self.words, self.snake)
        # 确保普通果实不与蛇身重叠
        while self.food.position in self.snake.positions:
            self.food.randomize_position()
        self.score = 0
        self.last_quiz_score = -50
        self.speed = 2.5
        self.game_over = False
        if self.bgm:
            self.bgm.play(-1)

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(self.speed)


# -------------------------- 启动游戏 --------------------------
if __name__ == "__main__":
    game = Game()
    game.run()