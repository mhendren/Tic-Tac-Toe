#!/usr/bin/python

from random import choice

from Board import Board
from Evaluation import Evaluation

class AI:
    def __init__(self, player, board):
        player = 'X' if player not in ['X', 'O'] else player
        self.player = player
        self.otherPlayer = 'O' if player == 'X' else 'X'
        self.board = board

    def __generateBoards(self):
        return {option:Board(self.board.fetch(), self.board.getPlayer()).move(option) for option in self.board.validPositions()}

    def __isFirstMove(self):
        if self.board.isEmpty():
            return True
        return False

    # A corner or the center is the best starting move
    def __selectFirstMove(self):
        return choice([1, 3, 5, 7, 9])
    
    def __isSecondMove(self):
        if len(self.board.validPositions()) == 8:
            return True
        return False

    # If the opponent has taken the center, pick a corner,
    # If the opponent has taken a corner, take the center
    # otherwise pick a corner or the center
    def __selectSecondMove(self):
        validMoves = self.board.validPositions()
        if 5 not in validMoves:
            return choice([1, 3, 7, 9])
        if len([pos for pos in [1, 3, 7, 9] if pos not in validMoves]) != 0:
            return 5
        return choice([1, 3, 5, 7, 9])
    
    def __findWinner(self, boards):
        for (option, board) in boards.items():
            e = Evaluation(board)
            if e.winner() == self.player:
                return option
        return None

    def __mustBlock(self):
        for move in self.board.validPositions():
            test = Board(self.board.fetch(), self.otherPlayer).move(move)
            evaluation = Evaluation(test)
            if evaluation.winner() == self.otherPlayer:
                return move
        return None

    def __wouldWin(self, board):
        for move in board.validPositions():
            test = Board(board.fetch(), self.player).move(move)
            evaluation = Evaluation(test)
            if evaluation.winner() == self.player:
                return True
        return False

    def __countLosingMoves(self, board):
        count = 0
        for move in board.validPositions():
            test = Board(board.fetch(), self.otherPlayer).move(move)
            evaluation = Evaluation(test)
            if evaluation.winner() == self.otherPlayer:
                count = count + 1
        return count

    def __countBlocks(self, board):
        maxCount = 0
        for move in board.validPositions():
            test = Board(board.fetch(), self.otherPlayer).move(move)
            # if this move would allow a win, then there are no must blocks
            count = 0
            if not self.__wouldWin(test):
                count = self.__countLosingMoves(test)
            maxCount = count if count > maxCount else maxCount
        return maxCount

    def __multiBlockMoves(self, boards):
        multiBlockMoves = []
        for (move, board) in boards.items():
            for otherMove in board.validPositions():
                test = Board(board.fetch(), self.otherPlayer).move(move)
                if self.__countBlocks(test) > 1:
                    multiBlockMoves = multiBlockMoves + [move]
                    break
        return multiBlockMoves

    def __noMultiBlockMoves(self, boards):
        multiBlockMoves = self.__multiBlockMoves(boards)
        return [move for move in boards.keys() if move not in multiBlockMoves]
            
    def __selectBestMove(self):
        if self.__isFirstMove():
            return self.__selectFirstMove()
        if self.__isSecondMove():
            return self.__selectSecondMove()
        boards = self.__generateBoards()
        win = self.__findWinner(boards)
        if win != None:
            return win
        mustBlock = self.__mustBlock()
        if mustBlock != None:
            return mustBlock
        noMultiBlockMoves = self.__noMultiBlockMoves(boards)
        if noMultiBlockMoves != []:
            return choice(noMultiBlockMoves)
        # somehow, all moves are multiblock moves, and this fails
        # this should be impossible to reach
        return choice(self.board.validPositions())      
        
    def makeMove(self):
        self.board.move(self.__selectBestMove())
