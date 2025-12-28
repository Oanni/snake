"""
Игра "Змейка" (Snake Game).

Классическая игра, где игрок управляет змейкой,
которая движется по игровому полю и ест яблоки.
"""

import pygame
import random
from typing import List, Tuple

# Константы игрового поля
CELL_SIZE = 20
FIELD_WIDTH = 32
FIELD_HEIGHT = 24
SCREEN_WIDTH = FIELD_WIDTH * CELL_SIZE  # 640
SCREEN_HEIGHT = FIELD_HEIGHT * CELL_SIZE  # 480

# Цвета
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Направления движения
UP = (0, -CELL_SIZE)
DOWN = (0, CELL_SIZE)
LEFT = (-CELL_SIZE, 0)
RIGHT = (CELL_SIZE, 0)

# Все возможные ячейки на поле
ALL_CELLS = set((x * CELL_SIZE, y * CELL_SIZE)
                for x in range(FIELD_WIDTH)
                for y in range(FIELD_HEIGHT))

# Центральная позиция игрового поля
CENTER_POSITION = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)


class GameObject:
    """Базовый класс для игровых объектов."""

    def __init__(self, position: Tuple[int, int] = None):
        """
        Инициализирует игровой объект.

        Args:
            position: Позиция объекта на игровом поле.
                     По умолчанию - центр экрана.
        """
        if position is None:
            position = CENTER_POSITION
        self.position = position
        self.body_color = None

    def draw_cell(self, screen: pygame.Surface, position: Tuple[int, int], color: Tuple[int, int, int]):
        """
        Отрисовывает одну ячейку на игровом поле.

        Args:
            screen: Поверхность для отрисовки.
            position: Позиция ячейки (x, y).
            color: Цвет ячейки (RGB).
        """
        rect = pygame.Rect(position[0], position[1], CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, color, rect)

    def draw(self, screen: pygame.Surface):
        """
        Абстрактный метод для отрисовки объекта.

        Должен быть переопределен в дочерних классах.
        """
        pass


class Apple(GameObject):
    """Класс яблока на игровом поле."""

    def __init__(self, occupied_positions: List[Tuple[int, int]] = None):
        """
        Инициализирует яблоко.

        Args:
            occupied_positions: Список занятых позиций (тело змейки),
                               чтобы яблоко не появилось на них.
        """
        super().__init__()
        self.body_color = RED
        self.occupied_positions = occupied_positions or []
        self.randomize_position()

    def randomize_position(self, occupied_positions: List[Tuple[int, int]] = None):
        """
        Устанавливает случайное положение яблока на игровом поле.

        Args:
            occupied_positions: Список занятых позиций. Если не указан,
                               используется self.occupied_positions.
        """
        if occupied_positions is not None:
            self.occupied_positions = occupied_positions

        # Вычисляем свободные ячейки
        occupied_set = set(self.occupied_positions)
        free_cells = tuple(ALL_CELLS - occupied_set)

        if free_cells:
            self.position = random.choice(free_cells)
        else:
            # Если все ячейки заняты (маловероятно), выбираем случайную
            self.position = random.choice(tuple(ALL_CELLS))

    def draw(self, screen: pygame.Surface):
        """
        Отрисовывает яблоко на игровой поверхности.

        Args:
            screen: Поверхность для отрисовки.
        """
        self.draw_cell(screen, self.position, self.body_color)


