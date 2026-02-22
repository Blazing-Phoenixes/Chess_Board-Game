# ==========================================================
# PROFESSIONAL TOURNAMENT CHESS – MASTER AI 2.0
# ==========================================================

import chess
import json
import random
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.animation import Animation
from kivy.core.audio import SoundLoader
from kivy.graphics import Color, RoundedRectangle, Ellipse
from kivy.clock import Clock
from kivy.core.window import Window

# ================= BOARD SETTINGS =================
BOARD_SIZE = min(Window.width, Window.height) * 0.8
TOP_PADDING = 100
SQUARE = BOARD_SIZE / 8


def square_to_pos(file, rank):
    return file * SQUARE, rank * SQUARE + TOP_PADDING


# ================= DRAGGABLE PIECE =================
class DraggablePiece(Image):
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            board = self.parent.parent
            if not board.drag_enabled:
                return False
            piece = board.board.piece_at(self.square)
            if piece is None or piece.color != board.board.turn:
                return False
            self.dragging = True
            self.offset_x = self.center_x - touch.x
            self.offset_y = self.center_y - touch.y
            board.show_legal_moves(self.square)
            return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if getattr(self, "dragging", False):
            self.center_x = touch.x + self.offset_x
            self.center_y = touch.y + self.offset_y
            return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if getattr(self, "dragging", False):
            self.dragging = False
            self.parent.parent.end_drag(self, touch)
            return True
        return super().on_touch_up(touch)


