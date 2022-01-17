# https://docs.blender.org/api/current/gpu.html
import bpy
import gpu
from gpu_extras.batch import batch_for_shader

coords = [(6, 0), (6, 100)]
shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
batch = batch_for_shader(shader, 'LINES', {"pos": coords})


def draw():
    shader.bind()
    shader.uniform_float("color", (1, 1, 0, 1))
    batch.draw(shader)


bpy.types.SpaceSequenceEditor.draw_handler_add(draw, (), 'WINDOW', 'POST_VIEW')
