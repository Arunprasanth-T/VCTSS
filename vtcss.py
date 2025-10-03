import tkinter as tk
from tkinter import messagebox
import sqlite3

# Connect to database (creates if not exists)
conn = sqlite3.connect('tollsystem.db')
cursor = conn.cursor()

# Create vehicles table
cursor.execute('''CREATE TABLE IF NOT EXISTS vehicles (
                    vehicle_id TEXT PRIMARY KEY,
                    owner_name TEXT,
                    balance REAL)''')

# Create toll transactions table
cursor.execute('''CREATE TABLE IF NOT EXISTS toll_transactions (
                    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    vehicle_id TEXT,
                    toll_amount REAL,
                    date_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(vehicle_id) REFERENCES vehicles(vehicle_id))''')

# Create recharge history table
cursor.execute('''CREATE TABLE IF NOT EXISTS recharge_history (
                    recharge_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    vehicle_id TEXT,
                    amount REAL,
                    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(vehicle_id) REFERENCES vehicles(vehicle_id))''')

conn.commit()

# GUI Functions
def on_closing():
    conn.close()
    root.destroy()

def process_vehicle():
    vehicle_id = entry_id.get().strip()
    if not vehicle_id:
        messagebox.showwarning("Input Error", "Please enter a valid Vehicle ID.")
        return

    cursor.execute("SELECT owner_name, balance FROM vehicles WHERE vehicle_id=?", (vehicle_id,))
    result = cursor.fetchone()
    if result:
        owner, balance = result
        toll_amount = 50
        if balance >= toll_amount:
            new_balance = balance - toll_amount
            cursor.execute("UPDATE vehicles SET balance=? WHERE vehicle_id=?", (new_balance, vehicle_id))
            cursor.execute("INSERT INTO toll_transactions (vehicle_id, toll_amount) VALUES (?, ?)",
                           (vehicle_id, toll_amount))
            conn.commit()
            messagebox.showinfo("Success", f"Toll Paid!\nOwner: {owner}\nNew Balance: ₹{new_balance}")
        else:
            messagebox.showwarning("Low Balance", "Insufficient Balance! Recharge Needed.")
    else:
        messagebox.showerror("Error", "Vehicle not found!")
    entry_id.delete(0, tk.END)

def add_vehicle():
    vehicle_id = entry_new_id.get().strip()
    owner_name = entry_owner.get().strip()
    balance = entry_balance.get().strip()

    if not (vehicle_id and owner_name and balance):
        messagebox.showwarning("Input Error", "Please enter all details.")
        return

    try:
        balance = float(balance)
        if balance < 0:
            messagebox.showerror("Invalid Entry", "Balance cannot be negative!")
            return

        cursor.execute("INSERT INTO vehicles (vehicle_id, owner_name, balance) VALUES (?, ?, ?)",
                       (vehicle_id, owner_name, balance))
        conn.commit()
        messagebox.showinfo("Success", "Vehicle Added Successfully!")
        entry_new_id.delete(0, tk.END)
        entry_owner.delete(0, tk.END)
        entry_balance.delete(0, tk.END)
    except ValueError:
        messagebox.showerror("Error", "Balance must be a valid number!")
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Vehicle ID already exists!")

def recharge_vehicle():
    vehicle_id = entry_recharge_id.get().strip()
    amount = entry_recharge_amount.get().strip()

    if not (vehicle_id and amount):
        messagebox.showwarning("Input Error", "Please enter both Vehicle ID and Amount.")
        return

    try:
        amount = float(amount)
        if amount < 0:
            messagebox.showerror("Invalid Entry", "You cannot recharge with a negative amount!")
            return

        cursor.execute("SELECT balance FROM vehicles WHERE vehicle_id=?", (vehicle_id,))
        result = cursor.fetchone()
        if result:
            new_balance = result[0] + amount
            cursor.execute("UPDATE vehicles SET balance=? WHERE vehicle_id=?", (new_balance, vehicle_id))
            cursor.execute("INSERT INTO recharge_history (vehicle_id, amount) VALUES (?, ?)", (vehicle_id, amount))
            conn.commit()
            messagebox.showinfo("Recharge Successful", f"₹{amount} added to Vehicle ID: {vehicle_id}\nNew Balance: ₹{new_balance}")
            entry_recharge_id.delete(0, tk.END)
            entry_recharge_amount.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "Vehicle ID not found!")
    except ValueError:
        messagebox.showerror("Error", "Amount must be a valid number!")

