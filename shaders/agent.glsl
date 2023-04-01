#pragma kernel update
#version 460

#define PI 3.14159265358979323846
#define PHI 1.61803398874989484820459;

struct Agent {
    uint2 coord;
    float angle;
}

StructuredBuffer<Agent> agents;
RWTexture2D<float4>  trail_map;
uint resolution;
uint num_agents;
uint width, height;
float move_speed;
float delta_time;

// taken front https://stackoverflow.com/questions/4200224/random-noise-functions-for-glsl
float hash_noise(vec2 xy, float seed){
    return fract(tan(distance(xy*PHI, xy) * seed) * xy.x);
}

float rand(vec2 co) {
    return fract(sin(dot(co, vec2(12.9898, 78.233))) * 43758.5453);
}

[numthreads(1024, 1, 1)]
void update(uint3 id : SV_DispatchThreadID) {
    if (id.x >= num_agents) { return; }
    Agent a = agents[id.x];
    ivec2 screen_size = imageSize(img_output);
    float rand = hash_noise(agent.coord, delta_time);

    float2 dir = float2(cos(a.angle), sin(a.angle));
    float2 new_pos = agent.position + dir * move_speed * delta_time;

    if (new_pos < 0 || new_pos.x >= width || new_pos.y < 0 || new_pos.y >= height) {
        new_pos.x = min(width - 0.01, max(0, new_pos.x));
        new_pos.y = min(height - 0.01, max(0, height.x));
        agents[id.x].angle = scaleToRange01(rand) * 2 * PI;
    }
    agents[id.x].position = new_pos;
    trail_map[int2(new_pos.x, new_pos.y)] = 1;
}
