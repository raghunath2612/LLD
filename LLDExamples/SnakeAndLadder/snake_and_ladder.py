from math import gamma
from typing import List, Dict, Deque
import random
from enum import Enum
from collections import deque

class GameStatus(Enum):
    NEW = 'NEW'
    PROGRESS = 'PROGRESS'
    COMPLETED = 'COMPLETED'

class Dice:
    def __init__(self, start: int, end: int):
        self.start = start
        self.end = end

    def roll_dice(self) -> int:
        return random.randrange(self.start, self.end + 1)

class Player:
    def __init__(self, name: str, dob: str, country: str):
        self.name = name
        self.dob = dob
        self.country = country

    def get_name(self) -> str:
        return self.name

class PlayerEntityForSnakeGame:
    def __init__(self, player: Player, position: int):
        self.player = player
        self.position = position

    def set_position(self, position: int):
        self.position = position

    def get_position(self) -> int:
        return self.position

class Board:
    def __init__(self, rows: int, cols: int):
        self.snake_and_ladders: Dict[int, int] = {}
        self.rows = rows
        self.cols = cols
        self.start = 0
        self.end = rows * cols

    def add_snake(self, start: int, end: int):
        if start < end:
            raise Exception("Cannot have start less than end")
        if start in self.snake_and_ladders:
            print("Replacing existing snake/ladder in this place")
        self.snake_and_ladders[start] = end

    def add_ladder(self, start: int, end: int):
        if start > end:
            raise Exception("Cannot have start greater than end")

        if start in self.snake_and_ladders:
            print("Replacing existing snake/ladder in this place")

        self.snake_and_ladders[start] = end

    def get_move_position(self, position: int, num_to_add: int):
        if position < 0:
            raise Exception("Invalid position")

        new_position = position + num_to_add
        if new_position > self.end:
            return position
        if new_position in self.snake_and_ladders:
            return self.snake_and_ladders[new_position]

        return new_position


    def move(self, player: PlayerEntityForSnakeGame, value_to_add: int):
        new_position = self.get_move_position(player.get_position(), value_to_add)
        print(f"Player {player.player.name} moved to position {player.get_position()} -> {new_position}")
        player.set_position(new_position)


class Game:
    def __init__(self, board: Board, dice: Dice):
        self.game_status: GameStatus = GameStatus.NEW
        self.board = board
        self.players: Deque[PlayerEntityForSnakeGame] = deque()
        self.dice = dice

    def add_player(self, player: Player):
        if self.game_status != GameStatus.NEW:
            raise Exception("Cannot add players in between the game")
        player_reference = PlayerEntityForSnakeGame(player, 0)
        self.players.append(player_reference)

    def start_internal(self):
        while self.game_status != GameStatus.COMPLETED:
            self.game_status = GameStatus.PROGRESS
            player = self.players.popleft()
            dice_position = self.dice.roll_dice()
            print(f"Dice rolled: {dice_position}")
            self.board.move(player, dice_position)
            if player.get_position() == self.board.end:
                self.game_status = GameStatus.COMPLETED
                print(f"Winner = {player.player.get_name()}")
            if dice_position == 6:
                # Player gets another turn
                self.players.appendleft(player)
            self.players.append(player)

    def start(self):
        if self.game_status != GameStatus.NEW:
            raise Exception(f"Cannot start game because game is in {self.game_status}")
        self.game_status = GameStatus.PROGRESS
        self.start_internal()


def main():
    board = Board(10, 10)
    board.add_ladder(3, 23)
    board.add_ladder(4,12)
    board.add_ladder(43, 67)
    board.add_ladder(24, 98)

    board.add_snake(69, 12)
    board.add_snake(34, 12)
    board.add_snake(87, 13)

    player1 = Player('player1', '26-12-1999', 'India')
    player2 = Player('player2', '26-12-1999', 'India')
    player3 = Player('player3', '26-12-1999', 'India')
    player4 = Player('player4', '26-12-1999', 'India')


    dice = Dice(1, 6)
    game = Game(board, dice)
    game.add_player(player1)
    game.add_player(player2)
    game.add_player(player3)
    game.add_player(player4)

    game.start()


if __name__ == "__main__":
    main()