import math
import random

class GameLogic:
    def __init__(self, rows=3, cols=3, streak_to_win=3):
        self.rows = rows
        self.cols = cols
        self.streak_to_win = streak_to_win
        self.board = {} 
        self.current_player = "X" 
        self.game_over = False
        self.winner = None
        self.ai_mode = True
        
        self.ai_char = "O"
        self.human_char = "X"
        
        self.max_depth = 3 if rows * cols > 20 else 9

    def is_valid_move(self, r, c):
        return (0 <= r < self.rows) and (0 <= c < self.cols) and ((r, c) not in self.board) and not self.game_over

    # --- ĐÂY LÀ HÀM CẦN SỬA ---
    def make_move(self, r, c):
        if not self.is_valid_move(r, c): return None
        
        # [SỬA LỖI]: Lưu lại người vừa đánh trước khi đổi lượt
        player_moved = self.current_player 
        
        # Ghi nhận nước đi
        self.board[(r, c)] = player_moved
        
        # Kiểm tra thắng thua
        if self.check_winner(r, c):
            self.game_over = True
            self.winner = player_moved
        elif len(self.board) == self.rows * self.cols:
            self.game_over = True 
            self.winner = "Draw"
        else:
            # Đổi lượt cho người tiếp theo
            self.current_player = "O" if self.current_player == "X" else "X"
        
        # [QUAN TRỌNG]: Trả về người VỪA ĐÁNH (player_moved) 
        # thay vì người chơi tiếp theo (self.current_player)
        return player_moved 
    # --------------------------

    def check_winner(self, r, c):
        player = self.board.get((r, c))
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for dr, dc in directions:
            count = 1
            for k in range(1, self.streak_to_win):
                if self.board.get((r + k*dr, c + k*dc)) == player: count += 1
                else: break
            for k in range(1, self.streak_to_win):
                if self.board.get((r - k*dr, c - k*dc)) == player: count += 1
                else: break
            if count >= self.streak_to_win: return True
        return False

    # ... (Giữ nguyên phần Minimax AI bên dưới không đổi) ...
    
    def get_ai_move(self):
        possible_moves = self.generate_moves()
        if not possible_moves: return (self.rows // 2, self.cols // 2)

        self.ai_char = self.current_player
        self.human_char = "O" if self.ai_char == "X" else "X"

        best_score = -math.inf
        best_move = None
        alpha = -math.inf
        beta = math.inf

        for move in possible_moves:
            self.board[move] = self.ai_char 
            score = self.minimax(self.max_depth - 1, alpha, beta, False)
            del self.board[move]
            
            if score > best_score:
                best_score = score
                best_move = move
            
            alpha = max(alpha, score)
            if beta <= alpha: break
                
        return best_move

    def minimax(self, depth, alpha, beta, is_maximizing):
        if depth == 0 or self.check_game_over_simulated():
            return self.evaluate_board()

        possible_moves = self.generate_moves()
        if not possible_moves: return 0 

        if is_maximizing:
            max_eval = -math.inf
            for move in possible_moves:
                self.board[move] = self.ai_char 
                eval_score = self.minimax(depth - 1, alpha, beta, False)
                del self.board[move]
                
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha: break 
            return max_eval
        else:
            min_eval = math.inf
            for move in possible_moves:
                self.board[move] = self.human_char 
                eval_score = self.minimax(depth - 1, alpha, beta, True)
                del self.board[move]
                
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha: break 
            return min_eval

    def generate_moves(self):
        if not self.board: return [(self.rows//2, self.cols//2)]
        candidates = set()
        for (r, c) in self.board.keys():
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0: continue
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < self.rows and 0 <= nc < self.cols and (nr, nc) not in self.board:
                        candidates.add((nr, nc))
        return list(candidates)

    def evaluate_board(self):
        return self.scan_score(self.ai_char) - self.scan_score(self.human_char) * 1.2

    def scan_score(self, player):
        score = 0
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        processed = set()
        
        for (r, c), p in self.board.items():
            if p != player or (r,c) in processed: continue
            
            for dr, dc in directions:
                prev = (r - dr, c - dc)
                if self.board.get(prev) == player: continue
                
                count = 0
                curr_r, curr_c = r, c
                while self.board.get((curr_r, curr_c)) == player:
                    count += 1
                    curr_r += dr
                    curr_c += dc
                
                blocked = 0
                if not (0 <= prev[0] < self.rows and 0 <= prev[1] < self.cols) or \
                   (self.board.get(prev) is not None and self.board.get(prev) != player): blocked += 1
                   
                next_pos = (curr_r, curr_c)
                if not (0 <= next_pos[0] < self.rows and 0 <= next_pos[1] < self.cols) or \
                   (self.board.get(next_pos) is not None and self.board.get(next_pos) != player): blocked += 1
                
                score += self.get_shape_score(count, blocked)
        return score

    def get_shape_score(self, count, blocked):
        if count >= self.streak_to_win: return 10000000
        if blocked == 2: return 0
        if count == self.streak_to_win - 1: return 100000 if blocked == 0 else 1000
        if count == self.streak_to_win - 2: return 1000 if blocked == 0 else 100
        return 10

    def check_game_over_simulated(self):
        return False