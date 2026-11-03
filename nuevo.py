import customtkinter as ctk

# Configurar la ventana principal
ctk.set_appearance_mode("System")  # Opciones: "System", "Dark", "Light"
ctk.set_default_color_theme("blue")  # Temas: "blue", "green", "dark-blue"

app = ctk.CTk()
app.geometry("700x500")
app.title("Mi Aplicación - Progreso")

# Función que se ejecuta al presionar el botón
def accion_boton():
    print("¡Botón presionado!")

# Crear un título
titulo = ctk.CTkLabel(app, text="Bienvenido al Sistema", font=("Arial", 20, "bold"))
titulo.pack(pady=20)

# Crear un botón moderno
boton = ctk.CTkButton(app, text="Guardar Datos", command=accion_boton)
boton.pack(pady=10)

app.mainloop()



app = trabajador = ctk.CTk()
app.geometry("400x300")

# 1. Primero defines la función que quieres que pase al hacer clic
def cambiar_texto():
    mi_label.configure(text="¡Te pasaste a otra sección!")

# 2. Creas los elementos
mi_label = ctk.CTkLabel(app, text="Pantalla Principal", font=("Arial", 16))
mi_label.pack(pady=20)

# 3. Al botón le pasas la función en el parámetro 'command' (sin paréntesis)
btn_siguiente = ctk.CTkButton(app, text="Ir al siguiente paso", command=cambiar_texto)
btn_siguiente.pack(pady=10)

app.mainloop()