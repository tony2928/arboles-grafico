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
        self.root.title("BST Visualizador - Retroceso de Puntero")
        self.root.geometry("1200x850")
        self.root.configure(bg="#f8fafc")
        self.tree_root = None
        self.animation_token = 0
        self.node_width = 90
        self.node_height = 40
        self.pointer_colors = {
            "AP": "#e53935",  # Rojo
            "AUX": "#1e88e5",  # Azul
            "AUX1": "#43a047",  # Verde
            "DEL": "#fb8c00",  # Naranja
        }

        self.status_var = tk.StringVar(value="Listo")
        self.delay_var = tk.IntVar(value=700)

        self._build_ui()

    def _build_ui(self):
        main_frame = tk.Frame(self.root, bg="#f8fafc")
        main_frame.pack(fill="both", expand=True)

        # --- SECCIÓN DE CONTROLES (IZQUIERDA) ---
        controls = tk.Frame(
            main_frame,
            width=280,
            bg="#ffffff",
            highlightthickness=1,
            highlightbackground="#e2e8f0",
        )
        controls.pack(side="left", fill="y", padx=5, pady=5)
        controls.pack_propagate(False)

        tk.Label(
            controls,
            text="CONTROLES DE ARBOL",
            font=("Arial", 12, "bold"),
            bg="#ffffff",
            fg="#1e293b",
        ).pack(pady=15)
        self.value_entry = tk.Entry(
            controls,
            font=("Arial", 12),
            justify="center",
            bd=2,
            relief="groove",
        )
        self.value_entry.pack(pady=5, padx=20, fill="x")
        self.value_entry.bind("<Return>", lambda _event: self.on_insert())

        tk.Button(
            controls,
            text="INSERTAR NODO (Auto)",
            command=self.on_insert,
            bg="#3b82f6",
            fg="white",
            font=("Arial", 9, "bold"),
        ).pack(pady=5, padx=20, fill="x")
        tk.Button(
            controls,
            text="CREAR ARBOL (Manual)",
            command=self.create_manual,
            bg="#10b981",
            fg="white",
            font=("Arial", 9, "bold"),
        ).pack(pady=5, padx=20, fill="x")
        tk.Button(
            controls,
            text="BUSCAR NODO",
            command=self.on_search,
            bg="#f1f5f9",
            fg="#1e293b",
            font=("Arial", 9, "bold"),
        ).pack(pady=5, padx=20, fill="x")
        tk.Button(
            controls,
            text="ELIMINAR NODO",
            command=self.on_delete,
            bg="#fee2e2",
            fg="#b91c1c",
            font=("Arial", 9, "bold"),
        ).pack(pady=5, padx=20, fill="x")

        tk.Label(controls, text="Velocidad (ms)", bg="#ffffff", font=("Arial", 8)).pack(
            pady=(15, 0)
        )
        tk.Scale(
            controls,
            from_=100,
            to=2000,
            orient="horizontal",
            variable=self.delay_var,
            bg="#ffffff",
            relief="flat",
            highlightthickness=0,
        ).pack(fill="x", padx=20)

        tk.Label(
            controls,
            text="RECORRIDOS",
            font=("Arial", 10, "bold"),
            bg="#ffffff",
        ).pack(pady=(20, 5))
        tk.Button(
            controls,
            text="Preorden",
            command=lambda: self.on_traverse("pre"),
        ).pack(pady=2, padx=20, fill="x")
        tk.Button(
            controls,
            text="Inorden",
            command=lambda: self.on_traverse("in"),
        ).pack(pady=2, padx=20, fill="x")
        tk.Button(
            controls,
            text="Postorden",
            command=lambda: self.on_traverse("post"),
        ).pack(pady=2, padx=20, fill="x")

        tk.Button(
            controls,
            text="LIMPIAR ARBOL",
            command=self.clear_tree,
            bg="#1e293b",
            fg="white",
            font=("Arial", 9, "bold"),
        ).pack(side="bottom", pady=20, padx=20, fill="x")

        # --- SECCIÓN DEL CANVAS CON SCROLLBARS (DERECHA) ---
        main_content = tk.Frame(main_frame, bg="#f8fafc")
        main_content.pack(side="right", fill="both", expand=True)

        canvas_frame = tk.Frame(main_content, bg="#f8fafc")
        canvas_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Crear barras de desplazamiento
        h_scroll = tk.Scrollbar(canvas_frame, orient="horizontal")
        v_scroll = tk.Scrollbar(canvas_frame, orient="vertical")

        # Configurar el canvas para usar los scrollbars
        self.canvas = tk.Canvas(
            canvas_frame,
            bg="#f8fafc",
            xscrollcommand=h_scroll.set,
            yscrollcommand=v_scroll.set,
            highlightthickness=0,
        )

        # Conectar scrollbars al movimiento del canvas
        h_scroll.config(command=self.canvas.xview)
        v_scroll.config(command=self.canvas.yview)

        # Ubicar elementos usando Grid
        self.canvas.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")

        # Hacer que el canvas se expanda para llenar el espacio
        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)

        # Opcional: Atajo para mover el árbol con el click derecho del mouse
        self.canvas.bind("<ButtonPress-3>", lambda e: self.canvas.scan_mark(e.x, e.y))
        self.canvas.bind(
            "<B3-Motion>", lambda e: self.canvas.scan_dragto(e.x, e.y, gain=1)
        )

        # --- SECCIÓN INFERIOR (ESTADO Y SALIDA) ---
        status_frame = tk.Frame(main_content, bg="#f8fafc")
        status_frame.pack(fill="x", padx=30)
        tk.Label(
            status_frame,
            textvariable=self.status_var,
            font=("Arial", 10, "bold"),
            fg="#334155",
            bg="#f8fafc",
        ).pack(anchor="w", pady=(0, 6))

        self.output_text = tk.Text(
            main_content,
            height=4,
            font=("Consolas", 11),
            bg="#0f172a",
            fg="#f1f5f9",
            padx=15,
            pady=10,
        )
        self.output_text.pack(fill="x", padx=30, pady=(0, 10))

    def run(self):
        self.root.mainloop()

    # --- LÓGICA DE SINCRONIZACIÓN DE AP ---

    def create_manual(self):
        self.animation_token += 1
        self.tree_root = None
        val = self._ask_value("Valor del nodo raiz")
        if val is not None:
            self.tree_root = Node(val)
            self._create_children_recursive(self.tree_root, None, None)
        self.draw_tree()

    def _create_children_recursive(self, node, min_val, max_val):
        # Aquí sincronizamos visualmente AP con el nodo actual que se está procesando
        self.draw_tree(pointers={"AP": node})
        self.root.update()  # Forzar actualización de la UI

        if messagebox.askyesno(
            "Hijo Izquierdo", f"¿Crear hijo izquierdo para {node.value}?"
        ):
            left_val = self._ask_valid_child_value(
                f"Valor izquierdo de {node.value}",
                min_val,
                node.value,
            )
            if left_val is not None:
                node.left = Node(left_val)
                self._create_children_recursive(node.left, min_val, node.value)
                # Al volver de la recursión, re-sincronizar AP al nodo padre
                self.draw_tree(pointers={"AP": node})

        if messagebox.askyesno(
            "Hijo Derecho", f"¿Crear hijo derecho para {node.value}?"
        ):
            right_val = self._ask_valid_child_value(
                f"Valor derecho de {node.value}",
                node.value,
                max_val,
            )
            if right_val is not None:
                node.right = Node(right_val)
                self._create_children_recursive(node.right, node.value, max_val)
                self.draw_tree(pointers={"AP": node})

    def animate_steps(self, steps):
        self.animation_token += 1
        token = self.animation_token

        def advance(index=0):
            if token != self.animation_token or index >= len(steps):
                return

            step = steps[index]
            action = step.get("action")
            if callable(action):
                action()
            # Sincronización: Pasamos los punteros definidos en el paso a la función de dibujo
            self.status_var.set(step.get("message", ""))
            self.draw_tree(pointers=step.get("pointers", {}))

            self.root.after(self.delay_var.get(), lambda: advance(index + 1))

        advance(0)

    # --- MÉTODOS DE DIBUJO ---

    def _assign_positions(self, node, level, info):
        if node is None:
            return

        # 1. Procesar subárbol izquierdo
        self._assign_positions(node.left, level + 1, info)

        # 2. Procesar nodo actual
        # Usamos un contador global (info['x_count']) para dar una X única
        node.x = info["x_count"] * (self.node_width + 20) + 50
        node.y = level * 100 + 50
        info["x_count"] += 1  # Incrementamos para el siguiente nodo

        # 3. Procesar subárbol derecho
        self._assign_positions(node.right, level + 1, info)

    def draw_tree(self, pointers=None, message=None):
        self.canvas.delete("all")
        if self.tree_root is None:
            return

        info = {"x_count": 0}
        self._assign_positions(self.tree_root, 0, info)

        # --- NUEVO: Calcular límites dinámicos ---
        # Ancho: depende de cuántos nodos hay (x_count)
        total_width = info["x_count"] * (self.node_width + 40) + 200

        # Alto: depende de la profundidad máxima (podemos calcularla o usar un valor alto)
        # Aquí calculamos una altura base por nivel (100px por nivel)
        total_height = 1100

        # Activar el área de desplazamiento
        self.canvas.config(scrollregion=(0, 0, total_width, total_height))

        self._draw_edges(self.tree_root)
        self._draw_nodes(self.tree_root, pointers or {})

    def _draw_edges(self, node):
        if node is None:
            return

        if node.left:
            start_x, start_y, end_x, end_y = self._edge_points(node, node.left)
            self.canvas.create_line(
                start_x,
                start_y,
                end_x,
                end_y,
                arrow=tk.LAST,
                arrowshape=(12, 14, 6),
                fill="#444",
                width=2,
            )
            self._draw_edges(node.left)

        if node.right:
            start_x, start_y, end_x, end_y = self._edge_points(node, node.right)
            self.canvas.create_line(
                start_x,
                start_y,
                end_x,
                end_y,
                arrow=tk.LAST,
                arrowshape=(12, 14, 6),
                fill="#444",
                width=2,
            )
            self._draw_edges(node.right)

    def _edge_points(self, parent, child):
        half_w = self.node_width / 2
        half_h = self.node_height / 2
        dx = child.x - parent.x
        dy = child.y - parent.y
        if dx == 0 and dy == 0:
            return parent.x, parent.y, child.x, child.y
        scale_parent = max(abs(dx) / half_w, abs(dy) / half_h)
        start_x = parent.x + dx / scale_parent
        start_y = parent.y + dy / scale_parent
        scale_child = max(abs(dx) / half_w, abs(dy) / half_h)
        end_x = child.x - dx / scale_child
        end_y = child.y - dy / scale_child
        return start_x, start_y, end_x, end_y

    def _draw_nodes(self, node, pointers):
        if not node:
            return

        # Identificar si hay punteros apuntando a este nodo
        node_labels = [name for name, target in pointers.items() if target == node]

        fill_color = "white"
        outline_color = "#333"

        # Si AP está aquí, podemos resaltar el nodo
        if "AP" in node_labels:
            outline_color = self.pointer_colors["AP"]
        if "DEL" in node_labels:
            fill_color = "#ffcdd2"

        # Dibujar rectángulos del nodo (simulando estructura C)
        w, h = self.node_width, self.node_height
        x1, y1 = node.x - w / 2, node.y - h / 2
        x2, y2 = node.x + w / 2, node.y + h / 2

        self.canvas.create_rectangle(
            x1, y1, x2, y2, fill=fill_color, outline=outline_color, width=2
        )
        # Líneas divisorias de punteros LI y LD
        self.canvas.create_line(x1 + w / 3, y1, x1 + w / 3, y2, fill=outline_color)
        self.canvas.create_line(x2 - w / 3, y1, x2 - w / 3, y2, fill=outline_color)

        # Textos
        self.canvas.create_text(
            node.x, node.y, text=str(node.value), font=("Arial", 10, "bold")
        )
        if node.left is None:
            self.canvas.create_text(x1 + w / 6, node.y, text="/", font=("Arial", 10))
        if node.right is None:
            self.canvas.create_text(x2 - w / 6, node.y, text="/", font=("Arial", 10))

        # --- DIBUJAR ETIQUETAS DE PUNTEROS (AP, AUX, etc) ---
        for i, label in enumerate(node_labels):
            offset = (i + 1) * 20
            self.canvas.create_text(
                node.x,
                y1 - offset,
                text=f" ↓ {label}",
                fill=self.pointer_colors.get(label, "black"),
                font=("Arial", 9, "bold"),
            )

        self._draw_nodes(node.left, pointers)
        self._draw_nodes(node.right, pointers)

    # --- MÉTODOS DE SOPORTE (Adaptados de tu código) ---
    def _read_value(self):
        try:
            return int(self.value_entry.get())
        except:
            return None

    def _ask_value(self, title):
        return simpledialog.askinteger("Dato", title)

    def _ask_valid_child_value(self, prompt, min_val, max_val):
        while True:
            val = self._ask_value(prompt)
            if val is None:
                return None
            if (min_val is not None and val <= min_val) or (
                max_val is not None and val >= max_val
            ):
                low = "-inf" if min_val is None else str(min_val)
                high = "inf" if max_val is None else str(max_val)
                messagebox.showwarning(
                    "Valor invalido",
                    f"El valor debe estar entre {low} y {high} (sin incluir extremos).",
                )
                continue
            return val

    def on_insert(self):
        val = self._read_value()
        if val is not None:
            self.insert_value(val)

    def insert_value(self, value):
        steps = []

        if self.tree_root is None:
            steps.append(
                {
                    "pointers": {},
                    "message": "Arbol vacio, crear raiz",
                }
            )
            pointer_holder = {"AP": None}

            def apply_root():
                new_node = Node(value)
                self.tree_root = new_node
                pointer_holder["AP"] = new_node

            steps.append(
                {
                    "pointers": pointer_holder,
                    "message": f"Insertado {value} como raiz",
                    "action": apply_root,
                }
            )
            steps.append(
                {
                    "pointers": pointer_holder,
                    "message": "AP regresa a la raiz",
                }
            )
            self.animate_steps(steps)
            return

        current = self.tree_root
        parent = None
        side = None
        path = []
        while True:
            steps.append(
                {
                    "pointers": {"AP": current},
                    "message": f"Comparando {value} con {current.value}",
                }
            )

            if value < current.value:
                if current.left is None:
                    parent = current
                    side = "left"
                    break
                parent = current
                path.append(current)
                current = current.left
            elif value > current.value:
                if current.right is None:
                    parent = current
                    side = "right"
                    break
                parent = current
                path.append(current)
                current = current.right
            else:
                # --- AQUÍ ESTÁ EL CAMBIO ---
                # El valor ya existe en el árbol
                steps.append(
                    {
                        "pointers": {"AP": current},
                        "message": f"El valor {value} ya existe",
                    }
                )
                self.animate_steps(steps)  # Mostramos hasta dónde llegó AP

                # Lanzamos la ventana de error/advertencia
                messagebox.showwarning(
                    "Elemento duplicado",
                    f"El valor {value} ya se encuentra en el árbol.\nNo se permiten duplicados.",
                )
                return  # Salimos de la función sin insertar nada

        steps.append(
            {
                "pointers": {"AP": parent} if parent else {},
                "message": "Ubicacion encontrada, insertar nodo",
            }
        )

        pointer_holder = {"AP": None}

        def apply_insert():
            new_node = Node(value)
            if side == "left":
                parent.left = new_node
            else:
                parent.right = new_node
            pointer_holder["AP"] = new_node

        steps.append(
            {
                "pointers": pointer_holder,
                "message": f"Insertado {value} como hijo {side}",
                "action": apply_insert,
            }
        )

        backtrack_nodes = list(reversed(path))
        if parent is not None:
            backtrack_nodes.insert(0, parent)
        for node in backtrack_nodes:
            msg = (
                "Regresar a la raiz"
                if node == self.tree_root
                else f"Regresar a {node.value}"
            )
            steps.append({"pointers": {"AP": node}, "message": msg})

        self.animate_steps(steps)

    def clear_tree(self):
        self.tree_root = None
        self.canvas.delete("all")
        self.status_var.set("Árbol limpiado")

    def on_search(self):
        val = self._read_value()
        if val is None:
            return
        steps = []
        curr = self.tree_root
        found = False
        path = []
        while curr:
            steps.append(
                {"pointers": {"AP": curr}, "message": f"¿Es {val} == {curr.value}?"}
            )
            path.append(curr)
            if val == curr.value:
                steps.append({"pointers": {"AP": curr}, "message": "¡Encontrado!"})
                found = True
                break
            curr = curr.left if val < curr.value else curr.right
        if not found:
            steps.append({"pointers": {}, "message": "No se encontró el valor"})
        backtrack_nodes = list(reversed(path[:-1]))
        for node in backtrack_nodes:
            msg = (
                "Regresar a la raiz"
                if node == self.tree_root
                else f"Regresar a {node.value}"
            )
            steps.append({"pointers": {"AP": node}, "message": msg})
        self.animate_steps(steps)

    def on_delete(self):
        val = self._read_value()
        if val is not None:
            self.delete_value(val)

    def delete_value(self, value):
        steps = []
        parent = None
        current = self.tree_root
        removed = False
        path = []

        while current is not None and current.value != value:
            steps.append(
                {
                    "pointers": {"AP": current},
                    "message": f"Buscar {value} desde {current.value}",
                }
            )
            path.append(current)
            parent = current
            current = current.left if value < current.value else current.right

        if current is None:
            steps.append(
                {
                    "pointers": {"AP": parent} if parent else {},
                    "message": "La informacion no se encuentra",
                }
            )
            backtrack_nodes = list(reversed(path[:-1]))
            for node in backtrack_nodes:
                msg = (
                    "Regresar a la raiz"
                    if node == self.tree_root
                    else f"Regresar a {node.value}"
                )
                steps.append({"pointers": {"AP": node}, "message": msg})
            self.animate_steps(steps)
            return

        path.append(current)
        steps.append(
            {"pointers": {"DEL": current}, "message": "Nodo a eliminar encontrado"}
        )

        if current.right is None:
            replacement = current.left
            steps.append(
                {
                    "pointers": (
                        {"DEL": current, "AUX": replacement}
                        if replacement
                        else {"DEL": current}
                    ),
                    "message": "Reemplazar por subarbol izquierdo",
                }
            )
            steps.append(
                {
                    "pointers": {"AP": replacement} if replacement else {},
                    "message": "Nodo eliminado",
                    "action": lambda p=parent, c=current, r=replacement: self._replace_child(
                        p, c, r
                    ),
                }
            )
            removed = True
        elif current.left is None:
            replacement = current.right
            steps.append(
                {
                    "pointers": (
                        {"DEL": current, "AUX": replacement}
                        if replacement
                        else {"DEL": current}
                    ),
                    "message": "Reemplazar por subarbol derecho",
                }
            )
            steps.append(
                {
                    "pointers": {"AP": replacement} if replacement else {},
                    "message": "Nodo eliminado",
                    "action": lambda p=parent, c=current, r=replacement: self._replace_child(
                        p, c, r
                    ),
                }
            )
            removed = True
        else:
            aux_parent = current
            aux = current.left
            moved = False
            steps.append(
                {
                    "pointers": {"DEL": current, "AUX": aux},
                    "message": "Buscar predecesor (maximo en izquierda)",
                }
            )
            while aux.right is not None:
                aux_parent = aux
                aux = aux.right
                moved = True
                steps.append(
                    {
                        "pointers": {"DEL": current, "AUX": aux, "AUX1": aux_parent},
                        "message": "Mover AUX a la derecha",
                    }
                )

            steps.append(
                {
                    "pointers": {"DEL": current, "AUX": aux, "AUX1": aux_parent},
                    "message": "Listo para reemplazar con predecesor",
                }
            )

            def apply_predecessor(
                target=current,
                pred=aux,
                pred_parent=aux_parent,
                moved_right=moved,
            ):
                target.value = pred.value
                if moved_right:
                    pred_parent.right = pred.left
                else:
                    target.left = pred.left

            steps.append(
                {
                    "pointers": {"DEL": current},
                    "message": "Predecesor copiado, AUX eliminado",
                    "action": apply_predecessor,
                }
            )
            removed = True

        if removed:
            backtrack_nodes = list(reversed(path[:-1]))
            for node in backtrack_nodes:
                msg = (
                    "Regresar a la raiz"
                    if node == self.tree_root
                    else f"Regresar a {node.value}"
                )
                steps.append({"pointers": {"AP": node}, "message": msg})
            steps.append(
                {
                    "pointers": {"AP": self.tree_root} if self.tree_root else {},
                    "message": "Eliminacion finalizada",
                }
            )

        self.animate_steps(steps)

    def _replace_child(self, parent, current, new_child):
        if parent is None:
            self.tree_root = new_child
            return
        if parent.left is current:
            parent.left = new_child
        else:
            parent.right = new_child

    def on_traverse(self, mode):
        steps = []
        res = []
        parent_map = {}
        last_node = {"node": None}

        def walk(n, parent=None):
            if not n:
                return
            if parent is not None:
                parent_map[n] = parent
            if mode == "pre":
                steps.append({"pointers": {"AP": n}, "message": f"Visitando {n.value}"})
                res.append(n.value)
                last_node["node"] = n
            walk(n.left, n)
            if mode == "in":
                steps.append({"pointers": {"AP": n}, "message": f"Visitando {n.value}"})
                res.append(n.value)
                last_node["node"] = n
            walk(n.right, n)
            if mode == "post":
                steps.append({"pointers": {"AP": n}, "message": f"Visitando {n.value}"})
                res.append(n.value)
                last_node["node"] = n

        walk(self.tree_root)

        node = last_node["node"]
        while node in parent_map:
            node = parent_map[node]
            msg = (
                "Regresar a la raiz"
                if node == self.tree_root
                else f"Regresar a {node.value}"
            )
            steps.append({"pointers": {"AP": node}, "message": msg})
        self.output_text.insert("1.0", f"{mode.upper()}: {res}\n")
        self.animate_steps(steps)


if __name__ == "__main__":
    app = BSTVisualizer()
    # Esperar un poco a que el canvas obtenga sus dimensiones reales
    app.root.after(100, app.draw_tree)
    app.run()
