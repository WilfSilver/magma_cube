#version 460

#define PI 3.14159265358979323846
#define PHI 1.61803398874989484820459

struct Agent {
    int x;
    int y;
    float angle;
};

uniform uint num_agents;
uniform uint width;
uniform uint height;
uniform float move_speed;
uniform float delta_time;
uniform float time;
uniform float sensor_angle_spacing;
uniform float turn_speed;

layout(local_size_x = 1, local_size_y = 1) in;
layout(std430, binding=0) buffer buffer_0 {
    Agent agents[];
};
layout(std430, binding=1) buffer buffer_1 {
    vec2 debug_out[];
};
layout(rgba8, location=0) uniform image2D trail_map;

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

ivec2 agent_pos(Agent a) {
    return ivec2(a.x, a.y);
}

float sense(Agent a, float angle_offset) {
    float angle = a.angle + angle_offset;

    vec2 dir = vec2(cos(angle), sin(angle));
    ivec2 pos = ivec2(agent_pos(a) + 3 * dir * move_speed * delta_time);

    vec4 colour = imageLoad(trail_map, pos);
    return colour.x;
}

void main() {
    uint id = gl_GlobalInvocationID.x;

    if (id >= num_agents) { return; }

    // Agent a = agents[id];
    Agent a = agents[id];
    float rand = hash_noise(agent_pos(a), mod(time, 37));

    vec2 dir = vec2(cos(a.angle), sin(a.angle));
    ivec2 new_pos = ivec2(agent_pos(a) + dir * move_speed * delta_time);

    if (new_pos.x < 0 || new_pos.x >= width || new_pos.y < 0 || new_pos.y >= height) {
        debug_out[id] = agent_pos(a);
        new_pos.x = int(round(min(width - 1, max(1, new_pos.x))));
        new_pos.y = int(round(min(height - 1, max(1, new_pos.y))));
        agents[id].angle = scale_to_range(rand) * 2 * PI;
    }

    float weight_forward = sense(a, 0);
    float weight_left = sense(a, sensor_angle_spacing);
    float weight_right = sense(a, -sensor_angle_spacing);

    if (weight_forward > weight_left && weight_forward > weight_right) {
        agents[id].angle += 0;
    } else if (weight_forward < weight_left && weight_forward < weight_right) {
        agents[id].angle += (rand - 0.5) * 2 * turn_speed * delta_time;
    } else if (weight_right > weight_left) {
        agents[id].angle -= rand * turn_speed * delta_time;
    } else if (weight_left > weight_right) {
        agents[id].angle += rand * turn_speed * delta_time;
    }

    agents[id].x = new_pos.x;
    agents[id].y = new_pos.y;
    for (int x = -1; x < 2; x++) {
        for (int y = -1; y < 2; y++) {
            imageStore(trail_map, ivec2(new_pos.x + x, new_pos.y + y), vec4(1.0, 1.0, 1.0, 1.0));
        }
    }
    // imageStore(trail_map, new_pos, vec4(1.0, 1.0, 1.0, 1.0));
}
