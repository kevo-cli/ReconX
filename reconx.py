import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
import ttkbootstrap as ttk
from ttkbootstrap import Style
from tkinter import *
import nmap
import re
import time
import ipaddress
from openai import OpenAI
from PIL import Image, ImageTk, ImageSequence
import threading
from tkinterweb import HtmlFrame
import webbrowser
import os
from intro_fullscreen_vlc import intro_vlc_fullscreen

class AnimatedGIF(tk.Label):
    def __init__(self, master, path, delay=100):
        super().__init__(master)
        self.delay = delay
        self.frames = []

        im = Image.open(path)
        for frame in ImageSequence.Iterator(im):
            frame = frame.convert("RGBA")
            self.frames.append(ImageTk.PhotoImage(frame))

        self.idx = 0
        self.cancel = None
        self.play()

    def play(self):
        self.config(image=self.frames[self.idx])
        self.idx = (self.idx + 1) % len(self.frames)
        self.cancel = self.after(self.delay, self.play)

    def stop(self):
        if self.cancel:
            self.after_cancel(self.cancel)
            self.cancel = None


class AnimatedGIF2(tk.Label):
    def __init__(self, master, path, delay=100):
        super().__init__(master)
        self.delay = delay
        self.frames = []

        im = Image.open(path)
        for frame in ImageSequence.Iterator(im):
            frame = frame.convert("RGBA")
            self.frames.append(ImageTk.PhotoImage(frame))

        self.idx = 0
        self.cancel = None
        self.play()

    def play(self):
        self.config(image=self.frames[self.idx])
        self.idx = (self.idx + 1) % len(self.frames)
        self.cancel = self.after(self.delay, self.play)

    def stop(self):
        if self.cancel:
            self.after_cancel(self.cancel)
            self.cancel = None


promt_IA = """Eres un analista senior en ciberseguridad. Has recibido un resultado completo de un escaneo de puertos y vulnerabilidades.
Genera un INFORME HTML EXTENSO, DETALLADO y CLARO que incluya:

1. Resumen ejecutivo (2-3 párrafos):
   - Estado general de seguridad.
   - Puntos críticos detectados.
   - Riesgo global (bajo, medio, alto, crítico) con icono visual.

2. Top 3 riesgos principales:
   - Tabla con columnas: Riesgo, Descripción, Impacto, Recomendaciones inmediatas.
   - Ordenados por severidad y número de vulnerabilidades.
   - Usa iconos/emojis para representar el riesgo (✅, 🟠, ⚠️, 🔥).

3. Mapa de vulnerabilidades por puerto:
   - Tabla con columnas: Puerto, Servicio, Nº Vulnerabilidades, Nivel de riesgo (visual con emoji), CVEs destacados.
   - Colorear fondo según severidad:
     Verde (#22c55e) → Bajo
     Amarillo (#eab308) → Medio
     Naranja (#f97316) → Alto
     Rojo (#dc2626) → Crítico

4. Recomendaciones detalladas:
   - Tabla con acciones prácticas: cerrar puertos, actualizar versiones, migrar protocolos, implementar firewalls, reforzar autenticación.
   - Incluir prioridad (Alta, Media, Baja) y tiempo estimado de aplicación.

5. Análisis técnico profundo:
   - Explicar patrones detectados: servicios inseguros, versiones obsoletas, protocolos inseguros, configuraciones expuestas.
   - Relacionar puertos con potenciales vectores de ataque.
   - Señalar vulnerabilidades encadenables.

6. Glosario educativo (si es necesario):
   - Definir brevemente conceptos técnicos encontrados: CVE, exploit, puerto, servicio, protocolo.

Requisitos de presentación:
- No repetir el input original.
- Texto claro para técnicos y directivos.
- Usar colores HTML inline y emojis para resaltar riesgos, advertencias y buenas prácticas.
- HTML moderno, legible y adaptado para HtmlFrame (sin dependencias externas).
- Secciones separadas con etiquetas h2 y tablas con border=0 y cellpadding=6, con colores de fondo.
- Incluir hr entre secciones principales.

Entrega únicamente el HTML.
"""

root = ttk.Window(themename="cyborg")
root.title("ReconX")
root.configure(background="#000000")
root.resizable(False, False)
#root.geometry("1920x1080")
root.iconbitmap("logo.ico")
root.withdraw()  # ⟵ ocultar la app hasta que el login pase

#Estilos
style = Style("cyborg")  # base theme

