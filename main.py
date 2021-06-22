import pygame
from random import shuffle, randint
from time import sleep
from copy import deepcopy

pygame.init()


class Grid:
    def __init__(self, known_cells_count):
        self.puzzle: list = [[0 for _ in range(9)] for _ in range(9)]
        self.grid: list = [[0 for _ in range(9)] for _ in range(9)]
        self.grid_filled: bool = False
        self.generate_puzzle(known_cells_count)

    # Function to return randomized list that contains all elements of a range()
    @staticmethod
    def shuffled_range(start: int, end: int) -> list:
        result: list = [i for i in range(start, end)]
        shuffle(result)
        return result

    # Function to apply puzzle to grid
    def apply_puzzle_to_grid(self) -> None:
        for known_cell in self.puzzle:
            self.grid[known_cell[1][0]][known_cell[1][1]] = known_cell[0]

    # Function to check if row in grid is valid
    def check_row_validity(self, row: int) -> bool:
        seen: list = []
        for i in self.grid[row]:
            if i not in seen and i != 0:
                seen.append(i)
            elif i in seen:
                return False
        return True

    # Function to check if column in grid is valid
    def check_column_validity(self, column: int) -> bool:
        column: list = [self.grid[i][column] for i in range(9)]
        seen: list = []
        for i in column:
            if i not in seen and i != 0:
                seen.append(i)
            elif i in seen:
                return False
        return True

    # Function to check if 3x3 subgrid in grid is valid
    def check_subgrid_validity(self, row: int, column: int) -> bool:
        subgrid_x: int = 0 if row <= 2 else (3 if row <= 5 else 6)
        subgrid_y: int = 0 if column <= 2 else (3 if column <= 5 else 6)
        subgrid: list = [self.grid[y][x] for x in range(subgrid_x, subgrid_x + 3) for y in range(subgrid_y, subgrid_y + 3)]
        seen: list = []
        for i in subgrid:
            if i not in seen and i != 0:
                seen.append(i)
            elif i in seen:
                return False
        return True

    # Wrapper function to check for a location and related region is valid
    def check_location_validity(self, row: int, column: int) -> bool:
        return (
            self.check_row_validity(row)
            and self.check_column_validity(column)
            and self.check_subgrid_validity(row, column)
        )

    # Function to check the validity of the whole grid
    def check_grid_validity(self) -> bool:
        for i in range(9):
            for j in range(9):
                if (
                    self.grid[i][j] == 0
                    or not self.check_row_validity(i)
                    or not self.check_column_validity(j)
                    or not self.check_subgrid_validity(i, j)
                ):
                    return False
        return True

    # Solve function using backtracking.
    def solve_grid(self) -> bool:
        for row in range(9):
            for column in range(9):
                if self.grid[row][column] == 0:
                    for num in self.shuffled_range(1, 10):
                        self.grid[row][column] = num
                        if self.check_location_validity(row, column) and self.solve_grid():
                            return True
                        self.grid[row][column] = 0
                    return False
        self.grid_filled = True
        return True

    # Solves an empty grid, then removes random cells.
    def generate_puzzle(self, known_cells_count: int) -> None:
        self.solve_grid()
        self.puzzle = deepcopy(self.grid)
        self.grid = [[0 for _ in range(9)] for _ in range(9)]
        for _ in range(81 - known_cells_count):
            coordinates: list = [(x, y) for x in range(9) for y in range(9)]
            shuffle(coordinates)
            while True:
                c = coordinates.pop()
                row, column = c[0], c[1]
                if self.puzzle[row][column] == 0:
                    continue
                self.puzzle[row][column] = 0
                break
        self.grid = deepcopy(self.puzzle)