# ================= DASHBOARD =================
class Dashboard(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", spacing=20, padding=40)
        title = Label(text="♟ PROFESSIONAL CHESS", font_size=32)
        layout.add_widget(title)

        pvp = Button(text="Player vs Player")
        ai = Button(text="Player vs AI")

        pvp.bind(on_press=lambda x: self.start_game("pvp"))
        ai.bind(on_press=lambda x: self.start_game("ai"))

        layout.add_widget(pvp)
        layout.add_widget(ai)
        self.add_widget(layout)

    def start_game(self, mode):
        game = self.manager.get_screen("game")
        game.mode = mode
        game.reset_game()
        self.manager.current = "game"


# ================= CHESS BOARD =================
class ChessBoard(Screen):
    piece_values = {
        chess.PAWN: 1,
        chess.KNIGHT: 3,
        chess.BISHOP: 3,
        chess.ROOK: 5,
        chess.QUEEN: 9,
        chess.KING: 1000,
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mode = "pvp"
        self.board = chess.Board()
        self.drag_enabled = True
        self.undo_stack = []
        self.redo_stack = []
        self.active_popup = None

        # Load sounds
        self.move_sound = SoundLoader.load("assets/move.mp3")
        self.checkmate_sound = SoundLoader.load("assets/checkmate.mp3")

        self.layout = FloatLayout()
        self.add_widget(self.layout)

        self.draw_board()
        self.draw_ui()
        self.draw_pieces()

    # ================= BOARD =================
    def draw_board(self):
        with self.layout.canvas.before:
            for rank in range(8):
                for file in range(8):
                    Color(0.95, 0.9, 0.8) if (rank + file) % 2 == 0 else Color(
                        0.4, 0.25, 0.1
                    )
                    RoundedRectangle(
                        pos=(file * SQUARE, rank * SQUARE + TOP_PADDING),
                        size=(SQUARE, SQUARE),
                    )

    # ================= UI =================
    def draw_ui(self):
        self.status = Label(
            text="White to move", size_hint=(1, None), height=40, pos=(0, 60)
        )
        self.layout.add_widget(self.status)

        controls = BoxLayout(size_hint=(1, None), height=50, pos=(0, 0))
        undo = Button(text="Undo")
        redo = Button(text="Redo")
        save = Button(text="Save")
        load = Button(text="Load")
        back = Button(text="Back to Menu")

        undo.bind(on_press=self.undo_move)
        redo.bind(on_press=self.redo_move)
        save.bind(on_press=self.save_game)
        load.bind(on_press=self.load_game)
        back.bind(on_press=self.back_to_menu)

        for btn in [undo, redo, save, load, back]:
            controls.add_widget(btn)
        self.layout.add_widget(controls)

    def back_to_menu(self, instance):
        self.manager.current = "menu"

    # ================= PIECES =================
    def draw_pieces(self):
        # Remove old pieces
        for w in list(self.layout.children):
            if isinstance(w, DraggablePiece):
                self.layout.remove_widget(w)
        # Clear highlights
        self.layout.canvas.after.clear()

        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                file = chess.square_file(square)
                rank = chess.square_rank(square)
                color = "w" if piece.color else "b"
                symbol = piece.symbol().lower()
                x, y = square_to_pos(file, rank)
                widget = DraggablePiece(
                    source=f"assets/pieces/{color}{symbol}.png",
                    size=(SQUARE, SQUARE),
                    size_hint=(None, None),
                    pos=(x, y),
                )
                widget.square = square
                self.layout.add_widget(widget)

        self.update_status()
        self.highlight_check()

    # ================= LEGAL MOVES =================
    def show_legal_moves(self, square):
        self.layout.canvas.after.clear()
        for move in self.board.legal_moves:
            if move.from_square == square:
                file = chess.square_file(move.to_square)
                rank = chess.square_rank(move.to_square)
                with self.layout.canvas.after:
                    Color(0, 1, 0, 0.4)
                    Ellipse(
                        pos=(
                            file * SQUARE + SQUARE / 4,
                            rank * SQUARE + TOP_PADDING + SQUARE / 4,
                        ),
                        size=(SQUARE / 2, SQUARE / 2),
                    )

    # ================= DRAGGING =================
    def end_drag(self, piece, touch):
        self.layout.canvas.after.clear()
        file = int(touch.x // SQUARE)
        rank = int((touch.y - TOP_PADDING) // SQUARE)
        if not (0 <= file <= 7 and 0 <= rank <= 7):
            self.snap_back(piece)
            return

        target_square = chess.square(file, rank)
        piece_at_sq = self.board.piece_at(piece.square)

        # Pawn Promotion
        if piece_at_sq.piece_type == chess.PAWN and (rank == 0 or rank == 7):
            self.show_promotion_popup(piece.square, target_square)
            return

        move = chess.Move(piece.square, target_square)
        if move in self.board.legal_moves:
            self.make_move(move)
            if self.mode == "ai" and not self.board.is_game_over():
                Clock.schedule_once(lambda dt: self.ai_move(), 0.3)
        else:
            self.snap_back(piece)

    # ================= MAKE MOVE =================
    def make_move(self, move):
        self.undo_stack.append(self.board.fen())
        self.redo_stack.clear()
        self.board.push(move)
        self.play_move_sound()
        self.draw_pieces()
        self.check_game_state()

    # ================= STRONG AI MOVE (UNPREDICTABLE) =================
    def ai_move(self):
        if self.board.is_game_over():
            return

        best_move = self.minimax_root(
            3, self.board.turn
        )  # depth 3, strong & unpredictable
        if best_move:
            # Auto pawn promotion
            piece = self.board.piece_at(best_move.from_square)
            if piece and piece.piece_type == chess.PAWN:
                rank = chess.square_rank(best_move.to_square)
                if (piece.color and rank == 7) or (not piece.color and rank == 0):
                    best_move = chess.Move(
                        best_move.from_square,
                        best_move.to_square,
                        promotion=chess.QUEEN,
                    )
            self.make_move(best_move)

    # ================= MINIMAX WITH ALPHA-BETA =================
    def minimax_root(self, depth, color):
        best_moves = []
        max_eval = -9999
        for move in self.board.legal_moves:
            self.board.push(move)
            evaluation = self.minimax(depth - 1, -9999, 9999, False, color)
            self.board.pop()
            if evaluation > max_eval:
                max_eval = evaluation
                best_moves = [move]
            elif evaluation == max_eval:
                best_moves.append(move)
        return random.choice(best_moves) if best_moves else None

    def minimax(self, depth, alpha, beta, is_maximizing, color):
        if depth == 0 or self.board.is_game_over():
            return self.evaluate_board(color)
        if is_maximizing:
            max_eval = -9999
            for move in self.board.legal_moves:
                self.board.push(move)
                eval = self.minimax(depth - 1, alpha, beta, False, color)
                self.board.pop()
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = 9999
            for move in self.board.legal_moves:
                self.board.push(move)
                eval = self.minimax(depth - 1, alpha, beta, True, color)
                self.board.pop()
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval

    def evaluate_board(self, color):
        score = 0
        for sq in chess.SQUARES:
            piece = self.board.piece_at(sq)
            if piece:
                value = self.piece_values[piece.piece_type]
                score += value if piece.color == color else -value
        return score

    # ================= PROMOTION =================
    def show_promotion_popup(self, from_sq, to_sq):
        box = BoxLayout(orientation="vertical", spacing=10, padding=10)
        for piece_type in [chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT]:
            btn = Button(text=chess.piece_name(piece_type).capitalize())
            btn.bind(
                on_press=lambda inst, p=piece_type: self.promote(from_sq, to_sq, p)
            )
            box.add_widget(btn)
        self.promo_popup = Popup(
            title="Choose Promotion",
            content=box,
            size_hint=(None, None),
            size=(300, 300),
            auto_dismiss=False,
        )
        self.promo_popup.open()

    def promote(self, from_sq, to_sq, piece_type):
        move = chess.Move(from_sq, to_sq, promotion=piece_type)
        if move in self.board.legal_moves:
            self.make_move(move)
        self.promo_popup.dismiss()

    # ================= GAME STATE =================
    def check_game_state(self):
        if self.board.is_checkmate():
            self.drag_enabled = False
            self.play_checkmate_sound()
            winner = "White" if not self.board.turn else "Black"
            self.show_popup(f"Checkmate!\n{winner} Wins!", restart=True)
        elif self.board.is_stalemate():
            self.drag_enabled = False
            self.show_popup("Stalemate!\nDraw!", restart=True)

    # ================= CHECK HIGHLIGHT =================
    def highlight_check(self):
        self.layout.canvas.after.clear()
        if self.board.is_check():
            king_square = self.board.king(self.board.turn)
            file = chess.square_file(king_square)
            rank = chess.square_rank(king_square)
            with self.layout.canvas.after:
                Color(1, 0, 0, 0.5)
                RoundedRectangle(
                    pos=(file * SQUARE, rank * SQUARE + TOP_PADDING),
                    size=(SQUARE, SQUARE),
                )

    # ================= UTILS =================
    def snap_back(self, piece):
        file = chess.square_file(piece.square)
        rank = chess.square_rank(piece.square)
        x, y = square_to_pos(file, rank)
        Animation(x=x, y=y, duration=0.15).start(piece)

    def update_status(self):
        turn = "White" if self.board.turn else "Black"
        self.status.text = f"{turn} to move"

    def undo_move(self, instance):
        if self.undo_stack:
            self.redo_stack.append(self.board.fen())
            self.board.set_fen(self.undo_stack.pop())
            self.draw_pieces()

    def redo_move(self, instance):
        if self.redo_stack:
            self.undo_stack.append(self.board.fen())
            self.board.set_fen(self.redo_stack.pop())
            self.draw_pieces()

    def save_game(self, instance):
        with open("savegame.json", "w") as f:
            json.dump({"fen": self.board.fen()}, f)
        self.show_popup("Game Saved!")

    def load_game(self, instance):
        try:
            with open("savegame.json") as f:
                data = json.load(f)
                self.board.set_fen(data["fen"])
                self.draw_pieces()
                self.show_popup("Game Loaded!")
        except FileNotFoundError:
            self.show_popup("No saved game found!")

    def show_popup(self, message, restart=False):
        if self.active_popup:
            self.active_popup.dismiss()
        box = BoxLayout(orientation="vertical", spacing=20, padding=20)
        label = Label(text=message, font_size=20)
        box.add_widget(label)
        if restart:
            restart_btn = Button(text="Restart")
            restart_btn.bind(
                on_press=lambda x: (self.reset_game(), self.active_popup.dismiss())
            )
            box.add_widget(restart_btn)
        popup = Popup(
            title="Game Status", content=box, size_hint=(None, None), size=(350, 250)
        )
        self.active_popup = popup
        popup.open()

    def reset_game(self):
        self.board.reset()
        self.drag_enabled = True
        self.undo_stack.clear()
        self.redo_stack.clear()
        self.draw_pieces()

    def quit_game(self, instance):
        App.get_running_app().stop()

    def play_move_sound(self):
        if self.move_sound:
            self.move_sound.play()

    def play_checkmate_sound(self):
        if self.checkmate_sound:
            self.checkmate_sound.play()


# ================= APP =================
class ChessApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(Dashboard(name="menu"))
        sm.add_widget(ChessBoard(name="game"))
        return sm


if __name__ == "__main__":
    ChessApp().run()
