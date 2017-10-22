"""
This is the only file you should change in your submission!
"""
from connectfour import ConnectFourBoard, human_player, run_game
from basicplayer import basic_evaluate, minimax, get_all_next_moves, is_terminal
from util import memoize, run_search_function, INFINITY, NEG_INFINITY
import pprint

# TODO Uncomment and fill in your information here. Think of a creative name that's relatively unique.
# We may compete your agent against your classmates' agents as an experiment (not for marks).
# Are you interested in participating if this competition? Set COMPETE=TRUE if yes.

# STUDENT_ID = 12345678
# AGENT_NAME =
# COMPETE = False

# TODO Change this evaluation function so that it tries to win as soon as possible
# or lose as late as possible, when it decides that one side is certain to win.
# You don't have to change how it evaluates non-winning positions.

def focused_evaluate(board):
    """
    Given a board, return a numeric rating of how good
    that board is for the current player.
    A return value >= 1000 means that the current player has won;
    a return value <= -1000 means that the current player has lost
    """
    if board.is_game_over():
        # If the game has been won, we know that it must have been
        # won or ended by the previous move.
        # The previous move was made by our opponent.
        # The score is proportional to number of remaining places to fill
        # So more remaining places means early in the game and
        # lesser remaining pieces in late in the game
        score = -1000 * (board.board_width * board.board_height - board.num_tokens_on_board())       
    else:
        score = board.longest_chain(board.get_current_player_id()) * 10
        # Prefer having your pieces in the center of the board.
        for row in range(6):
            for col in range(7):
                if board.get_cell(row, col) == board.get_current_player_id():
                    score -= abs(3-col)
                elif board.get_cell(row, col) == board.get_other_player_id():
                    score += abs(3-col)

    return score


# Create a "player" function that uses the focused_evaluate function
# You can test this player by choosing 'quick' in the main program.
quick_to_win_player = lambda board: minimax(board, depth=4,
                                            eval_fn=focused_evaluate)

def get_all_next_moves_for_alpha_beta(board):
    column_order = [3, 2, 4, 1, 5, 0, 6]
    ordered_moves = []
    for column in column_order:
        for move in get_all_next_moves(board):
            if move[0] == column:
                ordered_moves.append(move)
    return ordered_moves

def alpha_beta_search_find_board_value(board, depth,
                      alpha, beta, isMaxNode,
                      eval_fn,
                      get_next_moves_fn=get_all_next_moves,
                      is_terminal_fn=is_terminal):

    #For terminal node, just simply return the utility of the node
    if is_terminal_fn(depth, board):
        if isMaxNode:
            return eval_fn(board)
        else:
            return -1 * eval_fn(board)

    if isMaxNode:
        best_val = NEG_INFINITY
        for move, new_board in get_next_moves_fn(board):
            val = alpha_beta_search_find_board_value(new_board, depth-1, alpha, beta, False, eval_fn,
                                                get_next_moves_fn, is_terminal_fn)
            if val > best_val:
                best_val = val
                
            if best_val > alpha:
                alpha = best_val

            if beta <= best_val:
                break                
    else:
        best_val = INFINITY
        for move, new_board in get_next_moves_fn(board):
            val = alpha_beta_search_find_board_value(new_board, depth-1, alpha, beta, True, eval_fn,
                                            get_next_moves_fn, is_terminal_fn)
            if val < best_val:
                best_val = val
                
            if best_val < beta:
                beta = best_val

            if alpha >= best_val:
                break

    return best_val


# TODO Write an alpha-beta-search procedure that acts like the minimax-search
# procedure, but uses alpha-beta pruning to avoid searching bad ideas
# that can't improve the result. The tester will check your pruning by
# counting the number of static evaluations you make.

