#!/usr/bin/env python3

from copy import deepcopy
import easygui
import networkx as nx
import matplotlib
matplotlib.use("TkAgg")
from matplotlib import pyplot as plt

# Global graph
G = nx.Graph()


class SixPoints:
    def __init__(self, other=None):
        self.moves = 0
        self.lost = False
        self.loser = None

        if other:
            self.adj = deepcopy(other.adj)
            self.moves = other.moves
            self.lost = other.lost
            self.loser = other.loser
        else:
            self.adj = [[None for _ in range(6)] for _ in range(6)]

    def isOver(self):
        return self.moves >= 15 or self.lost

    def isFree(self, i, j):
        """Returns whether board position i, j is free"""
        if self.adj[i][j]:
            return False
        else:
            return True

    def takeTurn(self, player, i, j):
        """Receives the player marker, and board position,
           and returns True if the move results in a loss for that player """

        if self.adj[i][j]:
            raise ValueError(
                'An edge between {} and {} already exists'.format(i, j))

        if i == j:
            raise ValueError(
                'Cannot place an edge between {} and itself'.format(i))

        lost = False

        for k, iNeighbor in enumerate(self.adj[i]):
            for l, jNeighbor in enumerate(self.adj[j]):
                if k == l and iNeighbor == player and jNeighbor == player:
                    lost = True

        self.adj[i][j] = player
        self.adj[j][i] = player

        self.moves += 1
        if lost:
            self.lost = True
            self.loser = player

        return lost

    def __str__(self):
        s = "Board:\n"
        s += " 123456\n"
        for i in range(6):
            s += str(i + 1)
            #s +=" " * i
            for j in range(6):
                if i > j:
                    s += "{}".format(self.adj[j][i]
                                     if self.adj[j][i] != None else '.')
            s += '\n'

        s += "\nEdge List:\n"
        edges = []
        for i in range(6):
            for j in range(6):
                if i < j and self.adj[i][j]:
                    edges.append((self.adj[i][j], i, j))

        prevPlayer = 's'
        for edge in reversed(sorted(edges)):
            s += "{}: {} - {}\n".format(*edge)
        return s


class AI:
    def __init__(self, player):
        self.player = player
        self.otherPlayer = 'd' if player == 's' else 's'

    def takeTurn(self, game):
        moves = []

        for i in range(6):
            for j in range(6):
                if i != j and game.isFree(i, j):
                    move = SixPoints(game)
                    move.takeTurn(self.player, i, j)

                    v = self.minimax(move, game.moves + 4, -
                                     1, 1, self.player == 's')
                    moves.append((v, (i, j)))

        moves = list(reversed(sorted(moves)))
        G.add_edge(*moves[0][1], style='dashed', color='r')
        edges = G.edges()
        styles = [G[u][v]['style'] for u, v in edges]
        colors = [G[u][v]['color'] for u, v in edges]
        nx.draw(G, nx.get_node_attributes(G, 'pos'),
                edge_color=colors, style=styles, with_labels=True)
        plt.show(block=False)

        if len(moves) > 0:
            return game.takeTurn(self.player, *moves[0][1])
        else:
            return True

    def minimax(self, game, depth, a, b, amMax):

        if game.isOver() or depth == 0:
            if game.loser == self.player:
                return -1
            else:
                return 1

        if amMax:
            best = -1
            for i in range(6):
                for j in range(6):
                    if(i != j and game.isFree(i, j)):
                        newGame = SixPoints(game)
                        newGame.takeTurn(self.player, i, j)
                        v = self.minimax(newGame, depth - 1, a, b, False)
                        best = max(best, v)
                        a = max(a, best)
                        if b <= a:
                            return best
            return best
        else:
            best = 1
            for i in range(6):
                for j in range(6):
                    if(i != j and game.isFree(i, j)):
                        newGame = SixPoints(game)
                        newGame.takeTurn(self.otherPlayer, i, j)
                        v = self.minimax(newGame, depth - 1, a, b, True)
                        best = min(best, v)
                        b = min(b, best)
                        if b <= a:
                            return best
            return best


def PlayGame():
    game = SixPoints()
    G.clear()
    G.add_node(1, pos=(1, 2))
    G.add_node(2, pos=(2, 1))
    G.add_node(3, pos=(3, 1))
    G.add_node(4, pos=(4, 2))
    G.add_node(5, pos=(3, 3))
    G.add_node(0, pos=(2, 3))

    FirstTurn = easygui.buttonbox(
        'Do you want to go first or second?', 'Hexagon Game', ('First', 'Second'))
    if FirstTurn == 'First':
        try:
            print("#### d's turn ####\n")
            a = int(easygui.buttonbox(
                'Pick the first node.', 'Hexagon Game', ('0', '1', '2', '3', '4', '5')))
            b = int(easygui.buttonbox(
                'Pick the second node.', 'Hexagon Game', ('0', '1', '2', '3', '4', '5')))

            game.takeTurn('d', a, b)

        except KeyboardInterrupt:
            raise
        except:
            print("Invalid move. Try again")
        finally:
            G.add_edge(a, b, style='solid', color='g')
            edges = G.edges()
            styles = [G[u][v]['style'] for u, v in edges]
            colors = [G[u][v]['color'] for u, v in edges]
            nx.draw(G, nx.get_node_attributes(G, 'pos'),
                    edge_color=colors, style=styles, with_labels=True)
            plt.show(block=False)

    ai = AI('s')

    over = False

    while not over:
        print("#### s's turn ####\n")

        print("Thinking...\n")
        if ai.takeTurn(game):
            over = True
        print(game)

        while not over:
            try:
                print("#### d's turn ####\n")
                a = int(easygui.buttonbox(
                    'Pick the first node.', 'Hexagon Game', ('0', '1', '2', '3', '4', '5')))
                b = int(easygui.buttonbox(
                    'Pick the second node.', 'Hexagon Game', ('0', '1', '2', '3', '4', '5')))

                if game.takeTurn('d', a, b):
                    over = True
                break
            except KeyboardInterrupt:
                raise
            except:
                print("Invalid move. Try again")
                continue
            finally:
                G.add_edge(a, b, style='solid', color='g')
                edges = G.edges()
                styles = [G[u][v]['style'] for u, v in edges]
                colors = [G[u][v]['color'] for u, v in edges]
                nx.draw(G, nx.get_node_attributes(G, 'pos'),
                        edge_color=colors, style=styles, with_labels=True)
                plt.show(block=False)

    print(game)
    edges = G.edges()
    styles = [G[u][v]['style'] for u, v in edges]
    colors = [G[u][v]['color'] for u, v in edges]
    nx.draw(G, nx.get_node_attributes(G, 'pos'),
            edge_color=colors, style=styles, with_labels=True)
    plt.show()

    print(game.adj)

    return game.loser


if __name__ == '__main__':
    loser = PlayGame()
    message = loser + " lost."
    Active = True

    while Active:
        playAgain = easygui.buttonbox(
            message, 'Hexagon Game', ('Play again', 'Exit'))
        if playAgain == 'Play again':
            PlayGame()
        else:
            quit()
