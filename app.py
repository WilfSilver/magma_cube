import traceback as tb

import colorama
import typing
import moderngl_window as mglw

if typing.TYPE_CHECKING:

def gl_version(version_string="4.4"):
    version = version_string.split(".")
    return tuple(int(i) for i in version)


def panic(msg: str) -> None:
    """
    panic! from Rust.
    """
    print(
          f"{colorama.Fore.RED}PANIC! {msg}\nStack Trace:{colorama.Fore.RESET}"
         )
    list(map(print, map(lambda s: f"\t{s}", tb.format_tb(None))))
    exit(7)


def get_shader(filename: str) -> str:
    with open(filename, 'r', encoding="utf8") as shader_file:
        return shader_file.read()


class MagmaWindow(mglw.WindowConfig):
    gl_version = gl_version(version_string="4.6")
    window_size = (1920, 1080)
    aspect_ratio = 16 / 9
    title = "Magma Window"
    resizable = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.agent = self.ctx.compute_shader(
            get_shader("compute.glsl")
        )

    def render(self, time, frametime):
        print("CALLED!")
        # ctx = self.ctx
        # self.ctx.clear(1.0, 1.0, 0.0, 0.0)


def window():
    MagmaWindow.run()


if __name__ == "__main__":
    window()
