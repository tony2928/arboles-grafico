import tkinter as tk
from tkinter import messagebox, simpledialog


class Node:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None
        self.x = 0
        self.y = 0


class BSTVisualizer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Arbol binario de busqueda - Visualizador")
        self.tree_root = None
        self.animation_token = 0
        self.node_radius = 18
        self.pointer_colors = {
            "AP": "#e53935",
            "AUX": "#1e88e5",
            "AUX1": "#43a047",
            "DEL": "#fb8c00",
        }

        self.status_var = tk.StringVar(value="Listo")
        self.delay_var = tk.IntVar(value=700)

        self._build_ui()

    def _build_ui(self):
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill="both", expand=True)

        controls = tk.Frame(main_frame, padx=10, pady=10)
        controls.pack(side="left", fill="y")

        canvas_frame = tk.Frame(main_frame)
        canvas_frame.pack(side="right", fill="both", expand=True)

        tk.Label(controls, text="Valor").pack(anchor="w")
        self.value_entry = tk.Entry(controls, width=12)
        self.value_entry.pack(anchor="w", pady=(0, 10))

        tk.Button(controls, text="Crear arbol manual", command=self.create_manual).pack(
            fill="x"
        )
        tk.Button(controls, text="Nuevo arbol vacio", command=self.clear_tree).pack(
            fill="x", pady=(4, 8)
        )

        tk.Button(controls, text="Insertar", command=self.on_insert).pack(fill="x")
        tk.Button(controls, text="Eliminar", command=self.on_delete).pack(
            fill="x", pady=(4, 0)
        )
        tk.Button(controls, text="Buscar", command=self.on_search).pack(
            fill="x", pady=(4, 8)
        )

        tk.Button(
            controls, text="Preorden", command=lambda: self.on_traverse("pre")
        ).pack(fill="x")
        tk.Button(
            controls, text="Inorden", command=lambda: self.on_traverse("in")
        ).pack(fill="x", pady=(4, 0))
        tk.Button(
            controls, text="Postorden", command=lambda: self.on_traverse("post")
        ).pack(fill="x", pady=(4, 8))

        tk.Label(controls, text="Velocidad (ms)").pack(anchor="w")
        tk.Scale(
            controls,
            from_=200,
            to=1500,
            resolution=100,
            orient="horizontal",
            variable=self.delay_var,
            length=150,
        ).pack(anchor="w", pady=(0, 8))

        tk.Button(controls, text="Limpiar salida", command=self.clear_output).pack(
            fill="x"
        )

        self.canvas = tk.Canvas(canvas_frame, bg="#f5f5f5")
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", lambda _event: self.draw_tree())

        bottom = tk.Frame(self.root, padx=10, pady=8)
        bottom.pack(fill="x")
        tk.Label(bottom, textvariable=self.status_var, anchor="w").pack(fill="x")

        output_frame = tk.Frame(self.root, padx=10)
        output_frame.pack(fill="both", pady=(0, 10))

        scrollbar = tk.Scrollbar(output_frame)
        scrollbar.pack(side="right", fill="y")
        self.output_text = tk.Text(output_frame, height=6, yscrollcommand=scrollbar.set)
        self.output_text.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.output_text.yview)

    def run(self):
        self.root.mainloop()

    def clear_tree(self):
        self.animation_token += 1
        self.tree_root = None
        self.status_var.set("Arbol vacio")
        self.draw_tree()

    def clear_output(self):
        self.output_text.delete("1.0", tk.END)

    def append_output(self, text):
        self.output_text.insert(tk.END, text + "\n")
        self.output_text.see(tk.END)

    def _read_value(self):
        raw = self.value_entry.get().strip()
        if not raw:
            messagebox.showwarning("Dato", "Ingrese un valor")
            return None
        try:
            return int(raw)
        except ValueError:
            messagebox.showerror("Error", "El valor debe ser entero")
            return None

    def _ask_value(self, prompt):
        value = simpledialog.askinteger("Dato", prompt)
        return value

    def create_manual(self):
        self.animation_token += 1
        value = self._ask_value("Valor del nodo raiz")
        if value is None:
            return
        self.tree_root = Node(value)
        self.status_var.set("Creando arbol manual")
        self._create_children(self.tree_root)
        self.status_var.set("Arbol creado")
        self.draw_tree()

    def _create_children(self, node):
        self.draw_tree({"AP": node}, f"En nodo {node.value}")

        if messagebox.askyesno("Crear", "Existe nodo por izquierda? (Si/No)"):
            left_val = self._ask_value("Valor del hijo izquierdo")
            if left_val is not None:
                node.left = Node(left_val)
                self._create_children(node.left)

        if messagebox.askyesno("Crear", "Existe nodo por derecha? (Si/No)"):
            right_val = self._ask_value("Valor del hijo derecho")
            if right_val is not None:
                node.right = Node(right_val)
                self._create_children(node.right)

    def on_insert(self):
        value = self._read_value()
        if value is None:
            return
        self.insert_value(value)

    def on_search(self):
        value = self._read_value()
        if value is None:
            return
        self.search_value(value)

    def on_delete(self):
        value = self._read_value()
        if value is None:
            return
        self.delete_value(value)

    def on_traverse(self, order):
        self.traverse(order)

    def insert_value(self, value):
        steps = []

        if self.tree_root is None:
            self.tree_root = Node(value)
            steps.append(
                {"pointers": {"AP": self.tree_root}, "message": "Insertado como raiz"}
            )
            self.animate_steps(steps)
            return

        current = self.tree_root
        while True:
            steps.append(
                {
                    "pointers": {"AP": current},
                    "message": f"Comparar {value} con {current.value}",
                }
            )
            if value < current.value:
                if current.left is None:
                    current.left = Node(value)
                    steps.append(
                        {
                            "pointers": {"AP": current.left},
                            "message": f"Insertado a la izquierda de {current.value}",
                        }
                    )
                    break
                current = current.left
            elif value > current.value:
                if current.right is None:
                    current.right = Node(value)
                    steps.append(
                        {
                            "pointers": {"AP": current.right},
                            "message": f"Insertado a la derecha de {current.value}",
                        }
                    )
                    break
                current = current.right
            else:
                steps.append(
                    {"pointers": {"AP": current}, "message": "El nodo ya existe"}
                )
                break

        self.animate_steps(steps)

    def search_value(self, value):
        steps = []
        current = self.tree_root
        while current is not None:
            steps.append(
                {
                    "pointers": {"AP": current},
                    "message": f"Comparar {value} con {current.value}",
                }
            )
            if value == current.value:
                steps.append(
                    {"pointers": {"AP": current}, "message": "Nodo encontrado"}
                )
                self.animate_steps(steps)
                return
            if value < current.value:
                current = current.left
            else:
                current = current.right

        steps.append({"pointers": {}, "message": "Nodo no encontrado"})
        self.animate_steps(steps)

    def traverse(self, order):
        if self.tree_root is None:
            self.status_var.set("Arbol vacio")
            return

        steps = []
        output = []

        def visit(node):
            if node is None:
                return
            if order == "pre":
                steps.append(
                    {"pointers": {"AP": node}, "message": f"Visitar {node.value}"}
                )
                output.append(node.value)
            visit(node.left)
            if order == "in":
                steps.append(
                    {"pointers": {"AP": node}, "message": f"Visitar {node.value}"}
                )
                output.append(node.value)
            visit(node.right)
            if order == "post":
                steps.append(
                    {"pointers": {"AP": node}, "message": f"Visitar {node.value}"}
                )
                output.append(node.value)

        visit(self.tree_root)

        label = {"pre": "Preorden", "in": "Inorden", "post": "Postorden"}.get(
            order, "Recorrido"
        )
        self.append_output(f"{label}: {', '.join(str(x) for x in output)}")
        self.animate_steps(steps)

    def delete_value(self, value):
        steps = []
        parent = None
        current = self.tree_root

        while current is not None and current.value != value:
            steps.append(
                {
                    "pointers": {"AP": current},
                    "message": f"Buscar {value} desde {current.value}",
                }
            )
            parent = current
            if value < current.value:
                current = current.left
            else:
                current = current.right

        if current is None:
            steps.append(
                {
                    "pointers": {"AP": parent} if parent else {},
                    "message": "No encontrado",
                }
            )
            self.animate_steps(steps)
            return

        steps.append(
            {"pointers": {"DEL": current}, "message": "Nodo a eliminar encontrado"}
        )

        if current.right is None:
            steps.append(
                {
                    "pointers": {"DEL": current},
                    "message": "Reemplazar por subarbol izquierdo",
                }
            )
            self._replace_child(parent, current, current.left)
        elif current.left is None:
            steps.append(
                {
                    "pointers": {"DEL": current},
                    "message": "Reemplazar por subarbol derecho",
                }
            )
            self._replace_child(parent, current, current.right)
        else:
            aux_parent = current
            aux = current.left
            steps.append(
                {
                    "pointers": {"DEL": current, "AUX": aux},
                    "message": "Buscar predecesor (maximo en izquierda)",
                }
            )
            while aux.right is not None:
                aux_parent = aux
                aux = aux.right
                steps.append(
                    {
                        "pointers": {"DEL": current, "AUX": aux, "AUX1": aux_parent},
                        "message": "Mover AUX a la derecha",
                    }
                )

            current.value = aux.value
            steps.append(
                {
                    "pointers": {"DEL": current, "AUX": aux, "AUX1": aux_parent},
                    "message": "Copiar predecesor y eliminar AUX",
                }
            )

            if aux_parent == current:
                aux_parent.left = aux.left
            else:
                aux_parent.right = aux.left

        self.animate_steps(steps)

    def _replace_child(self, parent, current, new_child):
        if parent is None:
            self.tree_root = new_child
            return
        if parent.left is current:
            parent.left = new_child
        else:
            parent.right = new_child

    def animate_steps(self, steps):
        self.animation_token += 1
        token = self.animation_token

        if not steps:
            self.draw_tree()
            return

        def advance(index=0):
            if token != self.animation_token:
                return
            if index >= len(steps):
                return
            step = steps[index]
            self.status_var.set(step.get("message", ""))
            self.draw_tree(step.get("pointers"), step.get("message", ""))
            delay = max(200, int(self.delay_var.get()))
            self.root.after(delay, lambda: advance(index + 1))

        advance(0)

    def draw_tree(self, pointers=None, message=None):
        _ = message
        self.canvas.delete("all")
        width = max(self.canvas.winfo_width(), 600)
        height = max(self.canvas.winfo_height(), 400)

        if self.tree_root is None:
            self.canvas.create_text(
                width / 2,
                height / 2,
                text="Arbol vacio",
                fill="#555555",
                font=("TkDefaultFont", 12, "italic"),
            )
            return

        margin = 40
        level_gap = 70
        self._assign_positions(
            self.tree_root, margin, width - margin, margin, level_gap
        )
        self._draw_edges(self.tree_root)
        self._draw_nodes(self.tree_root, pointers or {})

    def _assign_positions(self, node, x_min, x_max, y, level_gap):
        if node is None:
            return
        node.x = (x_min + x_max) / 2
        node.y = y
        self._assign_positions(node.left, x_min, node.x, y + level_gap, level_gap)
        self._assign_positions(node.right, node.x, x_max, y + level_gap, level_gap)

    def _draw_edges(self, node):
        if node is None:
            return
        if node.left is not None:
            self.canvas.create_line(
                node.x, node.y, node.left.x, node.left.y, fill="#666666"
            )
        if node.right is not None:
            self.canvas.create_line(
                node.x, node.y, node.right.x, node.right.y, fill="#666666"
            )
        self._draw_edges(node.left)
        self._draw_edges(node.right)

    def _draw_nodes(self, node, pointers):
        if node is None:
            return

        labels_by_node = {}
        for name, target in pointers.items():
            if target is not None:
                labels_by_node.setdefault(target, []).append(name)

        def draw_node(n):
            labels = labels_by_node.get(n, [])
            fill = "#ffffff"
            outline = "#333333"
            if labels:
                fill = self.pointer_colors.get(labels[0], "#cccccc")
                outline = "#222222"

            r = self.node_radius
            self.canvas.create_oval(
                n.x - r, n.y - r, n.x + r, n.y + r, fill=fill, outline=outline, width=2
            )
            self.canvas.create_text(
                n.x,
                n.y,
                text=str(n.value),
                fill="#000000",
                font=("TkDefaultFont", 10, "bold"),
            )

            for idx, label in enumerate(labels):
                self.canvas.create_text(
                    n.x,
                    n.y - r - 6 - idx * 12,
                    text=label,
                    fill=self.pointer_colors.get(label, "#000000"),
                    font=("TkDefaultFont", 9, "bold"),
                )

        draw_node(node)
        self._draw_nodes(node.left, pointers)
        self._draw_nodes(node.right, pointers)


if __name__ == "__main__":
    BSTVisualizer().run()
