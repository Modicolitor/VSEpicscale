# https://docs.blender.org/api/current/gpu.html
import bpy
import gpu
from gpu_extras.batch import batch_for_shader
import copy


class BE_OT_MarkProblems(bpy.types.Operator):
    bl_idname = "vsepic.markproblems"
    bl_label = "BE_OT_MarkProblems"
    bl_options = {'REGISTER', 'UNDO'}

    show_marker: bpy.props.BoolProperty(
        name='Show markers', description='', default=True)
    height: bpy.props.FloatProperty(
        name='Show markers', description='', default=50)

    def execute(self, context):
        coords = []
        if self.show_marker:
            coords = self.find_nostrip(context)
        draw_in_vse.update_line_coords(coords)
        #drawlines_in_VSE(context, coords)

        return {'FINISHED'}

    def find_nostrip(self, context):
        area_start = context.scene.frame_start
        area_end = context.scene.frame_end

        # make a list of all frame numbers in the renderarea
        errorlist = self.all_frames_list(area_start, area_end)
        sequences = context.sequences
        # remove the not hiden seqneces frames from the list
        for seq in sequences:
            if not seq.mute == True:
                # here should be a function to dependence from oppacity
                errorlist = self.remove_seqence_frames(context, seq, errorlist)

        coords = self.frames_to_coords(errorlist)
        return coords

    def frames_to_coords(self, errorlist):
        # self.height = 100
        coords = []
        for frame in errorlist:
            start = (frame, 0)
            end = (frame, self.height)
            coords.append(start)
            coords.append(end)
        return coords

    def remove_seqence_frames(self, context, seq, errorlist):

        area_start = seq.frame_final_start
        area_end = seq.frame_final_end
        print(
            f'removing for seqence {seq.name} from {area_start} to {area_end}')

        frame = area_start
        while frame <= area_end:
            if frame in errorlist:
                if self.follows_coverdemands(context, frame, seq):
                    errorlist.remove(frame)
            frame += 1
        return errorlist

    def follows_coverdemands(self, context, frame, seq):
        frameori = copy.copy(context.scene.frame_current)
        context.scene.frame_current = frame
        # get opacity

        # opacity check
        opacity = self.get_opacity(context, frame, seq)
        if opacity < 1:
            print(f'opacity false {frame} in {seq.name} opacity {opacity}')
            # print(f)
            return False

        context.scene.frame_current = frameori
        return True

    def get_opacity(self, context, frame, seq):
        fcurves = context.scene.animation_data.action.fcurves  # [2].data_path
        for fcu in fcurves:
            if seq.name in fcu.data_path:
                if 'blend_alpha' in fcu.data_path:
                    atframe = fcu.evaluate(frame)
                    print(f'name in {atframe}')
                    return atframe

        return context.scene.sequence_editor.sequences_all[seq.name].blend_alpha
        # context.scene.animation_data.action.fcurves[2].data_path

    def all_frames_list(self, area_start, area_end):

        list = [i for i in range(area_start, area_end)]
        '''list = []

        frame = area_start
        while frame <= area_end:
            print(f'add frame {frame}')
            list.append(frame)
            frame += 1'''
        return list

    # coords pair consist of frame ,
    def seq_covers_frame(self, frame, seq):
        if frame > seq.frame_final_start:
            if frame < seq.frame_final_start:
                return True


class draw_handler_vse:
    # def drawlines_in_VSE(context, coords):
    # coords = [(6, 0), (6, 100), (10, 0), (10, 100)]

    def __init__(self, context):
        self.context = context
        self.shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')  # UNIFORM
        self.update_line_coords([])
        self.make_handler()

    def update_line_coords(self, coords):
        self.batch = batch_for_shader(self.shader, 'LINES', {"pos": coords})

    def make_handler(self):
        def draw():
            if hasattr(bpy.context.scene, 'vsepicprops'):
                vsepicprops = bpy.context.scene.vsepicprops
                if vsepicprops.show_error_marks:  # self.show_marker:
                    self.shader.bind()
                    self.shader.uniform_float("color", (1, 0.5, 0, 0.1))
                    self.batch.draw(self.shader)
                else:
                    self.shader.unbind()
                    # bpy.types.SpaceSequenceEditor.draw_handler_remove(handler)

        self.handler = bpy.types.SpaceSequenceEditor.draw_handler_add(
            draw, (), 'WINDOW', 'POST_VIEW')


draw_in_vse = draw_handler_vse(bpy.context)
