#version 460 core

uniform sampler2D textures[];
uniform bool enable_birb;

// in vec4 agent2;
// in vec4 agent3;

out vec4 frag_colour;
in vec2 uv;

void main() {
    vec3 birb_color = texture(textures[1], uv).rgb;

    if (enable_birb) {
        vec4 col = vec4(texture(textures[0], uv).rgb, 1);
        frag_colour = ((birb_color.r == 1.0 && col.g != 1.0) ? vec4(0.0, 1.0, 0.0, 1.0) : vec4(0.0, 0.0, 0.0, 0.0)) + vec4(texture(textures[0], uv).rgb, 1);
    } else {
        frag_colour = vec4(texture(textures[0], uv).rgb, 1.0);
    }
}
