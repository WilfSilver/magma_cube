#version 460

#define PI 3.14159265358979323846
#define PHI 1.61803398874989484820459

struct Agent {
    ivec2 pos;
    float dir;
};

layout(local_size_x = 1, local_size_y = 1) in;
layout(std430, binding=0) buffer buffer_0 {
    Agent agents[];
};
layout(rgba8, location=0) uniform image2D trail_map;

uniform uint num_agents;
uniform uint width;
uniform uint height;
uniform float move_speed;
uniform float delta_time;
uniform float time;

// taken front https://stackoverflow.com/questions/4200224/random-noise-functions-for-glsl
float hash_noise(vec2 xy, float seed){
    return fract(tan(distance(xy * PHI, xy) * seed) * xy.x);
}

float rand(vec2 co) {
    return fract(sin(dot(co, vec2(12.9898, 78.233))) * 43758.5453);
}

float scale_to_range(float r) {
    return r; // / 2 + 0.01; // / 4294967295.0;
}

void main() {
    uint id = gl_GlobalInvocationID.x;

    if (id >= num_agents) { return; }

    // Agent a = agents[id];
    Agent a = agents[id];
    float rand = hash_noise(a.pos, mod(100, 37));

    vec2 dir = vec2(cos(a.dir), sin(a.dir));
    ivec2 new_pos = ivec2(a.pos + dir * move_speed * delta_time);

    if (new_pos.x < 0 || new_pos.x >= width || new_pos.y < 0 || new_pos.y >= height) {
        new_pos.x = int(round(min(width - 1, max(0, new_pos.x))));
        new_pos.y = int(round(min(height - 1, max(0, new_pos.y))));
        agents[id].dir = scale_to_range(rand) * 2 * PI;
    }

    agents[id].pos = new_pos;
    // for (int x = -1; x < 2; x++) {
    //     for (int y = -1; y < 2; y++) {
    //         imageStore(trail_map, ivec2(new_pos.x + x, new_pos.y + y), vec4(1.0, 1.0, 1.0, 1.0));
    //     }
    // }
    imageStore(trail_map, new_pos, vec4(1.0, 1.0, 1.0, 1.0));
}
