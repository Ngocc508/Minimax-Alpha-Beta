import tkinter as tk
from tkinter import messagebox, ttk
import game_logic as logic

class GameApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TicTacToe / Gomoku - Custom AI")
        self.root.geometry("1100x750")
        self.root.configure(bg="#2c3e50")
        
        self.game = logic.GameLogic(3, 3, 3)
        self.cell_size = 60
        self.ai_symbol = "O"   
        self.user_symbol = "X" 
        
        self._setup_ui()

    def _setup_ui(self):
        sidebar = tk.Frame(self.root, bg="white", padx=20, pady=20, width=320)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="CẤU HÌNH GAME", font=("Segoe UI", 16, "bold"), bg="white", fg="#2c3e50").pack(pady=(0, 20))

        self.entry_rows = self.create_input(sidebar, "Số Dòng:", "3")
        self.entry_cols = self.create_input(sidebar, "Số Cột:", "3")
        self.entry_streak = self.create_input(sidebar, "Số thắng (Streak):", "3")
  
        tk.Label(sidebar, text="Chế độ chơi:", bg="white", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(10, 0))
        self.combo_mode = ttk.Combobox(sidebar, values=["Người vs Người", "Người vs Máy (AI)"], state="readonly")
        self.combo_mode.current(1)
        self.combo_mode.pack(fill=tk.X, pady=(0, 10))

        tk.Label(sidebar, text="Bạn chọn quân:", bg="white", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.combo_symbol = ttk.Combobox(sidebar, values=["X", "O"], state="readonly")
        self.combo_symbol.current(0) # Mặc định chọn X
        self.combo_symbol.pack(fill=tk.X, pady=(0, 10))

        # 4. Chọn Thứ tự đi
        tk.Label(sidebar, text="Thứ tự đi:", bg="white", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.combo_order = ttk.Combobox(sidebar, values=["Tôi đi trước (First)", "Máy đi trước (Second)"], state="readonly")
        self.combo_order.current(0) # Mặc định người đi trước
        self.combo_order.pack(fill=tk.X, pady=(0, 20))

        # Nút Bắt đầu
        tk.Button(sidebar, text="▶ BẮT ĐẦU GAME", bg="#27ae60", fg="white", font=("Arial", 11, "bold"),
                  command=self.start_game).pack(fill=tk.X, ipady=12)

        # Trạng thái
        tk.Label(sidebar, text="\nLượt hiện tại:", bg="white").pack(pady=(20, 5))
        self.lbl_turn = tk.Label(sidebar, text="...", font=("Arial", 50, "bold"), bg="white", fg="#7f8c8d")
        self.lbl_turn.pack(pady=10)
        
        self.lbl_status = tk.Label(sidebar, text="Sẵn sàng", font=("Arial", 11, "italic"), bg="white", fg="blue")
        self.lbl_status.pack()

        wrapper = tk.Frame(self.root, bg="#34495e")
        wrapper.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.canvas = tk.Canvas(wrapper, bg="#ecf0f1")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Button-1>", self.on_click)

    def create_input(self, parent, label, default):
        tk.Label(parent, text=label, bg="white").pack(anchor="w")
        entry = tk.Entry(parent, font=("Arial", 12), bg="#ecf0f1")
        entry.insert(0, default)
        entry.pack(fill=tk.X, pady=(0, 5))
        return entry

    def start_game(self):
        try:
            r = int(self.entry_rows.get())
            c = int(self.entry_cols.get())
            s = int(self.entry_streak.get())
            if s < 3:
                messagebox.showwarning("Lỗi", "Số thắng tối thiểu phải là 3!")
                return

            self.game = logic.GameLogic(r, c, s)

            mode = self.combo_mode.get()
            self.game.ai_mode = (mode == "Người vs Máy (AI)")
 
            user_choice = self.combo_symbol.get()
            order_choice = self.combo_order.get()
            
            self.user_symbol = user_choice
            self.ai_symbol = "O" if user_choice == "X" else "X"
           
            if "Tôi đi trước" in order_choice:
                self.game.current_player = self.user_symbol
            else:
                self.game.current_player = self.ai_symbol

            if r > 15 or c > 15: self.cell_size = 30
            elif r > 10 or c > 10: self.cell_size = 40
            else: self.cell_size = 60
            
            self.draw_board()
            self.update_ui_state()

            if self.game.ai_mode and self.game.current_player == self.ai_symbol:
                self.root.after(500, self.ai_turn)

        except ValueError:
            messagebox.showerror("Lỗi", "Vui lòng nhập số nguyên hợp lệ!")

    def draw_board(self):
        self.canvas.delete("all")
        rows, cols, sz = self.game.rows, self.game.cols, self.cell_size
        
        # Vẽ giữa màn hình
        board_w, board_h = cols * sz, rows * sz
        offset_x, offset_y = 10, 10
        
        for i in range(rows + 1):
            self.canvas.create_line(offset_x, offset_y + i*sz, offset_x + board_w, offset_y + i*sz, fill="#bdc3c7")
        for j in range(cols + 1):
            self.canvas.create_line(offset_x + j*sz, offset_y, offset_x + j*sz, offset_y + board_h, fill="#bdc3c7")

    def on_click(self, event):
        if self.game.game_over: return
        
        # Nếu đang là lượt AI thì chặn người chơi bấm
        if self.game.ai_mode and self.game.current_player == self.ai_symbol:
            return 

        # Tính tọa độ click
        col = int((event.x - 10) // self.cell_size)
        row = int((event.y - 10) // self.cell_size)

        self.handle_move(row, col)

    def handle_move(self, r, c):
        # Gọi Logic đánh cờ
        player = self.game.make_move(r, c)
        
        if player: # Nước đi hợp lệ
            self.draw_symbol(r, c, player)
            
            if self.game.game_over:
                self.end_game()
                return

            self.update_ui_state()
            
            # Kích hoạt AI nếu đến lượt
            if self.game.ai_mode and self.game.current_player == self.ai_symbol:
                # Cập nhật màn hình TRƯỚC khi AI suy nghĩ để tránh bị đơ
                self.root.update_idletasks()
                self.root.after(100, self.ai_turn)

    def ai_turn(self):
        self.lbl_status.config(text=f"AI ({self.ai_symbol}) đang tính toán...", fg="red")
        self.root.update()
        
        move = self.game.get_ai_move()
        if move:
            self.handle_move(move[0], move[1])

    def draw_symbol(self, r, c, player):
        sz = self.cell_size
        x = 10 + c*sz + sz/2
        y = 10 + r*sz + sz/2
        
        color = "#e74c3c" if player == "X" else "#3498db" # Đỏ cho X, Xanh cho O
        self.canvas.create_text(x, y, text=player, fill=color, font=("Arial", int(sz*0.6), "bold"))

    def update_ui_state(self):
        curr = self.game.current_player
        self.lbl_turn.config(text=curr, fg="#e74c3c" if curr=="X" else "#3498db")
        
        if self.game.ai_mode:
            if curr == self.user_symbol:
                self.lbl_status.config(text="➤ Lượt của BẠN", fg="green")
            else:
                self.lbl_status.config(text="➤ Lượt của MÁY", fg="red")
        else:
            self.lbl_status.config(text=f"Lượt người chơi {curr}", fg="black")

    def end_game(self):
        self.lbl_status.config(text="GAME OVER", fg="purple")
        
        msg = "HÒA!"
        if self.game.winner != "Draw":
            if self.game.ai_mode:
                if self.game.winner == self.user_symbol:
                    msg = "CHÚC MỪNG! BẠN ĐÃ THẮNG 🎉"
                else:
                    msg = "TIẾC QUÁ! MÁY ĐÃ THẮNG 🤖"
            else:
                msg = f"Người chơi {self.game.winner} chiến thắng!"
        
        messagebox.showinfo("Kết quả", msg)

if __name__ == "__main__":
    root = tk.Tk()
    app = GameApp(root)
    root.mainloop()