# Crear un nuevo style para Button
style.configure(
    "Custom.TButton",
    foreground="#f8fafc",   # Texto blanco casi puro
    background="#212529",   # Azul más sobrio
    bordercolor="#ffffff",
    focusthickness=3,
    focuscolor="#3b82f6",
    font=("Segoe UI", 10, "bold")
)

# Declarando algunas variables :) ----------------------------------------------------------
puertos_a_escanear = ('10 Más Comunes', '50 Más Comunes',
                      '100 Más Comunes', '1,000 Más Comunes', 'Todos Los Puertos')
portscombo_string = tk.StringVar(value=puertos_a_escanear[2])

tipo_de_escaneo_lista = ('Silencioso', 'Moderado', 'Agresivo')
scantype_string = tk.StringVar(value=tipo_de_escaneo_lista[1])

# Frames---------------------------------------
main_frame = ttk.Frame(root, width=1920, height=1080)



# ____________________________________Pantalla principal________________________________________
def main_page():
    root.state("zoomed")

    def extraer_cves(vulnerabilidades):
        # Utilizamos una expresión regular para encontrar patrones de CVE
        cves_encontrados = re.findall(r'CVE-\d{4}-\d{4,7}', vulnerabilidades)
        
        cves_unicos = list(set(cves_encontrados))
        
        # Devolvemos una cadena que contiene los CVEs encontrados
        return ', '.join(cves_unicos)

    def resumir_vulnerabilidades(vulnerabilidades):
        # Extraemos los CVEs de las vulnerabilidades
        cves = extraer_cves(vulnerabilidades)
        
        return cves
    
    def aplicar_estilo_titulo(widget, text):
        widget.tag_configure("tituloVulners", font=("Arial", 14, "bold"))
        widget.insert(tk.END, text, "tituloVulners")

    def aplicar_estilo_columna(widget, text):
        widget.tag_configure("columnaVulners", font=("Helvetica", 10))
        widget.insert(tk.END, text, "columnaVulners")

    def escaneo_con_carga():
        # Crear y mostrar animación
        loading_anim = AnimatedGIF(main_frame, "loading.gif", delay=16)
        loading_anim.place(x=0, y=0)  # Ajusta la posición


        def tarea_escaneo():

            inicio_scan = time.time()
            escaneo()  # Tu función pesada de escaneo
            fin = time.time()
            tiempo_total = fin - inicio_scan

                # Una vez terminado, quitar animación (en el hilo principal)
            def quitar_animacion():
                    loading_anim.stop()
                    loading_anim.destroy()
                    info_results.config(state=tk.NORMAL)
                    info_results.insert(tk.END, "\nTiempo total del escaneo: {:.2f} segundos\n".format(tiempo_total))
                    info_results.config(state=tk.DISABLED)
                
            root.after(0, quitar_animacion)  # Ejecutar en hilo principal

        # Ejecutar escaneo en un hilo para no bloquear UI
        hilo = threading.Thread(target=tarea_escaneo, daemon=True)
        hilo.start()
        
    def scan_click():

        try:
            ipaddress.IPv4Address(ip.get())
        except ipaddress.AddressValueError:
            messagebox.showerror("Error", "La dirección IP ingresada no es válida.")
            return
        
        escaneo_con_carga()

    def escaneo():
        resultados.config(state=tk.NORMAL)
        vuln_results.config(state=tk.NORMAL)
        info_results.config(state=tk.NORMAL)
        
        def IA_con_carga():
            # 0) Capturar el texto más reciente ANTES de tocar la UI
            root.update_idletasks()
            texto_scan = obtener_resultado_completo()
            payload = f"{texto_scan}\n\n{promt_IA}"

            # 1) Ocultar la vista de escaneo y crear la vista de IA
            #    (opcional ocultar; si no, la de IA simplemente la cubre)
            # main_frame.place_forget()

            ia_view = ttk.Frame(root)  # contenedor exclusivo para la vista IA
            ia_view.place(x=0, y=0, width=root.winfo_width(), height=root.winfo_height())

            # Botón volver (destruye la vista IA y vuelve a mostrar el escaneo)
            def volver_al_escaneo():
                ia_view.destroy()
                # Si ocultaste el main_frame con place_forget(), vuelve a colocarlo:
                # main_frame.place(x=0, y=0)

            back_btn = ttk.Button(
                ia_view,
                text="← Volver al escaneo",
                style="Custom.TButton",
                command=volver_al_escaneo
            )
            back_btn.place(x=10, y=10, height=40)

            # 2) Animación de carga dentro de la vista IA
            loading_anim = AnimatedGIF(ia_view, "loading_ia.gif", delay=16)
            loading_anim.place(relx=0.5, rely=0.5, anchor="center")

            # 3) Trabajo en segundo plano (llamada a la IA)
            def tarea_IA(payload_local):
                try:
                    client = OpenAI(api_key="")  # mejor usar variable de entorno
                    completion = client.chat.completions.create(
                        model="gpt-4.1-nano-2025-04-14",
                        store=True,
                        messages=[{"role": "user", "content": payload_local}]
                    )
                    respuesta_html = completion.choices[0].message.content
                except Exception as e:
                    respuesta_html = f"<div style='color:#f87171;'>Error consultando IA: {e}</div>"

                # 4) Pintar el resultado en la vista IA
                def mostrar_respuesta():
                    loading_anim.stop()
                    loading_anim.destroy()

                    # HtmlFrame dentro de ia_view (y no en root) para que “Volver” funcione
                    IA_answer = HtmlFrame(
                        ia_view,
                        horizontal_scrollbar="auto",
                        vertical_scrollbar="auto",
                        messages_enabled=False
                    )
                    # deja un margen superior por el botón Volver
                    IA_answer.place(x=10, y=60, width=root.winfo_width()-20, height=root.winfo_height()-70)
                    IA_answer.load_html(respuesta_html)

                root.after(0, mostrar_respuesta)

            threading.Thread(target=tarea_IA, args=(payload,), daemon=True).start()

        def obtener_resultado_completo():
            puertos = resultados.get("1.0", "end").strip()
            vulnerabilidades = vuln_results.get("1.0", "end").strip()
            info_general = info_results.get("1.0", "end").strip()

            resultado = (
                "=== PUERTOS & SERVICIOS ===\n"
                f"{puertos}\n\n"
                "=== VULNERABILIDADES ===\n"
                f"{vulnerabilidades}\n\n"
                "=== INFORMACIÓN GENERAL ===\n"
                f"{info_general}"
            )
            return resultado

        def copiar_resultado():
            resultado = obtener_resultado_completo()
            root.clipboard_clear()
            root.clipboard_append(resultado)
            root.update()


        def exportar_resultado_txt():
            resultado = obtener_resultado_completo()

            archivo = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text Files", "*.txt")],
                title="Guardar resultado como..."
            )

            if archivo:
                with open(archivo, "w", encoding="utf-8") as f:
                    f.write(resultado)

        count_open_ports = 0
        count_cve_vulnerabilities = 0

        # ----- Puertos -----
        seleccion = opciones_argumentos.get()
        if seleccion == '10 Más Comunes':
            ports_args = "--top-ports 10 --script vulners -n -sV -Pn"
            cantidad_puertos = "10"
        elif seleccion == '50 Más Comunes':
            ports_args = "--top-ports 50 --script vulners -n -sV -Pn"
            cantidad_puertos = "50"
        elif seleccion == '100 Más Comunes':
            ports_args = "--top-ports 100 --script vulners -n -sV -Pn"
            cantidad_puertos = "100"
        elif seleccion == '1,000 Más Comunes':
            ports_args = "--top-ports 1000 --script vulners -n -sV -Pn"
            cantidad_puertos = "1,000"
        else:  # 'Todos Los Puertos'
            ports_args = "-p- --script vulners -n -sV -Pn"
            cantidad_puertos = "65,536"

        # ----- Protocolo (TCP/UDP) -----
        modo = velocidad_seleccionada.get()  # '1' | '2' | '3'
        if modo == "1":
            proto_args = "-sT"
            protocolo_seleccionado = "TCP"
        elif modo == "2":
            proto_args = "-sU"
            protocolo_seleccionado = "UDP"
        else:  # "3"
            proto_args = "-sS -sU"
            protocolo_seleccionado = "TCP & UDP"

        # ----- Perfil de velocidad (T1..T5) -----
        perfil = scantype_string.get()  # 'Silencioso' | 'Moderado' | 'Agresivo'
        if perfil == "Silencioso":
            speed_args = "-T1"
        elif perfil == "Moderado":
            speed_args = "-T3"
        else:
            speed_args = "-T5"

        # ----- Componer argumentos finales -----
        argumentos = f"{proto_args} {speed_args} {ports_args}"


        host = ip.get()
      
        nm = nmap.PortScanner()
        results = nm.scan(host, arguments=argumentos)
        
        # Limpiar el widget de texto antes de mostrar nuevos resultados
        resultados.delete('1.0', tk.END)
        vuln_results.delete('1.0', tk.END)
        info_results.delete('1.0', tk.END)

        # Establecer estilos para las columnas
        resultados.tag_configure("titulo", font=("Arial", 20, "bold"))
        resultados.tag_configure("columna", font=("Arial", 12))

        # vuln_results.tag_configure("columna", font=("Arial", 12))

        # Escribir los encabezados de las columnas
        resultados.insert(tk.END, "{:<15} {:<20} {:<20} {:<20}\n".format(
            "Puerto", "Estado", "Servicio", "Versión"), "titulo")

        # Iterar a través de los protocolos escaneados (generalmente TCP)
        for proto in nm[host].all_protocols():
            # Obtener la lista de puertos y ordenarla
            lport = list(nm[host][proto].keys())
            lport.sort()

            # Iterar a través de los puertos y mostrar información
            for port in lport:
                puerto = port
                estado = nm[host][proto][port]['state']

                # Verificar si se ha detectado información de versión
                if 'version' in nm[host][proto][port]:
                    servicio = nm[host][proto][port]['name']
                    version = nm[host][proto][port]['version']
                else:
                    servicio = nm[host][proto][port]['name']
                    version = "No se encontró información de versión"

                    # Obtener las vulnerabilidades encontradas por el script vulners
                vulnerabilities = "No se encontraron vulnerabilidades"
                if 'script' in nm[host][proto][port]:
                    if 'vulners' in nm[host][proto][port]['script']:
                        vulnerabilities = resumir_vulnerabilidades(nm[host][proto][port]['script']['vulners'])
                        count_cve_vulnerabilities += len(re.findall(r'\bCVE-\d+-\d+\b', vulnerabilities))
                  
                # Escribir la información en el widget de texto
                resultados.insert(tk.END, "{:<35} {:<40} {:<35} {:<20}\n".format(
                    puerto, estado, servicio, version), "columna")

                aplicar_estilo_titulo(vuln_results, "Puerto {}: ".format(port))
                aplicar_estilo_columna(vuln_results, "{}\n".format(vulnerabilities))
                
                if estado.lower() == 'open':
                    count_open_ports += 1

                
        info_results.insert(tk.END, "Dirección IP escaneada: {}\n".format(host))
        info_results.insert(tk.END, "\nProtocolo: {}\n".format(protocolo_seleccionado))
        info_results.insert(tk.END, "\nCantidad de puertos escaneados: {}\n".format(cantidad_puertos))
        info_results.insert(tk.END, "\nPuertos abiertos: {}\n".format(count_open_ports))
        info_results.insert(tk.END, "\nVulnerabilidades encontradas: {}\n".format(count_cve_vulnerabilities))

        

        # Agregar espacio en blanco al final para llenar el frame
        resultados.insert(tk.END, "\n" * 10)
        resultados.config(state=tk.DISABLED)
        vuln_results.config(state=tk.DISABLED)
        info_results.config(state=tk.DISABLED)


        copy_scan = ttk.Button(main_frame, text="COPIAR RESULTADOS",
                                style="Custom.TButton", command=copiar_resultado)
        
        AI_button = ttk.Button(main_frame, text="ANALIZAR RESULTADOS CON IA",
                                style="Custom.TButton", command=IA_con_carga)
        
        export_results = ttk.Button(main_frame, text="EXPORTAR RESULTADOS",
                                style="Custom.TButton", command=exportar_resultado_txt)
        
        copy_scan.place(x=1085, y=40, height=40)
        AI_button.place(x=1310, y=40, height=40)
        export_results.place(x=1620, y=40, height=40)


    def limpiar_toda_pantalla():
        for widget in main_frame.winfo_children():
            widget.destroy()



    # ------------------------------------------------------------------
    #                          Label Frames                            #
    # ------------------------------------------------------------------

    hacer_escaneo = ttk.LabelFrame(
        main_frame, text="Realizar Escaneo", style="primary")

    ip_label = ttk.Label(
        hacer_escaneo, text="Ingrese la IP objetivo", font="Arial 14 bold")

    start_scan = ttk.Button(hacer_escaneo, text="ESCANEAR",
                            style="Custom.TButton", command=scan_click)

    ip = ttk.Entry(hacer_escaneo, font="Arial 18", width=14, style="blue")

    hacer_escaneo.place(x=10, y=10, width=560, height=120)

    ip_label.grid(row=0, column=0, padx=1, pady=1)
    ip.grid(row=1, column=0, padx=7, pady=3)
    start_scan.place(x=270, y=40, height=40)
    
    # Combo Boxes Y Radio Buttons----------------------------------------------------------------------------------------------------

    # Label correspondiente a la ComboBox de Puertos A Escanear------------------
    opciones_argumentos_label = ttk.Label(
        main_frame, text="Puertos A Escanear", font="Arial 12 bold", foreground="light blue")
    opciones_argumentos_label.place(x=609, y=11)

    # ComboBox Puertos A Escanear
    opciones_argumentos = ttk.Combobox(main_frame, style="primary", textvariable=portscombo_string)
    opciones_argumentos.config(font="Arial 14", width=17,
                               values=puertos_a_escanear, state="readonly")
    opciones_argumentos.place(x=610, y=40)

    # Label correspondiente a la ComboBox de tipos de escaneo-------------------
    tipos_de_escaneo_label = ttk.Label(
        main_frame, text="Tipo De Escaneo", font="Arial 12 bold", foreground="light blue")
    tipos_de_escaneo_label.place(x=870, y=11)

    # ComboBox Tipos de Escaneo
    tipo_de_escaneo = ttk.Combobox(main_frame, style="primary")
    tipo_de_escaneo.config(font="Arial 14", width=12, values=tipo_de_escaneo_lista, 
                           state="readonly", textvariable=scantype_string)
    tipo_de_escaneo.place(x=875, y=40)

    # Velocidad Label ---------------------------------------------
    velocidad_label = ttk.Label(
        main_frame, text="Protocolo a escanear:", font="Arial 12 bold", foreground="light blue")
    velocidad_label.place(x=580, y=101.7)

    # Protocolo Buttons ----------------------------------------
    
    velocidad_seleccionada = tk.StringVar(value="1")
    
    radiobutton = ttk.Radiobutton(main_frame, text="TCP", style="primary", value=1, variable=velocidad_seleccionada)
    radiobutton.place(x=810, y=107)

    radiobutton2 = ttk.Radiobutton(main_frame, text="UDP", style="primary", value=2, variable=velocidad_seleccionada)
    radiobutton2.place(x=885, y=107)

    radiobutton3 = ttk.Radiobutton(main_frame, text="TCP & UDP", style="primary", value=3, variable=velocidad_seleccionada)
    radiobutton3.place(x=960, y=107)

    # ------------------------------------------------------------------------------------------------------
    #                           Área de ports & services
    portsandservices = ttk.LabelFrame(
        main_frame, text="Puertos & Servicios", style="primary")
    portsandservices.place(x=10, y=130, width=1055, height=835)

    resultados = tk.Text(portsandservices, wrap=tk.WORD,
                         height=40, width=129, state=tk.DISABLED)
    resultados.configure(bg="#000000", highlightbackground="#000000", highlightthickness=0)
    resultados.edit_modified(False)
    resultados.place(x=2.5, y=0)
    # --------------------------------------------------------------------------------------------
    #                            Área de vulnerabilidades
    vulnerabilidades = ttk.LabelFrame(
        main_frame, text="Vulnerabilidades", style="primary")
    vulnerabilidades.place(x=1085, y=130, width=820, height=470)

    vuln_results = tk.Text(vulnerabilidades, wrap=tk.WORD, height=21, width=99)
    vuln_results.configure(bg="#000000", highlightbackground="#000000", highlightthickness=0, state=tk.DISABLED)
    vuln_results.place(x=3.5, y=0)

    # --------------------------------------------------------------------------------------------
    #                            Área de información general
    generalinfo = ttk.LabelFrame(
        main_frame, text="Información General", style="primary")
    generalinfo.place(x=1085, y=613, width=820, height=352)

    info_results = tk.Text(generalinfo, wrap=tk.WORD, height=11, width=61)
    info_results.configure(bg="#000000", highlightbackground="#000000", highlightthickness=0, state=tk.DISABLED, font="Arial 14")
    info_results.place(x=5, y=5)

    main_frame.place(x=0, y=0)
    

