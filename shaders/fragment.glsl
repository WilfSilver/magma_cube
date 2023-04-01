#version 330

uniform sampler2D texture0;
out vec4 frag_colour;
in vec2 uv;

void main() {
    frag_colour = texture(texture0, uv);
}
