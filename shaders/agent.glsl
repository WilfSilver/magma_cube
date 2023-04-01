#version 460

#define PI 3.14159265358979323846
#define PHI 1.61803398874989484820459

layout(local_size_x = 1, local_size_y = 1) in;
layout(std430, binding=0) buffer buffer_0 {
    ivec2 agents_coords[];
};

layout(std430, binding=1) buffer buffer_1 {
    float agents_dirs[];
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
    ivec2 a_pos = agents_coords[id];
    float a_dir = agents_dirs[id];
    float rand = hash_noise(a_pos, time);

    vec2 dir = vec2(cos(a_dir), sin(a_dir));
    ivec2 new_pos = ivec2(a_pos + dir * move_speed * delta_time);

    if (new_pos.x < 0 || new_pos.x >= width || new_pos.y < 0 || new_pos.y >= height) {
        new_pos.x = int(round(min(width - 1, max(0, new_pos.x))));
        new_pos.y = int(round(min(height - 1, max(0, new_pos.y))));
        agents_dirs[id] = scale_to_range(rand) * 2 * PI;
    }

    agents_coords[id] = new_pos;
    imageStore(trail_map, new_pos, vec4(1.0, 1.0, 1.0, 1.0));
    new_pos.x += 1;
    imageStore(trail_map, new_pos, vec4(1.0, 1.0, 1.0, 1.0));
    new_pos.x -= 2;
    imageStore(trail_map, new_pos, vec4(1.0, 1.0, 1.0, 1.0));
    new_pos.x += 1;
    new_pos.y += 1;
    imageStore(trail_map, new_pos, vec4(1.0, 1.0, 1.0, 1.0));
    new_pos.y -= 2;
    imageStore(trail_map, new_pos, vec4(1.0, 1.0, 1.0, 1.0));
}
