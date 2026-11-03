from tkinter import messagebox
print("Hola bienvenido a mi empresa de desarrollo de software")
nombre = input("como te llamas?")
print("______________________________________________________")
print ("hola "+ nombre + " bienvenido a mi empresa de desarrollo de software")
messagebox.showinfo("Bienvenido", "Hola "+ nombre + " bienvenido al mundo del software")
import tkinter as tk

ventana = tk.Tk()           # Crea la ventana principal
ventana.title("Mi primera ventana")  # Cambia el título

ventana.mainloop()    

