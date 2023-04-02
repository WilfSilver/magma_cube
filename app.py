import traceback as tb

import colorama
import math
import moderngl as mgl
import moderngl_window as mglw
import numpy as np

from random import randint, random


from process_image import load_food

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
    # window_size = (1920, 1080)
    window_size = (1280, 720)
    aspect_ratio = 16 / 9
    title = "Magma Window"
    resizable = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.quad_program = self.ctx.program(
            vertex_shader=get_shader('vertex'),
            # fragment_shader=get_shader('fragment'),
            fragment_shader=get_shader('compositor-fragment'),
        )

        self.agent = self.ctx.compute_shader(get_shader("agent"))
        self.agent['trail_map'] = 0
        self.agents_num = 40000

        info = np.array([
            (0, 0, 0.0)
            for _ in range(self.agents_num)], np.dtype("i4, i4, f4"))
        self.debug_buffer = self.ctx.buffer(data=info)
        info = np.array([
            (tuple(randint(0, x) for x in self.window_size),
             2 * math.pi * random(), 1.0)
            for _ in range(self.agents_num)], np.dtype("(2)i4, f4, f4"))

        self.agents_buffer = self.ctx.buffer(data=info)

        a = np.frombuffer(self.agents_buffer.read(), dtype=np.dtype("i4, i4, f4, f4"))
        print(a)
        self.debug_print_count = 0
        self.agent['num_agents'] = self.agents_num
        self.agent['move_speed'] = 90

        self.agent['sensor_angle_spacing'] = math.pi / 12
        self.agent['turn_speed'] = 2 * math.pi * 4.5
        self.agent['sensor_offset_dist'] = 10.0
        self.agent['sensor_size'] = 5
        self.agent['enable_food'] = ENABLE_BIRB

        self.trail_maps = [
            self.ctx.texture(
                self.window_size,
                4,
            ) for _ in range(2)
        ]
        for map in self.trail_maps:
            map.filter = mgl.NEAREST, mgl.NEAREST
        self.curr_trail_map = 0

        self.blur_compute = self.ctx.compute_shader(get_shader('blur'))
        self.blur_compute['decay_rate'] = 1

        self.food_blur_compute = self.ctx.compute_shader(get_shader('food_blur'))
        self.food_blur_compute['decay_rate'] = 1

        self.quad_fs = mglw.geometry.quad_fs()

        # Load food!
        food = load_food("birb.png", MAX_PASSES=16)
        self.food_texture = self.ctx.texture(food.size, 3, food.tobytes("raw", "RGB"))
        self.food_texture.filter = mgl.BLEND, mgl.BLEND

        print("Finished setup")

    def __del__(self):
        self.agent.release()
        self.food_texture.release()

    def render(self, time, frame_time):
        self.ctx.clear(0, 0, 0)

        next_trail_map_index = 1 if self.curr_trail_map == 0 else 0

        trail_map = self.trail_maps[self.curr_trail_map]
        next_trail_map = self.trail_maps[next_trail_map_index]


        food_trail_map = self.food_trail_maps[self.curr_trail_map]
        next_food_trail_map = self.food_trail_maps[next_trail_map_index]

        w, h = trail_map.size

        self.agent['random_seed'] = random()
        self.agent['width'] = w
        self.agent['height'] = h
        self.agent['delta_time'] = frame_time

        trail_map.bind_to_image(0, read=True, write=True)

        self.food_texture.bind_to_image(1, read=True, write=True)
        food_trail_map.bind_to_image(2, read=True, write=False)

        self.agents_buffer.bind_to_storage_buffer(0)
        self.agent.run(self.agents_num, 1, 1)

        self.blur_compute['delta_time'] = frame_time
        next_trail_map.bind_to_image(1, read=False, write=True)
        self.blur_compute.run(w, h, 1)

        # self.food_blur_compute['delta_time'] = frame_time
        food_trail_map.bind_to_image(0, read=True, write=False)
        next_food_trail_map.bind_to_image(1, read=False, write=True)
        self.food_texture.bind_to_image(2, read=True, write=False)
        self.food_blur_compute.run(w, h, 1)
        next_food_trail_map.use(location=0)

        # next_trail_map.use(location=0)

        self.quad_program["textures"] = [0, 1]
        self.quad_program["enable_birb"] = True

        # print(dir(self.quad_program))
        self.quad_fs.render(self.quad_program)
        self.curr_trail_map = next_trail_map_index

def window():
    MagmaWindow.run()


if __name__ == "__main__":
    window()
