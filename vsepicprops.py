from email.utils import encode_rfc2231
import bpy
from bpy.types import Scene, Image, Object, PropertyGroup, MovieTrackingTrack


# def get_track_list_callback(context):
#    items = context.scene.vsepictracks
#    return items


class VSEpicTrackElement(bpy.types.PropertyGroup):
    #track: bpy.props.PointerProperty(name='track')
    posstab: bpy.props.BoolProperty(name='StabilizePosition', default=True)
    rotstab: bpy.props.BoolProperty(name='StabilizeRotation', default=True)
    firstmarker: bpy.props.IntProperty(name='firstmarker', default=-100)
    startframe: bpy.props.IntProperty(name='startframe', default=-100)
    startvalue: bpy.props.FloatVectorProperty(
        name='startvalue', default=(0.0, 0.0), step=2, precision=2, size=2, subtype='COORDINATES')
    lastmarker: bpy.props.IntProperty(name='startframe', default=-100)
    endframe: bpy.props.IntProperty(name='startframe', default=-100)
    endvalue: bpy.props.FloatVectorProperty(
        name='startvalue', default=(0.0, 0.0), step=2, precision=2, size=2, subtype='COORDINATES')

    def set_track(self, track, posstab, rotstab, firstmarker, startframe, startvalue, lastmarker, endframe, endvalue):
        print('---------------------------------------------------------------')
        print(
            f'set a track {self.name} startvalue {startvalue} endvalue {endvalue}')
        #self.track = track
        self.posstab = posstab
        self.rotstab = rotstab
        self.startframe = startframe
        self.startvalue = startvalue

        self.endframe = endframe
        print(f'endvalue in set track {endvalue}')
        self.endvalue = endvalue
        self.firstmarker = firstmarker
        self.lastmarker = lastmarker
        print(
            f'new trackvalues {self.name} startvalue {self.startvalue} endvalue {self.endvalue}')
        print('---------------------------------------------------------------')
        return self


class VSEpicSegement(bpy.types.PropertyGroup):
    tracks:  bpy.props.CollectionProperty(type=VSEpicTrackElement)