fps_cap: int = 60
clock = pygame.time.Clock()
display_surface = pygame.display.set_mode((85 * 9, 85 * 9))
pygame.display.set_icon(pygame.image.load("assets/numbers.png").subsurface(0, 85, 85, 85))
pygame.display.set_caption("Sudoku!")
assets: dict = {}
sudoku: Grid
known_cells_count: int = 0
chosen_cell_x, chosen_cell_y = -1, -1
cell_values = {
    pygame.K_0: 0,
    pygame.K_BACKSPACE: 0,
    pygame.K_DELETE: 0,
    pygame.K_1: 1,
    pygame.K_2: 2,
    pygame.K_3: 3,
    pygame.K_4: 4,
    pygame.K_5: 5,
    pygame.K_6: 6,
    pygame.K_7: 7,
    pygame.K_8: 8,
    pygame.K_9: 9
}

def reset_screen() -> None:
    global display_surface
    display_surface = pygame.display.set_mode((85 * 9, 85 * 9))
    pygame.display.set_icon(pygame.image.load("assets/numbers.png").subsurface(0, 85, 85, 85))
    pygame.display.set_caption("Sudoku!")
    display_surface.fill((0, 0, 0, 255))

def initialize_assets() -> None:
    assets["cell_org"] = pygame.image.load("assets/cell.png").subsurface(0, 0, 85, 85)
    assets["cell_alt"] = pygame.image.load("assets/cell.png").subsurface(85, 0, 85, 85)

    for number in "123456789":
        assets[number] = {}
        for tag in [("known", 0), ("input", 1), ("invalid", 2), ("complete", 3)]:
            assets[number][tag[0]] = pygame.image.load("assets/numbers.png").subsurface(
                (int(number) - 1) * 85, tag[1] * 85, 85, 85
            )

def draw_difficulty_screen() -> None:
    reset_screen()
    draw_background()
    loading_font = pygame.font.SysFont("Trebuchet MS", 26)
    loading_text = loading_font.render("(E)asy ---- (M)edium ---- (H)ard", True, (0, 0, 0))
    display_surface.blit(loading_text, (85 * 3 + 24, 85 * 6 + 47))
    loading_text = loading_font.render("Input a character for difficulty.", True, (0, 0, 0))
    display_surface.blit(loading_text, (85 * 3 + 35, 85 * 6 + 15))
    pygame.display.update()

def draw_loading_screen() -> None:
    reset_screen()
    draw_background()
    loading_font = pygame.font.SysFont("Trebuchet MS", 50)
    loading_text = loading_font.render("Loading...", True, (0, 0, 0))
    display_surface.blit(loading_text, (85 * 4 + 45, 85 * 6 + 35))
    pygame.display.update()

def draw_waiting_screen() -> None:
    reset_screen()
    draw_background()
    loading_font = pygame.font.SysFont("Trebuchet MS", 32)
    loading_text = loading_font.render("Press enter to start!", True, (0, 0, 0))
    display_surface.blit(loading_text, (85 * 5 + 15, 85 * 7))
    pygame.display.update()

def draw_background() -> None:
    background: list = [
        ["cell_org" if i % 2 == 0 else "cell_alt" for i in range(9)] if j % 2 == 0
        else ["cell_alt" if i % 2 == 0 else "cell_org" for i in range(9)] for j in range(9)
                        ]
    for i in range(9):
        for j in range(9):
            display_surface.blit(assets[background[i][j]], (i * 85, j * 85))

    for i in [5, 85 * 3, 85 * 6]:
        pygame.draw.rect(display_surface, (0, 0, 0, 225), (i - 5, 0, 6, 85 * 9), 0)
        pygame.draw.rect(display_surface, (0, 0, 0, 225), (0, i - 5, 85 * 9, 6), 0)
    pygame.draw.rect(display_surface, (0, 0, 0, 225), (85 * 9 - 5, 0, 6, 85 * 9), 0)
    pygame.draw.rect(display_surface, (0, 0, 0, 225), (0, 85 * 9 - 5, 85 * 9, 6), 0)

    pygame.display.update()

def draw_puzzle() -> None:
    for i in range(9):
        for j in range(9):
            if sudoku.puzzle[i][j] != 0:
                display_surface.blit(assets[str(sudoku.puzzle[i][j])]["known"], (i * 85, j * 85))

    pygame.display.update()

def draw_grid() -> None:
    for i in range(9):
        for j in range(9):
            if sudoku.grid[i][j] != 0 and sudoku.puzzle[i][j] == 0:
                display_surface.blit(assets[str(sudoku.grid[i][j])]["input"], (i * 85, j * 85))

