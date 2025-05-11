import tkinter as tk
from tkinter import ttk
import threading

class NutricionMonitor:
    def __init__(self, total_consultas):
        self.root = tk.Tk()
        self.root.title("Monitor de Nutrición de Sassy")
        self.root.geometry("600x400")
        self.root.resizable(False, False)
        self.total_consultas = total_consultas
        self.recuerdos = 0
        self.fuente_actual = ""
        self.mensajes = []
        self.textos = []
        self._after_id = None  # Para guardar el id del callback after

        self.label_contador = tk.Label(self.root, text="Recuerdos recolectados: 0", font=("Arial", 14))
        self.label_contador.pack(pady=10)

        self.progress = ttk.Progressbar(self.root, orient="horizontal", length=500, mode="determinate")
        self.progress.pack(pady=10)
        self.progress['maximum'] = total_consultas

        self.label_fuente = tk.Label(self.root, text="Fuente actual: -", font=("Arial", 12))
        self.label_fuente.pack(pady=5)

        self.text_area = tk.Text(self.root, height=10, width=70, state='disabled', font=("Arial", 10))
        self.text_area.pack(pady=10)

        self.root.protocol("WM_DELETE_WINDOW", self.cerrar)
        self.cerrado = False

    def actualizar(self, recuerdos, fuente, mensaje, texto):
        self.recuerdos = recuerdos
        self.fuente_actual = fuente
        self.label_contador.config(text=f"Recuerdos recolectados: {recuerdos}")
        self.progress['value'] = recuerdos
        self.label_fuente.config(text=f"Fuente actual: {fuente}")
        self.text_area.config(state='normal')
        if mensaje:
            self.text_area.insert('end', f"{mensaje}\n", ('msg',))
        if texto:
            self.text_area.insert('end', f"→ {texto[:120]}...\n", ('recuerdo',))
        self.text_area.see('end')
        self.text_area.config(state='disabled')
        self.root.update_idletasks()

    def programar_actualizacion(self, callback, ms=100):
        # Guarda el id del after para poder cancelarlo
        self._after_id = self.root.after(ms, callback)

    def cancelar_actualizacion(self):
        if self._after_id is not None:
            try:
                self.root.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None

    def cerrar(self):
        self.cerrado = True
        self.cancelar_actualizacion()
        self.root.destroy()

    def iniciar(self):
        threading.Thread(target=self.root.mainloop, daemon=True).start() 