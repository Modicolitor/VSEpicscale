#from email.utils import encode_rfc2231
import bpy
#from bpy.types import Scene, Image, Object, PropertyGroup, MovieTrackingTrack
#import copy


# def get_track_list_callback(context):
#    items = context.scene.vsepictracks
#    return items


class VSEpicTrackElement(bpy.types.PropertyGroup):
    # track: bpy.props.PointerProperty(name='track')
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
        # self.track = track
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


class VSEpicCommentElement(bpy.types.PropertyGroup):
    comment: bpy.props.StringProperty(default='None')


class VSEpicSegement(bpy.types.PropertyGroup):
    tracks:  bpy.props.CollectionProperty(type=VSEpicTrackElement)
    comments: bpy.props.CollectionProperty(type=VSEpicCommentElement)


class VSEpicTrackCol(bpy.types.PropertyGroup):
    tracks:  bpy.props.CollectionProperty(type=VSEpicTrackElement)
    # list of lists grouping tracks in anschließende gruppen von tracks with pos or rot flag
    segements: bpy.props.CollectionProperty(type=VSEpicSegement)
    # list of tracks for posstabilisation
    postracks: bpy.props.CollectionProperty(type=VSEpicTrackElement)
    # list of tracks for rot/scale stabilisation
    rottracks: bpy.props.CollectionProperty(type=VSEpicTrackElement)
    ####
    ui_comments: bpy.props.CollectionProperty(type=VSEpicCommentElement)
    # ui tracklist at the bottom

    def update(self, context, realtracks):
        self.update_scene_name(context)
        print('alive')
        if len(realtracks) == 0:
            print('no tracks')
            return

        for track in realtracks:
            # self.trackelement = bpy.props.PointerProperty(type=VSEpicTrackElement)
            track, posstab, rotstab, firstmarker, startframe, startvalue, lastmarker, endframe, endvalue = self.get_trackdata(
                track)
            # check whether a track is just changed or renamed or really new
            self.new_or_old(track, posstab, rotstab, firstmarker,
                            startframe, startvalue, lastmarker, endframe, endvalue)

        # check wherther tracks and saved tracks is the same or pop anything with wrong name
        if len(realtracks) != len(self.tracks):
            self.pop_too_much(realtracks)

        # self.tracksegments ist a listoflist of track in segments, it a intermediate to later build the structure in blenders properties
        self.tracksegments = []
        # list of tracks as tuple for ui
        self.make_ui_list(context)
        # guess konfiguration: overlapping tracks, pos/rot decision, grouping for stab panels and final processing
        self.tracksegments = self.make_track_lists()
        # translate track list into segments ----> necessary because I don't wanne refactore function before
        self.fill_tracks(self.tracksegments)
        # self.add_comments(self.segements)
        print(f'self.tracksegments before fill {self.tracksegments}')
        self.Ctlintermediattracksegments(self.tracksegments)

        self.find_solution()
        self.trim_solution(realtracks)

        self.fill_postracks(self.segements)
        self.fill_rottracks(self.segements)

        # self.fill_comments()
        # self.analyse_comments()
    # reduces the
    def find_solution(self):
        # gibts nur ein segment???

        if len(self.segements) == 0:
            return
        elif len(self.segements) == 1:
            for track in self.segements[0].tracks:
                if track.posstab:
                    self.set_only_pos(track, self.segements[0])
                    break

            for track in self.segements[0].tracks:
                if track.rotstab:
                    self.set_only_rot(track, self.segements[0])
                    break
            return

        # anfang müsste auch getestet werden
        # pro segment schau ans ende tr1 und anfang tr2  ob der Track pospositiv ist und mit
        for s, seg in enumerate(self.segements):
            if self.not_last(s, self.segements):
                found = False
                tr1_found = None
                tr2_found = None

                for tr1 in seg.tracks:
                    if tr1.posstab:
                        for tr2 in self.segements[s+1].tracks:
                            if tr2.posstab:
                                overlap, quality, posspec = self.find_overlap(
                                    tr1, tr2)
                                if quality == 'perfect' or quality == 'toolong':
                                    tr1_found = tr1
                                    tr2_found = tr2
                                    found = True
                            if found:
                                break
                    if found:
                        break
                # what happens when nothing ist found ????????????????

                # when something is found
                self.set_only_pos(tr1_found, seg)
                self.set_only_pos(tr2_found, self.segements[s+1])

                # rotation part
                found = False
                tr1_found = None
                tr2_found = None

                for tr1 in seg.tracks:
                    if tr1.rotstab:
                        for tr2 in self.segements[s+1].tracks:
                            if tr2.rotstab:
                                overlap, quality, posspec = self.find_overlap(
                                    tr1, tr2)
                                if quality == 'perfect' or quality == 'toolong':
                                    tr1_found = tr1
                                    tr2_found = tr2
                                    found = True
                            if found:
                                break
                    if found:
                        break
                if tr1_found != None:
                    self.set_only_rot(tr1_found, seg)
                if tr2_found != None:
                    self.set_only_rot(tr2_found, self.segements[s+1])

    def trim_solution(self, realtracks):

        def update_addon_tracks(track, realtrack, frame, pos):
            newendvalue = self.get_realtrack_co_at_frame(
                realtrack, frame)
            if newendvalue != None:
                if pos == 'back':
                    track.endframe = frame
                    track.endvalue = newendvalue
                elif pos == 'front':
                    track.startframe = frame
                    track.startvalue = newendvalue
        # still ignores that both might be too long and not perfekt

        for s, seg in enumerate(self.segements):
            if self.not_last(s, self.segements):
                postrackend = self.get_postrack(seg)
                rottrackend = self.get_rottrack(seg)
                # hack when there is no rottrack
                if rottrackend == None:
                    rottrackend = postrackend
                postrackstart = self.get_postrack(self.segements[s+1])
                rottrackstart = self.get_rottrack(self.segements[s+1])
                # hack when there is no rottrack
                if rottrackstart == None:
                    rottrackstart = postrackstart

                print('schleife 1')
                frame = postrackend.endframe
                test = True
                while test:
                    if rottrackend.endframe >= frame:
                        test = False
                    elif frame == 0:
                        print('follow track failed in loop')
                        test = False
                    else:
                        frame -= 1

                print('schleife 2')
                test = True
                while test:
                    if postrackstart.startframe <= frame+1 and rottrackstart.startframe <= frame+1:
                        test = False
                    elif frame == 0:
                        print('follow track failed in loop')
                        test = False
                    else:
                        frame -= 1

                realpostrackend = self.get_realtrack(postrackend, realtracks)
                realrottrackend = self.get_realtrack(rottrackend, realtracks)
                realpostrackstart = self.get_realtrack(
                    postrackstart, realtracks)
                realrottrackstart = self.get_realtrack(
                    rottrackstart, realtracks)

                # trim to frame in realtracks and segments
                self.trim_realtrack(realpostrackend, frame, 'back')
                self.trim_realtrack(realrottrackend, frame, 'back')
                self.trim_realtrack(realpostrackstart, frame+1, 'front')
                self.trim_realtrack(realrottrackstart, frame+1, 'front')

                update_addon_tracks(
                    postrackend, realpostrackend, frame, 'back')
                update_addon_tracks(
                    rottrackend, realrottrackend, frame, 'back')
                update_addon_tracks(
                    postrackstart, realpostrackstart, frame+1, 'front')
                update_addon_tracks(
                    rottrackstart, realrottrackstart, frame+1, 'front')

        def find_start(startframe, bedingung, pos):
            frame = startframe
            test = True
            while test:
                if bedingung:
                    test = False
                elif frame == 0:
                    print('follow track failed in loop')
                    test = False
                else:
                    if pos == 'front':
                        frame += 1
                    elif pos == 'back':
                        frame -= 1
            return frame

        # trim start
        postrackstart = self.get_postrack(self.segements[0])
        rottrackstart = self.get_rottrack(self.segements[0])
        if rottrackstart == None:
            rottrackstart = postrackstart
        realpostrackstart = self.get_realtrack(postrackstart, realtracks)
        realrottrackstart = self.get_realtrack(rottrackstart, realtracks)
        if realrottrackstart == None:
            rottrackstart = realpostrackstart

        frame = postrackstart.startframe
        frame = find_start(postrackstart.startframe,
                           rottrackstart.startframe <= frame, 'front')

        print(f'-----------Trim start to frame {frame}')
        self.trim_realtrack(realpostrackstart, frame, 'front')
        self.trim_realtrack(realrottrackstart, frame, 'front')

        update_addon_tracks(
            postrackstart, realpostrackstart, frame, 'front')
        update_addon_tracks(
            rottrackstart, realrottrackstart, frame, 'front')

        # trim end
        postrackend = self.get_postrack(self.segements[-1])
        rottrackend = self.get_rottrack(self.segements[-1])
        if rottrackend == None:
            rottrackend = postrackend
        print(f'--Trim end initial frame {postrackend.endframe}')

        realpostrackend = self.get_realtrack(postrackend, realtracks)
        realrottrackend = self.get_realtrack(rottrackend, realtracks)

        frame = find_start(postrackend.endframe,
                           rottrackend.endframe >= frame, 'back')

        print(f'-----------Trim end to frame {frame}')

        self.trim_realtrack(realpostrackend, frame, 'back')
        self.trim_realtrack(realrottrackend, frame, 'back')

        update_addon_tracks(
            postrackend, realpostrackend, frame, 'back')
        update_addon_tracks(
            rottrackend, realrottrackend, frame, 'back')

    def trim_realtrack(self, track, frame, position):
        # position is 'front' or 'back'
        if position == 'front':
            for marker in track.markers:
                if marker.frame < frame:
                    marker.mute = True
        elif position == 'back':
            for marker in track.markers:
                if marker.frame > frame:
                    marker.mute = True

    def set_only_pos(self, tr, seg):
        for tracks in seg.tracks:
            tracks.posstab = False

        tr.posstab = True
        tr.rotstab = False

    def get_realtrack(self, track, realtracks):
        if track != None:
            for realtrack in realtracks:
                if realtrack.name == track.name:
                    return realtrack
        else:
            return None

    def set_only_rot(self, tr, seg):
        for tracks in seg.tracks:
            tracks.rotstab = False

        tr.rotstab = True
        tr.posstab = False

    def not_last(self, n, list):
        return len(list)-1 != n

    def analyse_comments(self):
        self.ui_comments.clear()
        for n, seg in enumerate(self.segements):
            print(f'segment number {n}')
            has_toolong = False
            has_tooshort = False
            next_perfect = False
            for com in seg.comments:
                com = com.comment
                print(f'com in analyses {com}')
                if 'toolong' in com:
                    has_toolong = True
                if 'tooshort' in com:
                    has_tooshort = True

            if has_toolong:
                newcom = self.ui_comments.add()
                newcom.name = str(n)+'long'
                newcom.comment = 'Seg ' + \
                    str(n) + ' has long elements, but is fixable'
            if has_tooshort:
                newcom = self.ui_comments.add()
                newcom.name = str(n)+'short'
                newcom.comment = 'Seg ' + \
                    str(n) + ' has short elements, please extend Tracks to the same length'
            if not has_tooshort and not has_toolong:
                newcom = self.ui_comments.add()
                newcom.name = str(n)+'perfect'
                newcom.comment = 'Seq ' + str(n) + 'Tracks are perfect!'

            # search for perfect in the next one
            perfect = False
            perfect_index = -1
            has_toolongnext = False
            has_tooshortnext = False
            if n != len(self.segements)-1:
                for thistrack in seg.tracks:
                    for nexttrack in self.segements[n+1].tracks:
                        overlap, quality, specpos = self.find_overlap(
                            thistrack, thistrack)
                        if quality == 'perfect':
                            perfect = True
                            perfect_index = seg.tracks.find(thistrack.name)
                        if quality == 'tooshort':
                            has_tooshortnext = True
                        if quality == 'toolong':
                            has_toolongnext = True

                newcom = self.ui_comments.add()
                newcom.name = str(n)+'Next'
                if perfect and not has_toolongnext and not has_tooshortnext:
                    newcom.comment = 'Transision Seq' + \
                        str(n) + ' to ' + str(n+1) + ' is perfect!'
                    continue
                if perfect and has_toolongnext and not has_tooshortnext:
                    newcom.comment = 'Transision Seq' + \
                        str(n) + ' to ' + \
                        ' str(n+1)' 'is perfect and some too long!'
                    continue
                if perfect and has_toolongnext and has_tooshortnext:
                    newcom.comment = 'Transision Seq' + \
                        str(n) + ' to ' + \
                        ' str(n+1)' 'is perfect and some too long, the short one might be ignored!'
                    continue
                if not perfect and has_toolongnext and not has_tooshortnext:
                    newcom.comment = 'Transision Seq' + \
                        str(n) + ' to ' + \
                        ' str(n+1)' 'is too long but would work.'
                    continue
                if not perfect and has_toolongnext and has_tooshortnext:
                    newcom.comment = ' Transision Seq' + \
                        str(n) + ' to ' + \
                        ' str(n+1)' 'is too long or too short. the short one might make a problem'
                    continue
                newcom.comment = ' Transision Seq' + \
                    str(n) + ' to ' + \
                    ' str(n+1)' 'something in me is wrong'

    def fill_comments(self):
        if len(self.segements) != 0:
            for seg in self.segements:
                seg.comments.clear()
                for n, track in enumerate(seg.tracks):
                    print(len(seg.tracks))
                    if n != len(seg.tracks)-1:
                        overlap, quality, posspec = self.find_overlap(
                            seg.tracks[n], seg.tracks[n+1])
                        com = seg.comments.add()
                        com.name = seg.name
                        comment = quality
                        if quality != 'None':
                            comment += posspec
                        com.comment = comment

    def fill_tracks(self, listoflists):
        # print(listoflists)
        self.segements.clear()
        for list in listoflists:
            seg = self.segements.add()
            seg.name = str(list[0].startframe) + "-" + str(list[0].endframe)
            for track in list:
                newtrack = seg.tracks.add()
                # print(track)
                # print(track.name)
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
        for track in segement.tracks:
            if track.rotstab:
                selection.append(track)

        # ist that necessary after find soulution refactor
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
                f'segment has no rotstab')
            return None

    def get_postrack(self, segement):
        selection = []
        for track in segement.tracks:
            if track.posstab:
                selection.append(track)
        le = len(selection)

        print(f'postracks selection list {selection}')
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
        # track.track = newtrack.track
        newtrack.name = track.name
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

        if len(overviewlist) == 0:
            print('NOOOOO TRACKS for building Trackssegements!! ')
        elif len(overviewlist) == 1:
            self.tracksegments.append([overviewlist[0]])

        complete = False
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
                    # print segment state at this point for bug fixing
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
            print('contibranch')
            # can you find overlap with any segment
            foundoverlap = False
            trnumberoverlap = 0
            for tr in oplist[:]:
                print(f'test {tr} has an overlap with any segment')
                for n, segement in enumerate(self.tracksegments[:]):
                    print(f' testing segment {n}  {segement[0].name}')
                    otype0, quality0, specifypos0 = self.find_overlap(
                        segement[0], tr)
                    print(f'sub {otype0} {quality0} {specifypos0}')
                    # notes = quality0 + specifypos0
                    if otype0 == 'overlap':
                        segement.insert(-1, tr)
                        print('found a place overlapping')
                        oplist.remove(tr)
                        foundoverlap = True
                        trnumberoverlap += 1
                        break
                        # segement[-1] += notes

            if foundoverlap:
                print('len oplist after found overlap {len(oplist)}')
                if trnumberoverlap == 2:
                    print('overlap for both')
                    return

            print(f' oplist after conti overlap check {oplist}')
            # when there is no overlap then make add a new segment when perfect
            for tr in oplist:
                for n, segement in enumerate(self.tracksegments[:]):
                    otype0, quality0, specifypos0 = self.find_overlap(
                        segement[0], tr)
                    print(f'sub {otype0} {quality0} {specifypos0}')
                    # obligatorisches if
                    if otype0 == 'conti':
                        if quality0 == 'perfect' and specifypos0 == 'front':
                            # gibts eins davor
                            self.tracksegments.insert(n, [tr])
                            oplist.remove(tr)
                            print('found a the front position ')
                            break
                        elif quality0 == 'perfect' and specifypos0 == 'back':
                            # test if the next segments overlaps
                            if n != len(self.tracksegments)-1:

                                self.tracksegments.insert(n+1, [tr])
                                oplist.remove(tr)
                                break
                                print('found back position under else')

            # jetzt haben wir bis zum schluß nichts gefunden was perfect drauf oder davor liegt
            # bleibt nur noch alles ist noch zerstückelt aus ein ander oder alles nach ganz hinten
            # ach fuck ich frag einfach einzeln
            if tr1 in oplist:
                got_front = False  # when there is no front than they are definetly at the back
                front_index = -100
                for n, segement in enumerate(self.tracksegments[:]):
                    otype0, quality0, specifypos0 = self.find_overlap(
                        segement[0], tr1)
                    if specifypos0 == 'front':
                        got_front = True
                        self.tracksegments.insert(n, [tr1])

                if not got_front:
                    if specifypos == 'back':
                        self.tracksegments.append([tr1])

            if tr2 in oplist:
                got_front = False  # when there is no front than they are definetly at the back
                front_index = -100
                for n, segement in enumerate(self.tracksegments[:]):
                    otype0, quality0, specifypos0 = self.find_overlap(
                        segement[0], tr2)
                    if specifypos0 == 'front':
                        got_front = True
                        self.tracksegments.insert(n, [tr2])

                if not got_front:
                    if specifypos == 'back':
                        self.tracksegments.append([tr2])

        print('reached the end')

    def is_trackSegcomplete(self):
        tracks = self.tracks[:]
        for seg in self.tracksegments:
            for t in seg:
                if t in tracks:
                    print(
                        'ist das überhaupt aktiv, sieht nicht funktionierend aus mit den list, aber auch nicht schlimm')
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

    def update_scene_name(self, context):
        context.scene.vsepicprops.scenename == context.scene.name

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
                specifypos = 'None'
                return overlaptype, quality, specifypos
        # overlap but too long in both directions
        if start1 > start2:
            if end1 < end2:
                overlaptype = 'overlap'
                quality = 'toolong'
                specifypos = 'both'
                return overlaptype, quality, specifypos
        # overlap but too short in both directions
        if start1 < start2:
            if end1 > end2:
                overlaptype = 'overlap'
                quality = 'tooshort'
                specifypos = 'both'
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

    def pop_too_much(self, realtracks):
        # fill a new list with all trackelements
        testlist = []
        for ele in self.tracks:
            testlist.append(ele)

        print(f'test list pre (all tracks) {testlist}')
        # check by name whether its in realtracks --> pop from that list
        for n, ele in enumerate(testlist[:]):
            print(f'n {n}')
            for t in realtracks[:]:
                if ele.name == t.name:
                    print(
                        f'found trackelement existing in n {n} elename {ele.name} {t.name}')
                    testlist.pop(n)

        # print(f'test list post {testlist}')
        # after all, pop all remaining elements in list from self.tracks
        # print(
        #    f'Before track removal Testlist {testlist} and -------- {self.tracks}')

        # there must be a better way, but without the while not all tracks get removed
        namelist = []
        for ele in testlist[:]:
            namelist.append(ele.name)
        for name in namelist:
            self.tracks.remove(self.tracks.find(name))

        if len(self.tracks) != len(realtracks):
            print(
                f'----Warning still not all removed from testlist----{testlist}')

    def new_or_old(self, track, posstab, rotstab, firstmarker,
                   startframe, startvalue, lastmarker, endframe, endvalue):
        for ele in self.tracks:
            # same name exist, update all but not posstab and rotstab
            if ele.name == track.name:  # self.is_real_eq_ele(ele, track):  #
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

    def is_real_eq_ele(self, ele, track):  # ele.name == track.name:
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
        return False

    def get_trackdata(self, track):

        firstmarker, startframe = self.get_track_start(track)
        lastmarker, endframe = self.get_track_end(track)

        # just the defaults
        posstab = True
        rotstab = True
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

    def get_realtrack_co_at_frame(self, track, frame):
        for marker in track.markers:
            if marker.frame == frame:
                return marker.co
        return None

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
        name='Tracks',  # SingleCoupltypes
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
    scenename: bpy.props.StringProperty(default='None')
    show_error_marks: bpy.props.BoolProperty(
        name='show error marks', description='show error marks handler hack', default=True)
    check_coverage: bpy.props.BoolProperty(
        name='Check Coverage', description='', default=True)
    check_blend_type: bpy.props.BoolProperty(
        name='Check Blend Type', description='', default=True)

    # trackfactor: bpy.props.EnumProperty(items=get_track_list_callback()
    # )