def view_recharge_history():
    vehicle_id = entry_recharge_id.get().strip()
    if not vehicle_id:
        messagebox.showwarning("Input Error", "Please enter Vehicle ID.")
        return

    cursor.execute("SELECT amount, date FROM recharge_history WHERE vehicle_id=? ORDER BY date DESC", (vehicle_id,))
    records = cursor.fetchall()
    if records:
        history_text = f"Recharge History for Vehicle ID {vehicle_id}:\n\n"
        for amount, date in records:
            history_text += f"₹{amount} recharged on {date}\n"
        messagebox.showinfo("Recharge History", history_text)
    else:
        messagebox.showinfo("No History", "No recharge history found for this vehicle.")

def search_vehicle():
    vehicle_id = entry_search_id.get().strip()
    if not vehicle_id:
        messagebox.showwarning("Input Error", "Please enter Vehicle ID to search.")
        return

    cursor.execute("SELECT vehicle_id, owner_name, balance FROM vehicles WHERE vehicle_id=?", (vehicle_id,))
    result = cursor.fetchone()
    if result:
        messagebox.showinfo("Vehicle Found", f"ID: {result[0]}\nOwner: {result[1]}\nBalance: ₹{result[2]}")
    else:
        messagebox.showinfo("Not Found", "No vehicle found with this ID.")

# GUI
root = tk.Tk()
root.title("Virtual Toll Collection System")
root.geometry("400x600")
root.configure(bg="#ECF0F1")

# Process Toll
frame_toll = tk.Frame(root, bg="#D5DBDB", padx=10, pady=10)
frame_toll.pack(pady=10, fill="x")

tk.Label(frame_toll, text="Enter Vehicle ID:", bg="#D5DBDB", font=("Arial", 12)).grid(row=0, column=0)
entry_id = tk.Entry(frame_toll)
entry_id.grid(row=0, column=1)
tk.Button(frame_toll, text="Process Toll", command=process_vehicle, bg="#3498DB", fg="white").grid(row=1, column=0, columnspan=2, pady=5, sticky="ew")

# Add Vehicle
frame_add = tk.Frame(root, bg="#D5DBDB", padx=10, pady=10)
frame_add.pack(pady=10, fill="x")

tk.Label(frame_add, text="Add New Vehicle", bg="#D5DBDB", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2)
tk.Label(frame_add, text="Vehicle ID:", bg="#D5DBDB").grid(row=1, column=0)
entry_new_id = tk.Entry(frame_add)
entry_new_id.grid(row=1, column=1)

tk.Label(frame_add, text="Owner Name:", bg="#D5DBDB").grid(row=2, column=0)
entry_owner = tk.Entry(frame_add)
entry_owner.grid(row=2, column=1)

tk.Label(frame_add, text="Balance (₹):", bg="#D5DBDB").grid(row=3, column=0)
entry_balance = tk.Entry(frame_add)
entry_balance.grid(row=3, column=1)

tk.Button(frame_add, text="Add Vehicle", command=add_vehicle, bg="#2ECC71", fg="white").grid(row=4, column=0, columnspan=2, pady=5, sticky="ew")

# Recharge Section
frame_recharge = tk.Frame(root, bg="#D5DBDB", padx=10, pady=10)
frame_recharge.pack(pady=10, fill="x")

tk.Label(frame_recharge, text="Recharge Vehicle", bg="#D5DBDB", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2)
tk.Label(frame_recharge, text="Vehicle ID:", bg="#D5DBDB").grid(row=1, column=0)
entry_recharge_id = tk.Entry(frame_recharge)
entry_recharge_id.grid(row=1, column=1)

tk.Label(frame_recharge, text="Amount (₹):", bg="#D5DBDB").grid(row=2, column=0)
entry_recharge_amount = tk.Entry(frame_recharge)
entry_recharge_amount.grid(row=2, column=1)

tk.Button(frame_recharge, text="Recharge", command=recharge_vehicle, bg="#F39C12", fg="white").grid(row=3, column=0, columnspan=2, pady=5, sticky="ew")
tk.Button(frame_recharge, text="View Recharge History", command=view_recharge_history, bg="#8E44AD", fg="white").grid(row=4, column=0, columnspan=2, pady=5, sticky="ew")

# Search Vehicle
frame_search = tk.Frame(root, bg="#D5DBDB", padx=10, pady=10)
frame_search.pack(pady=10, fill="x")

tk.Label(frame_search, text="Search Vehicle by ID", bg="#D5DBDB", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2)
tk.Label(frame_search, text="Vehicle ID:", bg="#D5DBDB").grid(row=1, column=0)
entry_search_id = tk.Entry(frame_search)
entry_search_id.grid(row=1, column=1)
tk.Button(frame_search, text="Search", command=search_vehicle, bg="#1ABC9C", fg="white").grid(row=2, column=0, columnspan=2, pady=5, sticky="ew")

# Exit
tk.Button(root, text="Exit", command=root.quit, bg="#E74C3C", fg="white").pack(pady=10)

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
