import traceback as tb

import colorama
import typing
import math
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
        self.agents_num = 100
        info = np.array([500 for _ in range(2 * self.agents_num)], np.int32)
        # info = np.random.uniform(0.0, self.window_size[1], 2 * self.agents_num).astype(np.int64)
        print(info)
        print(len(info))
        self.agents_coords_buffer = self.ctx.buffer(data=info)
        info = np.array([2 * x * math.pi / self.agents_num for x in range(self.agents_num)], np.float32)
        self.agents_dirs_buffer = self.ctx.buffer(data=info)
        print(info)
        self.agent['num_agents'] = self.agents_num
        self.agent['move_speed'] = 100
        # self.out_color = np.array(
        #     [100, 0, 0, 255] * self.window_size[0] * self.window_size[1],
        #     dtype=np.uint8
        # )
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

        # self.agent['width'].value = self.window_size[0]
        # self.agent['height'].value = self.window_size[1]
        try:
            self.agent['time'].value = time
        except Exception:
            self.agent['time'].value = 100
            pass

        w, h = self.trail_map_img.size

        self.agent['width'] = w
        self.agent['height'] = h
        self.agent['delta_time'] = frame_time

        # gw, gh = 16, 16
        # nx, ny, nz = int(w/gw), int(h/gh), 1
        self.trail_map_img.bind_to_image(0, read=True, write=True)
        self.agents_coords_buffer.bind_to_storage_buffer(0)
        self.agents_dirs_buffer.bind_to_storage_buffer(1)
        self.agent.run(self.agents_num, 1, 1)

        output = np.frombuffer(self.agents_coords_buffer.read(), dtype=np.int32)
        # print(output)

        # a = np.frombuffer(self.trail_map_img.read(), dtype=np.uint8)
        self.trail_map_img.use(location=0)
        self.quad_fs.render(self.quad_program)
        # ctx = self.ctx

        # self.ctx.clear(1.0, 1.0, 0.0, 0.0)


def window():
    MagmaWindow.run()


if __name__ == "__main__":
    window()
