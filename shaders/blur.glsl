#version 460 core

#define PHI 1.61803398874989484820459

layout(local_size_x = 1, local_size_y = 1) in;
layout(rgba8, location=0) uniform image2D tex;
layout(rgba8, location=1) uniform image2D out_tex;

// Taken from https://www.rastergrid.com/blog/2010/09/efficient-gaussian-blur-with-linear-sampling/

// uniform float offset[5] = float[](-2.0, -1.0, 0, 1.0, 2.0);
// uniform float weight[5] = float[](0.2, 0.3, 0.3, 0.3, 0.2);
// uniform float offset[3] = float[](0.0, 1.3846153846, 3.2307692308);
// uniform float weight[3] = float[](0.5, 0.5, 0.5);
uniform float offset[3] = float[](0.0, 1, 1);
uniform float weight[3] = float[](0.2, 0.4, 0.1);
uniform float delta_time;
uniform int decay_rate;

void main(void) {
    ivec2 pos = ivec2(gl_GlobalInvocationID.xy);
    // vec4 color = vec4(0.0);
    // for (int i=0; i<3; i++) {
    //     ivec2 ydelta = ivec2(pos + ivec2(0.0, offset[i]));
    //     color += imageLoad(tex, ydelta) * weight[i];
    //     ivec2 xdelta = ivec2(pos - ivec2(offset[i], 0));
    //     color += imageLoad(tex, ivec2(xdelta)) * weight[i];
    //     imageStore(out_tex, pos, color);
    // }
    vec4 sum = vec4(0.0);
    float weight_sum = 0;
    for (int x = -1; x < 2; x++) {
        for (int y = -1; y < 2; y++) {
            ivec2 pixel = ivec2(pos.x + x, pos.y + y);
            float weight = 2 - distance(pos, pixel);
            sum += imageLoad(tex, pixel) * weight;
            weight_sum += weight;
        }
    }
    vec4 colour = sum / weight_sum;
    vec4 new_col = colour - vec4(decay_rate * delta_time);
    imageStore(out_tex, pos, max(vec4(0), new_col));

}
