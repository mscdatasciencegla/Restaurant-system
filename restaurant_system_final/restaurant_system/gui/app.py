import tkinter as tk
from collections.abc import Callable
from pathlib import Path
from tkinter import messagebox, ttk

from exceptions import RestaurantError
from file_manager.manager import FileManager
from models.customer import Customer
from models.menu_item import DrinkItem, FoodItem
from models.payment import Payment
from models.restaurant import Restaurant
from models.table import Table


class RestaurantApp:
    COLORS = {
        "ink": "#18332C",
        "green": "#244B3F",
        "green_deep": "#1B352F",
        "green_light": "#E5EFE9",
        "green_soft": "#F1F7F3",
        "cream": "#F5F1EA",
        "cream_deep": "#EEE9E1",
        "white": "#FFFFFF",
        "muted": "#718078",
        "line": "#E3E8E2",
        "line_soft": "#EDF1ED",
        "orange": "#D98245",
        "orange_dark": "#B96531",
        "orange_light": "#F6E3D3",
        "red_light": "#FCE9E4",
        "red": "#A54B3B",
        "shadow": "#C9D6CE",
    }

    def __init__(self, root: tk.Tk, data_dir: str | Path | None = None) -> None:
        self.root = root
        self.restaurant = Restaurant("My Restaurant")
        self.file_manager = FileManager(data_dir)
        try:
            self._load_data()
        except (OSError, ValueError, KeyError, TypeError, RestaurantError) as error:
            messagebox.showerror("Could not load restaurant data", str(error))
            self.root.destroy()
            raise

        self.root.title("Restaurant Management System")
        self.root.geometry("1240x780")
        self.root.minsize(1000, 650)
        self.root.configure(bg=self.COLORS["cream"])
        self.root.option_add("*tearOff", False)
        self._configure_style()
        self._build_layout()
        self._refresh_all()
        self.root.protocol("WM_DELETE_WINDOW", self._close)

    def _load_data(self) -> None:
        self.file_manager.ensure_data_files()
        for item in self.file_manager.load_menu():
            self.restaurant.add_menu_item(item)
        for customer in self.file_manager.load_customers():
            self.restaurant.add_customer(customer)
        for table in self.file_manager.load_tables():
            self.restaurant.add_table(table)

        payments: dict[str, dict[str, object]] = {}
        for row in self.file_manager.load_payments():
            order_id = str(row["order_id"])
            if order_id in payments:
                raise ValueError(f"Duplicate payment record for order {order_id}.")
            payments[order_id] = row
        orders = self.file_manager.load_orders()
        restored_order_ids: set[str] = set()
        seen_order_ids: set[str] = set()
        for index, row in enumerate(orders):
            order_id = row.get("id", self.file_manager.order_id(index))
            if order_id in seen_order_ids:
                raise ValueError(f"Duplicate saved order ID: {order_id}.")
            seen_order_ids.add(order_id)
            order = self.restaurant.create_order(
                row["customer_id"], int(row["table_number"])
            )
            for item in row["items"]:
                order.add_item(
                    self.restaurant.find_menu_item(item["menu_item_id"]),
                    int(item["quantity"]),
                )
            if row["status"] == "Paid":
                payment = payments.get(order_id)
                if payment is None:
                    raise ValueError(
                        f"Paid order {order_id} is missing its payment record."
                    )
                self.restaurant.pay_order(
                    order, float(payment["amount"]), str(payment["method"])
                )
                restored_order_ids.add(order_id)
            elif row["status"] != "Open":
                raise ValueError(
                    f"Unsupported saved order status: {row['status']}"
                )
        orphaned_payments = set(payments) - restored_order_ids
        if orphaned_payments:
            raise ValueError(
                "Payment records refer to missing or unpaid orders: "
                + ", ".join(sorted(orphaned_payments))
            )

    def _persist_data(self) -> None:
        self.file_manager.save_menu(self.restaurant.menu)
        self.file_manager.save_customers(self.restaurant.customers)
        self.file_manager.save_tables(self.restaurant.tables)
        self.file_manager.save_orders(self.restaurant.orders)
        self.file_manager.save_payments(
            self.restaurant.payments, self.restaurant.orders
        )

    def _configure_style(self) -> None:
        style = ttk.Style(self.root)
        if "clam" in style.theme_names():
            style.theme_use("clam")
        style.configure(".", font=("Segoe UI", 10))
        style.configure("TFrame", background=self.COLORS["cream"])
        style.configure("TLabel", background=self.COLORS["cream"], foreground=self.COLORS["ink"])
        style.configure("TNotebook", background=self.COLORS["cream"])
        style.configure("TNotebook.Tab", padding=(18, 10), font=("Segoe UI", 10, "bold"))
        style.map("TNotebook.Tab", background=[("selected", self.COLORS["white"])], foreground=[("selected", self.COLORS["green"])])
        style.configure(
            "Title.TLabel",
            font=("Segoe UI", 22, "bold"),
            foreground=self.COLORS["ink"],
        )
        style.configure("Subtitle.TLabel", foreground=self.COLORS["muted"], font=("Segoe UI", 10))
        style.configure(
            "Metric.TLabel",
            font=("Segoe UI", 24, "bold"),
            foreground=self.COLORS["ink"],
            background=self.COLORS["white"],
        )
        style.configure(
            "Card.TFrame",
            background=self.COLORS["white"],
            relief="flat",
        )
        style.configure(
            "MetricName.TLabel",
            font=("Segoe UI", 9, "bold"),
            foreground=self.COLORS["muted"],
            background=self.COLORS["white"],
        )
        style.configure(
            "Section.TLabelframe",
            background=self.COLORS["white"],
            bordercolor=self.COLORS["line"],
            relief="solid",
        )
        style.configure(
            "Section.TLabelframe.Label",
            background=self.COLORS["white"],
            foreground=self.COLORS["ink"],
            font=("Segoe UI", 10, "bold"),
        )
        style.configure(
            "TButton",
            padding=(12, 9),
            background=self.COLORS["green_light"],
            foreground=self.COLORS["green"],
            borderwidth=0,
            relief="flat",
            focusthickness=0,
        )
        style.map(
            "TButton",
            background=[("active", "#D4E4DA"), ("pressed", "#C4D8CC")],
            foreground=[("active", self.COLORS["green"])],
        )
        style.configure(
            "Accent.TButton",
            background=self.COLORS["orange"],
            foreground=self.COLORS["white"],
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            padding=(14, 9),
            borderwidth=0,
        )
        style.map(
            "Accent.TButton",
            background=[("active", self.COLORS["orange_dark"]), ("pressed", self.COLORS["orange_dark"])],
            foreground=[("active", self.COLORS["white"])],
        )
        style.configure(
            "Treeview",
            rowheight=34,
            background=self.COLORS["white"],
            fieldbackground=self.COLORS["white"],
            foreground=self.COLORS["ink"],
            bordercolor=self.COLORS["line"],
            font=("Segoe UI", 10),
        )
        style.map(
            "Treeview",
            background=[("selected", self.COLORS["green_light"])],
            foreground=[("selected", self.COLORS["ink"])],
        )
        style.configure(
            "Treeview.Heading",
            font=("Segoe UI", 9, "bold"),
            background="#F0F3EF",
            foreground=self.COLORS["muted"],
            padding=(8, 9),
            relief="flat",
        )
        style.map("Treeview.Heading", background=[("active", "#E7ECE7")])
        style.configure(
            "TEntry",
            padding=(8, 7),
            fieldbackground=self.COLORS["white"],
            bordercolor=self.COLORS["line"],
        )
        style.configure(
            "TCombobox",
            padding=(7, 6),
            fieldbackground=self.COLORS["white"],
        )
        style.configure(
            "TLabelframe",
            background=self.COLORS["cream"],
            bordercolor=self.COLORS["line"],
        )
        style.configure(
            "TLabelframe.Label",
            background=self.COLORS["cream"],
            foreground=self.COLORS["ink"],
            font=("Segoe UI", 10, "bold"),
        )

    def _build_layout(self) -> None:
        shell = tk.Frame(self.root, bg=self.COLORS["cream"])
        shell.pack(fill="both", expand=True, padx=18, pady=18)
        sidebar = tk.Frame(shell, bg=self.COLORS["green"], width=220)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        brand = tk.Frame(sidebar, bg=self.COLORS["green"])
        brand.pack(fill="x", padx=20, pady=(25, 32))
        tk.Label(
            brand,
            text="●  OLIVE & OAK",
            bg=self.COLORS["green"],
            fg="#F5BC83",
            font=("Segoe UI", 15, "bold"),
        ).pack(anchor="w")
        tk.Label(
            brand,
            text="RESTAURANT POS",
            bg=self.COLORS["green"],
            fg="#B6C8BD",
            font=("Segoe UI", 8, "bold"),
        ).pack(anchor="w", padx=(21, 0), pady=(4, 0))
        tk.Label(
            sidebar,
            text="WORKSPACE",
            bg=self.COLORS["green"],
            fg="#91AA9D",
            font=("Segoe UI", 8, "bold"),
        ).pack(anchor="w", padx=22, pady=(0, 8))

        content_shell = tk.Frame(shell, bg=self.COLORS["cream"])
        content_shell.pack(side="left", fill="both", expand=True, padx=(18, 0))
        header = tk.Frame(content_shell, bg=self.COLORS["white"], height=80)
        header.pack(fill="x", padx=2)
        header.pack_propagate(False)
        title_block = tk.Frame(header, bg=self.COLORS["white"])
        title_block.pack(side="left", padx=28, pady=13)
        self.page_title = tk.Label(
            title_block,
            text="Dashboard",
            bg=self.COLORS["white"],
            fg=self.COLORS["ink"],
            font=("Segoe UI", 18, "bold"),
        )
        self.page_title.pack(anchor="w")
        tk.Label(
            title_block,
            text="A better service starts with a clear view.",
            bg=self.COLORS["white"],
            fg=self.COLORS["muted"],
            font=("Segoe UI", 9),
        ).pack(anchor="w")
        self.status_label = tk.Label(
            header,
            text="●  Ready",
            bg=self.COLORS["green_light"],
            fg=self.COLORS["green"],
            font=("Segoe UI", 9, "bold"),
            padx=12,
            pady=7,
            relief="flat",
            borderwidth=0,
        )
        self.status_label.pack(side="right", padx=26)

        self.page_host = tk.Frame(content_shell, bg=self.COLORS["cream"])
        self.page_host.pack(fill="both", expand=True, padx=4, pady=(18, 12))
        self.dashboard_tab = ttk.Frame(self.page_host, padding=4)
        self.menu_tab = ttk.Frame(self.page_host, padding=4)
        self.customers_tab = ttk.Frame(self.page_host, padding=4)
        self.tables_tab = ttk.Frame(self.page_host, padding=4)
        self.orders_tab = ttk.Frame(self.page_host, padding=4)
        self.pages = {
            "Dashboard": self.dashboard_tab,
            "Menu": self.menu_tab,
            "Customers": self.customers_tab,
            "Tables": self.tables_tab,
            "Orders": self.orders_tab,
        }
        for page in self.pages.values():
            page.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.nav_buttons: dict[str, tk.Button] = {}
        for name, icon in (
            ("Dashboard", "⌂"),
            ("Menu", "≡"),
            ("Customers", "♙"),
            ("Tables", "▦"),
            ("Orders", "▤"),
        ):
            button = tk.Button(
                sidebar,
                text=f"  {icon}    {name}",
                anchor="w",
                relief="flat",
                bd=0,
                padx=18,
                pady=12,
                bg=self.COLORS["green"],
                fg="#D9E5DD",
                activebackground="#315C4D",
                activeforeground=self.COLORS["white"],
                font=("Segoe UI", 10, "bold"),
                cursor="hand2",
                command=lambda page=name: self._show_page(page),
            )
            button.pack(fill="x", padx=12, pady=2)
            self.nav_buttons[name] = button
        tk.Frame(sidebar, bg="#557466", height=1).pack(fill="x", padx=20, pady=20)
        tk.Label(
            sidebar,
            text="SERVICE • QUALITY • CARE",
            bg=self.COLORS["green"],
            fg="#91AA9D",
            font=("Segoe UI", 8, "bold"),
        ).pack(side="bottom", anchor="w", padx=21, pady=20)

        self._build_dashboard()
        self._build_menu()
        self._build_customers()
        self._build_tables()
        self._build_orders()
        self._show_page("Dashboard")

    def _show_page(self, name: str) -> None:
        self.pages[name].tkraise()
        self.page_title.configure(text=name)
        for page_name, button in self.nav_buttons.items():
            selected = page_name == name
            button.configure(
                bg="#315C4D" if selected else self.COLORS["green"],
                fg="#FFFFFF" if selected else "#D9E5DD",
            )

    def _build_dashboard(self) -> None:
        ttk.Label(
            self.dashboard_tab,
            text="Today at a glance",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(0, 16))
        metrics = ttk.Frame(self.dashboard_tab)
        metrics.pack(fill="x")
        self.metric_labels: dict[str, ttk.Label] = {}
        metric_names = (
            ("menu_count", "Menu items"),
            ("customers_count", "Customers"),
            ("tables_available", "Tables available"),
            ("orders_count", "Orders served"),
            ("total_sales", "Payments received"),
        )
        for key, title in metric_names:
            card = tk.Frame(metrics, bg=self.COLORS["white"], padx=16, pady=16)
            card.pack(side="left", fill="both", expand=True, padx=(0, 10))
            tk.Label(card, text=title, bg=self.COLORS["white"], fg=self.COLORS["muted"], font=("Segoe UI", 9, "bold")).pack(anchor="w")
            label = tk.Label(card, text="0", bg=self.COLORS["white"], fg=self.COLORS["ink"], font=("Segoe UI", 24, "bold"))
            label.pack(anchor="w", pady=(8, 0))
            self.metric_labels[key] = label

        welcome = tk.Frame(self.dashboard_tab, bg=self.COLORS["white"], padx=22, pady=24)
        welcome.pack(fill="x", pady=(22, 0))
        tk.Label(
            welcome,
            text="Welcome to your service station",
            bg=self.COLORS["white"],
            fg=self.COLORS["ink"],
            font=("Segoe UI", 15, "bold"),
        ).pack(anchor="w")
        tk.Label(
            welcome,
            text="Keep your menu fresh, seats ready, and every order moving smoothly.",
            bg=self.COLORS["white"],
            fg=self.COLORS["muted"],
            font=("Segoe UI", 10),
        ).pack(anchor="w", pady=(5, 16))
        ttk.Button(
            welcome,
            text="Start a new order",
            style="Accent.TButton",
            command=lambda: self._show_page("Orders"),
        ).pack(anchor="w")

    def _build_menu(self) -> None:
        toolbar = ttk.Frame(self.menu_tab)
        toolbar.pack(fill="x", pady=(0, 10))
        self.menu_search = tk.StringVar()
        search_entry = ttk.Entry(toolbar, textvariable=self.menu_search, width=28)
        search_entry.pack(side="right", padx=(0, 10))
        search_entry.bind("<KeyRelease>", lambda _event: self._refresh_menu())
        ttk.Label(toolbar, text="Search:").pack(side="right", padx=(0, 6))
        ttk.Button(
            toolbar,
            text="+  Add menu item",
            style="Accent.TButton",
            command=self._add_menu_item,
        ).pack(side="right")
        self.menu_tree = self._tree(
            self.menu_tab,
            ("id", "name", "type", "price", "details"),
            ("ID", "Name", "Type", "Price", "Details"),
            (90, 180, 120, 100, 320),
        )
        self.menu_tree.tag_configure("stripe", background="#F8FAF7")

    def _build_customers(self) -> None:
        toolbar = ttk.Frame(self.customers_tab)
        toolbar.pack(fill="x", pady=(0, 10))
        ttk.Button(
            toolbar, text="+  Add customer", style="Accent.TButton",
            command=self._add_customer
        ).pack(side="right")
        self.customer_tree = self._tree(
            self.customers_tab,
            ("id", "name", "phone", "type"),
            ("ID", "Name", "Phone", "Customer type"),
            (100, 220, 180, 150),
        )
        self.customer_tree.tag_configure("stripe", background="#F8FAF7")

    def _build_tables(self) -> None:
        toolbar = ttk.Frame(self.tables_tab)
        toolbar.pack(fill="x", pady=(0, 10))
        ttk.Button(
            toolbar, text="+  Add table", style="Accent.TButton",
            command=self._add_table
        ).pack(side="right")
        self.table_tree = self._tree(
            self.tables_tab,
            ("number", "capacity", "status"),
            ("Table", "Capacity", "Status"),
            (120, 140, 160),
        )
        self.table_tree.tag_configure("stripe", background="#F8FAF7")

    def _build_orders(self) -> None:
        toolbar = ttk.Frame(self.orders_tab)
        toolbar.pack(fill="x", pady=(0, 10))
        ttk.Button(
            toolbar,
            text="+  Create order",
            style="Accent.TButton",
            command=self._create_order,
        ).pack(side="right")
        self.order_status_filter = tk.StringVar(value="All")
        status_filter = ttk.Combobox(
            toolbar,
            textvariable=self.order_status_filter,
            values=("All", "Open", "Paid"),
            state="readonly",
            width=10,
        )
        status_filter.pack(side="right", padx=12)
        status_filter.bind("<<ComboboxSelected>>", lambda _event: self._refresh_orders())
        ttk.Label(toolbar, text="Status:").pack(side="right")

        body = ttk.Panedwindow(self.orders_tab, orient="horizontal")
        body.pack(fill="both", expand=True)
        order_frame = ttk.LabelFrame(
            body, text="All orders", padding=10, style="Section.TLabelframe"
        )
        detail_frame = ttk.LabelFrame(
            body, text="Selected order", padding=10, style="Section.TLabelframe"
        )
        body.add(order_frame, weight=3)
        body.add(detail_frame, weight=2)
        self.order_tree = self._tree(
            order_frame,
            ("customer", "table", "status", "total"),
            ("Customer", "Table", "Status", "Total"),
            (160, 80, 100, 100),
        )
        self.order_tree.bind("<<TreeviewSelect>>", self._show_order_details)

        actions = ttk.Frame(detail_frame)
        actions.pack(fill="x", pady=(0, 8))
        ttk.Button(actions, text="Add item", command=self._add_order_item).pack(
            side="left", padx=(0, 5)
        )
        ttk.Button(actions, text="Remove item", command=self._remove_order_item).pack(
            side="left", padx=5
        )
        ttk.Button(
            actions, text="Take payment", style="Accent.TButton", command=self._pay_order
        ).pack(side="right")
        self.order_items_tree = self._tree(
            detail_frame,
            ("item", "quantity", "subtotal"),
            ("Item", "Qty", "Subtotal"),
            (180, 60, 100),
        )
        self.order_tree.tag_configure("stripe", background="#F8FAF7")
        self.order_items_tree.tag_configure("stripe", background="#F8FAF7")
        self.order_summary = ttk.Label(detail_frame, text="Select an order to view it.")
        self.order_summary.pack(anchor="e", pady=(8, 0))

    @staticmethod
    def _tree(
        parent: ttk.Frame,
        columns: tuple[str, ...],
        headings: tuple[str, ...],
        widths: tuple[int, ...],
    ) -> ttk.Treeview:
        wrapper = ttk.Frame(parent)
        wrapper.pack(fill="both", expand=True)
        tree = ttk.Treeview(wrapper, columns=columns, show="headings")
        scrollbar = ttk.Scrollbar(wrapper, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        for column, heading, width in zip(columns, headings, widths):
            tree.heading(column, text=heading)
            tree.column(column, width=width, minwidth=60, anchor="w")
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        return tree

    def _refresh_all(self) -> None:
        self._refresh_dashboard()
        self._refresh_menu()
        self._refresh_customers()
        self._refresh_tables()
        self._refresh_orders()

    def _refresh_dashboard(self) -> None:
        stats = self.restaurant.get_dashboard()
        for key, label in self.metric_labels.items():
            value = stats[key]
            label.configure(text=f"${value:.2f}" if key == "total_sales" else str(value))

    def _refresh_menu(self) -> None:
        self.menu_tree.delete(*self.menu_tree.get_children())
        query = self.menu_search.get().strip().casefold()
        for row, item in enumerate(self.restaurant.menu):
            if query and query not in item.name.casefold() and query not in item.id.casefold():
                continue
            self.menu_tree.insert(
                "",
                "end",
                tags=("stripe",) if row % 2 else (),
                values=(
                    item.id,
                    item.name,
                    type(item).__name__.replace("Item", ""),
                    f"${item.price:.2f}",
                    item.get_details(),
                ),
            )

    def _refresh_customers(self) -> None:
        self.customer_tree.delete(*self.customer_tree.get_children())
        for row, customer in enumerate(self.restaurant.customers):
            self.customer_tree.insert(
                "",
                "end",
                tags=("stripe",) if row % 2 else (),
                values=(
                    customer.id,
                    customer.name,
                    customer.phone,
                    "VIP (10% discount)" if customer.is_vip else "Regular",
                ),
            )

    def _refresh_tables(self) -> None:
        self.table_tree.delete(*self.table_tree.get_children())
        for row, table in enumerate(self.restaurant.tables):
            self.table_tree.insert(
                "",
                "end",
                tags=("stripe",) if row % 2 else (),
                values=(
                    table.number,
                    table.capacity,
                    "Occupied" if table.is_occupied else "Available",
                ),
            )

    def _refresh_orders(self, selected_index: int | None = None) -> None:
        self.order_tree.delete(*self.order_tree.get_children())
        status_filter = self.order_status_filter.get()
        visible_row = 0
        for index, order in enumerate(self.restaurant.orders):
            if status_filter != "All" and order.status != status_filter:
                continue
            self.order_tree.insert(
                "",
                "end",
                iid=str(index),
                tags=("stripe",) if visible_row % 2 else (),
                values=(
                    order.customer.name,
                    order.table.number,
                    order.status,
                    f"${order.total:.2f}",
                ),
            )
            visible_row += 1
        if selected_index is not None and self.order_tree.exists(str(selected_index)):
            self.order_tree.selection_set(str(selected_index))
            self.order_tree.focus(str(selected_index))
            self._display_order(selected_index)
        else:
            self.order_items_tree.delete(*self.order_items_tree.get_children())
            self.order_summary.configure(text="Select an order to view it.")

    def _display_order(self, index: int) -> None:
        order = self.restaurant.orders[index]
        self.order_items_tree.delete(*self.order_items_tree.get_children())
        for row, item in enumerate(order.items):
            self.order_items_tree.insert(
                "",
                "end",
                iid=item.menu_item.id,
                tags=("stripe",) if row % 2 else (),
                values=(
                    item.menu_item.name,
                    item.quantity,
                    f"${item.subtotal:.2f}",
                ),
            )
        self.order_summary.configure(
            text=(
                f"Subtotal: ${order.subtotal:.2f}   "
                f"Discount: ${order.discount:.2f}   "
                f"Total: ${order.total:.2f}"
            )
        )

    def _show_order_details(self, _event: tk.Event) -> None:
        index = self._selected_order_index()
        if index is not None:
            self._display_order(index)

    def _selected_order_index(self) -> int | None:
        selected = self.order_tree.selection()
        return int(selected[0]) if selected else None

    def _add_menu_item(self) -> None:
        dialog = tk.Toplevel(self.root)
        dialog.title("Add menu item")
        dialog.configure(bg=self.COLORS["cream"])
        dialog.transient(self.root)
        dialog.resizable(False, False)
        dialog.geometry("440x490")

        form = ttk.Frame(dialog, padding=24)
        form.pack(fill="both", expand=True)
        ttk.Label(form, text="Add to your menu", style="Title.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w"
        )
        ttk.Label(
            form, text="Enter item details below.", style="Subtitle.TLabel"
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(4, 18))

        ttk.Label(form, text="Item type").grid(row=2, column=0, sticky="w", pady=5)
        item_type = tk.StringVar(value="Food")
        type_selector = ttk.Combobox(
            form,
            textvariable=item_type,
            values=("Food", "Drink"),
            state="readonly",
            width=28,
        )
        type_selector.grid(row=2, column=1, sticky="ew", pady=5)

        fields: dict[str, ttk.Entry] = {}
        for row, (key, label) in enumerate(
            (("id", "Item ID"), ("name", "Item name"), ("price", "Price")),
            start=3,
        ):
            ttk.Label(form, text=label).grid(row=row, column=0, sticky="w", pady=5)
            entry = ttk.Entry(form, width=31)
            entry.grid(row=row, column=1, sticky="ew", pady=5)
            fields[key] = entry

        detail_frame = ttk.Frame(form)
        detail_frame.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        prep_label = ttk.Label(detail_frame, text="Preparation time (minutes)")
        prep_label.grid(row=0, column=0, sticky="w", pady=5)
        fields["prep_time"] = ttk.Entry(detail_frame, width=31)
        fields["prep_time"].grid(row=0, column=1, sticky="ew", pady=5)
        size_label = ttk.Label(detail_frame, text="Drink size")
        size_label.grid(row=0, column=0, sticky="w", pady=5)
        fields["size"] = ttk.Entry(detail_frame, width=31)
        fields["size"].grid(row=0, column=1, sticky="ew", pady=5)
        form.columnconfigure(1, weight=1)
        detail_frame.columnconfigure(1, weight=1)

        error_label = ttk.Label(form, text="", foreground=self.COLORS["red"])
        error_label.grid(row=7, column=0, columnspan=2, sticky="w", pady=(12, 2))

        def update_type_fields(_event: tk.Event | None = None) -> None:
            prep_label.grid_remove()
            fields["prep_time"].grid_remove()
            size_label.grid_remove()
            fields["size"].grid_remove()
            if item_type.get() == "Food":
                prep_label.grid(row=0, column=0, sticky="w", pady=5)
                fields["prep_time"].grid(row=0, column=1, sticky="ew", pady=5)
            else:
                size_label.grid(row=0, column=0, sticky="w", pady=5)
                fields["size"].grid(row=0, column=1, sticky="ew", pady=5)
            error_label.configure(text="")

        type_selector.bind("<<ComboboxSelected>>", update_type_fields)

        def submit() -> None:
            item_id = fields["id"].get().strip()
            name = fields["name"].get().strip()
            price_text = fields["price"].get().strip()
            if not item_id or not name or not price_text:
                error_label.configure(text="Complete the ID, name, and price fields.")
                return
            if any(existing.id == item_id for existing in self.restaurant.menu):
                error_label.configure(text=f"ID '{item_id}' is already in the menu.")
                fields["id"].focus_set()
                return
            try:
                price = float(price_text)
                if price <= 0:
                    raise ValueError("Price must be greater than zero.")
                if item_type.get() == "Food":
                    prep_time_text = fields["prep_time"].get().strip()
                    if not prep_time_text:
                        raise ValueError("Enter the food preparation time.")
                    prep_time = int(prep_time_text)
                    if prep_time <= 0:
                        raise ValueError("Preparation time must be greater than zero.")
                    item = FoodItem(item_id, name, price, prep_time)
                else:
                    size = fields["size"].get().strip()
                    if not size:
                        raise ValueError("Enter the drink size.")
                    item = DrinkItem(item_id, name, price, size)
                self.file_manager.save_menu([*self.restaurant.menu, item])
                self.restaurant.add_menu_item(item)
            except (RestaurantError, ValueError, OSError) as error:
                error_label.configure(text=str(error))
                return

            self._refresh_menu()
            self._refresh_dashboard()
            self.status_label.configure(
                text="●  Menu item added",
                bg=self.COLORS["green_light"],
                fg=self.COLORS["green"],
            )
            dialog.destroy()

        buttons = ttk.Frame(form)
        buttons.grid(row=8, column=0, columnspan=2, sticky="e", pady=(10, 0))
        ttk.Button(buttons, text="Cancel", command=dialog.destroy).pack(
            side="left", padx=(0, 8)
        )
        ttk.Button(
            buttons, text="Save item", style="Accent.TButton", command=submit
        ).pack(side="left")
        update_type_fields()
        dialog.bind("<Return>", lambda _event: submit())
        fields["id"].focus_set()
        dialog.grab_set()

    def _data_entry_dialog(
        self,
        title: str,
        subtitle: str,
        field_specs: tuple[
            tuple[str, str, str, tuple[str, ...], str], ...
        ],
        on_save: Callable[[dict[str, str]], None],
    ) -> None:
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.configure(bg=self.COLORS["cream"])
        dialog.transient(self.root)
        dialog.resizable(False, False)
        dialog.geometry(f"500x{min(650, 210 + len(field_specs) * 52)}")

        form = ttk.Frame(dialog, padding=24)
        form.pack(fill="both", expand=True)
        ttk.Label(form, text=title, style="Title.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w"
        )
        ttk.Label(form, text=subtitle, style="Subtitle.TLabel").grid(
            row=1, column=0, columnspan=2, sticky="w", pady=(4, 18)
        )

        inputs: dict[str, ttk.Entry | ttk.Combobox] = {}
        first_input: ttk.Entry | ttk.Combobox | None = None
        for row, (key, label, kind, choices, default) in enumerate(
            field_specs, start=2
        ):
            ttk.Label(form, text=label).grid(
                row=row, column=0, sticky="w", padx=(0, 16), pady=6
            )
            if kind == "choice":
                widget = ttk.Combobox(
                    form,
                    values=choices,
                    state="readonly",
                )
                selected = default or (choices[0] if choices else "")
                if selected in choices:
                    widget.current(choices.index(selected))
            else:
                widget = ttk.Entry(form)
                if default:
                    widget.insert(0, default)
            widget.grid(row=row, column=1, sticky="ew", pady=6)
            inputs[key] = widget
            if first_input is None:
                first_input = widget

        form.columnconfigure(1, weight=1)
        error_label = ttk.Label(form, text="", foreground=self.COLORS["red"])
        error_label.grid(
            row=len(field_specs) + 2,
            column=0,
            columnspan=2,
            sticky="w",
            pady=(10, 2),
        )

        def submit() -> None:
            values: dict[str, str] = {}
            for key, widget in inputs.items():
                value = widget.get().strip()
                if not value:
                    error_label.configure(text="Complete all fields before saving.")
                    widget.focus_set()
                    return
                values[key] = value
            try:
                on_save(values)
            except (RestaurantError, ValueError, OSError) as error:
                error_label.configure(text=str(error))
                return
            dialog.destroy()

        buttons = ttk.Frame(form)
        buttons.grid(
            row=len(field_specs) + 3,
            column=0,
            columnspan=2,
            sticky="e",
            pady=(10, 0),
        )
        ttk.Button(buttons, text="Cancel", command=dialog.destroy).pack(
            side="left", padx=(0, 8)
        )
        ttk.Button(
            buttons, text="Save", style="Accent.TButton", command=submit
        ).pack(side="left")
        dialog.bind("<Return>", lambda _event: submit())
        if first_input is not None:
            first_input.focus_set()
        dialog.grab_set()

    def _add_customer(self) -> None:
        def save_customer(values: dict[str, str]) -> None:
            customer = Customer(
                values["id"],
                values["name"],
                values["phone"],
                is_vip=values["type"] == "VIP",
            )
            self.restaurant.add_customer(customer)
            self._persist_data()
            self._refresh_customers()
            self._refresh_dashboard()
            self._set_status("Customer added")

        self._data_entry_dialog(
            "Add customer",
            "Add a customer profile and choose their membership type.",
            (
                ("id", "Customer ID", "entry", (), ""),
                ("name", "Full name", "entry", (), ""),
                ("phone", "Phone number", "entry", (), ""),
                ("type", "Membership", "choice", ("Regular", "VIP"), "Regular"),
            ),
            save_customer,
        )

    def _add_table(self) -> None:
        def save_table(values: dict[str, str]) -> None:
            number = int(values["number"])
            capacity = int(values["capacity"])
            if number < 1 or capacity < 1:
                raise ValueError("Table number and capacity must be greater than zero.")
            self.restaurant.add_table(Table(number, capacity))
            self._persist_data()
            self._refresh_tables()
            self._refresh_dashboard()
            self._set_status("Table added")

        self._data_entry_dialog(
            "Add table",
            "Set the table number and guest capacity.",
            (
                ("number", "Table number", "entry", (), ""),
                ("capacity", "Seating capacity", "entry", (), ""),
            ),
            save_table,
        )

    def _create_order(self) -> None:
        if not self.restaurant.customers:
            messagebox.showerror("Create order", "Add a customer before creating orders.")
            return
        if not self.restaurant.available_tables():
            messagebox.showerror("Create order", "There are no available tables.")
            return

        customer_options = {
            f"{customer.name} ({customer.id})": customer.id
            for customer in self.restaurant.customers
        }
        table_options = {
            f"Table {table.number} · {table.capacity} seats": str(table.number)
            for table in self.restaurant.available_tables()
        }

        def save_order(values: dict[str, str]) -> None:
            table_number = int(table_options[values["table"]])
            self.restaurant.create_order(
                customer_options[values["customer"]], table_number
            )
            self._persist_data()
            self._refresh_tables()
            self._refresh_dashboard()
            self._set_status("Order created")
            self._show_page("Orders")
            self._refresh_orders(len(self.restaurant.orders) - 1)

        self._data_entry_dialog(
            "Create order",
            "Choose who the order is for and reserve an available table.",
            (
                (
                    "customer",
                    "Customer",
                    "choice",
                    tuple(customer_options),
                    next(iter(customer_options)),
                ),
                (
                    "table",
                    "Available table",
                    "choice",
                    tuple(table_options),
                    next(iter(table_options)),
                ),
            ),
            save_order,
        )

    def _add_order_item(self) -> None:
        index = self._selected_order_index()
        if index is None:
            messagebox.showinfo("Add item", "Select an order first.")
            return
        order = self.restaurant.orders[index]
        if order.status != "Open":
            messagebox.showerror("Add item", "Items can only be added to open orders.")
            return
        if not self.restaurant.menu:
            messagebox.showerror("Add item", "Add a menu item before editing orders.")
            return
        item_options = {
            f"{item.name} ({item.id}) — ${item.price:.2f}": item.id
            for item in self.restaurant.menu
        }

        def save_order_item(values: dict[str, str]) -> None:
            quantity = int(values["quantity"])
            if quantity < 1:
                raise ValueError("Quantity must be greater than zero.")
            order.add_item(
                self.restaurant.find_menu_item(item_options[values["item"]]),
                quantity,
            )
            self._persist_data()
            self._refresh_orders(index)
            self._refresh_dashboard()
            self._set_status("Order item added")

        self._data_entry_dialog(
            "Add item to order",
            f"Order for {order.customer.name} · Table {order.table.number}",
            (
                ("item", "Menu item", "choice", tuple(item_options), next(iter(item_options))),
                ("quantity", "Quantity", "entry", (), "1"),
            ),
            save_order_item,
        )

    def _remove_order_item(self) -> None:
        index = self._selected_order_index()
        if index is None:
            messagebox.showinfo("Remove item", "Select an order first.")
            return
        order = self.restaurant.orders[index]
        selected = self.order_items_tree.selection()
        if not selected:
            messagebox.showinfo("Remove item", "Select an item in the order.")
            return
        item_id = selected[0]
        self._perform(
            lambda: order.remove_item(item_id),
            "Item removed from order.",
            refresh_orders=True,
            selected_order=index,
        )

    def _pay_order(self) -> None:
        index = self._selected_order_index()
        if index is None:
            messagebox.showinfo("Take payment", "Select an order first.")
            return
        order = self.restaurant.orders[index]
        if order.status != "Open":
            messagebox.showerror("Take payment", "This order has already been paid.")
            return
        payment: list[Payment] = []

        def save_payment(values: dict[str, str]) -> None:
            amount = float(values["amount"])
            if amount < 0:
                raise ValueError("Amount received cannot be negative.")
            payment.append(
                self.restaurant.pay_order(order, amount, values["method"])
            )
            self._persist_data()
            self._refresh_orders(index)
            self._refresh_tables()
            self._refresh_dashboard()
            self._set_status("Payment accepted")
            messagebox.showinfo(
                "Payment complete",
                f"Change due: ${payment[0].change:.2f}",
            )

        self._data_entry_dialog(
            "Take payment",
            f"Amount due: ${order.total:.2f}. Enter the amount received and method.",
            (
                ("amount", "Amount received", "entry", (), f"{order.total:.2f}"),
                ("method", "Payment method", "choice", ("Cash", "Card"), "Cash"),
            ),
            save_payment,
        )

    def _set_status(self, message: str) -> None:
        self.status_label.configure(
            text=f"●  {message}",
            bg=self.COLORS["green_light"],
            fg=self.COLORS["green"],
        )

    def _perform(
        self,
        action: Callable[[], None],
        success_message: str,
        *,
        refresh_menu: bool = False,
        refresh_customers: bool = False,
        refresh_tables: bool = False,
        refresh_orders: bool = False,
        selected_order: int | None = None,
    ) -> None:
        try:
            action()
        except (RestaurantError, ValueError, OSError) as error:
            messagebox.showerror("Could not complete action", str(error))
            return
        self._refresh_dashboard()
        if refresh_menu:
            self._refresh_menu()
        if refresh_customers:
            self._refresh_customers()
        if refresh_tables or refresh_orders:
            self._refresh_tables()
        if refresh_orders:
            self._refresh_orders(selected_order)
        try:
            self._persist_data()
        except OSError as error:
            messagebox.showerror("Could not save restaurant data", str(error))
            return
        self._set_status(success_message)

    def _close(self) -> None:
        try:
            self._persist_data()
        except OSError as error:
            messagebox.showerror("Could not save menu", str(error))
            return
        self.root.destroy()


def run() -> None:
    root = tk.Tk()
    RestaurantApp(root)
    root.mainloop()
