import bpy
import copy
#from bpy import props


class BE_OT_AnimateMultiPointStab(bpy.types.Operator):
    '''Takes a selected audio and an active Video and corrects the time difference with a speed control'''
    bl_idname = "object.multipointstab"
    bl_label = "BE_OT_MultiPointStab"
    bl_options = {'REGISTER', 'UNDO'}

    target_scale: bpy.props.FloatProperty(
        name='Target Scale', description='Set the Scale', default=1.1)
    offset_x: bpy.props.FloatProperty(
        name='Xoffset', description='Add Offset in x', default=0.0)
    offset_y: bpy.props.FloatProperty(
        name='Yoffset', description='Add Offset in y', default=0.0)
    const_x: bpy.props.BoolProperty(
        name='Const X', description='Donnot animate in X derection because y is main direction of camera movement', default=False)
    const_y: bpy.props.BoolProperty(
        name='Const Y', description='Donnot animate in Y derection because x is main direction of camera movement', default=False)

    @ classmethod
    def poll(cls, context):

        if context.scene.epicmovieclip != None and context.area.type == 'CLIP_EDITOR':
            return True
        else:
            return False

    def execute(self, context):
        print(context.area.type)
        clip = context.scene.epicmovieclip
        #clip = bpy.data.movieclips["DSC_1923_OpenMaryPan.MP4"]
        tracks = clip.tracking.tracks
        stabilization = clip.tracking.stabilization

        stabilization.use_2d_stabilization = True
        context.space_data.show_stable = True
        stabilization.target_scale = self.target_scale

        for track in tracks:
            track.select = True
        bpy.ops.clip.stabilize_2d_add()

        # add tracks to stabilzer
        # for track in tracks:
        #    stabilization.tracks.append(track)

        # remove old keyframes of position in stabilisation
        self.remove_targetpos_keys(clip)

        # start situation: is tracked
        # activate stabilisation and add
        #  get coordinates of pic and track at each end of tracks
        # start coordinaten at frame
        # self.sort_tracks(tracks) sorting needs to be writen
        sortedtracks = tracks
        self.uebertrag = (0, 0)

        sortedtracksinfo = []
        for track in sortedtracks:
            firstmarker = 0
            while track.markers[firstmarker].mute:
                print("first one ding")
                print(firstmarker)
                print(track.markers[firstmarker].frame)
                firstmarker += 1
                if firstmarker < len(track.markers)-1:
                    print("first break")
                    break

            startframe = [track.markers[firstmarker].frame,
                          track.markers[firstmarker].co]

            lastmarker = len(track.markers)-1
            while track.markers[lastmarker].mute:
                lastmarker -= 1
                if lastmarker < 0:
                    break

            endframe = [track.markers[lastmarker].frame,
                        track.markers[lastmarker].co]
            trackinfo = startframe + endframe
            sortedtracksinfo.append(trackinfo)

        print(sortedtracksinfo)

        for n, track in enumerate(sortedtracks):
            print(f"n {n}")
            # bist du ganz vorne: starte von 0,0,
            if True:  # n != len(sortedtracksinfo)-1:
                startvalue = self.set_startvalueZero(
                    context, clip, sortedtracksinfo, n)

                endframe = sortedtracksinfo[n][2]
                # compensate track movement

                endvaluemove = self.correct_trackMovement(
                    context, sortedtracksinfo, n)
                if n != len(sortedtracksinfo)-1:
                    # compensate Scaleoffset
                    endvaluescale = self.correct_scaleOffset(
                        context, self.target_scale, sortedtracksinfo, n)

                    endvalue = endvaluemove - endvaluescale
                else:
                    endvalue = endvaluemove

                # make x or y constant
                # uebertrag zum startvalue des nächsten Frames
                # offset in start value enthalten also nicht doppelt zufügen zu ende
                if self.const_x:
                    self.uebertrag = (-endvalue[0], 0)
                    endvalue = (startvalue[0], endvalue[1])
                    print('x const')
                    # y-offset not transportet by uebertrag
                    endvalue = (endvalue[0], endvalue[1] + self.offset_y)

                if self.const_y:
                    self.uebertrag = (0, -endvalue[1])
                    endvalue = (endvalue[0], startvalue[1])
                    # x-offset not transportet by uebertrag
                    endvalue = (endvalue[0] + self.offset_x, endvalue[1])

                if not self.const_x and not self.const_y:

                    print("mainoffset")
                    endvalue = (endvalue[0] + self.offset_x,
                                endvalue[1] + self.offset_y)

                '''
                if not self.const_y:
                    endvalue = (endvalue[0] + self.offset_x,
                                endvalue[1] + self.offset_y)
                '''

                print(f"übertrag {self.uebertrag}")
                # Add Global Offset

                self.keyframe_targetposition(
                    context, clip.tracking.stabilization, endframe, endvalue)
            # biste du nicht ganz vorne

        # bpy.data.movieclips["DSC_1923_OpenMaryPan.MP4"].tracking.tracks["Track.001"].name

        # set keyframes (xy) for each end of each track
        # if its the earliest track set initial values
        fcurves = clip.animation_data.action.fcurves
        for fcurve in fcurves:
            for n, key in enumerate(fcurve.keyframe_points):
                key.interpolation = 'BEZIER'
                key.handle_right_type = 'VECTOR'
                key.handle_left_type = 'VECTOR'
                if n != len(fcurve.keyframe_points)-1:
                    self.set_handle_pos(key, fcurve.keyframe_points[n+1])

        # bpy.data.movieclips["DSC_1923_OpenMaryPan.MP4"].animation_data.action.fcurves[0].keyframe_points[0].interpolation

        # if its last track set finale frame
        #
        # if its one in the middle

        # set linear bpy.data.movieclips["DSC_1923_OpenMaryPan.MP4"].tracking.stabilization.target_position[1]

        return {'FINISHED'}

    def set_handle_pos(self, key1, key2):
        x = (key2.co[0] - key1.co[0])/2 + key1.co[0]
        y = (key2.co[1] - key1.co[1])/2 + key1.co[1]
        key1.handle_right = (x, y)
        key2.handle_left = (x, y)

    def correct_scaleOffset(self, context, scale, sortedtracksinfo, n):
        # n 0     1                                                 2    3
        # [[786, Vector((0.4448029696941376, 0.9553800225257874)), 965, Vector((0.6166502833366394, 0.029292989522218704))],
        # n+1
        # [966, Vector((0.5837005376815796, 0.8613118529319763)), 1009, Vector((0.6502138376235962, 0.6435660719871521))]]
        PJetzt = sortedtracksinfo[n][3]
        PNext = sortedtracksinfo[n+1][1]

        PStern = PJetzt + scale * (-PJetzt+PNext)
        print(f'PNext {PNext}')
        print(f'PJetzt {PJetzt}')
        print(f'Pstern {PStern}')

        offset = PStern - PNext
        print(f'scale offset is {offset}')
        return offset

    def correct_trackMovement(self, context, sortedtracksinfo, n):

        offset = -(sortedtracksinfo[n][1]-sortedtracksinfo[n][3])
        print(f'Trackmovemnt offset is {offset}')
        return offset

    def set_startvalueZero(self, context, clip, sortedtracksinfo, n):
        startframe = sortedtracksinfo[n][0]
        print(f'for {n} start uebertrag {self.uebertrag}')
        startvalue = (0+self.offset_x +
                      self.uebertrag[0], 0+self.offset_y + self.uebertrag[1])

        self.keyframe_targetposition(
            context, clip.tracking.stabilization, startframe, startvalue)
        return startvalue

    def keyframe_targetposition(self, context, path, frame, value):
        oriframecurrent = copy.copy(context.scene.frame_current)
        ###

        # go to frame
        context.scene.frame_current = frame
        # set value
        path.target_position = value
        # insert keyframe
        path.keyframe_insert(data_path="target_position")

        context.scene.frame_current = oriframecurrent

    def sort_tracks(self, tracks):
        pass

    def remove_targetpos_keys(self, clip):

        keys, action, data_path = self.get_keyframes_data_path(
            clip, 'tracking.stabilization.target_position')  # schau hier nochmal rein tracking.stabilization.target_position
        print(f'data path {data_path} keys amount {len(keys)}')
        #wave_scale = get_largest_keyvalue(context, keys)
        if len(keys) > 0:
            for key in keys:
                print('delete')
                try:
                    clip.tracking.stabilization.keyframe_delete(data_path='target_position',
                                                                index=-1, frame=key.co[0])
                except:
                    print(f'Huppsi Key delete, no Action left at key {key.co}')
        print('delete end')

    def get_keyframes_data_path(self, object, data_path):
        keys = []
        action = None
        if hasattr(object.animation_data, "action"):
            action = object.animation_data.action
            print('has action')
            if hasattr(object.animation_data.action, "fcurves"):
                print('has fcurves')
                for fc in action.fcurves:
                    if fc.data_path == data_path:
                        print('found keys')
                        for key in fc.keyframe_points:
                            if key not in keys:
                                keys.append(key)

        return keys, action, data_path
