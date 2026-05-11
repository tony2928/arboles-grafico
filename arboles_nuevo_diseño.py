import tkinter as tk
from tkinter import simpledialog
import math

class BSTNode:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None
        self.x, self.y = 0, 0

class BSTApp:
    def __init__(self, root):
        self.window = root
        self.window.title("BST Visualizador - Retroceso de Puntero")
        self.window.geometry("1200x850")
        
        self.tree_root = None
        self.busy = False
        self.speed = 700
        self.visited_path_nodes = [] 
        
        self.colors = {
            "AP": "#ca8a04", "DEL": "#ef4444", "TRAIL_ARROW": "#0284c7",
            "NODE_BG": "#ffffff", "TEXT": "#1e293b", "BORDER": "#64748b"
        }
        self.radius = 22
        self._setup_ui()

    def _setup_ui(self):
        self.sidebar = tk.Frame(self.window, width=280, bg="#ffffff", highlightthickness=1, highlightbackground="#e2e8f0")
        self.sidebar.pack(side="left", fill="y", padx=5, pady=5)
        
        tk.Label(self.sidebar, text="CONTROLES DE ÁRBOL", font=("Arial", 12, "bold"), bg="white").pack(pady=15)
        self.input_val = tk.Entry(self.sidebar, font=("Arial", 12), justify="center", bd=2, relief="groove")
        self.input_val.pack(pady=5, padx=20, fill="x")

        tk.Button(self.sidebar, text="INSERTAR NODO (Auto)", command=self.handle_insert, bg="#3b82f6", fg="white", font=("Arial", 9, "bold")).pack(pady=5, padx=20, fill="x")
        tk.Button(self.sidebar, text="CREAR NODO (Manual)", command=self.handle_create_node, bg="#10b981", fg="white", font=("Arial", 9, "bold")).pack(pady=5, padx=20, fill="x")
        tk.Button(self.sidebar, text="BUSCAR NODO", command=self.handle_search, bg="#f1f5f9", font=("Arial", 9, "bold")).pack(pady=5, padx=20, fill="x")
        tk.Button(self.sidebar, text="ELIMINAR NODO", command=self.handle_delete, bg="#fee2e2", fg="#b91c1c", font=("Arial", 9, "bold")).pack(pady=5, padx=20, fill="x")
        
        tk.Label(self.sidebar, text="Velocidad (ms)", bg="white", font=("Arial", 8)).pack(pady=(15, 0))
        self.speed_slider = tk.Scale(self.sidebar, from_=100, to=2000, orient="horizontal", bg="white", relief="flat")
        self.speed_slider.set(self.speed)
        self.speed_slider.pack(fill="x", padx=20)

        tk.Label(self.sidebar, text="RECORRIDOS", font=("Arial", 10, "bold"), bg="white").pack(pady=(20, 5))
        for mode in [("Preorden", "pre"), ("Inorden", "in"), ("Postorden", "post")]:
            tk.Button(self.sidebar, text=mode[0], command=lambda m=mode[1]: self.start_traversal(m)).pack(pady=2, padx=20, fill="x")

        tk.Button(self.sidebar, text="LIMPIAR ÁRBOL", command=self.handle_clear_tree, bg="#1e293b", fg="white").pack(side="bottom", pady=20, padx=20, fill="x")

        self.main_content = tk.Frame(self.window, bg="#f8fafc")
        self.main_content.pack(side="right", expand=True, fill="both")
        self.canvas = tk.Canvas(self.main_content, bg="#f8fafc", highlightthickness=0)
        self.canvas.pack(expand=True, fill="both")
        
        self.output_text = tk.Text(self.main_content, height=4, font=("Consolas", 11), bg="#0f172a", fg="#f1f5f9", padx=15, pady=10)
        self.output_text.pack(fill="x", padx=30, pady=10)

    # --- Animación Core con Retorno Visual ---
    def animate(self, steps, final_root=None, result_txt=None):
        self.busy = True
        self.visited_path_nodes = []
        delay = self.speed_slider.get()

        def run_forward(idx):
            if idx < len(steps):
                step = steps[idx]
                val = step.get("hl")
                ptr = step.get("ptr", "AP")
                
                if val is not None:
                    # Si ya visitamos este nodo en el camino actual, significa que estamos "subiendo"
                    if self.visited_path_nodes and val in self.visited_path_nodes:
                        while self.visited_path_nodes and self.visited_path_nodes[-1] != val:
                            self.visited_path_nodes.pop()
                    else:
                        self.visited_path_nodes.append(val)

                self.draw_tree(hl_val=val, ptr_type=ptr)
                if "msg" in step: self._write_output(step["msg"])
                self.window.after(delay, lambda: run_forward(idx + 1))
            else:
                # Al terminar los pasos hacia adelante, iniciamos el retorno automático a la raíz
                self.window.after(delay, run_backward)

        def run_backward():
            if len(self.visited_path_nodes) > 1:
                self.visited_path_nodes.pop() # Sacamos el nodo actual
                current_top = self.visited_path_nodes[-1] # El nuevo "tope" es el padre
                self.draw_tree(hl_val=current_top, ptr_type="AP")
                self.window.after(int(delay * 0.7), run_backward)
            else:
                # Ya regresamos a la raíz o el camino está vacío
                if final_root is not None: self.tree_root = final_root
                if result_txt: self._write_output(result_txt)
                self.busy = False
                self.visited_path_nodes = []
                self.draw_tree()

        run_forward(0)

    # --- Operaciones ---
    def handle_insert(self):
        val = self._get_input()
        if val is None or self.busy: return
        if not self.tree_root:
            self.tree_root = BSTNode(val)
            self.draw_tree()
            self._write_output(f"Raíz {val} creada.")
            return
        
        steps, curr = [], self.tree_root
        while curr:
            steps.append({"hl": curr.value, "ptr": "AP"})
            if val < curr.value:
                if not curr.left: 
                    curr.left = BSTNode(val)
                    steps.append({"hl": val, "ptr": "AP"})
                    break
                curr = curr.left
            elif val > curr.value:
                if not curr.right: 
                    curr.right = BSTNode(val)
                    steps.append({"hl": val, "ptr": "AP"})
                    break
                curr = curr.right
            else: break
        self.animate(steps, result_txt=f"Nodo {val} insertado.")

    def handle_search(self):
        val = self._get_input()
        if val is None or self.busy or not self.tree_root: return
        steps, curr, found = [], self.tree_root, False
        while curr:
            steps.append({"hl": curr.value, "ptr": "AP"})
            if val == curr.value: found = True; break
            curr = curr.left if val < curr.value else curr.right
        self.animate(steps, result_txt=f"Búsqueda {val}: {'ENCONTRADO' if found else 'NO EXISTE'}")

    def handle_delete(self):
        val = self._get_input()
        if val is None or self.busy or not self.tree_root: return
        steps = []
        def delete_logic(n, v):
            if not n: return None
            steps.append({"hl": n.value, "ptr": "AP"})
            if v < n.value: n.left = delete_logic(n.left, v)
            elif v > n.value: n.right = delete_logic(n.right, v)
            else:
                steps.append({"hl": n.value, "ptr": "DEL"})
                if not n.left: return n.right
                if not n.right: return n.left
                succ = n.right
                while succ.left: succ = succ.left
                n.value = succ.value
                n.right = delete_logic(n.right, succ.value)
            return n
        new_r = delete_logic(self.tree_root, val)
        self.animate(steps, final_root=new_r, result_txt=f"Eliminación de {val} procesada.")

    # --- Dibujo ---
    def draw_tree(self, hl_val=None, ptr_type="AP"):
        self.canvas.delete("all")
        if not self.tree_root: return
        self.window.update_idletasks()
        self._assign_positions(self.tree_root, 50, self.canvas.winfo_width()-50, 60)
        self._draw_all_connections(self.tree_root)
        if self.busy and len(self.visited_path_nodes) > 1:
            self._draw_recursion_trail()
        self._draw_nodes(self.tree_root, hl_val, ptr_type)

    def _assign_positions(self, node, x_min, x_max, y):
        if not node: return
        node.x = (x_min + x_max) / 2
        node.y = y
        self._assign_positions(node.left, x_min, node.x, y + 90)
        self._assign_positions(node.right, node.x, x_max, y + 90)

    def _draw_all_connections(self, node):
        if not node: return
        for child in [node.left, node.right]:
            if child:
                angle = math.atan2(child.y - node.y, child.x - node.x)
                ix, iy = child.x - self.radius * math.cos(angle), child.y - self.radius * math.sin(angle)
                self.canvas.create_line(node.x, node.y, ix, iy, fill=self.colors["BORDER"], width=2, arrow=tk.LAST)
                self._draw_all_connections(child)

    def _draw_recursion_trail(self):
        node_map = {}
        def map_it(n):
            if n: node_map[n.value] = n; map_it(n.left); map_it(n.right)
        map_it(self.tree_root)
        for i in range(len(self.visited_path_nodes) - 1):
            p, c = node_map.get(self.visited_path_nodes[i]), node_map.get(self.visited_path_nodes[i+1])
            if p and c:
                self.canvas.create_line(p.x, p.y, c.x, c.y, fill=self.colors["TRAIL_ARROW"], width=4, arrow=tk.LAST)

    def _draw_nodes(self, n, hl_val, ptr_type):
        if not n: return
        is_hl = (n.value == hl_val)
        col = self.colors.get(ptr_type, self.colors["BORDER"]) if is_hl else self.colors["BORDER"]
        if is_hl:
            ty = n.y - self.radius - 8
            self.canvas.create_line(n.x, ty - 20, n.x, ty, fill=col, width=3, arrow=tk.LAST)
            self.canvas.create_text(n.x, ty - 30, text=ptr_type, fill=col, font=("Arial", 9, "bold"))
        self.canvas.create_oval(n.x-self.radius, n.y-self.radius, n.x+self.radius, n.y+self.radius, fill="white", outline=col, width=3 if is_hl else 2)
        self.canvas.create_text(n.x, n.y, text=str(n.value), font=("Arial", 10, "bold"))
        self._draw_nodes(n.left, hl_val, ptr_type)
        self._draw_nodes(n.right, hl_val, ptr_type)

    # --- Resto de funciones ---
    def handle_create_node(self):
        val = self._get_input()
        if val is None or self.busy: return
        if not self.tree_root: self.tree_root = BSTNode(val); self.draw_tree(); return
        curr = self.tree_root
        path = [curr.value]
        while True:
            self.draw_tree(hl_val=curr.value)
            dir = simpledialog.askstring("Manual", f"En {curr.value}: ¿i o d?", parent=self.window)
            if not dir: break
            dir = dir.lower()
            if dir == 'i':
                if curr.left: curr = curr.left; path.append(curr.value)
                else: curr.left = BSTNode(val); path.append(val); break
            elif dir == 'd':
                if curr.right: curr = curr.right; path.append(curr.value)
                else: curr.right = BSTNode(val); path.append(val); break
            else: break
        # Para el modo manual, creamos una animación artificial que solo muestre el retorno
        steps = [{"hl": v} for v in path]
        self.animate(steps)

    def start_traversal(self, mode):
        if not self.tree_root or self.busy: return
        steps, res_list = [], []
        def traverse(n):
            if not n: return
            steps.append({"hl": n.value})
            if mode == "pre":
                res_list.append(str(n.value))
                steps.append({"hl": n.value, "msg": f"PRE: {' -> '.join(res_list)}"})
            traverse(n.left)
            steps.append({"hl": n.value})
            if mode == "in":
                res_list.append(str(n.value))
                steps.append({"hl": n.value, "msg": f"IN: {' -> '.join(res_list)}"})
            traverse(n.right)
            steps.append({"hl": n.value})
            if mode == "post":
                res_list.append(str(n.value))
                steps.append({"hl": n.value, "msg": f"POST: {' -> '.join(res_list)}"})
        traverse(self.tree_root)
        self.animate(steps, result_txt=f"Fin {mode.upper()}")

    def handle_clear_tree(self):
        self.tree_root = None
        self.draw_tree()
        self._write_output("Árbol limpio.")

    def _write_output(self, txt):
        self.output_text.config(state="normal")
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert("1.0", f"> {txt}")
        self.output_text.config(state="disabled")

    def _get_input(self):
        try:
            v = int(self.input_val.get())
            self.input_val.delete(0, tk.END)
            return v
        except: return None

if __name__ == "__main__":
    root = tk.Tk()
    app = BSTApp(root)
    root.after(200, lambda: app.draw_tree()) 
    root.mainloop()