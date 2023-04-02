#version 460

#define PI 3.14159265358979323846
#define PHI 1.61803398874989484820459

struct Agent {
    int x;
    int y;
    float angle;
    uint species;
};

uniform float sensor_angle_spacing;
uniform float turn_speed;
uniform float sensor_offset_dist;
uniform uint sensor_size;

uniform uint num_agents;
uniform uint width;
uniform uint height;
uniform float move_speed;
uniform float delta_time;
uniform float random_seed;
uniform float hunger_reset;
uniform bool eat_food;
uniform bool enable_food;
uniform bool repel;

layout(local_size_x = 1, local_size_y = 1) in;
layout(std430, binding=0) buffer buffer_0 {
    Agent agents[];
};
layout(std430, binding=1) buffer buffer_1 {
    vec3 debug_out[];
};
layout(rgba8, location=0) uniform image2D trail_map;
layout(rgba8, location=1) uniform image2D food_map;
layout(rgba8, location=2) uniform image2D food_trail_map;

// taken front https://stackoverflow.com/questions/4200224/random-noise-functions-for-glsl
float hash_noise(vec2 xy, float seed){
    return fract(tan(distance(xy * PHI, xy) * seed) * xy.x);
}

ivec2 agent_pos(Agent a) {
    return ivec2(a.x, a.y);
}

vec4 image_load_default(image2D img, ivec2 pos) {
    if (pos.x < 0 || pos.x >= width || pos.y < 0 || pos.y >= height) {
        return vec4(0);
    }

    return imageLoad(img, pos);
}

float sense_with_map(Agent a, float angle_offset, image2D map) {
    float angle = a.angle + angle_offset;
    vec2 dir = vec2(cos(angle), sin(angle));
    ivec2 centre = agent_pos(a) + ivec2(dir * sensor_offset_dist);
    float sum = 0;

    for (int x = -int(sensor_size); x <= int(sensor_size); x++) {
        for (int y = -int(sensor_size); y <= int(sensor_size); y++) {
            ivec2 pos = centre + ivec2(x, y);

            vec4 colour = image_load_default(map, pos);
            for (int i = 0; i < 3; i++) {
                if (i == a.species) {
                    sum += colour[i];
                } else if (repel) {
                    sum -= colour[i];
                }
            }
        }
    }

    return sum;
}

float sense(Agent a, float angle_offset) {
    return sense_with_map(a, angle_offset, food_trail_map);
}

void main() {
    uint id = gl_GlobalInvocationID.x;

    if (id >= num_agents) { return; }


    // Agent a = agents[id];
    Agent a = agents[id];
    float r = hash_noise(agent_pos(a) + width, random_seed);

    vec2 dir = vec2(cos(a.angle), sin(a.angle));
    ivec2 new_pos = ivec2(round(agent_pos(a) + dir * move_speed * delta_time));

    if (new_pos.x <= 0 || new_pos.x >= width || new_pos.y <= 0 || new_pos.y >= height) {
        // debug_out[id] = vec3(agent_pos(a), a.hunger);
        new_pos.x = int(round(min(width, max(0, new_pos.x))));
        new_pos.y = int(round(min(height, max(0, new_pos.y))));
        agents[id].angle = r * 2 * PI;
    }

    a.x = new_pos.x;
    a.y = new_pos.y;

    float weight_forward = sense(a, 0);
    float weight_left = sense(a, sensor_angle_spacing);
    float weight_right = sense(a, -sensor_angle_spacing);

    if (weight_forward >= weight_left && weight_forward >= weight_right) {
    } else if (weight_forward < weight_left && weight_forward < weight_right) {
        agents[id].angle += (r - 0.5) * 2 * turn_speed * delta_time;
    } else if (weight_left > weight_right) {
        agents[id].angle += r * turn_speed * delta_time;
    } else if (weight_right > weight_left) {
        agents[id].angle -= r * turn_speed * delta_time;
    }

    agents[id].x = new_pos.x;
    agents[id].y = new_pos.y;
    vec4 colour = vec4(0.0, 0.0, 0.0, 1.0);
    colour[a.species] = 1.0;
    for (int x = 0; x < 2; x++) {
        for (int y = 0; y < 2; y++) {
            imageStore(trail_map, ivec2(new_pos.x + x, new_pos.y + y), colour);
        }
    }
    // imageStore(trail_map, ivec2(new_pos.x, new_pos.y), vec4(a.hunger, 1.0 - a.hunger, 1.0 - a.hunger, 1.0));
    // imageStore(trail_map, new_pos, vec4(1.0, 1.0, 1.0, 1.0));
}
