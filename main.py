import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import hashlib
import os
from database import db, cursor

# GLOBAL STATE / SETTINGS

app_settings = {
    "low_stock_threshold": 5,
    "currency_symbol": "$",
}

current_user = {"username": None}

COLORS = {
    "sidebar": "#316D86",          # Dark Navy
    "sidebar_hover": "#D90505",    # Hover Blue

    "accent": "#70BBEE",           # Primary Blue
    "accent_dark": "#3AC7EE",      # Dark Blue
    "accent_light": "#579605",     # Light Blue

    "bg": "#F8FAFC",               # Light Background
    "card_bg": "#FFFFFF",          # White Cards

    "danger": "#DC2626",           # Red
    "warning": "#F59E0B",          # Orange
    "success": "#16A34A",          # Green

    "text_light": "#E3E4E6",       # White Text
}

SECURITY_QUESTIONS = [
    "What was your first pet's name?",
    "What city were you born in?",
    "What is your mother's maiden name?",
]

# HELPERS

def is_number(value, allow_float=False):
    try:
        float(value) if allow_float else int(value)
        return True
    except ValueError:
        return False

def safe_query(sql, params=None, fetch="all"):
    try:
        cursor.execute(sql, params or ())
        if fetch == "all":
            return cursor.fetchall()
        elif fetch == "one":
            return cursor.fetchone()
        return None
    except Exception:
        return None


def safe_execute(sql, params=None):
    try:
        cursor.execute(sql, params or ())
        db.commit()
        return True, None
    except Exception as e:
        return False, str(e)


def hash_text(text, salt=None):
    if salt is None:
        salt = os.urandom(16).hex()
    digest = hashlib.sha256((salt + text).encode()).hexdigest()
    return f"{salt}${digest}"


def verify_text(text, stored_hash):
    try:
        salt, _ = stored_hash.split("$", 1)
    except (ValueError, AttributeError):
        return False
    return hash_text(text, salt) == stored_hash

def add_placeholder(entry, placeholder_text):
    entry.insert(0, placeholder_text)
    entry.config(fg="grey")

    def on_focus_in(event):
        if entry.get() == placeholder_text:
            entry.delete(0, tk.END)
            entry.config(fg="black")

    def on_focus_out(event):
        if entry.get() == "":
            entry.insert(0, placeholder_text)
            entry.config(fg="grey")

    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)
    entry.placeholder = placeholder_text


def get_real_value(entry):
    val = entry.get()
    return "" if val == getattr(entry, "placeholder", None) else val.strip()


def fmt_currency(value):
    try:
        return f"{app_settings['currency_symbol']}{float(value):,.2f}"
    except (ValueError, TypeError):
        return f"{app_settings['currency_symbol']}0.00"


def clear_and_placeholder(entry, placeholder_text):
    entry.delete(0, tk.END)
    entry.insert(0, placeholder_text)
    entry.config(fg="grey")


def add_hover(widget, normal_bg, hover_bg):
    """Lightens/darkens a button on mouse-over so the UI feels responsive to touch/click."""
    widget.bind("<Enter>", lambda e: widget.config(bg=hover_bg))
    widget.bind("<Leave>", lambda e: widget.config(bg=normal_bg))


def styled_button(parent, text, bg, fg="white", width=16, command=None, state=tk.NORMAL, hover_bg=None):
    """Bigger, friendlier button with a hover effect and consistent look across the app."""
    btn = tk.Button(
        parent, text=text, width=width, bg=bg, fg=fg, command=command, state=state,
        font=("Segoe UI", 10, "bold"), bd=0, relief="flat", cursor="hand2",
        activebackground=hover_bg or bg, activeforeground=fg, padx=6, pady=8
    )
    add_hover(btn, bg, hover_bg or bg)
    return btn

# ROOT WINDOW

root = tk.Tk()
root.title("Mobile Shop Management System")
root.geometry("1200x700")
root.resizable(False, False)
root.configure(bg=COLORS["bg"])

style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview", rowheight=26, font=("Segoe UI", 10))
style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

pages = {}

def show_page(name):
    pages[name].tkraise()


# AUTH PAGES: LOGIN / SIGNUP / FORGOT PASSWORD

def build_login_page():
    frame = tk.Frame(root, bg=COLORS["bg"])

    card = tk.Frame(frame, bg="white", width=420, height=430)
    card.place(relx=0.5, rely=0.5, anchor="center")
    card.pack_propagate(False)

    tk.Label(card, text="📱", font=("Segoe UI", 36), bg="white").pack(pady=(30, 0))
    tk.Label(card, text="Mobile Shop Login", font=("Segoe UI", 16, "bold"), bg="white", fg="#1a1a2e").pack(pady=(5, 20))

    tk.Label(card, text="Username", bg="white", anchor="w").pack(fill="x", padx=50)
    username_entry = tk.Entry(card, width=30)
    username_entry.pack(pady=(0, 10), padx=50)

    tk.Label(card, text="Password", bg="white", anchor="w").pack(fill="x", padx=50)
    password_entry = tk.Entry(card, width=30, show="*")
    password_entry.pack(pady=(0, 15), padx=50)

    status_label = tk.Label(card, text="", bg="white", fg=COLORS["danger"], font=("Segoe UI", 9))
    status_label.pack()

    def do_login():
        u = username_entry.get().strip()
        p = password_entry.get().strip()
        if u == "" or p == "":
            status_label.config(text="Please enter username and password")
            return
        row = safe_query("SELECT password_hash FROM users WHERE username=%s", (u,), fetch="one")
        if row is None:
            status_label.config(text="Invalid username or password")
            return
        if not verify_text(p, row[0]):
            status_label.config(text="Invalid username or password")
            return
        current_user["username"] = u
        status_label.config(text="")
        username_entry.delete(0, tk.END)
        password_entry.delete(0, tk.END)
        welcome_label.config(text=f"👋 Welcome, {current_user['username']}")
        show_page("main_app")

    password_entry.bind("<Return>", lambda e: do_login())

    login_btn = styled_button(card, "Login", COLORS["accent"], width=25, command=do_login, hover_bg=COLORS["accent_dark"])
    login_btn.pack(pady=5, ipady=4)

    link_row = tk.Frame(card, bg="white")
    link_row.pack(pady=(10, 5))
    tk.Button(link_row, text="Sign Up", bg="white", fg=COLORS["accent"], bd=0, cursor="hand2",
              command=lambda: show_page("signup")).grid(row=0, column=0, padx=10)
    tk.Button(link_row, text="Forgot Password?", bg="white", fg=COLORS["accent"], bd=0, cursor="hand2",
              command=lambda: show_page("forgot")).grid(row=0, column=1, padx=10)

    styled_button(card, "🛍️ Continue as Customer (Browse Stock)", COLORS["accent_light"],
                  width=32, command=lambda: show_page("customer_catalog"),
                  hover_bg=COLORS["accent"]).pack(pady=(15, 0), ipady=4)

    return frame


