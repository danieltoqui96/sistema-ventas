import tkinter as tk
from tkinter import messagebox
import pandas as pd

def cargar_excel():
    try:
        df = pd.read_excel("productos.xlsx")
        messagebox.showinfo("Excel", "Excel cargado correctamente")
        return df
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo cargar el Excel: {e}")
        return None
    
# Configuración de la ventana principal
root = tk.Tk()
root.title("Sistema de Ventas")

# Botón para cargar el Excel
btn_cargar = tk.Button(root, text="Cargar Productos", command=cargar_excel)
btn_cargar.pack(pady=20)

root.mainloop()