# You can use minimax() in basicplayer.py as an example.
# NOTE: You should use get_next_moves_fn when generating
# next board configurations, and is_terminal_fn when
# checking game termination.
# The default functions for get_next_moves_fn and is_terminal_fn set here will work for connect_four.
def alpha_beta_search(board, depth,
                      eval_fn,
                      get_next_moves_fn=get_all_next_moves,
                      is_terminal_fn=is_terminal, verbose=False):
    """
     board is the current tree node.

     depth is the search depth.  If you specify depth as a very large number then your search will end at the leaves of trees.
     
     def eval_fn(board):
       a function that returns a score for a given board from the
       perspective of the state's current player.
    
     def get_next_moves(board):
       a function that takes a current node (board) and generates
       all next (move, newboard) tuples.
    
     def is_terminal_fn(depth, board):
       is a function that checks whether to statically evaluate
       a board/node (hence terminating a search branch).
    """
    best_val = None
    alpha = NEG_INFINITY
    beta = INFINITY
    isMaxNode = False
    
    for move, new_board in get_next_moves_fn(board):
        val = alpha_beta_search_find_board_value(new_board, depth - 1, alpha, beta, isMaxNode, eval_fn,
                                            get_next_moves_fn,
                                            is_terminal_fn)
        if best_val is None or val > best_val[0]:
            best_val = (val, move, new_board)
                
        if best_val[0] > alpha:
            alpha = best_val[0]

        if beta <= best_val[0]:
            break
            
    if verbose:
        print("ALPHA-BETA SEARCH: Decided on column {} with rating {}".format(best_val[1], best_val[0]))

    return best_val[1]


# Now you should be able to search twice as deep in the same amount of time.
# (Of course, this alpha-beta-player won't work until you've defined alpha_beta_search.)
def alpha_beta_player(board):
    return alpha_beta_search(board, depth=8, eval_fn=focused_evaluate, get_next_moves_fn=get_all_next_moves_for_alpha_beta)


# This player uses progressive deepening, so it can kick your ass while
# making efficient use of time:
def ab_iterative_player(board):
    return run_search_function(board, search_fn=alpha_beta_search, eval_fn=focused_evaluate, timeout=5)


# TODO Finally, come up with a better evaluation function than focused-evaluate.
# By providing a different function, you should be able to beat
# simple-evaluate (or focused-evaluate) while searching to the same depth.

def get_direct_win_count(board):
    directWinCount = 0
    for col in range(7):
        colHeight = board.get_height_of_column(col)
        canPlay = colHeight != -1
        if canPlay:
            if colHeight == 6: colHeight -= 1
            directWinCount += int(board.do_move(col)._max_length_from_cell(colHeight, col) == 4)
    return directWinCount

def get_threats(board):
    odd_threats = []
    even_threats = []
    for chain in board.chain_cells(board.get_current_player_id()):
        if len(chain) == 3:
            if chain[0][0] == chain[1][0]: #horizontal
                if check_empty(board, chain[0][0], chain[0][1] + 1):
                    if chain[0][0] % 2 == 0:
                        even_threats.append((chain[0][0], chain[0][1] + 1))
                    else:
                        odd_threats.append((chain[0][0], chain[0][1] + 1))
                if check_empty(board, chain[-1][0], chain[-1][1] - 1):
                    if chain[-1][0] % 2 == 0:
                       even_threats.append((chain[-1][0], chain[-1][1] - 1)) 
                    else:
                       odd_threats.append((chain[-1][0], chain[-1][1] - 1))                        
            elif chain[0][1] == chain[1][1]: #vertical
                if check_empty(board, chain[-1][0] - 1, chain[-1][1]):
                    if (chain[-1][0] - 1) % 2 == 0:
                        even_threats.append((chain[-1][0] - 1, chain[-1][1]))
                    else:
                        odd_threats.append((chain[-1][0] - 1, chain[-1][1]))
            elif chain[0][0] - 1 == chain[1][0] and chain[0][1] - 1 ==  chain[1][1]: #diagonal down
                if check_empty(board, chain[0][0] + 1, chain[0][1] + 1):
                    if (chain[0][0] + 1) % 2 == 0:
                        even_threats.append((chain[0][0] + 1, chain[0][1] + 1))
                    else:
                        odd_threats.append((chain[0][0] + 1, chain[0][1] + 1))
                if check_empty(board, chain[-1][0] - 1, chain[-1][1] - 1):
                    if (chain[-1][0] - 1) % 2 == 0:
                        even_threats.append((chain[-1][0] - 1, chain[-1][1] - 1))
                    else:
                        odd_threats.append((chain[-1][0] - 1, chain[-1][1] - 1))
            elif chain[0][0] + 1 == chain[1][0] and chain[0][1] - 1 ==  chain[1][1]: #diagonal up
                if check_empty(board, chain[0][0] - 1, chain[0][1] + 1):
                    if (chain[0][0] - 1) % 2 == 0:
                        even_threats.append((chain[0][0] - 1, chain[0][1] + 1))
                    else:
                        odd_threats.append((chain[0][0] - 1, chain[0][1] + 1))
                if check_empty(board, chain[-1][0] + 1, chain[-1][1] - 1):
                    if (chain[-1][0] + 1) % 2 == 0:
                        even_threats.append((chain[-1][0] + 1, chain[-1][1] - 1))
                    else:
                        odd_threats.append((chain[-1][0] + 1, chain[-1][1] - 1))
    return odd_threats, even_threats

