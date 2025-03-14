import tkinter as tk
from tkinter import messagebox, ttk
import pandas as pd

class SalesSystem:
    def __init__(self, excel_path="productos.xlsx"):
        self.excel_path = excel_path
        self.df_products = self.load_excel()
        self.product_names = self.get_product_names()
        self.total_amount = 0.0
        self.setup_ui()

    def load_excel(self):
        """Carga el archivo Excel y retorna un DataFrame de pandas."""
        try:
            df = pd.read_excel(self.excel_path)
            messagebox.showinfo("Excel", "Excel cargado correctamente")
            return df
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el Excel: {e}")
            return None

    def get_product_names(self):
        """Extrae y retorna la lista de nombres de producto desde el DataFrame."""
        if self.df_products is not None and "Nombre" in self.df_products.columns:
            self.df_products["Nombre"] = self.df_products["Nombre"].astype(str).fillna("")
            return self.df_products["Nombre"].unique().tolist()
        else:
            return []

    def setup_ui(self):
        """Configura la interfaz gráfica con sus frames, widgets y eventos."""
        self.root = tk.Tk()
        self.root.geometry("800x600")
        self.root.title("Sistema de Ventas")

        # Configurar grid en la ventana principal
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=3)
        self.root.grid_rowconfigure(2, weight=1)

        # Frame de búsqueda (arriba, color azul claro)
        self.frame_search = tk.Frame(self.root, bg="lightblue")
        self.frame_search.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Frame para lista de productos (en el medio, color verde claro)
        self.frame_list = tk.Frame(self.root, bg="lightgreen")
        self.frame_list.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        # Frame para finalizar venta (abajo, color coral claro)
        self.frame_sale = tk.Frame(self.root, bg="lightcoral")
        self.frame_sale.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)

        # Combobox de búsqueda con autocompletar
        self.search_combobox = ttk.Combobox(self.frame_search, width=40)
        self.search_combobox["values"] = self.product_names
        self.search_combobox.pack(pady=10)
        self.search_combobox.bind("<KeyRelease>", self.on_combobox_keyrelease)
        self.search_combobox.bind("<<ComboboxSelected>>", self.on_combobox_select)

        # Tabla (Treeview) para mostrar los productos seleccionados
        columns = ("Nombre", "Precio", "Cantidad")
        self.products_table = ttk.Treeview(self.frame_list, columns=columns, show="headings")
        for col in columns:
            self.products_table.heading(col, text=col)
        self.products_table.pack(fill="both", expand=True)

        # Label para mostrar el total acumulado
        self.total_label = tk.Label(
            self.frame_list, text="Total: 0.00", bg="lightgreen", font=("Arial", 12, "bold")
        )
        self.total_label.pack(pady=10, anchor="e")

        # Botón para procesar la venta
        sale_button = tk.Button(self.frame_sale, text="Realizar Venta", command=self.process_sale)
        sale_button.pack(pady=10)

    def on_combobox_keyrelease(self, event):
        """Filtra las opciones del combobox según el texto ingresado."""
        typed_text = self.search_combobox.get().lower()
        filtered_list = (
            self.product_names
            if typed_text == ""
            else [name for name in self.product_names if typed_text in name.lower()]
        )
        self.search_combobox["values"] = filtered_list
        if filtered_list:
            self.search_combobox.event_generate("<Down>")

    def on_combobox_select(self, event):
        """
        Al seleccionar un producto del combobox, agrega una fila en la tabla
        con Nombre, Precio y Cantidad, y actualiza el total.
        """
        selected_product = self.search_combobox.get()
        if not selected_product:
            return
        
        # Obtener la fila del producto seleccionado
        df_row = self.df_products[self.df_products["Nombre"] == selected_product]
        if not df_row.empty:
            row_data = df_row.iloc[0]
            product_name = row_data["Nombre"]
            product_price = row_data["Precio"]
            product_quantity = row_data["Cantidad"]
            
            # Insertar la fila en la tabla
            self.products_table.insert(
                "", "end", values=(product_name, product_price, product_quantity)
            )
            
            try:
                price_value = float(product_price)
            except ValueError:
                price_value = 0.0
            self.total_amount += price_value
            self.total_label.config(text=f"Total: {self.total_amount:.2f}")

    def process_sale(self):
        """
        Procesa la venta, descontando 1 unidad por cada producto vendido
        en el DataFrame y actualizando el archivo Excel.
        """
        # Contar cuántas veces se vendió cada producto
        sale_counts = {}
        for child in self.products_table.get_children():
            product_name = self.products_table.item(child, "values")[0]
            sale_counts[product_name] = sale_counts.get(product_name, 0) + 1

        # Actualizar el stock en el DataFrame
        for product, count in sale_counts.items():
            idx = self.df_products[self.df_products["Nombre"] == product].index
            if not idx.empty:
                current_quantity = self.df_products.loc[idx, "Cantidad"].values[0]
                if current_quantity >= count:
                    self.df_products.loc[idx, "Cantidad"] = current_quantity - count
                else:
                    messagebox.showerror("Error", f"Stock insuficiente para {product}")
                    return

        # Guardar los cambios en el Excel
        try:
            self.df_products.to_excel(self.excel_path, index=False)
            messagebox.showinfo("Venta", "Venta procesada y stock actualizado en Excel.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar el Excel: {e}")
            return

        # Limpiar la tabla y reiniciar el total
        for child in self.products_table.get_children():
            self.products_table.delete(child)
        self.total_amount = 0.0
        self.total_label.config(text="Total: 0.00")

    def run(self):
        """Ejecuta el bucle principal de la aplicación."""
        self.root.mainloop()

if __name__ == "__main__":
    app = SalesSystem()
    app.run()