class Snake(GameObject):
    """Класс змейки."""

    def __init__(self):
        """Инициализирует змейку в начальном состоянии."""
        # Начальная позиция - центр экрана
        initial_position = CENTER_POSITION
        super().__init__(initial_position)
        self.body_color = GREEN
        self.length = 1
        self.positions = [initial_position]
        self.direction = RIGHT
        self.next_direction = None

    def update_direction(self):
        """Обновляет направление движения змейки."""
        if self.next_direction is not None:
            # Проверяем, что змейка не пытается двигаться назад
            opposite_directions = {
                UP: DOWN,
                DOWN: UP,
                LEFT: RIGHT,
                RIGHT: LEFT
            }
            if self.next_direction != opposite_directions.get(self.direction):
                self.direction = self.next_direction
            self.next_direction = None

    def move(self, grow: bool = False):
        """
        Обновляет позицию змейки.

        Args:
            grow: Если True, змейка увеличивается (не удаляется хвост).
        """
        # Получаем текущую позицию головы
        head_x, head_y = self.get_head_position()

        # Вычисляем новую позицию головы с учетом прохождения через границы
        new_head_x = (head_x + self.direction[0]) % SCREEN_WIDTH
        new_head_y = (head_y + self.direction[1]) % SCREEN_HEIGHT
        new_head = (new_head_x, new_head_y)

        # Добавляем новую голову в начало списка
        self.positions.insert(0, new_head)

        # Если змейка не растет, удаляем хвост
        if not grow:
            self.positions.pop()
        else:
            self.length = len(self.positions)

    def get_head_position(self) -> Tuple[int, int]:
        """
        Возвращает позицию головы змейки.

        Returns:
            Кортеж с координатами головы (x, y).
        """
        return self.positions[0]

    def check_self_collision(self) -> bool:
        """
        Проверяет столкновение змейки с самой собой.

        Returns:
            True, если произошло столкновение, False иначе.
        """
        # Если длина меньше 4, самоукус невозможен
        if self.length < 4:
            return False

        head = self.get_head_position()
        # Проверяем, есть ли голова в теле (кроме самой головы)
        return head in self.positions[1:]

    def reset(self):
        """Сбрасывает змейку в начальное состояние после столкновения."""
        initial_position = CENTER_POSITION
        self.length = 1
        self.positions = [initial_position]
        self.direction = RIGHT
        self.next_direction = None
        self.position = initial_position

    def draw(self, screen: pygame.Surface, last_tail_position: Tuple[int, int] = None):
        """
        Отрисовывает змейку на экране.

        Args:
            screen: Поверхность для отрисовки.
            last_tail_position: Позиция последнего хвостового сегмента
                               для затирания следа (если змейка не растет).
        """
        # Затираем след (последний хвостовой сегмент), если змейка не растет
        if last_tail_position is not None:
            self.draw_cell(screen, last_tail_position, BLACK)

        # Отрисовываем все сегменты змейки
        for position in self.positions:
            self.draw_cell(screen, position, self.body_color)


def handle_keys(event: pygame.event.Event, snake: Snake) -> bool:
    """
    Обрабатывает нажатия клавиш для управления змейкой.

    Args:
        event: Событие клавиатуры от Pygame.
        snake: Экземпляр змейки для управления.

    Returns:
        True, если была нажата клавиша ESC (выход из игры),
        False в противном случае.
    """
    # Словарь для определения нового направления
    # Ключ: (нажатая_клавиша, текущее_направление), значение: новое_направление
    direction_map = {
        (pygame.K_UP, RIGHT): UP,
        (pygame.K_UP, LEFT): UP,
        (pygame.K_DOWN, RIGHT): DOWN,
        (pygame.K_DOWN, LEFT): DOWN,
        (pygame.K_LEFT, UP): LEFT,
        (pygame.K_LEFT, DOWN): LEFT,
        (pygame.K_RIGHT, UP): RIGHT,
        (pygame.K_RIGHT, DOWN): RIGHT,
    }

    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            return True

        # Определяем новое направление через словарь
        new_direction = direction_map.get((event.key, snake.direction))
        if new_direction is not None:
            snake.next_direction = new_direction

    return False


def main():
    """Основной игровой цикл."""
    # Инициализация Pygame
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Змейка")
    clock = pygame.time.Clock()

    # Создание игровых объектов
    snake = Snake()
    apple = Apple(snake.positions)

    # Переменная для отслеживания позиции хвоста для затирания
    last_tail_position = None
    best_length = 1

    running = True
    while running:
        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if handle_keys(event, snake):
                running = False

        # Обновление направления движения змейки
        snake.update_direction()

        # Сохраняем позицию хвоста перед движением для затирания
        if snake.positions:
            last_tail_position = snake.positions[-1]

        # Вычисляем следующую позицию головы для проверки поедания яблока
        head_x, head_y = snake.get_head_position()
        next_head_x = (head_x + snake.direction[0]) % SCREEN_WIDTH
        next_head_y = (head_y + snake.direction[1]) % SCREEN_HEIGHT
        next_head = (next_head_x, next_head_y)

        # Проверка, съест ли змейка яблоко на следующем шаге
        will_grow = next_head == apple.position

        # Движение змейки
        if will_grow:
            snake.move(grow=True)
            # Обновляем рекорд
            if snake.length > best_length:
                best_length = snake.length
                pygame.display.set_caption(f"Змейка - Рекорд: {best_length}")
            # Перемещаем яблоко на новую позицию
            apple.randomize_position(snake.positions)
            # Не затираем хвост при росте
            last_tail_position = None
        else:
            snake.move(grow=False)

        # Проверка столкновения змейки с самой собой
        if snake.check_self_collision():
            # При самоукусе оставляем только голову
            head_pos = snake.get_head_position()
            snake.positions = [head_pos]
            snake.length = 1
            last_tail_position = None

        # Заливка экрана черным цветом
        screen.fill(BLACK)

        # Отрисовка
        snake.draw(screen, last_tail_position)
        apple.draw(screen)

        # Обновление экрана
        pygame.display.update()

        # Контроль скорости игры (20 кадров в секунду)
        clock.tick(20)

    pygame.quit()


if __name__ == "__main__":
    main()