def get_winner(board):
    boardForP1 = ConnectFourBoard(board._board_array, current_player = 1)
    boardForP2 = ConnectFourBoard(board._board_array, current_player = 2)
    
    P1_threats = get_threats(boardForP1)
    P2_threats = get_threats(boardForP2)
    
    ODD = len(P2_threats[0]) - len(P1_threats[0])
    EVEN = len(P2_threats[1])
    MIXED = len(set(P1_threats[0]).intersection(P2_threats[0]))

    if ODD < 0:
        return 1
    elif ODD == 0:
        if MIXED % 2 != 0:
            return 1
        else:
            if MIXED == 0:
                if EVEN == 0:
                    return 0
                elif EVEN > 0:
                    return 2
            elif MIXED > 0:
                return 2
    elif ODD == 1:
        if MIXED == 0:
            if EVEN == 0:
                return 0
            elif EVEN > 0:
                return 2
        elif MIXED % 2 != 0:
            return 2
        else:
            return 1
    elif ODD > 1:
        return 2
        
    
def check_empty(board, row, col):
    if row < 0 or row > 5 or col < 0 or col > 6:
        return False
    return board.get_cell(row, col) == 0
    

def better_evaluate(board):
    if board.is_game_over():
        # If the game has been won, we know that it must have been
        # won or ended by the previous move.
        # The previous move was made by our opponent.
        # The score is proportional to number of remaining places to fill
        # So more remaining places means early in the game and
        # lesser remaining pieces in late in the game
        score = -1000 * (board.board_width * board.board_height - board.num_tokens_on_board())
    else:
        score = board.longest_chain(board.get_current_player_id()) * 100
        winner = get_winner(board)
        if winner == board.get_current_player_id():
            score += 100
        elif winner == board.get_other_player_id():
            score -= 100
            
        #dwScore = get_direct_win_count(board) * (board.board_width * board.board_height - board.num_tokens_on_board()) / 4
        #boardForOpponent = ConnectFourBoard(board._board_array, board_already_won=board._is_win, current_player = board.get_other_player_id())
        #dlScore = get_direct_win_count(boardForOpponent) * (boardForOpponent.board_width * boardForOpponent.board_height - boardForOpponent.num_tokens_on_board()) / 4
        #print('Direct-Win score = %d' % dwScore)
        #score += dwScore
        #score -= dlScore
        #print('Direct Wins = %d' % directWinCount)
            
        # Prefer having your pieces in the center of the board.
        for row in range(6):
            for col in range(7):
                if board.get_cell(row, col) == board.get_current_player_id():
                    score -= abs(3-col)
                elif board.get_cell(row, col) == board.get_other_player_id():
                    score += abs(3-col)
    return score                   

# Comment this line after you've fully implemented better_evaluate
#better_evaluate = memoize(basic_evaluate)

# Uncomment this line to make your better_evaluate run faster.
better_evaluate = memoize(better_evaluate)


# A player that uses alpha-beta and better_evaluate:
def my_player(board):
    return run_search_function(board, search_fn=alpha_beta_search, eval_fn=better_evaluate, timeout=5)

# my_player = lambda board: alpha_beta_search(board, depth=4, eval_fn=better_evaluate)

##if __name__ == '__main__':
##    board = ConnectFourBoard(board_array=
##                                                      ((0, 0, 0, 0, 0, 0, 0),
##                                                       (0, 0, 0, 0, 0, 0, 0),
##                                                       (0, 0, 0, 0, 0, 0, 0),
##                                                       (0, 0, 0, 0, 0, 0, 0),
##                                                       (0, 0, 2, 0, 0, 0, 0),
##                                                       (0, 0, 1, 0, 0, 0, 0),
##                                                       ),
##                                                      current_player=1)
##    print(get_winner(board))
##    #pprint.pprint(get_threats(board))
##    #boardForOpponent = ConnectFourBoard(board._board_array, current_player = board.get_other_player_id())
##    #pprint.pprint(get_threats(boardForOpponent))
##    #pprint.pprint(board._chain_sets_from_cell(4,2))
##    
    
