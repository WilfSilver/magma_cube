#version 460 core

#define PHI 1.61803398874989484820459

layout(local_size_x = 1, local_size_y = 1) in;
layout(rgba8, location=0) writeonly uniform image2D tex;

// taken front https://stackoverflow.com/questions/4200224/random-noise-functions-for-glsl
float hash_noise(vec2 xy, float seed){
    return fract(tan(distance(xy * PHI, xy) * seed) * xy.x);
}


// uniform RWTexture2D<float4> tex;
// uniform uint width;
// uniform uint height;
uniform float time;

void main() {
    ivec2 pos = ivec2(gl_GlobalInvocationID.xy);
    // if (pos.x < 0 || pos.x > width || pos.y < 0 || pos.x > height) { return; }

    float rand = hash_noise(pos, time);
    float val = rand / 4294967295.0;
    imageStore(tex, pos, vec4(rand, rand, rand, 1.0));
}
