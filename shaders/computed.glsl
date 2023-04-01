#version 460

Struct Agent {
    vec2 xy,
    vec4 colour,
    float theta
};

void main()
{
    ivec2 imagesize = imageSize();

    Agent agent;
    agent.xy = vec2(0.0, 0.0);
    agent.colour = vec4(1.0, 1.0, 1.0, 1.0);
    agent.theta = float(0);

    
    
}