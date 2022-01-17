import bpy
import copy
#from bpy import props

##################
# Anstiege gleichmachen


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
    mikrocorrect_x: bpy.props.FloatProperty(
        name='MicroCorrectX', description='Corrrects minimal imperfections in x', default=0.0)
    mikrocorrect_y: bpy.props.FloatProperty(
        name='MicroCorrectY', description='Corrrects minimal imperfections in y', default=0.0)
    const_x: bpy.props.BoolProperty(
        name='Const X', description='Donnot animate in X derection because y is main direction of camera movement', default=False)
    const_y: bpy.props.BoolProperty(
        name='Const Y', description='Donnot animate in Y direction because x is main direction of camera movement', default=False)
    const_slope_x: bpy.props.BoolProperty(
        name='Const Slope X', description='Keep Slope Const', default=False)
    const_slope_y: bpy.props.BoolProperty(
        name='Const Slope Y', description='Keep Slope Const', default=False)
    sel_slope: bpy.props.IntProperty(
        name='Slope Selection', description='Select the Sloop of a Track in timely order', default=1, min=1)
    slope_factor:   bpy.props.FloatProperty(
        name='SlopFactor', description='Adjust Slope with this Multiplier', default=1.0)

    @ classmethod
    def poll(cls, context):

        if context.scene.epicmovieclip != None and context.area.type == 'CLIP_EDITOR':
            return True
        else:
            return False

    def execute(self, context):

        oriframecurrent = copy.copy(context.scene.frame_current)
        # print(context.area.type)
        clip = context.scene.epicmovieclip
        #clip = bpy.data.movieclips["DSC_1923_OpenMaryPan.MP4"]
        tracks = clip.tracking.tracks
        stabilization = clip.tracking.stabilization

        stabilization.use_2d_stabilization = True
        context.space_data.show_stable = True
        stabilization.target_scale = self.target_scale

        # add all markers to stabilzisation
        for track in tracks:
            track.select = True
        bpy.ops.clip.stabilize_2d_add()

        # remove old keyframes of position in stabilisation
        self.remove_targetpos_keys(clip)

        sortedtracks = self.sort_tracks(tracks)
        self.uebertrag = (0, 0)

        # collect track infos
        sortedtracksinfo = []
        trackenumlist = []
        for n, track in enumerate(sortedtracks):
            firstmarker, frame = self.get_track_start(track)
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

            # print(sortedtracksinfo)
            trackenumlist.append(
                (str(n), str(track.name), '1'))

        # bpy.types.Scene.vsepictracks = bpy.props.EnumProperty(
        #    items=trackenumlist)
        print(trackenumlist)

        #context.scene.vsepicprops.trackfactor = context.scene.vsepictracks

        # calculate keyframe coord and set keyframes
        for n, track in enumerate(sortedtracks):
            #print(f"n {n}")
            # bist du ganz vorne: starte von 0,0,

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
                #print('x const')
                # y-offset not transportet by uebertrag
                endvalue = (endvalue[0], endvalue[1] + self.offset_y)

            if self.const_y:
                self.uebertrag = (0, -endvalue[1])
                endvalue = (endvalue[0], startvalue[1])
                # x-offset not transportet by uebertrag
                endvalue = (endvalue[0] + self.offset_x, endvalue[1])

            if not self.const_x and not self.const_y:

                # print("mainoffset")
                endvalue = (endvalue[0] + self.offset_x,
                            endvalue[1] + self.offset_y)

                print(f"übertrag {self.uebertrag}")
                # Add Global Offset
            # Mikrocorrections
            endvalue = (endvalue[0] + self.mikrocorrect_x/100,
                        endvalue[1] + self.mikrocorrect_y/100)

            self.keyframe_targetposition(
                context, clip.tracking.stabilization, endframe, endvalue)
            # biste du nicht ganz vorne

        if self.const_slope_x or self.const_slope_y:
            # calculate slops
            slopeinfos_x, slopeinfos_y = self.get_slopeinfos(
                clip)
            # get [n, key, co, slope]
            #      0   1    2   3
            if self.const_slope_x:
                # choose slope
                if self.sel_slope > len(slopeinfos_x):
                    self.sel_slope = len(slopeinfos_x)
                slope = slopeinfos_x[self.sel_slope*2-2][3]
                self.set_const_slope(slope, slopeinfos_x)
            if self.const_slope_y:
                # choose slope
                if self.sel_slope > len(slopeinfos_y):
                    self.sel_slope = len(slopeinfos_y)
                slope = slopeinfos_y[self.sel_slope*2-2][3]
                self.set_const_slope(slope, slopeinfos_y)
            # calculate new pos of end, --> calc delta

            # add delta to the right keyframes

        # bpy.data.movieclips["DSC_1923_OpenMaryPan.MP4"].tracking.tracks["Track.001"].name

        if hasattr(clip.animation_data, "action"):
            if hasattr(clip.animation_data.action, "fcurves"):
                fcurves = clip.animation_data.action.fcurves
                for fcurve in fcurves:
                    for n, key in enumerate(fcurve.keyframe_points):
                        key.interpolation = 'BEZIER'
                        key.handle_right_type = 'VECTOR'
                        key.handle_left_type = 'VECTOR'
                        if n != len(fcurve.keyframe_points)-1:
                            self.set_handle_pos(
                                key, fcurve.keyframe_points[n+1])

        # bpy.data.movieclips["DSC_1923_OpenMaryPan.MP4"].animation_data.action.fcurves[0].keyframe_points[0].interpolation

        # if its last track set finale frame
        #
        # if its one in the middle

        # set linear bpy.data.movieclips["DSC_1923_OpenMaryPan.MP4"].tracking.stabilization.target_position[1]
        context.scene.frame_current = oriframecurrent

        context.scene.vsepicprops.target_scale = self.target_scale
        context.scene.vsepicprops.offset_x = self.offset_x
        context.scene.vsepicprops.offset_y = self.offset_y
        context.scene.vsepicprops.mikrocorrect_x = self.mikrocorrect_x
        context.scene.vsepicprops.mikrocorrect_y = self.mikrocorrect_y
        context.scene.vsepicprops.const_x = self.const_x
        context.scene.vsepicprops.const_y = self.const_y
        context.scene.vsepicprops.const_slope_x = self.const_slope_x
        context.scene.vsepicprops.const_slope_y = self.const_slope_y
        context.scene.vsepicprops.sel_slope = self.sel_slope
        context.scene.vsepicprops.slope_factor = self.slope_factor
        return {'FINISHED'}

    def invoke(self, context, event):

        self.target_scale = context.scene.vsepicprops.target_scale
        self.offset_x = context.scene.vsepicprops.offset_x
        self.offset_y = context.scene.vsepicprops.offset_y
        self.mikrocorrect_x = context.scene.vsepicprops.mikrocorrect_x
        self.mikrocorrect_y = context.scene.vsepicprops.mikrocorrect_y
        self.const_x = context.scene.vsepicprops.const_x
        self.const_y = context.scene.vsepicprops.const_y
        self.const_slope_x = context.scene.vsepicprops.const_slope_x
        self.const_slope_y = context.scene.vsepicprops.const_slope_y
        self.sel_slope = context.scene.vsepicprops.sel_slope
        self.slope_factor = context.scene.vsepicprops.slope_factor
        return self.execute(context)

    def get_slopeinfos(self, clip):
        slopeinfos_x = []
        slopeinfos_y = []
        keyinfos = []
        if hasattr(clip.animation_data, "action"):
            if hasattr(clip.animation_data.action, "fcurves"):
                fcurves = clip.animation_data.action.fcurves
                for n, fcurve in enumerate(fcurves):
                    print(f'fcurve {n}')
                    if fcurve.data_path == "tracking.stabilization.target_position":
                        keys = fcurve.keyframe_points
                        for k, key in enumerate(keys):
                            slope = None
                            if len(keys)-1 != k:
                                co1 = key.co
                                co2 = keys[k+1].co
                                slope = (co2[1]-co1[1])/(co2[0]-co1[0])
                            keyinfo = [k, key, co1, slope]
                            if n == 0:
                                slopeinfos_x.append(keyinfo)
                            if n == 1:
                                slopeinfos_y.append(keyinfo)
        print(slopeinfos_x)
        print(slopeinfos_y)
        return slopeinfos_x, slopeinfos_y

    def set_const_slope(self, slope, slopeinfos):
        # get [n, key, co, slope]
        #      0   1    2   3
        slope *= self.slope_factor
        for l, info in enumerate(slopeinfos):
            # bei den endframes
            if info[0] % 2 != 0:
                # berechne neue Position
                distx = slopeinfos[l][1].co[0] - slopeinfos[l-1][1].co[0]
                starty = slopeinfos[l-1][1].co[1]
                oldy = slopeinfos[l][1].co[1]
                newy = slope * distx + starty
                offset = newy - oldy

                slopeinfos[l][1].co[1] += offset
                if l != len(slopeinfos)-1:
                    slopeinfos[l+1][1].co[1] += offset

    def set_handle_pos(self, key1, key2):
        x = (key2.co[0] - key1.co[0])/2 + key1.co[0]
        y = (key2.co[1] - key1.co[1])/2 + key1.co[1]
        key1.handle_right = (x, y)
        key2.handle_left = (x, y)

    def correct_scaleOffset(self, context, scale, sortedtracksinfo, n):

        PJetzt = sortedtracksinfo[n][3]
        PNext = sortedtracksinfo[n+1][1]
        PStern = PJetzt + scale * (-PJetzt+PNext)
        offset = PStern - PNext
        #print(f'scale offset is {offset}')
        return offset

    def correct_trackMovement(self, context, sortedtracksinfo, n):

        offset = -(sortedtracksinfo[n][1]-sortedtracksinfo[n][3])
        #print(f'Trackmovemnt offset is {offset}')
        return offset

    def set_startvalueZero(self, context, clip, sortedtracksinfo, n):
        startframe = sortedtracksinfo[n][0]
        #print(f'for {n} start uebertrag {self.uebertrag}')
        startvalue = (0+self.offset_x +
                      self.uebertrag[0], 0+self.offset_y + self.uebertrag[1])

        self.keyframe_targetposition(
            context, clip.tracking.stabilization, startframe, startvalue)
        return startvalue

    def keyframe_targetposition(self, context, path, frame, value):
        oriframecurrent = copy.copy(context.scene.frame_current)
        ###
        print(
            f'Current Frame before set keyframe {context.scene.frame_current} oriframe {oriframecurrent}')
        # go to frame
        context.scene.frame_current = frame
        # set value
        path.target_position = value
        # insert keyframe
        path.keyframe_insert(data_path="target_position")
        print(
            f'Current Frame before rest {context.scene.frame_current} oriframe {oriframecurrent}')
        context.scene.frame_current = oriframecurrent
        print(
            f'Current Frame after reset  {context.scene.frame_current} oriframe {oriframecurrent}')

    def sort_tracks(self, tracks):

        # go through tracks and record first (enabled) frame
        startframes = []
        for track in tracks:
            firstmarker, firstframe = self.get_track_start(track)
            startframes.append(firstframe)

        startframes.sort()
        print(f'startframes {startframes}')
        trackssorted = []
        for start in startframes:
            for track in tracks:
                marker, frame = self.get_track_start(track)
                if start == frame:
                    trackssorted.append(track)
        print(f'tracksorted {trackssorted}')
        return trackssorted

    def get_track_start(self, track):
        firstmarker = 0
        while track.markers[firstmarker].mute:
            firstmarker += 1
            if firstmarker < len(track.markers)-1:
                #print("first break")
                break

        return firstmarker, track.markers[firstmarker].frame  # ,
        # track.markers[firstmarker].co]

    def remove_targetpos_keys(self, clip):

        keys, action, data_path = self.get_keyframes_data_path(
            clip, 'tracking.stabilization.target_position')  # schau hier nochmal rein tracking.stabilization.target_position
        #print(f'data path {data_path} keys amount {len(keys)}')
        #wave_scale = get_largest_keyvalue(context, keys)
        if len(keys) > 0:
            for key in keys:
                # print('delete')
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