def build_signup_page():
    frame = tk.Frame(root, bg=COLORS["bg"])
    card = tk.Frame(frame, bg="white", width=460, height=560)
    card.place(relx=0.5, rely=0.5, anchor="center")
    card.pack_propagate(False)

    tk.Label(card, text="Create Account", font=("Segoe UI", 16, "bold"), bg="white", fg="#1a1a2e").pack(pady=(25, 15))

    fields = {}
    for label, show in [("Username", None), ("Email", None), ("Password", "*"), ("Confirm Password", "*")]:
        tk.Label(card, text=label, bg="white", anchor="w").pack(fill="x", padx=50)
        e = tk.Entry(card, width=32, show=show)
        e.pack(pady=(0, 10), padx=50)
        fields[label] = e

    tk.Label(card, text="Security Question", bg="white", anchor="w").pack(fill="x", padx=50)
    question_var = tk.StringVar(value=SECURITY_QUESTIONS[0])
    question_menu = ttk.Combobox(card, textvariable=question_var, values=SECURITY_QUESTIONS, state="readonly", width=30)
    question_menu.pack(pady=(0, 10), padx=50)

    tk.Label(card, text="Security Answer", bg="white", anchor="w").pack(fill="x", padx=50)
    answer_entry = tk.Entry(card, width=32)
    answer_entry.pack(pady=(0, 15), padx=50)

    status_label = tk.Label(card, text="", bg="white", fg=COLORS["danger"], font=("Segoe UI", 9), wraplength=350)
    status_label.pack()

    def do_signup():
        u = fields["Username"].get().strip()
        email = fields["Email"].get().strip()
        p = fields["Password"].get().strip()
        pc = fields["Confirm Password"].get().strip()
        answer = answer_entry.get().strip()

        if u == "" or p == "":
            status_label.config(text="Username and password are required")
            return
        if len(p) < 4:
            status_label.config(text="Password must be at least 4 characters")
            return
        if p != pc:
            status_label.config(text="Passwords do not match")
            return
        if answer == "":
            status_label.config(text="Please answer the security question (used for password reset)")
            return

        existing = safe_query("SELECT id FROM users WHERE username=%s", (u,), fetch="one")
        if existing is not None:
            status_label.config(text="Username already taken")
            return

        ok, err = safe_execute(
            "INSERT INTO users (username, password_hash, email, security_question, security_answer_hash) "
            "VALUES (%s,%s,%s,%s,%s)",
            (u, hash_text(p), email, question_var.get(), hash_text(answer.lower()))
        )
        if ok:
            messagebox.showinfo("Success", "Account created. You can now log in.")
            for e in fields.values():
                e.delete(0, tk.END)
            answer_entry.delete(0, tk.END)
            show_page("login")
        else:
            status_label.config(text=f"Database error: {err}")

    styled_button(card, "Create Account", COLORS["success"], width=25, command=do_signup, hover_bg="#128a3e").pack(pady=5, ipady=4)
    tk.Button(card, text="Back to Login", bg="white", fg=COLORS["accent"], bd=0, cursor="hand2",
              command=lambda: show_page("login")).pack(pady=(10, 0))

    return frame


def build_forgot_password_page():
    frame = tk.Frame(root, bg=COLORS["bg"])
    card = tk.Frame(frame, bg="white", width=440, height=430)
    card.place(relx=0.5, rely=0.5, anchor="center")
    card.pack_propagate(False)

    tk.Label(card, text="Reset Password", font=("Segoe UI", 16, "bold"), bg="white", fg="#1a1a2e").pack(pady=(25, 15))

    tk.Label(card, text="Username", bg="white", anchor="w").pack(fill="x", padx=50)
    username_entry = tk.Entry(card, width=32)
    username_entry.pack(pady=(0, 10), padx=50)

    question_label = tk.Label(card, text="Security question will appear here", bg="white", fg="#555",
                               wraplength=340, justify="left")
    question_label.pack(pady=(5, 5), padx=50, fill="x")

    tk.Label(card, text="Your Answer", bg="white", anchor="w").pack(fill="x", padx=50)
    answer_entry = tk.Entry(card, width=32)
    answer_entry.pack(pady=(0, 10), padx=50)

    tk.Label(card, text="New Password", bg="white", anchor="w").pack(fill="x", padx=50)
    new_pass_entry = tk.Entry(card, width=32, show="*")
    new_pass_entry.pack(pady=(0, 15), padx=50)

    status_label = tk.Label(card, text="", bg="white", fg=COLORS["danger"], font=("Segoe UI", 9), wraplength=340)
    status_label.pack()

    found_user = {"question": None, "answer_hash": None}

    def lookup_user():
        u = username_entry.get().strip()
        row = safe_query("SELECT security_question, security_answer_hash FROM users WHERE username=%s", (u,), fetch="one")
        if row is None:
            question_label.config(text="No account found with that username.")
            found_user["question"] = None
            return
        found_user["question"] = row[0]
        found_user["answer_hash"] = row[1]
        question_label.config(text=row[0] or "No security question set for this account.")

    username_entry.bind("<FocusOut>", lambda e: lookup_user())

    def do_reset():
        u = username_entry.get().strip()
        answer = answer_entry.get().strip()
        new_pass = new_pass_entry.get().strip()

        if found_user["answer_hash"] is None:
            status_label.config(text="Please enter a valid username first")
            return
        if not verify_text(answer.lower(), found_user["answer_hash"]):
            status_label.config(text="Security answer is incorrect")
            return
        if len(new_pass) < 4:
            status_label.config(text="New password must be at least 4 characters")
            return

        ok, err = safe_execute("UPDATE users SET password_hash=%s WHERE username=%s", (hash_text(new_pass), u))
        if ok:
            messagebox.showinfo("Success", "Password reset successfully. Please log in.")
            username_entry.delete(0, tk.END)
            answer_entry.delete(0, tk.END)
            new_pass_entry.delete(0, tk.END)
            question_label.config(text="Security question will appear here")
            show_page("login")
        else:
            status_label.config(text=f"Database error: {err}")

    styled_button(card, "Reset Password", COLORS["accent"], width=25, command=do_reset, hover_bg=COLORS["accent_dark"]).pack(pady=5, ipady=4)
    tk.Button(card, text="Back to Login", bg="white", fg=COLORS["accent"], bd=0, cursor="hand2",
              command=lambda: show_page("login")).pack(pady=(10, 0))

    return frame
# CUSTOMER CATALOG (read-only, no login required)