class VSEpicTrackCol(bpy.types.PropertyGroup):
    tracks:  bpy.props.CollectionProperty(type=VSEpicTrackElement)
    # list of lists grouping tracks in anschließende gruppen von tracks with pos or rot flag
    segements: bpy.props.CollectionProperty(type=VSEpicSegement)
    # list of tracks for posstabilisation
    postracks: bpy.props.CollectionProperty(type=VSEpicTrackElement)
    # list of tracks for rot/scale stabilisation
    rottracks: bpy.props.CollectionProperty(type=VSEpicTrackElement)

    def update(self, context, tracks):

        print('alive')
        for track in tracks:
            print(track.name)
            # self.trackelement = bpy.props.PointerProperty(type=VSEpicTrackElement)
            track, posstab, rotstab, firstmarker, startframe, startvalue, lastmarker, endframe, endvalue = self.get_trackdata(
                track)
            print(endvalue)
            # print(adf)
            # trackelement = [track, posstab, rotstab, firstmarker,
            #                startframe, startvalue, lastmarker, endframe, endvalue]

            # check whether a track is just changed or renamed or really new
            trackelement = self.new_or_old(track, posstab, rotstab, firstmarker,
                                           startframe, startvalue, lastmarker, endframe, endvalue)

        # check wherther tracks and saved tracks is the same or pop anything with wrong name
        if len(tracks) != len(self.tracks):
            self.pop_too_much(tracks)

        self.tracksegments = []
        # list of tracks as tuple for ui
        self.make_ui_list(context)
        # guess konfiguration: overlapping tracks, pos/rot decision, grouping for stab panels and final processing
        self.tracksegments = self.make_track_lists()
        # translate track list into segments ----> necessary because I don't wanne refactore function before
        self.fill_tracks(self.tracksegments)
        self.fill_postracks(self.tracksegments)
        self.fill_rottracks(self.tracksegments)

    def fill_tracks(self, listoflists):
        # print(listoflists)
        self.segements.clear()
        for list in listoflists:
            seg = self.segements.add()
            seg.name = str(list[0].startframe) + "-" + str(list[0].endframe)
            for track in list:
                newtrack = seg.tracks.add()
                print(track)
                print(track.name)
                # track, posstab, rotstab, firstmarker, startframe, startvalue, lastmarker, endframe, endvalue = self.get_trackdata(
                #    track)
                # newtrack.set_track(track, posstab, rotstab, firstmarker,
                #                   startframe, startvalue, lastmarker, endframe, endvalue)
                self.copy_track_data(track, newtrack)

    def fill_postracks(self, listoflists):
        self.postracks.clear()
        for segement in listoflists:
            oritrack = self.get_postrack(segement)
            print(f'ortrack in postrack is {oritrack}')
            if oritrack != None:
                newtrack = self.postracks.add()
                newtrack.name = oritrack.name
                self.copy_track_data(oritrack, newtrack)

    def fill_rottracks(self, listoflists):
        self.rottracks.clear()
        for list in listoflists:
            oritrack = self.get_rottrack(list)
            print(f'oritrack in rottrack is {oritrack}')
            if oritrack != None:
                newtrack = self.rottracks.add()
                newtrack.name = oritrack.name
                self.copy_track_data(oritrack, newtrack)

    def get_rottrack(self, segement):
        selection = []
        for track in segement:
            if track.rotstab:
                selection.append(track)
        le = len(selection)
        if le == 1:
            return selection[0]
        elif le > 1:
            print(
                f'segment {segement[0].startframe} - {segement[0].endframe}  has more than 1 posstab choose first')
            left = len(selection)
            sel = selection[:]
            for n, tr in enumerate(sel):
                for postrack in self.postracks:
                    if postrack.startvalue == tr.startvalue:
                        selection.remove(tr)
                        left = len(selection)
                        if left == 1:
                            break
                if left == 1:
                    break
            print(
                f'Choose {segement[0]} as rotstab in  selection 0 {selection[0]}')
            return selection[0]
        elif le == 0:
            print(
                f'segment {segement[0].startframe} - {segement[0].endframe} has no rotstab')
            return None

    def get_postrack(self, segement):
        selection = []
        for track in segement:
            if track.posstab:
                selection.append(track)
        le = len(selection)

        if le == 1:
            return selection[0]
        elif le > 1:
            print(
                f'segment {selection[0].startframe} - {selection[0].endframe} has more than 1 posstab choose first return []')
            return selection[0]
        elif le == 0:
            print(
                f'segment {selection[0].startframe} - {selection[0].endframe}  has no posstab')
            return None

    def copy_track_data(self, track, newtrack):
        #track.track = newtrack.track
        newtrack.posstab = track.posstab
        newtrack.rotstab = track.rotstab
        newtrack.firstmarker = track.firstmarker
        newtrack.startframe = track.startframe
        newtrack.startvalue[0] = track.startvalue[0]
        newtrack.startvalue[1] = track.startvalue[1]
        newtrack.lastmarker = track.lastmarker
        newtrack.endframe = track.endframe
        newtrack.endvalue[0] = track.endvalue[0]
        newtrack.endvalue[1] = track.endvalue[1]

    def make_track_lists(self):
        # self.tracksegments = []
        overviewlist = []
        for t in self.tracks:
            overviewlist.append(t)

        for tr1 in overviewlist:
            for tr2 in overviewlist:
                if tr1 != tr2:
                    # returns group of
                    overlaptype, quality, specifypos = self.find_overlap(
                        tr1, tr2)
                    print('---------------')
                    print(f'tr1 {tr1.name} tr2 {tr2.name}')
                    print(f'overlaptype {overlaptype}')
                    print(f'overlaptype {quality}')
                    print(f'overlaptype {specifypos}')
                    print('---------------')

                    self.put_target_segment(
                        tr1, tr2, overlaptype, quality, specifypos)
                    # [[t1, t2],[t4,t5], []]
                    self.Ctlintermediattracksegments(self.tracksegments)
                    complete = self.is_trackSegcomplete()
                    if complete:
                        break
            if complete:
                break
        return self.tracksegments

    def put_target_segment(self, tr1, tr2, overlaptype, quality, specifypos):
        # alles leer
        # Notes = quality+specifypos
        if len(self.tracksegments) == 0:
            if overlaptype == 'overlap':
                self.tracksegments.append([tr1, tr2])
                print(
                    f'put intial overlap for these {tr1.name} and {tr2.name}')
                print(f'tracksegement after initial{self.tracksegments}')
                return
            elif overlaptype == 'conti':
                if specifypos == 'front':
                    self.tracksegments.append([tr2])
                    self.tracksegments.append([tr1])
                    print(
                        'put initial conti front for these {tr1.name} and {tr2.name}')
                    print(f'tracksegement after initial{self.tracksegments}')
                elif specifypos == 'back':
                    self.tracksegments.append([tr1])
                    self.tracksegments.append([tr2])
                    print(
                        'put initial conti back for these {tr1.name} and {tr2.name}')
                    print(f'tracksegement after initial{self.tracksegments}')

        # nicht leer
        # gibts die schon ?
        oplist = [tr1, tr2]
        tr1_in = self.is_in_targetseqments(tr1)
        tr2_in = self.is_in_targetseqments(tr2)

        if tr1_in:
            oplist.remove(tr1)
        if tr2_in:
            oplist.remove(tr2)
        # beide schon drin
        if len(oplist) == 0:
            print('beide schon drin')
            return

        print(f'oplist {oplist}')

        if overlaptype == 'overlap':
            # tr1 and tr2 overlapping and we find a segment that overlapps with them
            for segement in self.tracksegments[:]:
                otype, oquality, ospecifypos = self.find_overlap(
                    segement[0], tr1)
                if otype == 'overlap':
                    if not tr1_in:
                        segement.insert(-1, tr1)
                        print('put 3')

                    if not tr2_in:
                        segement.insert(-1, tr2)

                    print('put 4')
                    return
            if len(oplist) == 2:
                # tr1 and tr2 overlapping and we find a spot for the segment
                # didn't find a existing segment --> make a new segment, find a place for it
                for n, segement in enumerate(self.tracksegments[:]):
                    otype0, quality0, specifypos0 = self.find_overlap(
                        self.tracksegments[n], tr1)
                    if quality0 == 'perfect':
                        if specifypos0 == 'front':
                            self.tracksegments.insert(n, [tr1, tr2])
                        elif specifypos0 == 'back':
                            self.tracksegments.insert(n+1, [tr1, tr2])
                        return
                    # !!!!!!!!!!hmmmm think about not perfect results

                    # way before first
                    if n == 0 and specifypos0 == 'front':
                        self.tracksegments.insert(n, [tr1, tr2])
                        return
                    # way after last
                    # letzte bedingung zuviel?
                    if n == len(self.tracksegments) and specifypos0 == 'back':
                        self.tracksegments.insert(n, [tr1, tr2])
                        return
        elif overlaptype == 'conti':
            for tr in oplist:
                for n, segement in enumerate(self.tracksegments[:]):
                    print(f' {segement[0]}')
                    otype0, quality0, specifypos0 = self.find_overlap(
                        segement[0], tr)
                    print(f'sub {otype0} {quality0} {specifypos0}')
                    # notes = quality0 + specifypos0
                    if otype0 == 'overlap':
                        segement.insert(-1, tr)
                        print('found a place overlapping')
                        break
                        # segement[-1] += notes
                    elif otype0 == 'conti':
                        if quality0 == 'perfect' and specifypos0 == 'front':
                            # gibts eins davor
                            self.tracksegments.insert(n, [tr])
                            print('found a the front position ')
                            break

                        elif quality0 == 'perfect' and specifypos0 == 'back':
                            # test if the next segments overlaps
                            if n != len(self.tracksegments):
                                o, q, s = self.find_overlap(
                                    tr, self.tracksegments[n+1][0])
                                # is the next overlapping otherwise insert
                                if o == 'overlap' and q == 'perfect':
                                    self.tracksegments[n+1].insert(-1, tr)
                                    break
                                    print('found back position ')
                                    # self.tracksegments[n+1][-1] += notes
                                else:
                                    # seems to be nothing good behind
                                    self.tracksegments.insert(n+1, [tr])
                                    break
                                    print('found back position under else')
                            else:
                                self.tracksegments.append([tr])
                                break

        print('reached the end')

    def is_trackSegcomplete(self):
        tracks = self.tracks[:]
        for seg in self.tracksegments:
            for t in seg:
                if t in tracks:
                    tracks.remove(t)
                    if len(tracks) == 0:
                        break
        return len(tracks) == 0

    def Ctlintermediattracksegments(self, tracksegments):
        for n, seg in enumerate(tracksegments):
            print(f'Segment {n}')
            for track in seg:
                print(f'      Segment {track.name}')

    def is_in_targetseqments(self, tr1):
        if len(self.tracksegments) == 0:
            return False
        for tracksegment in self.tracksegments:
            for track in tracksegment:
                if track == tr1:
                    return True
        return False

    def find_overlap(self, tr1, tr2):
        # track2 relative to track1 , front means track2 is before track1
        # overlaptype = conti, overlap;  quality =  perfect, tooshort, toolong; specifypos = front, back
        start1 = tr1.startframe
        end1 = tr1.endframe

        start2 = tr2.startframe
        end2 = tr2.endframe

        # perfect overlap: gleicher start gleiches ende
        if start1 == start2:
            if end1 == end2:
                overlaptype = 'overlap'
                quality = 'perfect'
                specifypos = None
                return overlaptype, quality, specifypos
        # perfect conti front
        if start1-1 == end2:
            overlaptype = 'conti'
            quality = 'perfect'
            specifypos = 'front'
            return overlaptype, quality, specifypos
        # perfect conti back
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
        # overlap too long front
        if end1 == end2:
            if start2 < start1:
                overlaptype = 'overlap'
                quality = 'toolong'
                specifypos = 'front'
                return overlaptype, quality, specifypos
        # overlap too long back
        if start1 == start2:
            if end1 < end2:
                overlaptype = 'overlap'
                quality = 'toolong'
                specifypos = 'back'
                return overlaptype, quality, specifypos
        # overlap too short front
        if end1 == end2:
            if start2 > start1:
                overlaptype = 'overlap'
                quality = 'tooshort'
                specifypos = 'front'
                return overlaptype, quality, specifypos
        # overlap too short back
        if start1 == start2:
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
                # ele.posstab =  posstab
                # ele.rotstab = rotstab
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
                    # ele.posstab =  posstab
                    # ele.rotstab = rotstab
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
                    # ele.posstab =  posstab
                    # ele.rotstab = rotstab
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
        newtrack.endvalue = (2, 3)
        newtrack.set_track(track, posstab, rotstab, firstmarker,
                           startframe, startvalue, lastmarker, endframe, endvalue)

    def get_trackdata(self, track):

        firstmarker, startframe = self.get_track_start(track)
        lastmarker, endframe = self.get_track_end(track)

        # just the defaults
        posstab = True
        rotstab = False
        # firstmarker = firstmarker
        # startframe = startframe
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
                # print("first break")
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

    # callback for ui tracker list
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
