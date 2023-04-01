#version 460 core

uniform sampler2D textures[];
uniform bool enable_birb;

// in vec4 agent2;
// in vec4 agent3;

out vec4 frag_color;
in vec2 uv;

void main() {
    vec3 birb_color = texture(textures[1], uv).rgb;

    if (enable_birb) {
        frag_color = ((birb_color.r == 1.0) ? vec4(0.0, 1.0, 0.0, 1.0) : vec4(0.0, 0.0, 0.0, 0.0)) + vec4(texture(textures[0], uv).rgb, 0.5);
    } else {
        frag_color = vec4(texture(textures[0], uv).rgb, 0.5);
    }

}