def build_customer_catalog_page():
    frame = tk.Frame(root, bg=COLORS["bg"])

    header = tk.Frame(frame, bg=COLORS["accent"], height=70)
    header.pack(fill="x")
    tk.Label(header, text="🛍️ Available Phones In Our Shop", font=("Segoe UI", 16, "bold"),
             bg=COLORS["accent"], fg="white").pack(side="left", padx=20, pady=15)
    tk.Button(header, text="⬅ Back to Login", bg="white", fg=COLORS["accent"],
              command=lambda: show_page("login")).pack(side="right", padx=20, pady=15)

    search_frame = tk.Frame(frame, bg=COLORS["bg"])
    search_frame.pack(fill="x", padx=30, pady=15)
    tk.Label(search_frame, text="Search:", bg=COLORS["bg"], font=("Segoe UI", 10)).pack(side="left")
    cat_search_entry = tk.Entry(search_frame, width=40)
    cat_search_entry.pack(side="left", padx=10)

    table_frame = tk.Frame(frame, bg=COLORS["bg"])
    table_frame.pack(fill="both", expand=True, padx=30, pady=(0, 20))

    cols = ("Brand", "Model", "Price", "Availability")
    cat_tree = ttk.Treeview(table_frame, columns=cols, show="headings")
    for c in cols:
        cat_tree.heading(c, text=c)
        cat_tree.column(c, width=200, anchor="center")
    cat_tree.pack(side="left", fill="both", expand=True)
    cat_tree.tag_configure("in_stock", foreground=COLORS["success"])
    cat_tree.tag_configure("low", foreground=COLORS["warning"])
    cat_tree.tag_configure("out", foreground=COLORS["danger"])

    sb = ttk.Scrollbar(table_frame, orient="vertical", command=cat_tree.yview)
    cat_tree.configure(yscroll=sb.set)
    sb.pack(side="right", fill="y")

    def refresh_catalog(keyword=""):
        cat_tree.delete(*cat_tree.get_children())
        if keyword:
            like_val = f"%{keyword}%"
            rows = safe_query(
                "SELECT brand, model, price, quantity FROM phones WHERE brand LIKE %s OR model LIKE %s",
                (like_val, like_val)
            ) or []
        else:
            rows = safe_query("SELECT brand, model, price, quantity FROM phones") or []

        for brand_v, model_v, price_v, qty_v in rows:
            try:
                qty_int = int(qty_v)
            except (ValueError, TypeError):
                qty_int = 0
            if qty_int == 0:
                availability, tag = "Out of Stock", "out"
            elif qty_int <= app_settings["low_stock_threshold"]:
                availability, tag = f"Only {qty_int} left", "low"
            else:
                availability, tag = "In Stock", "in_stock"
            cat_tree.insert("", tk.END, values=(brand_v, model_v, fmt_currency(price_v), availability), tags=(tag,))

    cat_search_entry.bind("<KeyRelease>", lambda e: refresh_catalog(cat_search_entry.get().strip()))

    frame.refresh = refresh_catalog
    refresh_catalog()
    return frame

# MAIN APP (admin dashboard) - built once, shown after login

