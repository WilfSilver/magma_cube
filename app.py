import traceback as tb

import colorama
import math
import moderngl as mgl
import moderngl_window as mglw
import numpy as np

from random import randint, random


from process_image import load_food

opts = {}


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
        self.agents_num = opts['num_agents']

        info = np.array([
            (0, 0, 0.0)
            for _ in range(self.agents_num)], np.dtype("i4, i4, f4"))
        self.debug_buffer = self.ctx.buffer(data=info)
        if opts['internal']['spawn']:
            points = []
            for s in range(opts['internal']['species']):
                print(s)
                centre = tuple(randint(200, x - 200) for x in self.window_size)
                radius = randint(100, 150)
                count = 0
                while count < self.agents_num / opts['internal']['species']:
                    x, y = randint(0, self.window_size[0]), randint(0, self.window_size[1])
                    if (((x - centre[0]) ** 2) + ((y - centre[1]) ** 2)) ** 0.5 >= 1.25*radius and (((x - centre[0]) ** 2) + ((y - centre[1]) ** 2)) ** 0.5 <= 1.5*radius:
                        points.append(((x, y), 2 * math.pi * random(), s))
                        count += 1

            info = np.array(points, np.dtype("(2)i4, f4, u4"))
        else:
            info = np.array([
                (tuple(randint(opts['internal']['boundry'], x - opts['internal']['boundry']) for x in self.window_size),
                2 * math.pi * random(), randint(0, opts['internal']['species'] - 1))
                for _ in range(self.agents_num)], np.dtype("(2)i4, f4, u4"))

        self.agents_buffer = self.ctx.buffer(data=info)

        a = np.frombuffer(self.agents_buffer.read(), dtype=np.dtype("i4, i4, f4, u4"))
        print(a)
        self.debug_print_count = 0

        for key, v in opts.items():
            if key == 'internal':
                continue
            self.agent[key] = v

        self.trail_maps = [
            self.ctx.texture(
                self.window_size,
                4,
            ) for _ in range(2)
        ]
        for m in self.trail_maps:
            m.filter = mgl.NEAREST, mgl.NEAREST
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

        w, h = trail_map.size

        self.agent['random_seed'] = random()
        self.agent['width'] = w
        self.agent['height'] = h
        self.agent['delta_time'] = frame_time

        trail_map.bind_to_image(0, read=True, write=True)

        self.agents_buffer.bind_to_storage_buffer(0)
        self.agent.run(self.agents_num, 1, 1)

        self.blur_compute['delta_time'] = frame_time
        next_trail_map.bind_to_image(1, read=False, write=True)
        self.blur_compute.run(w, h, 1)
        next_trail_map.use(0)

        self.quad_program["textures"] = [0, 1]
        self.quad_program["enable_birb"] = True

        # print(dir(self.quad_program))
        self.quad_fs.render(self.quad_program)
        self.curr_trail_map = next_trail_map_index

def window():
    MagmaWindow.run()


if __name__ == "__main__":
    presets = [
        {
            'num_agents': 40000,
            'move_speed': 70,
            'sensor_angle_spacing': math.pi / 9,
            'turn_speed': 2 * math.pi * 20,
            'sensor_offset_dist': 15.0,
            'sensor_size': 5,
            'repel': True,
            'internal': {
                'boundry': 0,
                'species': 3,
                'spawn': False,
            }
        },
        {
            'num_agents': 40000,
            'move_speed': 90,
            'sensor_angle_spacing': math.pi / 9,
            'turn_speed': 2 * math.pi * 60,
            'sensor_offset_dist': 15.0,
            'sensor_size': 5,
            'repel': False,
            'internal': {
                'boundry': 200,
                'species': 3,
                'spawn': False,
            }
        },
        {
            'num_agents': 20000,
            'move_speed': 65,
            'sensor_angle_spacing': math.pi / 9,
            'turn_speed': 2 * math.pi * 20,
            'sensor_offset_dist': 15.0,
            'sensor_size': 5,
            'repel': True,
            'internal': {
                'boundry': 200,
                'species': 3,
                'spawn': False,
            }
        },
        {
            'num_agents': 40000,
            'move_speed': 65,
            'sensor_angle_spacing': math.pi / 9,
            'turn_speed': 2 * math.pi * 10,
            'sensor_offset_dist': 15.0,
            'sensor_size': 5,
            'repel': True,
            'internal': {
                'boundry': 200,
                'species': 2,
                'spawn': False,
            }
        },
        {
            'num_agents': 40000,
            'move_speed': 70,
            'sensor_angle_spacing': math.pi / 9,
            'turn_speed': 2 * math.pi * 20,
            'sensor_offset_dist': 15.0,
            'sensor_size': 5,
            'repel': True,
            'internal': {
                'boundry': 0,
                'species': 2,
                'spawn': True,
            }
        },
        {
            'num_agents': 40000,
            'move_speed': 70,
            'sensor_angle_spacing': math.pi / 9,
            'turn_speed': 2 * math.pi * 20,
            'sensor_offset_dist': 15.0,
            'sensor_size': 5,
            'repel': True,
            'internal': {
                'boundry': 0,
                'species': 3,
                'spawn': True,
            }
        },
    ]
    p = int(input("Preset: "))
    opts = presets[p]
    window()
