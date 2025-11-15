import tkinter as tk
from tkinter import ttk, messagebox
import math

class State:
    def __init__(self, name, x, y, is_initial=False, is_final=False):
        self.name = name
        self.x = x
        self.y = y
        self.is_initial = is_initial
        self.is_final = is_final
        self.canvas_id = None
        self.text_id = None
        self.final_ring_id = None


class Transition:
    def __init__(self, from_state, to_state, symbol, canvas_id=None, text_id=None):
        self.from_state = from_state
        self.to_state = to_state
        self.symbol = symbol
        self.canvas_id = canvas_id
        self.text_id = text_id


class AutomataGUI:
    STATE_RADIUS = 25

    def __init__(self, root):
        self.root = root
        self.root.title("Editor de Autómatas Finitos")

        self.states = {}
        self.transitions = []
        self.state_counter = 0

        self.selected_state_name = tk.StringVar()
        self.initial_state_name = tk.StringVar()
        style = ttk.Style()
        style.configure("AddStateActive.TButton", background="#ffe680", foreground="black")
        self._build_ui()

    def _build_ui(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True)

        # Canvas para dibujar el autómata
        self.canvas = tk.Canvas(main_frame, bg="white", width=700, height=500)
        self.canvas.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=5, pady=5)

        # Panel lateral
        side_frame = ttk.Frame(main_frame)
        side_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        main_frame.columnconfigure(0, weight=3)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)

        # Sección de estados
        states_label = ttk.Label(side_frame, text="Estados")
        states_label.pack(anchor="w")

        self.states_list = tk.Listbox(side_frame, height=8)
        self.states_list.pack(fill="x", pady=2)

        self.btn_add_state = ttk.Button(
            side_frame,
            text="Agregar estado (click en canvas)",
            command=self.start_add_state_mode
        )
        self.btn_add_state.pack(fill="x", pady=2)

        btn_delete_state = ttk.Button(
            side_frame,
            text="Eliminar estado seleccionado",
            command=self.delete_selected_state
        )
        btn_delete_state.pack(fill="x", pady=2)

        btn_toggle_final = ttk.Button(
            side_frame,
            text="Final / No final",
            command=self.toggle_final_state
        )
        btn_toggle_final.pack(fill="x", pady=2)

        ttk.Separator(side_frame, orient="horizontal").pack(fill="x", pady=5)

        # Transiciones
        ttk.Label(side_frame, text="Transiciones").pack(anchor="w")

        trans_frame = ttk.Frame(side_frame)
        trans_frame.pack(fill="x", pady=2)

        ttk.Label(trans_frame, text="De:").grid(row=0, column=0, sticky="w")
        ttk.Label(trans_frame, text="A:").grid(row=1, column=0, sticky="w")
        ttk.Label(trans_frame, text="Símbolo:").grid(row=2, column=0, sticky="w")

        self.from_combo = ttk.Combobox(trans_frame, state="readonly")
        self.to_combo = ttk.Combobox(trans_frame, state="readonly")
        self.symbol_entry = ttk.Entry(trans_frame)

        self.from_combo.grid(row=0, column=1, sticky="ew", padx=2, pady=1)
        self.to_combo.grid(row=1, column=1, sticky="ew", padx=2, pady=1)
        self.symbol_entry.grid(row=2, column=1, sticky="ew", padx=2, pady=1)

        trans_frame.columnconfigure(1, weight=1)

        btn_add_transition = ttk.Button(
            side_frame,
            text="Agregar transición",
            command=self.add_transition
        )
        btn_add_transition.pack(fill="x", pady=2)

        btn_delete_transition = ttk.Button(
            side_frame,
            text="Eliminar transición seleccionada",
            command=self.delete_selected_transition
        )
        btn_delete_transition.pack(fill="x", pady=2)

        self.transitions_list = tk.Listbox(side_frame, height=8)
        self.transitions_list.pack(fill="x", pady=2)

        ttk.Separator(side_frame, orient="horizontal").pack(fill="x", pady=5)

        btn_equations = ttk.Button(
            side_frame,
            text="Representar en expresión regular",
            command=self.show_re
        )
        btn_equations.pack(fill="x", pady=2)

        # Eventos del canvas
        self.add_state_mode = False
        self.canvas.bind("<Button-1>", self.on_canvas_click)

    # ---------- Gestión de estados ----------

    def start_add_state_mode(self):
        self.add_state_mode = True

        # Cambiar apariencia visual del botón para indicar modo activo
        self.btn_add_state.config(style="AddStateActive.TButton")

        messagebox.showinfo(
            "Agregar estado",
            "Haz click en el canvas para posicionar el nuevo estado."
        )


    def on_canvas_click(self, event):
        if self.add_state_mode:
            self.add_state(event.x, event.y)
            self.add_state_mode = False

            # Restaurar estilo normal
            self.btn_add_state.config(style="TButton")


    def add_state(self, x, y):
        name = f"q{self.state_counter}"
        

        state = State(name, x, y)
        self.states[name] = state

        # Dibujar círculo
        r = self.STATE_RADIUS
        state.canvas_id = self.canvas.create_oval(
            x - r, y - r, x + r, y + r,
            outline="black", width=2, fill="lightgray"
        )
        state.text_id = self.canvas.create_text(x, y, text=name)

        # Actualizar listas
        self.refresh_states_list()
        self.refresh_state_combos()
        if self.state_counter == 0:
            self.set_initial_state(state)
        self.state_counter += 1

    def refresh_states_list(self):
        self.states_list.delete(0, tk.END)
        for name, state in sorted(self.states.items(), key=lambda x: x[0]):
            flags = []
            if state.is_initial:
                flags.append("I")
            if state.is_final:
                flags.append("F")
            label = name
            if flags:
                label += " (" + ",".join(flags) + ")"
            self.states_list.insert(tk.END, label)

    def refresh_state_combos(self):
        names = sorted(self.states.keys())
        self.from_combo["values"] = names
        self.to_combo["values"] = names

    def get_selected_state_name(self):
        idx = self.states_list.curselection()
        if not idx:
            return None
        label = self.states_list.get(idx[0])
        # label puede ser "q0 (I,F)"
        return label.split()[0]

    def delete_selected_state(self):

        
        if self.state_counter > 0:
            self.state_counter -= 1
        else:
            messagebox.showwarning("Atención", "No hay estado para eliminar.")
            return
        name = f"q{self.state_counter}"
        state = self.states.pop(name)

        # Borrar del canvas
        self.canvas.delete(state.canvas_id)
        self.canvas.delete(state.text_id)
        if state.final_ring_id:
            self.canvas.delete(state.final_ring_id)

        # Eliminar transiciones asociadas
        to_remove = [t for t in self.transitions
                     if t.from_state == name or t.to_state == name]
        for t in to_remove:
            self.canvas.delete(t.canvas_id)
            self.canvas.delete(t.text_id)
        self.transitions = [t for t in self.transitions if t not in to_remove]

        # Quitar como inicial si lo era
        if state.is_initial:
            self.initial_state_name.set("")

        self.refresh_states_list()
        self.refresh_state_combos()
        self.refresh_transitions_list()
        self.redraw_all()

    def toggle_final_state(self):
        name = self.get_selected_state_name()
        if not name:
            messagebox.showwarning("Atención", "Selecciona un estado.")
            return
        state = self.states[name]
        state.is_final = not state.is_final
        # Dibujar o borrar anillo de estado final
        if state.is_final:
            self.draw_final_ring(state)
        else:
            if state.final_ring_id:
                self.canvas.delete(state.final_ring_id)
                state.final_ring_id = None
        self.refresh_states_list()

    def draw_final_ring(self, state: State):
        r = self.STATE_RADIUS - 4
        if state.final_ring_id:
            self.canvas.delete(state.final_ring_id)
        state.final_ring_id = self.canvas.create_oval(
            state.x - r, state.y - r, state.x + r, state.y + r,
            outline="black", width=2
        )

    def set_initial_state(self, state):
        state.is_initial = True
        self.refresh_states_list()
        self.redraw_all()

    # ---------- Gestión de transiciones ----------

    def add_transition(self):
        from_state = self.from_combo.get()
        to_state = self.to_combo.get()
        symbol = self.symbol_entry.get().strip()

        if not from_state or not to_state or not symbol:
            messagebox.showwarning(
                "Atención",
                "Debes seleccionar estado origen, destino y símbolo."
            )
            return
        if from_state not in self.states or to_state not in self.states:
            messagebox.showerror("Error", "Estado origen o destino inválido.")
            return

        t = Transition(from_state, to_state, symbol)
        self.transitions.append(t)

        self.draw_transition(t)
        self.refresh_transitions_list()
        self.symbol_entry.delete(0, tk.END)

    def draw_transition(self, t: Transition):
        s1 = self.states[t.from_state]
        s2 = self.states[t.to_state]

        # ========= CASO 1: LOOP q -> q =========
        if t.from_state == t.to_state:
            x, y = s1.x, s1.y
            r = self.STATE_RADIUS

            # --- agrupar TODOS los loops de este estado ---
            loop_transitions = [
                tr for tr in self.transitions
                if tr.from_state == tr.to_state == t.from_state
            ]
            idx = loop_transitions.index(t)   # 0,1,2,...

            # --- controlas la separación entre loops aquí ---
            BASE_HEIGHT = r + 25   # altura del primer loop respecto al centro
            SPACING = 25           # distancia extra entre loops sucesivos

            loop_height = BASE_HEIGHT + idx * SPACING

            # inicio y final del loop (tangentes al estado)
            start_x = x - r * 0.6
            start_y = y - r

            end_x = x + r * 0.6
            end_y = y - r

            # punto de control (cuanto más alto, más grande el loop)
            cx = x
            cy = y - loop_height

            # dibujar el loop como curva con flecha
            t.canvas_id = self.canvas.create_line(
                start_x, start_y,
                cx, cy,
                end_x, end_y,
                smooth=True,
                arrow=tk.LAST
            )

            # ===== TEXTO: DISTANCIA FIJA RESPECTO A *SU* LOOP =====
            LABEL_GAP = 8  # distancia desde la curva hacia “arriba”

            # Punto medio de la curva (Bézier cuadrática en t = 0.5)
            bx = 0.25 * start_x + 0.5 * cx + 0.25 * end_x
            by = 0.25 * start_y + 0.5 * cy + 0.25 * end_y

            # El texto se coloca justo encima de ese punto de la curva
            label_x = bx
            label_y = by - LABEL_GAP

            t.text_id = self.canvas.create_text(
                label_x,
                label_y,
                text=t.symbol
            )
            return

        
        x1, y1 = s1.x, s1.y
        x2, y2 = s2.x, s2.y

        dx = x2 - x1
        dy = y2 - y1
        dist = math.hypot(dx, dy)
        if dist == 0:
            dist = 1

        r = self.STATE_RADIUS

        # recortar extremos para que la flecha no toque el círculo
        x1n = x1 + dx * (r / dist)
        y1n = y1 + dy * (r / dist)
        x2n = x2 - dx * (r / dist)
        y2n = y2 - dy * (r / dist)

        # punto medio de la línea base
        mx, my = (x1n + x2n) / 2, (y1n + y2n) / 2

        # vector perpendicular normalizado
        nx = -dy / dist
        ny = dx / dist

        # ===== Agrupar TODAS las transiciones entre este par {qi, qj} =====
        pair = {t.from_state, t.to_state}

        pair_transitions = [
            tr for tr in self.transitions
            if tr.from_state != tr.to_state and {tr.from_state, tr.to_state} == pair
        ]

        idx = pair_transitions.index(t)

        # ===== CONTROLAR SEPARACIÓN ENTRE CURVAS =====
        SPACING = 25  # píxeles entre flechas sucesivas

        # siempre hacia abajo (offset positivo)
        offset = (idx + 1) * SPACING

        # punto de control de la curva (más abajo cuanto mayor offset)
        cx = mx + nx * offset
        cy = my + ny * offset

        # dibujar curva con flecha
        t.canvas_id = self.canvas.create_line(
            x1n, y1n,
            cx, cy,
            x2n, y2n,
            smooth=True,
            arrow=tk.LAST
        )

        # ===== TEXTO: SIEMPRE A DISTANCIA FIJA DE SU CURVA =====
        LABEL_GAP = 10  # distancia desde la curva hacia la línea base

        # Punto medio de la curva (Bézier cuadrática en t = 0.5)
        bx = 0.25 * x1n + 0.5 * cx + 0.25 * x2n
        by = 0.25 * y1n + 0.5 * cy + 0.25 * y2n

        # Nos movemos desde la curva hacia la línea base, en dirección -normal
        label_x = bx - nx * LABEL_GAP
        label_y = by - ny * LABEL_GAP

        t.text_id = self.canvas.create_text(
            label_x,
            label_y,
            text=t.symbol
        )



    def refresh_transitions_list(self):
        self.transitions_list.delete(0, tk.END)
        for idx, t in enumerate(self.transitions):
            self.transitions_list.insert(
                tk.END,
                f"{idx}: {t.from_state} -{t.symbol}-> {t.to_state}"
            )

    def delete_selected_transition(self):
        idxs = self.transitions_list.curselection()
        if not idxs:
            messagebox.showwarning(
                "Atención",
                "Selecciona una transición para eliminar."
            )
            return
        idx = idxs[0]
        t = self.transitions.pop(idx)
        self.canvas.delete(t.canvas_id)
        self.canvas.delete(t.text_id)
        self.refresh_transitions_list()
        self.redraw_all()

    # ---------- Dibujado ----------

    def redraw_all(self):
        # Redibuja solo elementos que dependen de banderas (inicial / final)
        # Estado inicial: flecha de entrada
        self.canvas.delete("initial_arrow")
        for state in self.states.values():
            if state.is_initial:
                x, y = state.x, state.y
                r = self.STATE_RADIUS
                arrow_len = 30
                self.canvas.create_line(
                    x - r - arrow_len, y,
                    x - r, y,
                    arrow=tk.LAST,
                    tags="initial_arrow"
                )
            # Asegurar anillo de final si aplica
            if state.is_final and not state.final_ring_id:
                self.draw_final_ring(state)

        # Redibujar transiciones
        for t in self.transitions:
            if t.canvas_id:
                self.canvas.delete(t.canvas_id)
            if t.text_id:
                self.canvas.delete(t.text_id)
            self.draw_transition(t)

    # ---------- Ecuaciones de estados ----------

    def compute_equations(self):
        # Construir mapa de ecuaciones tipo:
        # A_q = (lambda si es final) + suma de (simbolo * A_destino)
        eqs = {}
        at_least_one_is_final = False
        exist_is_initial = False
        
        for name, state in self.states.items():
            terms = []
            
            if state.is_initial:
                exist_is_initial = True

            # Si es final, agregamos lambda (ε)
            if state.is_final:
                at_least_one_is_final = True
                terms.append("λ")

            for t in self.transitions:
                if t.from_state == name:
                    terms.append(f"{t.symbol}*A_{t.to_state}")

            if not terms:
                # Sin términos: conjunto vacío
                rhs = "∅"
            else:
                rhs = "U".join(terms)

            eqs[name] = f"A_{name}={rhs}"
            
        return eqs, at_least_one_is_final, exist_is_initial
    
    def calculate_re(self, eqs: dict):
        # eqs ej: {'q0': 'A_q0 = a*A_q1', 'q1': 'A_q1 = λ + b*A_q0'}
        return "<< Expresión regular calculado >>"

    def show_re(self):
        if not self.states:
            messagebox.showinfo("Expresión Regular", "No hay estados definidos.")
            return
        eqs, at_least_one_is_final, exist_is_initial = self.compute_equations()
        if not at_least_one_is_final:
            messagebox.showinfo("Expresión Regular", "No hay estado Final definido.")
            return
        if not exist_is_initial:
            messagebox.showinfo("Expresión Regular", "No hay estados Inicial definido.")
            return
        win = tk.Toplevel(self.root)
        win.title("Expresión Regular")
        print("Ecuaciones:", eqs)
        re_exp = self.calculate_re(eqs)

        text = tk.Text(win, width=50, height=20)
        text.pack(fill="both", expand=True)

        #for name in sorted(eqs.keys()):
        text.insert(tk.END, re_exp + "\n")
        text.config(state="disabled")


def main():
    root = tk.Tk()
    app = AutomataGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
