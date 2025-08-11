"""
Intro de video a pantalla completa (fluido) para Tkinter usando VLC.

Requisitos:
    pip install python-vlc
    Tener VLC instalado en el sistema (o libvlc disponible en PATH).

Integración rápida con tu app:
    1) Importa intro_vlc_fullscreen y llama intro_vlc_fullscreen(root,
       "/ruta/al/video.mp4", on_done=main_page) en lugar de main_page() al inicio.
    2) El usuario hace clic (o presiona Enter/Espacio) para continuar;
       también puedes mostrar un botón superpuesto si quieres.
"""

import sys
import platform
import tkinter as tk
import ttkbootstrap as ttk

try:
    import vlc  # python-vlc
except Exception as e:
    raise SystemExit(
        "Falta python-vlc. Instálalo con: pip install python-vlc\n"
        f"Detalle: {e}"
    )


def _set_video_handle(player, widget_id):
    """Asigna el handle de la superficie de video según el OS."""
    osname = platform.system()
    if osname == "Windows":
        player.set_hwnd(widget_id)
    elif osname == "Darwin":  # macOS
        player.set_nsobject(widget_id)
    else:  # Linux / X11
        player.set_xwindow(widget_id)


def intro_vlc_fullscreen(root: ttk.Window, video_path: str, on_done=None, mode: str = "stretch"):
    """Muestra un video a pantalla completa con VLC y continúa con on_done() al salir."""
    intro = tk.Toplevel(root)
    intro.attributes("-fullscreen", True)  # no uses overrideredirect con fullscreen

    container = tk.Frame(intro, bg="#000000")
    container.pack(fill="both", expand=True)

    video_surface = tk.Canvas(container, highlightthickness=0, bg="#000000")
    video_surface.pack(fill="both", expand=True)

    instance = vlc.Instance([
        "--vout=win32",
        "--avcodec-hw=none",
        "--no-video-title-show",
        "--file-caching=200",
        "--drop-late-frames",
        "--skip-frames",
        "--verbose=0",
        "--quiet"
    ])


    player = instance.media_player_new()
    media = instance.media_new(video_path)
    # Loop infinito del mismo archivo + desactivar HW por si la instancia no lo aplica
    media.add_option("input-repeat=-1")
    media.add_option(":avcodec-hw=none")
    media.add_option(":no-video-title-show")
    player.set_media(media)

    intro.update_idletasks()
    _set_video_handle(player, video_surface.winfo_id())

    # Botón para continuar
    btn = ttk.Button(intro, text="COMENZAR", style="Custom.TButton")
    btn.place(relx=0.5, rely=0.82, anchor="center", width=180, height=42)

    def _finish():
        try:
            player.stop()
        except Exception:
            pass
        try:
            intro.destroy()
        except Exception:
            pass
        if callable(on_done):
            on_done()

    def _on_key(evt):
        if evt.keysym in ("Return", "space", "Escape"):
            _finish()

    def _on_click(evt):
        _finish()

    intro.bind("<Key>", _on_key)
    intro.bind("<Button-1>", _on_click)
    btn.configure(command=_finish)

    # Reproducir
    player.play()

    # Asegurar inicio y mantener loop si tu VLC no respeta input-repeat
    def _ensure_playing():
        st = player.get_state()
        if st in (vlc.State.NothingSpecial, vlc.State.Stopped, vlc.State.Error):
            player.play()
        elif st == vlc.State.Ended:
            player.stop()
            player.play()
        intro.after(300, _ensure_playing)

    intro.after(150, _ensure_playing)


# --- Ejemplo de uso directo ---
if __name__ == "__main__":
    app = ttk.Window(themename="cyborg")
    app.withdraw()  # ocultamos raíz hasta que termine la intro

    def demo_main():
        app.deiconify()
        app.state("zoomed")
        app.title("Pantalla principal (demo)")
        frm = ttk.Frame(app)
        frm.pack(fill="both", expand=True)
        ttk.Label(frm, text="Aquí iría tu main_page()", font=("Segoe UI", 24, "bold")).pack(pady=40)

    intro_vlc_fullscreen(app, "intro_long.mp4", on_done=demo_main, mode="stretch")
    app.mainloop()
