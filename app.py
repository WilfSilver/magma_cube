import traceback as tb

import colorama
import math
import moderngl as mgl
import moderngl_window as mglw
import numpy as np

from random import randint, random


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
    path = './shaders/' + filename + '.glsl'
    with open(path, 'r', encoding="utf8") as shader_file:
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
            vertex_shader=get_shader('vertex'),
            fragment_shader=get_shader('fragment'),
        )

        self.agent = self.ctx.compute_shader(get_shader("agent"))
        self.agent['trail_map'] = 0
        self.agents_num = 400

        info = np.array([
            (randint(1, self.window_size[0] - 1),
             randint(1, self.window_size[1] - 1),
             2 * math.pi * random())
            for _ in range(self.agents_num)], np.dtype("i4, i4, f4"))
        print(info)
        print(len(info))
        self.agents_buffer = self.ctx.buffer(data=info)

        self.agent['num_agents'] = self.agents_num
        self.agent['move_speed'] = 100

        self.trail_map_img = self.ctx.texture(
            self.window_size,
            4,
        )
        self.trail_map_img.filter = mgl.NEAREST, mgl.NEAREST
        self.quad_fs = mglw.geometry.quad_fs()

    def __del__(self):
        self.agent.release()

    def render(self, time, frame_time):
        self.ctx.clear(0, 0, 0)

        try:
            self.agent['time'].value = time
        except Exception:
            pass
            # self.agent['time'].value = 100

        w, h = self.trail_map_img.size

        self.agent['width'] = w
        self.agent['height'] = h
        self.agent['delta_time'] = frame_time

        self.trail_map_img.bind_to_image(0, read=True, write=True)
        self.agents_buffer.bind_to_storage_buffer(0)
        self.agent.run(self.agents_num, 1, 1)

        self.trail_map_img.use(location=0)
        self.quad_fs.render(self.quad_program)


def window():
    MagmaWindow.run()


if __name__ == "__main__":
    window()