def draw_chosen_cell_frame() -> None:
    pygame.draw.rect(display_surface, (0, 0, 0, 255), (chosen_cell_x * 85, chosen_cell_y * 85, 85, 6), 0)
    pygame.draw.rect(display_surface, (0, 0, 0, 255), (chosen_cell_x * 85, chosen_cell_y * 85, 6, 85), 0)
    pygame.draw.rect(display_surface, (0, 0, 0, 255), ((chosen_cell_x + 1) * 85 - 6, chosen_cell_y * 85, 6, 85), 0)
    pygame.draw.rect(display_surface, (0, 0, 0, 255), (chosen_cell_x * 85, (chosen_cell_y + 1) * 85 - 6, 85, 6), 0)

    pygame.display.update()

def draw_invalid_cell() -> None:
    display_surface.blit(
        assets[str(sudoku.grid[chosen_cell_x][chosen_cell_y])]["invalid"],
        (chosen_cell_x * 85, chosen_cell_y * 85)
    )

    pygame.display.update()

def draw_complete_grid() -> None:
    for i in range(9):
        for j in range(9):
            if sudoku.grid[i][j] != 0:
                display_surface.blit(
                    assets[str(sudoku.grid[i][j])]["complete"],
                    (i * 85, j * 85)
                )

    pygame.display.update()

def update_graphics() -> None:
    draw_background()
    if sudoku.check_grid_validity():
        draw_complete_grid()
    else:
        draw_puzzle()
        draw_grid()
        clock.tick(fps_cap)
        if (chosen_cell_x, chosen_cell_y) != (-1, -1):
            draw_chosen_cell_frame()
            if not sudoku.check_location_validity(chosen_cell_x, chosen_cell_y):
                draw_invalid_cell()

def update_chosen_cell_coords() -> None:
    global chosen_cell_x, chosen_cell_y
    chosen_cell_coords = list(pygame.mouse.get_pos())
    chosen_cell_x, chosen_cell_y = chosen_cell_coords

    chosen_cell_x -= chosen_cell_x % 85
    chosen_cell_x //= 85
    chosen_cell_y -= chosen_cell_y % 85
    chosen_cell_y //= 85

def map_input_to_cell(event) -> None:
    if (chosen_cell_x, chosen_cell_y) != (-1, -1) and sudoku.puzzle[chosen_cell_x][chosen_cell_y] == 0:
        for keycode in cell_values:
            if event.key == keycode:
                sudoku.grid[chosen_cell_x][chosen_cell_y] = cell_values[keycode]
                return

def choose_difficulty() -> None:
    draw_difficulty_screen()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.display.quit()
                quit(0)
            elif event.type == pygame.KEYUP:
                global known_cells_count
                if event.key == pygame.K_e:
                    known_cells_count = randint(35, 50)
                elif event.key == pygame.K_m:
                    known_cells_count = randint(26, 34)
                elif event.key == pygame.K_h:
                    known_cells_count = randint(17, 25)
                return

def initialize_game() -> None:
    global sudoku
    initialize_assets()
    choose_difficulty()
    draw_loading_screen()
    sudoku = Grid(known_cells_count)
    draw_waiting_screen()

def wait_input() -> None:
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.display.quit()
                quit(0)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                reset_screen()
                return

def proceed_to_next_grid() -> None:
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.display.quit()
                quit(0)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                main()

def game_loop() -> None:
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.display.quit()
                quit(0)
            else:
                if event.type != pygame.MOUSEMOTION:
                    update_graphics()
                    if event.type == pygame.MOUSEBUTTONUP:
                        update_chosen_cell_coords()
                        update_graphics()
                        break
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            main()
                        else:
                            map_input_to_cell(event)
                            update_graphics()
                            break
                if sudoku.check_grid_validity():
                    proceed_to_next_grid()
                    main()
        sleep(0.05)

def main() -> None:
    initialize_assets()
    choose_difficulty()
    initialize_game()
    wait_input()
    game_loop()

if __name__ == "__main__":
    main()