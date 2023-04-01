import traceback as tb

import colorama
import typing
import moderngl as mgl
import moderngl_window as mglw
import numpy as np


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

        self.quad_program = self.ctx.program(
            vertex_shader="""
            #version 330
            in vec3 in_position;
            in vec2 in_texcoord_0;
            out vec2 uv;
            void main() {
                gl_Position = vec4(in_position, 1.0);
                uv = in_texcoord_0;
            }
            """,
            fragment_shader="""
            #version 330
            uniform sampler2D texture0;
            out vec4 fragColor;
            in vec2 uv;
            void main() {
                fragColor = texture(texture0, uv);
            }
            """,
        )

        self.agent = self.ctx.compute_shader(get_shader("shaders/test.glsl"))
        self.agent['tex'] = 0
        # self.out_color = np.array(
        #     [100, 0, 0, 255] * self.window_size[0] * self.window_size[1],
        #     dtype=np.uint8
        # )
        self.out_texture = self.ctx.texture(
            self.window_size,
            4,
        )
        self.out_texture.filter = mgl.NEAREST, mgl.NEAREST
        self.quad_fs = mglw.geometry.quad_fs()

    def __del__(self):
        self.agent.release()

    def render(self, time, frametime):
        self.ctx.clear(0, 0, 0)

        # self.agent['width'].value = self.window_size[0]
        # self.agent['height'].value = self.window_size[1]
        try:
            self.agent['time'].value = time
        except Exception:
            self.agent['time'].value = 100
            pass
        w, h = self.out_texture.size
        # gw, gh = 16, 16
        # nx, ny, nz = int(w/gw), int(h/gh), 1
        self.out_texture.bind_to_image(0, read=False, write=True)
        self.agent.run(w, h, 1)

        # a = np.frombuffer(self.out_texture.read(), dtype=np.uint8)
        self.out_texture.use(location=0)
        self.quad_fs.render(self.quad_program)
        # ctx = self.ctx

        # self.ctx.clear(1.0, 1.0, 0.0, 0.0)


def window():
    MagmaWindow.run()


if __name__ == "__main__":
    window()
