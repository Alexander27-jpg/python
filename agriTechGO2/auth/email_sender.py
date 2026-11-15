import resend

# 👇 PEGA AQUÍ LA CLAVE QUE TE DIO RESEND (la que empieza por re_...)
resend.api_key = "re_6Cf6CmHV_3RU3YhRDpnQ3oePYRdzSmoJ1"


def enviar_correo_bienvenida(correo_destino, nombre_usuario, roles_usuario):
  try:
    html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #f4f6f4; margin: 0; padding: 20px;">
            <div style="max-width: 600px; margin: auto; background: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
                <div style="background-color: #1b4332; padding: 30px; text-align: center;">
                    <h1 style="color: #ffffff; margin: 0; font-size: 26px;">AgriTechGO</h1>
                    <p style="color: #b7e4c7; margin: 5px 0 0 0; font-size: 14px;">Conectando el agro sin intermediarios</p>
                </div>
                <div style="padding: 30px; color: #333333;">
                    <h2 style="color: #1b4332; margin-top: 0;">¡Hola, {nombre_usuario}! 👋</h2>
                    <p>Nos alegra muchísimo que formes parte de nuestra comunidad. Tu cuenta ha sido creada exitosamente en <b>AgriTechGO</b>.</p>
                    <p>Roles con los que te has vinculado a la plataforma:</p>
                    <div style="background-color: #e9f5ed; border-left: 4px solid #52b788; padding: 12px 15px; margin: 20px 0; border-radius: 4px;">
                        <span style="color: #2d6a4f; font-weight: bold; font-size: 16px;">🌾 {roles_usuario}</span>
                    </div>
                    <p>Ya puedes iniciar sesión en la plataforma y empezar a explorar todas las herramientas diseñadas para impulsar el agro.</p>
                </div>
            </div>
        </body>
        </html>
        """

    params = {
        "from": "AgriTechGO <onboarding@resend.dev>",
        "to": [correo_destino],
        "subject": "¡Bienvenido a AgriTechGO! 🚀 Cultivando el Futuro",
        "html": html_content,
    }

    response = resend.Emails.send(params)
    print("Correo enviado con éxito:", response)
    return True

  except Exception as e:
    print(f"Error al enviar el correo con Resend: {e}")
    return False