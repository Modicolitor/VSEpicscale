from email.utils import encode_rfc2231
import bpy
from bpy.types import Scene, Image, Object, PropertyGroup, MovieTrackingTrack


# def get_track_list_callback(context):
#    items = context.scene.vsepictracks
#    return items


class TrackElement(bpy.types.PropertyGroup):
    #track: bpy.props.PointerProperty(name='track', type=MovieTrackingTrack)
    posstab: bpy.props.BoolProperty(name='StabilizePosition', default=True)
    rotstab: bpy.props.BoolProperty(name='StabilizeRotation', default=False)
    startframe: bpy.props.IntProperty(name='startframe', default=-100)
    startvalue = (-100, -100)
    endframe: bpy.props.IntProperty(name='startframe', default=-100)
    endvalue = (-100, -100)

    def set_track(self, track, posstab, rotstab, firstmarker, startframe, startvalue, lastmarker, endframe, endvalue):
        self.track = track
        self.posstab = posstab
        self.rotstab = rotstab
        self.startframe = startframe
        self.startvalue = startvalue
        self.endframe = endframe
        self.endvalue = endvalue
        self.firstmarker = firstmarker
        self.lastmarker = lastmarker
        return self


class VSEpicTrackCol(bpy.types.PropertyGroup):
    tracks:  bpy.props.CollectionProperty(type=TrackElement)
    #list of lists grouping tracks in anschließende gruppen von tracks with pos or rot flag
    tracksegments: []
    #list of tracks for posstabilisation 
    postracks: [] 
    #list of tracks for rot/scale stabilisation
    rottracks:[]
    

    def update(self, context, tracks):

        print('alive')
        for track in tracks:
            print(track.name)
            #self.trackelement = bpy.props.PointerProperty(type=TrackElement)
            track, posstab, rotstab, firstmarker, startframe, startvalue, lastmarker, endframe, endvalue = self.get_trackdata(
                track)
            # trackelement = [track, posstab, rotstab, firstmarker,
            #                startframe, startvalue, lastmarker, endframe, endvalue]

            # check whether a track is just changed or renamed or really new
            trackelement = self.new_or_old(track, posstab, rotstab, firstmarker,
                                           startframe, startvalue, lastmarker, endframe, endvalue)

        # check wherther tracks and saved tracks is the same or pop anything with wrong name
        if len(tracks) != len(self.tracks):
            self.pop_too_much(tracks)

        # list of tracks as tuple for ui
        self.make_ui_list(context)
        # guess konfiguration: overlapping tracks, pos/rot decision, grouping for stab panels and final processing
        self.make_track_lists()
        #self.find_stabconfiguration()

    def make_track_lists(self):
        self.tracksegments = []
        overviewlist = [] 
        for t in self.tracks:
            overviewlist.append(t)

        for tr1 in overviewlist:
            for tr2 in overviewlist:
                if tr1 != tr2:
                    #returns group of 
                    overlaptype, quality, specifypos = self.find_overlap(tr1, tr2)
                    self.put_target_segment(tr1, tr2, overlaptype, quality, specifypos) 
                    ### [[t1, t2],[t4,t5], []]
                    
    def put_target_segment(self, tr1, tr2, overlaptype, quality, specifypos):
        #alles leer
        if len(self.tracksegments) == 0:
            if overlaptype == 'overlap':
                Notes = quality+specifypos
                self.tracksegments.append([tr1,tr2,Notes])
                return 
              
        ####nicht leer 
        #gibts die schon ?
        oplist = [tr1, tr2]
        tr1_in = self.is_in_targetseqments(tr1)
        tr2_in = self.is_in_targetseqments(tr2)
                
        if tr1_in:
            oplist.pop(tr1) 
        if tr2_in:
            oplist.pop(tr2)
        # beide schon drin 
        if len(oplist) == 0:
            return
        
        
        if overlaptype == 'overlap': 
            ## tr1 and tr2 overlapping and we find a segment that overlapps with them 
            for segement in self.tracksegments[:]:
                otype, oquality, ospecifypos = self.find_overlap(segement[0], tr1)  
                if otype == 'overlap':
                    if not tr1_in:
                        segement.insert(-2, tr1)
                    if not tr2_in:
                        segement.insert(-2, tr2)
                    segement[-1] += oquality+ospecifypos
                    return
            if len(oplist) == 2:  
                ## tr1 and tr2 overlapping and we find a spot for the segment   
                ###didn't find a existing segment --> make a new segment, find a place for it
                for n,segement in enumerate(self.tracksegments[:]):
                    otype0, quality0, specifypos0 = self.find_overlap(self.tracksegments[n], tr1)  
                    if quality0 == 'perfect':
                        if specifypos0 == 'front':
                            self.tracksegments.insert(n, [tr1,tr2])
                        elif specifypos0 == 'back':
                            self.tracksegments.insert(n+1, [tr1,tr2])
                        return
                    ##!!!!!!!!!!hmmmm think about not perfect results
                    ### don't forget the notes 


                    ###way before first 
                    if n == 0 and specifypos0 == 'front':
                        self.tracksegments.insert(n, [tr1,tr2])
                        return
                    ###way after last
                    if n == len(self.tracksegments) and specifypos0 == 'back': ###letzte bedingung zuviel?
                        self.tracksegments.insert(n, [tr1,tr2])

            ### if len(oplist) == 1: wenn sie overlapp sind wird es oben mit abgedeckt       


        # when both are conti --> such wie oben aber je und dann zufügen 

        #self.is_in_targetseqments(tr1): 


            
        if overlaptype == 'overlap':
            if specifypos == "back":
            preorder = [tr1,tr2]

        

        #is the element somwhere 

    def is_in_targetseqments(self,tr1):
        if len(self.tracksegments) == 0:
            return False
        for tracksegment in self.tracksegments:
            for track in tracksegment: 
                if track == tr1:
                    return True
        return False


    def find_overlap(self, tr1, tr2):
        ##### track2 relative to track1 , front means track2 is before track1 
        ####overlaptype = conti, overlap;  quality =  perfect, tooshort, toolong; specifypos = front, back
        start1 = tr1.startframe
        end1 = tr1.endframe

        start2 = tr2.startframe
        end2 = tr2.endframe
        
        #perfect overlap: gleicher start gleiches ende 
        if start1 == start2:
           if end1 == end2:
                overlaptype = 'overlap' 
                quality = 'perfect'
                specifypos = None
                return overlaptype, quality, specifypos
        #perfect conti front 
        if start1-1 == end2:
            overlaptype = 'conti' 
            quality = 'perfect'
            specifypos = 'front'
            return overlaptype, quality, specifypos
        #perfect conti back 
        if end1+1 == start2:
            overlaptype = 'conti' 
            quality = 'perfect'
            specifypos = 'back'
            return overlaptype, quality, specifypos
        # conti too short front /distant track 
        if start1-1 > end2:
            overlaptype = 'conti' 
            quality = 'tooshort'
            specifypos = 'front'
            return overlaptype, quality, specifypos
        # conti  too short back /distant track 
        if end1+1 < start2:
            overlaptype = 'conti' 
            quality = 'tooshort'
            specifypos = 'back'
            return overlaptype, quality, specifypos
        # conti  too long front /distant track
        if start2 < start1:
            if end2 > start1:
                overlaptype = 'conti' 
                quality = 'toolong'
                specifypos = 'front'
                return overlaptype, quality, specifypos
        # conti  too long back /distant track 
        if end2 > end1:
            if end1 > start2:
                overlaptype = 'conti' 
                quality = 'toolong'
                specifypos = 'back'
                return overlaptype, quality, specifypos
        #overlap too long front 
        if end1 == end2:
            if start2 < start1:
                overlaptype = 'overlap' 
                quality = 'toolong'
                specifypos = 'front'
                return overlaptype, quality, specifypos
        #overlap too long back 
        if start1==start2:
            if end1 < end2:
                overlaptype = 'overlap' 
                quality = 'toolong'
                specifypos = 'back'
                return overlaptype, quality, specifypos
        #overlap too short front 
        if end1 == end2:
            if start2 > start1:
                overlaptype = 'overlap' 
                quality = 'tooshort'
                specifypos = 'front'
                return overlaptype, quality, specifypos
        #overlap too short back 
        if start1==start2:
            if end1 > end2:
                overlaptype = 'overlap' 
                quality = 'tooshort'
                specifypos = 'back'
                return overlaptype, quality, specifypos


    def pop_too_much(self, tracks):
        # fill a new list with all trackelements
        testlist = []
        for ele in self.tracks:
            testlist.append(ele)

        # check by name whether its in --> pop from that list
        for ele in testlist[:]:
            for t in tracks:
                if ele.name == t.name:
                    testlist.pop(ele)

        # after all, pop all remaining elements in list from self.tracks

        for ele in testlist:
            print(f'remove track {ele.name} as too much')
            self.tracks.pop(ele)

    def new_or_old(self, track, posstab, rotstab, firstmarker,
                   startframe, startvalue, lastmarker, endframe, endvalue):
        for ele in self.tracks:
            # same name exist, update all but not posstab and rotstab
            if ele.name == track.name:
                print(f'found Track with same name {ele.name}')
                ele.track = track
                #ele.posstab =  posstab
                #ele.rotstab = rotstab
                ele.firstmarker = firstmarker
                ele.startframe = startframe
                ele.startvalue = startvalue
                ele.lastmarker = lastmarker
                ele.endframe = endframe
                ele.endvalue = endvalue
                return ele

        for ele in self.tracks:
            # new name: is there a track with same start or end frame/value
            if ele.startvalue == startvalue:
                if ele.startframe == startframe:
                    ele.name = track.name
                    ele.track = track
                    #ele.posstab =  posstab
                    #ele.rotstab = rotstab
                    ele.firstmarker = firstmarker
                    ele.startframe = startframe
                    ele.startvalue = startvalue
                    ele.lastmarker = lastmarker
                    ele.endframe = endframe
                    ele.endvalue = endvalue
                    return ele
            elif ele.endvalue == startvalue:
                if ele.endframe == startframe:
                    ele.name = track.name
                    ele.track = track
                    #ele.posstab =  posstab
                    #ele.rotstab = rotstab
                    ele.firstmarker = firstmarker
                    ele.startframe = startframe
                    ele.startvalue = startvalue
                    ele.lastmarker = lastmarker
                    ele.endframe = endframe
                    ele.endvalue = endvalue
                    return ele
                # new name: is there a track with same start or end frame/value

                # posstab set

        # track don't exist
        print('track dont exist')
        newtrack = self.tracks.add()
        newtrack.name = track.name
        newtrack.set_track(track, posstab, rotstab, firstmarker,
                           startframe, startvalue, lastmarker, endframe, endvalue)

    def get_trackdata(self, track):

        firstmarker, startframe = self.get_track_start(track)
        lastmarker, endframe = self.get_track_end(track)

        # just the defaults
        posstab = True
        rotstab = False
        #firstmarker = firstmarker
        #startframe = startframe
        startvalue = track.markers[firstmarker].co
        # lastmarker =
        endframe = track.markers[lastmarker].frame
        endvalue = track.markers[lastmarker].co
        return track, posstab, rotstab, firstmarker, startframe, startvalue, lastmarker, endframe, endvalue

    def get_track_start(self, track):
        firstmarker = 0
        while track.markers[firstmarker].mute:
            firstmarker += 1
            if firstmarker < len(track.markers)-1:
                #print("first break")
                break
        return firstmarker, track.markers[firstmarker].frame

    def get_track_end(self, track):
        lastmarker = len(track.markers)-1
        while track.markers[lastmarker].mute:
            lastmarker -= 1
            if lastmarker < 0:
                break
        return lastmarker, track.markers[lastmarker].frame

    def is_in_collection(self, trackelement):
        # for track in self.tracks:
        #    if trackelement[0] == track[0]:
        #        return True
        return False
    ###callback for ui tracker list
    def make_ui_list(self, context):
        list = []
        for n, track in enumerate(self.tracks):
            list.append(
                (str(n), str(track.name), '1'))
        return list

    ui_track_list: bpy.props.EnumProperty(
        name='Global Presets',  # SingleCoupltypes
        description='ui_list',
        items=make_ui_list)


class VSEpicPropertyGroup(bpy.types.PropertyGroup):

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
    trackscol: bpy.props.PointerProperty(type=VSEpicTrackCol)

    # trackfactor: bpy.props.EnumProperty(items=get_track_list_callback()
    # )