# --- LOGIN ---------------------------------------------------------
def show_login(before_root: ttk.Window, on_success):
    """
    Muestra un login modal. Al validar, cierra el login,
    'desoculta' before_root y llama on_success().
    """
    # Ventana de login (hija, modal)
    login_page = tk.Toplevel(before_root)
    login_page.title("ReconX – Iniciar sesión")
    try:
        login_page.iconbitmap("logo.ico")
    except Exception:
        pass
    login_page.geometry("1400x850")
    login_page.resizable(False, False)
    login_page.configure(bg="#1c1c1c")
    login_page.transient(before_root)
    login_page.grab_set()  # modal

    # Fondo
    try:
        bg_image = Image.open("login.png")
        bg_photo = ImageTk.PhotoImage(bg_image)
        bg_label = tk.Label(login_page, image=bg_photo, borderwidth=0)
        bg_label.image = bg_photo
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
    except Exception:
        pass  # si no hay imagen, sigue sin fondo

    # Widgets
    ttk.Label(login_page, text="Correo", font=("Arial", 11), background="#212529", foreground="#f8fafc").place(x=175, y=270)
    correo = ttk.Entry(login_page, style="primary", font=("Arial", 12))
    correo.place(x=175, y=300, width=250, height=40)

    ttk.Label(login_page, text="Contraseña", font=("Arial", 11), background="#212529", foreground="#f8fafc").place(x=175, y=370)
    contraseña_var = tk.StringVar()
    contraseña = ttk.Entry(login_page, style="primary", font=("Arial", 12), textvariable=contraseña_var, show="*")
    contraseña.place(x=175, y=400, width=250, height=40)

    # Error bonito
    def custom_error(title, message):
        error_win = tk.Toplevel(login_page)
        error_win.title(title)
        try:
            error_win.iconbitmap("logo.ico")
        except Exception:
            pass
        error_win.geometry("410x200")
        error_win.resizable(False, False)
        error_win.configure(bg="#1c1c1c")

        ttk.Label(error_win, text=title, font=("Arial", 16, "bold"), foreground="red", background="#1c1c1c").pack(pady=10)
        ttk.Label(error_win, text=message, font=("Arial", 12), wraplength=350, background="#1c1c1c", foreground="white").pack(pady=5)
        ttk.Button(error_win, text="Aceptar", command=error_win.destroy, style="danger").pack(pady=15)

        # centrar el popup sobre el login
        error_win.update_idletasks()
        x = login_page.winfo_x() + (login_page.winfo_width() - error_win.winfo_width()) // 2
        y = login_page.winfo_y() + (login_page.winfo_height() - error_win.winfo_height()) // 2
        error_win.geometry(f"+{x}+{y}")

    # Lógica de login (simple para proyecto escolar)
    PASSWORD = os.environ.get("RECONX_PASSWORD", "admin")  # puedes usar variable de entorno
    def do_login(_evt=None):
        if contraseña_var.get() == PASSWORD:
            login_page.grab_release()
            login_page.destroy()
            before_root.deiconify()  # mostrar app
            on_success()             # arrancar intro + main
        else:
            custom_error("Error 401 – Unauthorized", "Credenciales incorrectas. Por favor, verifica tu nombre de usuario y contraseña.")
            contraseña_var.set("")
            contraseña.focus_set()

    ttk.Button(login_page, text="Iniciar Sesión", command=do_login, style="primary").place(x=190, y=500, width=200, height=45)

    ttk.Label(login_page, text="¿Aún no tienes cuenta?", font=("Arial", 10), background="#212529", foreground="#378dfc").place(x=200, y=770)
    ttk.Button(login_page, text="Haz clic aquí para crearla", style="dark", command=lambda: webbrowser.open("https://recon-x-kohl.vercel.app/")).place(x=190, y=790)

    # UX: Enter envía el login
    contraseña.bind("<Return>", do_login)

    # Si cierran el login, cierra todo
    def on_close():
        before_root.destroy()
    login_page.protocol("WM_DELETE_WINDOW", on_close)

    # Centrar login en pantalla
    login_page.update_idletasks()
    w, h = map(int, login_page.geometry().split("+")[0].split("x"))
    sw, sh = login_page.winfo_screenwidth(), login_page.winfo_screenheight()
    login_page.geometry(f"{w}x{h}+{(sw - w)//2}+{(sh - h)//2}")

# --- ARRANQUE CON LOGIN ------------------------------------------
def start_after_login():
    # Cuando el login valida, ejecutamos tu intro y luego la página principal
    intro_vlc_fullscreen(root, "intro_long.mp4", on_done=main_page, mode="stretch")

show_login(root, start_after_login)

# Importante: el mainloop es el de 'root' como siempre
root.mainloop()