def build_main_app_page():
    outer = tk.Frame(root, bg=COLORS["bg"])

    sidebar = tk.Frame(outer, bg=COLORS["sidebar"], width=220, height=700)
    sidebar.pack(side="left", fill="y")
    sidebar.pack_propagate(False)

    tk.Label(sidebar, text="📱 ShopManager", font=("Segoe UI", 14, "bold"),
              bg=COLORS["sidebar"], fg="white").pack(pady=(25, 5))
    global welcome_label
    welcome_label = tk.Label(sidebar, text="👋 Welcome", font=("Segoe UI", 9),
                              bg=COLORS["sidebar"], fg=COLORS["text_light"])
    welcome_label.pack(pady=(0, 20))

    nav_buttons = []

    def make_nav_button(text, command):
        btn = tk.Button(
            sidebar, text=text, anchor="w", font=("Segoe UI", 12), bd=0,
            bg=COLORS["sidebar"], fg=COLORS["text_light"], activebackground=COLORS["sidebar_hover"],
            activeforeground="white", padx=22, pady=16, command=command, cursor="hand2"
        )
        btn.pack(fill="x")
        add_hover(btn, COLORS["sidebar"], COLORS["sidebar_hover"])
        nav_buttons.append(btn)
        return btn

    content_area = tk.Frame(outer, bg=COLORS["bg"])
    content_area.pack(side="right", fill="both", expand=True)

    topbar = tk.Frame(content_area, bg=COLORS["card_bg"], height=50)
    topbar.pack(fill="x")
    clock_label = tk.Label(topbar, text="", font=("Segoe UI", 10), bg=COLORS["card_bg"], fg="#555")
    clock_label.pack(side="right", padx=20, pady=10)

    def tick_clock():
        clock_label.config(text=datetime.now().strftime("%A, %d %B %Y   |   %I:%M:%S %p"))
        root.after(1000, tick_clock)
    tick_clock()

    page_container = tk.Frame(content_area, bg=COLORS["bg"])
    page_container.pack(fill="both", expand=True)

    def show_sub_frame(f):
        f.tkraise()

    def set_active_nav(active_btn):
        for b in nav_buttons:
            b.config(bg=COLORS["sidebar"], fg=COLORS["text_light"])
            add_hover(b, COLORS["sidebar"], COLORS["sidebar_hover"])
        active_btn.config(bg=COLORS["accent"], fg="white")
        add_hover(active_btn, COLORS["accent"], COLORS["accent_dark"])

    def do_logout():
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            current_user["username"] = None
            show_page("login")

    # -- DASHBOARD --
    dashboard_frame = tk.Frame(page_container, bg=COLORS["bg"])
    tk.Label(dashboard_frame, text="📊 Dashboard Overview", font=("Segoe UI", 16, "bold"),
              bg=COLORS["bg"], fg="#1a1a2e").pack(anchor="w", padx=20, pady=(20, 15))

    cards_frame = tk.Frame(dashboard_frame, bg=COLORS["bg"])
    cards_frame.pack(fill="x", padx=20)

    def make_stat_card(parent, title, color, col):
        card = tk.Frame(parent, bg=color, width=260, height=110)
        card.grid(row=0, column=col, padx=10, sticky="nsew")
        card.grid_propagate(False)
        tk.Label(card, text=title, font=("Segoe UI", 10, "bold"), bg=color, fg="white").pack(anchor="w", padx=15, pady=(15, 0))
        value_label = tk.Label(card, text="0", font=("Segoe UI", 22, "bold"), bg=color, fg="white")
        value_label.pack(anchor="w", padx=15, pady=(0, 10))
        return value_label

    card_total_products = make_stat_card(cards_frame, "📈 Total Products", COLORS["accent"], 0)
    card_total_units = make_stat_card(cards_frame, "📦 Total Units", COLORS["accent_light"], 1)
    card_total_sales = make_stat_card(cards_frame, "💵 Total Sales", COLORS["accent_dark"], 2)
    card_low_stock = make_stat_card(cards_frame, "⚠️ Low Stock Alerts", COLORS["warning"], 3)
    for i in range(4):
        cards_frame.grid_columnconfigure(i, weight=1)

    def refresh_dashboard_stats():
        prod_result = safe_query("SELECT COUNT(*), SUM(quantity) FROM phones", fetch="one")
        total_products = prod_result[0] if prod_result and prod_result[0] else 0
        total_units = prod_result[1] if prod_result and prod_result[1] else 0
        low_stock_result = safe_query(
            f"SELECT COUNT(*) FROM phones WHERE quantity <= {app_settings['low_stock_threshold']}", fetch="one"
        )
        low_stock_count = low_stock_result[0] if low_stock_result else 0
        sales_result = safe_query("SELECT SUM(total_amount) FROM sales", fetch="one")
        total_sales = sales_result[0] if sales_result and sales_result[0] else None

        card_total_products.config(text=str(total_products))
        card_total_units.config(text=str(total_units))
        card_low_stock.config(text=str(low_stock_count))
        card_total_sales.config(text=fmt_currency(total_sales) if total_sales is not None else "N/A")

    # --- PRODUCTS -----
    products_frame = tk.Frame(page_container, bg=COLORS["bg"])
    tk.Label(products_frame, text="📦 Product Management", font=("Segoe UI", 16, "bold"),
              bg=COLORS["bg"], fg="#1a1a2e").pack(anchor="w", padx=20, pady=(20, 10))

    form_row = tk.Frame(products_frame, bg=COLORS["bg"])
    form_row.pack(fill="x", padx=20)

    form_frame = tk.LabelFrame(form_row, text="Phone Details", font=("Segoe UI", 10, "bold"), bg="white", padx=10, pady=10)
    form_frame.grid(row=0, column=0, sticky="n", padx=(0, 10))

    tk.Label(form_frame, text="Brand", bg="white").grid(row=0, column=0, sticky="w", pady=8)
    brand = tk.Entry(form_frame, width=28)
    brand.grid(row=0, column=1, pady=8)
    tk.Label(form_frame, text="Model", bg="white").grid(row=1, column=0, sticky="w", pady=8)
    model = tk.Entry(form_frame, width=28)
    model.grid(row=1, column=1, pady=8)
    tk.Label(form_frame, text="Price", bg="white").grid(row=2, column=0, sticky="w", pady=8)
    price = tk.Entry(form_frame, width=28)
    price.grid(row=2, column=1, pady=8)
    tk.Label(form_frame, text="Quantity", bg="white").grid(row=3, column=0, sticky="w", pady=8)
    quantity = tk.Entry(form_frame, width=28)
    quantity.grid(row=3, column=1, pady=8)

    add_placeholder(brand, "e.g. Samsung")
    add_placeholder(model, "e.g. Galaxy S24")
    add_placeholder(price, "e.g. 799.99")
    add_placeholder(quantity, "e.g. 10")

    action_frame = tk.LabelFrame(form_row, text="Actions", font=("Segoe UI", 10, "bold"), bg="white", padx=10, pady=10)
    action_frame.grid(row=0, column=1, sticky="n")

    selected_id = {"value": None}
    sort_state = {"col": None, "reverse": False}

    def update_button_states():
        state = tk.NORMAL if selected_id["value"] is not None else tk.DISABLED
        update_btn.config(state=state)
        delete_btn.config(state=state)

    def clear_fields():
        for e, ph in [(brand, "e.g. Samsung"), (model, "e.g. Galaxy S24"),
                      (price, "e.g. 799.99"), (quantity, "e.g. 10")]:
            clear_and_placeholder(e, ph)
        selected_id["value"] = None
        tree.selection_remove(tree.selection())
        update_button_states()

    def validate_form():
        b, m, p, q = get_real_value(brand), get_real_value(model), get_real_value(price), get_real_value(quantity)
        if b == "" or m == "":
            messagebox.showerror("Error", "Brand and Model cannot be empty")
            return False
        if not is_number(p, allow_float=True) or float(p) < 0:
            messagebox.showerror("Error", "Price must be a valid positive number")
            return False
        if not is_number(q) or int(q) < 0:
            messagebox.showerror("Error", "Quantity must be a valid whole number")
            return False
        return True

    def load_data(rows=None):
        tree.delete(*tree.get_children())
        if rows is None:
            rows = safe_query("SELECT * FROM phones") or []
        threshold = app_settings["low_stock_threshold"]
        for row in rows:
            tags = ()
            try:
                qty = int(row[4])
                if qty == 0:
                    tags = ("out_of_stock",)
                elif qty <= threshold:
                    tags = ("low_stock",)
            except (ValueError, TypeError, IndexError):
                pass
            tree.insert("", tk.END, values=row, tags=tags)
        tree.tag_configure("low_stock", background="#fff3cd")
        tree.tag_configure("out_of_stock", background="#f9eced")
        refresh_dashboard_stats()

    def save_phone():
        if not validate_form():
            return
        ok, err = safe_execute(
            "INSERT INTO phones (brand, model, price, quantity) VALUES (%s,%s,%s,%s)",
            (get_real_value(brand), get_real_value(model), get_real_value(price), get_real_value(quantity))
        )
        if ok:
            messagebox.showinfo("Success", "Phone Saved Successfully")
            clear_fields()
            load_data()
        else:
            messagebox.showerror("Database Error", err)

    def update_phone():
        if selected_id["value"] is None or not validate_form():
            return
        ok, err = safe_execute(
            "UPDATE phones SET brand=%s, model=%s, price=%s, quantity=%s WHERE id=%s",
            (get_real_value(brand), get_real_value(model), get_real_value(price), get_real_value(quantity), selected_id["value"])
        )
        if ok:
            messagebox.showinfo("Success", "Phone Updated Successfully")
            clear_fields()
            load_data()
        else:
            messagebox.showerror("Database Error", err)

    def delete_phone():
        if selected_id["value"] is None:
            return
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this phone?"):
            return
        ok, err = safe_execute("DELETE FROM phones WHERE id=%s", (selected_id["value"],))
        if ok:
            messagebox.showinfo("Success", "Phone Deleted Successfully")
            clear_fields()
            load_data()
        else:
            messagebox.showerror("Database Error", err)

    def select_record(event):
        selected = tree.focus()
        if selected == "":
            return
        values = tree.item(selected, "values")
        selected_id["value"] = values[0]
        for e, val in [(brand, values[1]), (model, values[2]), (price, values[3]), (quantity, values[4])]:
            e.delete(0, tk.END)
            e.insert(0, val)
            e.config(fg="black")
        update_button_states()

    def search_phone():
        keyword = search_entry.get().strip()
        if keyword == "" or keyword == getattr(search_entry, "placeholder", None):
            load_data()
            return
        like_val = f"%{keyword}%"
        rows = safe_query("SELECT * FROM phones WHERE brand LIKE %s OR model LIKE %s", (like_val, like_val)) or []
        load_data(rows)

    def reset_search():
        clear_and_placeholder(search_entry, "Search brand or model...")
        load_data()

    def sort_by_column(col_index, col_name):
        reverse = sort_state["col"] == col_name and not sort_state["reverse"]
        sort_state["col"] = col_name
        sort_state["reverse"] = reverse
        items = [(tree.set(k, columns[col_index]), k) for k in tree.get_children("")]

        def try_cast(val):
            try:
                return float(val)
            except ValueError:
                return val.lower()

        items.sort(key=lambda t: try_cast(t[0]), reverse=reverse)
        for index, (_, k) in enumerate(items):
            tree.move(k, "", index)

    def get_all_products():
        return safe_query("SELECT id, brand, model, price, quantity FROM phones") or []

    def adjust_product_stock(product_id, delta):
        return safe_execute("UPDATE phones SET quantity = quantity + %s WHERE id=%s", (delta, product_id))

    tk.Button(action_frame, text="Save", width=16, bg=COLORS["accent_light"], fg="white", command=save_phone).grid(row=0, column=0, padx=8, pady=8)
    update_btn = tk.Button(action_frame, text="Update", width=16, bg=COLORS["accent_dark"], fg="white", command=update_phone, state=tk.DISABLED)
    update_btn.grid(row=0, column=1, padx=8, pady=8)
    delete_btn = tk.Button(action_frame, text="Delete", width=16, bg=COLORS["danger"], fg="white", command=delete_phone, state=tk.DISABLED)
    delete_btn.grid(row=1, column=0, padx=8, pady=8)
    tk.Button(action_frame, text="Clear", width=16, bg=COLORS["accent"], fg="white", command=clear_fields).grid(row=1, column=1, padx=8, pady=8)
    tk.Button(action_frame, text="Refresh", width=16, bg=COLORS["accent"], fg="white", command=load_data).grid(row=2, column=0, columnspan=2, padx=8, pady=8, sticky="ew")

    search_frame = tk.LabelFrame(products_frame, text="Search", font=("Segoe UI", 10, "bold"), bg="white", padx=10, pady=10)
    search_frame.pack(fill="x", padx=20, pady=(15, 10))
    search_entry = tk.Entry(search_frame, width=40)
    search_entry.grid(row=0, column=0, padx=5)
    add_placeholder(search_entry, "Search brand or model...")
    search_entry.bind("<Return>", lambda event: search_phone())
    tk.Button(search_frame, text="Search", width=12, bg=COLORS["accent"], fg="white", command=search_phone).grid(row=0, column=1, padx=5)
    tk.Button(search_frame, text="Reset", width=12, bg=COLORS["accent"], fg="white", command=reset_search).grid(row=0, column=2, padx=5)

    table_frame = tk.Frame(products_frame, bg=COLORS["bg"])
    table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    columns = ("ID", "Brand", "Model", "Price", "Quantity")
    tree = ttk.Treeview(table_frame, columns=columns, show="headings")
    for i, col in enumerate(columns):
        tree.heading(col, text=col, command=lambda i=i, c=col: sort_by_column(i, c))
        tree.column(col, width=150, anchor="center")
    tree.pack(side="left", fill="both", expand=True)
    tree.bind("<ButtonRelease-1>", select_record)

    scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    # -- GENERIC CRUD BUILDER (Customers / Suppliers) --
    def build_crud_section(parent, title, icon, table_name, fields, id_col="id"):
        state = {"selected_id": None}
        frame = tk.Frame(parent, bg=COLORS["bg"])
        tk.Label(frame, text=f"{icon} {title}", font=("Segoe UI", 16, "bold"),
                 bg=COLORS["bg"], fg="#1a1a2e").pack(anchor="w", padx=20, pady=(20, 10))

        top_row = tk.Frame(frame, bg=COLORS["bg"])
        top_row.pack(fill="x", padx=20)

        form_frame = tk.LabelFrame(top_row, text=f"{title[:-1] if title.endswith('s') else title} Details",
                                    font=("Segoe UI", 10, "bold"), bg="white", padx=10, pady=10)
        form_frame.grid(row=0, column=0, sticky="n", padx=(0, 10))

        entries = {}
        for i, f in enumerate(fields):
            tk.Label(form_frame, text=f["label"], bg="white").grid(row=i, column=0, sticky="w", pady=8)
            e = tk.Entry(form_frame, width=28)
            e.grid(row=i, column=1, pady=8)
            add_placeholder(e, f.get("placeholder", f["label"]))
            entries[f["col"]] = e

        action_frame2 = tk.LabelFrame(top_row, text="Actions", font=("Segoe UI", 10, "bold"), bg="white", padx=10, pady=10)
        action_frame2.grid(row=0, column=1, sticky="n")

        def clear_form():
            state["selected_id"] = None
            for f in fields:
                clear_and_placeholder(entries[f["col"]], f.get("placeholder", f["label"]))
            tree2.selection_remove(tree2.selection())
            upd_btn.config(state=tk.DISABLED)
            del_btn.config(state=tk.DISABLED)

        def validate():
            first_col = fields[0]["col"]
            if get_real_value(entries[first_col]) == "":
                messagebox.showerror("Error", f"{fields[0]['label']} cannot be empty")
                return False
            return True

        def refresh(rows=None):
            tree2.delete(*tree2.get_children())
            if rows is None:
                db_cols = ", ".join([id_col] + [f["col"] for f in fields])
                rows = safe_query(f"SELECT {db_cols} FROM {table_name}")
            if rows is None:
                tree2.insert("", tk.END, values=[f"Table '{table_name}' not found - run create_tables.sql"] + [""] * len(fields))
                return
            for row in rows:
                tree2.insert("", tk.END, values=row)

        def save_record():
            if not validate():
                return
            cols = ", ".join(f["col"] for f in fields)
            placeholders = ", ".join(["%s"] * len(fields))
            values = tuple(get_real_value(entries[f["col"]]) for f in fields)
            ok, err = safe_execute(f"INSERT INTO {table_name} ({cols}) VALUES ({placeholders})", values)
            if ok:
                messagebox.showinfo("Success", "Saved successfully")
                clear_form()
                refresh()
            else:
                messagebox.showerror("Database Error", err)

        def update_record():
            if state["selected_id"] is None or not validate():
                return
            set_clause = ", ".join(f"{f['col']}=%s" for f in fields)
            values = tuple(get_real_value(entries[f["col"]]) for f in fields) + (state["selected_id"],)
            ok, err = safe_execute(f"UPDATE {table_name} SET {set_clause} WHERE {id_col}=%s", values)
            if ok:
                messagebox.showinfo("Success", "Updated successfully")
                clear_form()
                refresh()
            else:
                messagebox.showerror("Database Error", err)

        def delete_record():
            if state["selected_id"] is None:
                return
            if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this record?"):
                return
            ok, err = safe_execute(f"DELETE FROM {table_name} WHERE {id_col}=%s", (state["selected_id"],))
            if ok:
                messagebox.showinfo("Success", "Deleted successfully")
                clear_form()
                refresh()
            else:
                messagebox.showerror("Database Error", err)

        def on_select(event):
            sel = tree2.focus()
            if sel == "":
                return
            values = tree2.item(sel, "values")
            if len(values) < len(fields) + 1:
                return
            state["selected_id"] = values[0]
            for i, f in enumerate(fields):
                e = entries[f["col"]]
                e.delete(0, tk.END)
                e.insert(0, values[i + 1])
                e.config(fg="black")
            upd_btn.config(state=tk.NORMAL)
            del_btn.config(state=tk.NORMAL)

        tk.Button(action_frame2, text="Save", width=16, bg=COLORS["accent_light"], fg="white", command=save_record).grid(row=0, column=0, padx=8, pady=8)
        upd_btn = tk.Button(action_frame2, text="Update", width=16, bg=COLORS["accent_dark"], fg="white", command=update_record, state=tk.DISABLED)
        upd_btn.grid(row=0, column=1, padx=8, pady=8)
        del_btn = tk.Button(action_frame2, text="Delete", width=16, bg=COLORS["danger"], fg="white", command=delete_record, state=tk.DISABLED)
        del_btn.grid(row=1, column=0, padx=8, pady=8)
        tk.Button(action_frame2, text="Clear", width=16, bg=COLORS["accent"], fg="white", command=clear_form).grid(row=1, column=1, padx=8, pady=8)
        tk.Button(action_frame2, text="Refresh", width=16, bg=COLORS["accent"], fg="white", command=refresh).grid(row=2, column=0, columnspan=2, padx=8, pady=8, sticky="ew")

        table_wrap = tk.Frame(frame, bg=COLORS["bg"])
        table_wrap.pack(fill="both", expand=True, padx=20, pady=(15, 20))

        tree_cols = ["ID"] + [f["label"] for f in fields]
        tree2 = ttk.Treeview(table_wrap, columns=tree_cols, show="headings")
        for c in tree_cols:
            tree2.heading(c, text=c)
            tree2.column(c, width=150, anchor="center")
        tree2.pack(side="left", fill="both", expand=True)
        tree2.bind("<ButtonRelease-1>", on_select)

        sb2 = ttk.Scrollbar(table_wrap, orient="vertical", command=tree2.yview)
        tree2.configure(yscroll=sb2.set)
        sb2.pack(side="right", fill="y")

        frame.refresh = refresh
        refresh()
        return frame

    customers_frame = build_crud_section(
        page_container, "Customers", "👥", "customers",
        [
            {"col": "name", "label": "Name", "placeholder": "e.g. John Doe"},
            {"col": "phone", "label": "Phone", "placeholder": "e.g. 03001234567"},
            {"col": "email", "label": "Email", "placeholder": "e.g. john@email.com"},
            {"col": "address", "label": "Address", "placeholder": "e.g. Main Street 12"},
        ]
    )
    suppliers_frame = build_crud_section(
        page_container, "Suppliers", "🚚", "suppliers",
        [
            {"col": "company_name", "label": "Company", "placeholder": "e.g. TechDistributors Ltd"},
            {"col": "phone", "label": "Phone", "placeholder": "e.g. 03001234567"},
            {"col": "email", "label": "Email", "placeholder": "e.g. contact@supplier.com"},
            {"col": "address", "label": "Address", "placeholder": "e.g. Industrial Area 5"},
        ]
    )

    # ---------- SALES ----------
    def build_sales_section(parent):
        state = {"selected_id": None}
        frame = tk.Frame(parent, bg=COLORS["bg"])
        tk.Label(frame, text="💰 Sales", font=("Segoe UI", 16, "bold"),
                 bg=COLORS["bg"], fg="#1a1a2e").pack(anchor="w", padx=20, pady=(20, 10))

        top_row = tk.Frame(frame, bg=COLORS["bg"])
        top_row.pack(fill="x", padx=20)

        form_frame2 = tk.LabelFrame(top_row, text="New Sale", font=("Segoe UI", 10, "bold"), bg="white", padx=10, pady=10)
        form_frame2.grid(row=0, column=0, sticky="n", padx=(0, 10))

        tk.Label(form_frame2, text="Customer Name", bg="white").grid(row=0, column=0, sticky="w", pady=8)
        customer_name_entry = tk.Entry(form_frame2, width=28)
        customer_name_entry.grid(row=0, column=1, pady=8)
        add_placeholder(customer_name_entry, "e.g. Walk-in Customer")

        tk.Label(form_frame2, text="Product", bg="white").grid(row=1, column=0, sticky="w", pady=8)
        product_var = tk.StringVar()
        product_combo = ttk.Combobox(form_frame2, textvariable=product_var, width=26, state="readonly")
        product_combo.grid(row=1, column=1, pady=8)

        tk.Label(form_frame2, text="Quantity", bg="white").grid(row=2, column=0, sticky="w", pady=8)
        qty_entry = tk.Entry(form_frame2, width=28)
        qty_entry.grid(row=2, column=1, pady=8)
        add_placeholder(qty_entry, "e.g. 1")

        tk.Label(form_frame2, text="Total Amount", bg="white").grid(row=3, column=0, sticky="w", pady=8)
        total_label = tk.Label(form_frame2, text=fmt_currency(0), bg="white", font=("Segoe UI", 10, "bold"), fg=COLORS["accent"])
        total_label.grid(row=3, column=1, sticky="w", pady=8)

        product_lookup = {}

        def refresh_product_list():
            product_lookup.clear()
            products = get_all_products()
            display_values = []
            for p in products:
                pid, pbrand, pmodel, pprice, pstock = p
                display = f"{pbrand} {pmodel} (Stock: {pstock})"
                product_lookup[display] = (pid, float(pprice), int(pstock))
                display_values.append(display)
            product_combo["values"] = display_values

        def update_total(*args):
            selected_display = product_var.get()
            qty_val = get_real_value(qty_entry)
            if selected_display in product_lookup and is_number(qty_val):
                _, unit_price, _ = product_lookup[selected_display]
                total_label.config(text=fmt_currency(unit_price * int(qty_val)))
            else:
                total_label.config(text=fmt_currency(0))

        product_combo.bind("<<ComboboxSelected>>", update_total)
        qty_entry.bind("<KeyRelease>", update_total)

        action_frame3 = tk.LabelFrame(top_row, text="Actions", font=("Segoe UI", 10, "bold"), bg="white", padx=10, pady=10)
        action_frame3.grid(row=0, column=1, sticky="n")

        def clear_form():
            state["selected_id"] = None
            clear_and_placeholder(customer_name_entry, "e.g. Walk-in Customer")
            clear_and_placeholder(qty_entry, "e.g. 1")
            product_var.set("")
            total_label.config(text=fmt_currency(0))
            refresh_product_list()

        def refresh_sales(rows=None):
            tree3.delete(*tree3.get_children())
            if rows is None:
                rows = safe_query("SELECT id, customer_name, product_name, quantity, total_amount, sale_date FROM sales")
            if rows is None:
                tree3.insert("", tk.END, values=["Table 'sales' not found - run create_tables.sql", "", "", "", ""])
                return
            for row in rows:
                display_row = list(row)
                try:
                    display_row[4] = fmt_currency(row[4])
                except (IndexError, ValueError, TypeError):
                    pass
                tree3.insert("", tk.END, values=display_row)
            refresh_dashboard_stats()

        def record_sale():
            selected_display = product_var.get()
            cust_name = get_real_value(customer_name_entry)
            qty_val = get_real_value(qty_entry)

            if selected_display not in product_lookup:
                messagebox.showerror("Error", "Please select a product")
                return
            if cust_name == "":
                messagebox.showerror("Error", "Customer name cannot be empty")
                return
            if not is_number(qty_val) or int(qty_val) <= 0:
                messagebox.showerror("Error", "Quantity must be a positive whole number")
                return

            product_id, unit_price, stock = product_lookup[selected_display]
            qty = int(qty_val)
            if qty > stock:
                messagebox.showerror("Error", f"Not enough stock. Only {stock} units available.")
                return

            product_display_name = selected_display.split(" (Stock:")[0]
            total_amount = unit_price * qty
            sale_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            ok, err = safe_execute(
                "INSERT INTO sales (customer_name, product_name, quantity, total_amount, sale_date) VALUES (%s,%s,%s,%s,%s)",
                (cust_name, product_display_name, qty, total_amount, sale_date)
            )
            if not ok:
                messagebox.showerror("Database Error", err)
                return

            adjust_product_stock(product_id, -qty)
            messagebox.showinfo("Success", f"Sale recorded: {fmt_currency(total_amount)}")
            clear_form()
            refresh_sales()
            load_data()

        def delete_sale():
            if state["selected_id"] is None:
                return
            if not messagebox.askyesno("Confirm Delete", "Delete this sale record? (Stock will not be restored automatically)"):
                return
            ok, err = safe_execute("DELETE FROM sales WHERE id=%s", (state["selected_id"],))
            if ok:
                messagebox.showinfo("Success", "Sale record deleted")
                clear_form()
                refresh_sales()
            else:
                messagebox.showerror("Database Error", err)

        def on_select(event):
            sel = tree3.focus()
            if sel == "":
                return
            values = tree3.item(sel, "values")
            if len(values) < 5 or "not found" in str(values[0]):
                return
            state["selected_id"] = values[0]
            del_btn3.config(state=tk.NORMAL)

        tk.Button(action_frame3, text="Record Sale", width=16, bg=COLORS["accent_light"], fg="white", command=record_sale).grid(row=0, column=0, padx=8, pady=8)
        tk.Button(action_frame3, text="Clear", width=16, bg=COLORS["accent"], fg="white", command=clear_form).grid(row=0, column=1, padx=8, pady=8)
        del_btn3 = tk.Button(action_frame3, text="Delete", width=16, bg=COLORS["danger"], fg="white", command=delete_sale, state=tk.DISABLED)
        del_btn3.grid(row=1, column=0, padx=8, pady=8)
        tk.Button(action_frame3, text="Refresh", width=16, bg=COLORS["accent"], fg="white",
                  command=lambda: [refresh_sales(), refresh_product_list()]).grid(row=1, column=1, padx=8, pady=8)

        table_wrap = tk.Frame(frame, bg=COLORS["bg"])
        table_wrap.pack(fill="both", expand=True, padx=20, pady=(15, 20))

        tree_cols = ["ID", "Customer", "Product", "Qty", "Total", "Date"]
        tree3 = ttk.Treeview(table_wrap, columns=tree_cols, show="headings")
        for c in tree_cols:
            tree3.heading(c, text=c)
            tree3.column(c, width=150, anchor="center")
        tree3.pack(side="left", fill="both", expand=True)
        tree3.bind("<ButtonRelease-1>", on_select)

        sb3 = ttk.Scrollbar(table_wrap, orient="vertical", command=tree3.yview)
        tree3.configure(yscroll=sb3.set)
        sb3.pack(side="right", fill="y")

        frame.refresh = lambda: [refresh_sales(), refresh_product_list()]
        refresh_product_list()
        refresh_sales()
        return frame

    sales_frame = build_sales_section(page_container)

    # ---------- REPORTS ----------
    def build_reports_section(parent):
        frame = tk.Frame(parent, bg=COLORS["bg"])
        tk.Label(frame, text="📊 Reports", font=("Segoe UI", 16, "bold"),
                 bg=COLORS["bg"], fg="#1a1a2e").pack(anchor="w", padx=20, pady=(20, 10))

        summary_label = tk.Label(frame, text="", font=("Segoe UI", 11), bg=COLORS["bg"], fg="#333", justify="left")
        summary_label.pack(anchor="w", padx=20, pady=10)

        tk.Label(frame, text="Top Selling Products", font=("Segoe UI", 12, "bold"),
                 bg=COLORS["bg"], fg="#1a1a2e").pack(anchor="w", padx=20, pady=(10, 5))

        top_tree = ttk.Treeview(frame, columns=("Product", "Units Sold", "Revenue"), show="headings", height=6)
        for c in ("Product", "Units Sold", "Revenue"):
            top_tree.heading(c, text=c)
            top_tree.column(c, width=200, anchor="center")
        top_tree.pack(fill="x", padx=20, pady=(0, 15))

        def refresh_report():
            inv_result = safe_query("SELECT COUNT(*), SUM(quantity), SUM(price*quantity) FROM phones", fetch="one")
            total_models = inv_result[0] if inv_result and inv_result[0] else 0
            total_units = inv_result[1] if inv_result and inv_result[1] else 0
            total_value = inv_result[2] if inv_result and inv_result[2] else 0

            sales_result = safe_query("SELECT COUNT(*), SUM(quantity), SUM(total_amount) FROM sales", fetch="one")
            if sales_result is None:
                sales_text = "Sales data unavailable - run create_tables.sql to enable this report."
            else:
                num_sales = sales_result[0] or 0
                units_sold = sales_result[1] or 0
                revenue = sales_result[2] or 0
                sales_text = (
                    f"Total Transactions: {num_sales}\n"
                    f"Total Units Sold: {units_sold}\n"
                    f"Total Revenue: {fmt_currency(revenue)}"
                )

            summary_label.config(
                text=(
                    f"Total Product Models: {total_models}\n"
                    f"Total Units in Stock: {total_units}\n"
                    f"Total Inventory Value: {fmt_currency(total_value)}\n\n"
                    f"{sales_text}"
                )
            )

            top_tree.delete(*top_tree.get_children())
            top_rows = safe_query(
                "SELECT product_name, SUM(quantity), SUM(total_amount) FROM sales "
                "GROUP BY product_name ORDER BY SUM(quantity) DESC LIMIT 5"
            )
            if top_rows:
                for row in top_rows:
                    top_tree.insert("", tk.END, values=(row[0], row[1], fmt_currency(row[2])))

        tk.Button(frame, text="🔄 Refresh Report", bg=COLORS["accent"], fg="white", width=18, command=refresh_report).pack(anchor="w", padx=20)
        frame.refresh = refresh_report
        refresh_report()
        return frame

    reports_frame = build_reports_section(page_container)

    # ---------- SETTINGS ----------
    def build_settings_section(parent):
        frame = tk.Frame(parent, bg=COLORS["bg"])
        tk.Label(frame, text="⚙️ Settings", font=("Segoe UI", 16, "bold"),
                 bg=COLORS["bg"], fg="#1a1a2e").pack(anchor="w", padx=20, pady=(20, 10))

        settings_form = tk.LabelFrame(frame, text="Preferences", font=("Segoe UI", 10, "bold"), bg="white", padx=15, pady=15)
        settings_form.pack(anchor="w", padx=20, fill="x")

        tk.Label(settings_form, text="Low Stock Threshold", bg="white").grid(row=0, column=0, sticky="w", pady=8)
        threshold_entry = tk.Entry(settings_form, width=20)
        threshold_entry.insert(0, str(app_settings["low_stock_threshold"]))
        threshold_entry.grid(row=0, column=1, sticky="w", pady=8, padx=10)

        tk.Label(settings_form, text="Currency Symbol", bg="white").grid(row=1, column=0, sticky="w", pady=8)
        currency_entry = tk.Entry(settings_form, width=20)
        currency_entry.insert(0, app_settings["currency_symbol"])
        currency_entry.grid(row=1, column=1, sticky="w", pady=8, padx=10)

        status_label = tk.Label(frame, text="", bg=COLORS["bg"], fg=COLORS["accent"], font=("Segoe UI", 9, "bold"))
        status_label.pack(anchor="w", padx=20, pady=(5, 0))

        def save_settings():
            t_val = threshold_entry.get().strip()
            c_val = currency_entry.get().strip()
            if not is_number(t_val) or int(t_val) < 0:
                messagebox.showerror("Error", "Low stock threshold must be a positive whole number")
                return
            if c_val == "":
                messagebox.showerror("Error", "Currency symbol cannot be empty")
                return
            app_settings["low_stock_threshold"] = int(t_val)
            app_settings["currency_symbol"] = c_val
            status_label.config(text="Settings saved ✔")
            load_data()
            refresh_dashboard_stats()
            reports_frame.refresh()

        tk.Button(settings_form, text="Save Settings", bg=COLORS["accent"], fg="white", width=18,
                  command=save_settings).grid(row=2, column=0, columnspan=2, pady=(10, 0))

        tk.Label(frame, text="Note: settings apply for the current session only.",
                 font=("Segoe UI", 9), bg=COLORS["bg"], fg="#888888").pack(anchor="w", padx=20, pady=(15, 0))
        return frame

    settings_frame = build_settings_section(page_container)

    for f in (dashboard_frame, products_frame, customers_frame, suppliers_frame, sales_frame, reports_frame, settings_frame):
        f.place(x=0, y=0, relwidth=1, relheight=1)

    btn_dashboard = make_nav_button("📈  Dashboard", lambda: [show_sub_frame(dashboard_frame), set_active_nav(btn_dashboard), refresh_dashboard_stats()])
    btn_products = make_nav_button("📱  Products", lambda: [show_sub_frame(products_frame), set_active_nav(btn_products)])
    btn_customers = make_nav_button("👥  Customers", lambda: [show_sub_frame(customers_frame), set_active_nav(btn_customers), customers_frame.refresh()])
    btn_suppliers = make_nav_button("🚚  Suppliers", lambda: [show_sub_frame(suppliers_frame), set_active_nav(btn_suppliers), suppliers_frame.refresh()])
    btn_sales = make_nav_button("💰  Sales", lambda: [show_sub_frame(sales_frame), set_active_nav(btn_sales), sales_frame.refresh()])
    btn_reports = make_nav_button("📊  Reports", lambda: [show_sub_frame(reports_frame), set_active_nav(btn_reports), reports_frame.refresh()])
    btn_settings = make_nav_button("⚙️  Settings", lambda: [show_sub_frame(settings_frame), set_active_nav(btn_settings)])

    tk.Frame(sidebar, bg=COLORS["sidebar"], height=2).pack(fill="x", pady=15)
    logout_btn = tk.Button(sidebar, text="🚪  Logout", anchor="w", font=("Segoe UI", 12), bd=0,
              bg=COLORS["sidebar"], fg="#ff6b6b", activebackground="#3a1a2e",
              activeforeground="#ff6b6b", padx=22, pady=16, command=do_logout, cursor="hand2")
    logout_btn.pack(fill="x", side="bottom", pady=10)
    add_hover(logout_btn, COLORS["sidebar"], "#3a1a2e")

    show_sub_frame(dashboard_frame)
    set_active_nav(btn_dashboard)
    load_data()

    return outer


# ===========================
# BUILD ALL PAGES & START
# ===========================
pages["login"] = build_login_page()
pages["signup"] = build_signup_page()
pages["forgot"] = build_forgot_password_page()
pages["customer_catalog"] = build_customer_catalog_page()
pages["main_app"] = build_main_app_page()

for p in pages.values():
    p.place(x=0, y=0, relwidth=1, relheight=1)

show_page("login")
root.mainloop()