import FootprintWizardDrawingAids as fpda
import pcbnew
import math

class OutlineDrawingAids:

    flipNone = 0

    def __init__(self, wizard):
        self.draw = wizard.draw
        self.module = wizard.module
        self.buildmessages = wizard.buildmessages
    
    def min(self, v1, v2):
        if v1<v2:
            return v1
        return v2
    
    def max(self, v1, v2):
        if v1>v2:
            return v1
        return v2
    # return intersection point or None if no intersection
    def IntersectSegments(self, p1, p2, p3, p4):
        x=0
        y=1
        
        d = (p1[x]-p2[x])*(p3[y]-p4[y]) - (p1[y]-p2[y])*(p3[x]-p4[x])
#        print "IntersectSegments", p1, p2, p3, p4
#        print "IntersectSegments", "d=", d
        if d==0:
            return None
        
        p = [0, 0]
        p[x] = ((p3[x]-p4[x])*(p1[x]*p2[y]-p1[y]*p2[x])-(p1[x]-p2[x])*(p3[x]*p4[y]-p3[y]*p4[x]))/d
        p[y] = ((p3[y]-p4[y])*(p1[x]*p2[y]-p1[y]*p2[x])-(p1[y]-p2[y])*(p3[x]*p4[y]-p3[y]*p4[x]))/d;
 #       print "IntersectSegments", "p=", p

        if p[x]<self.min(p1[x], p2[x]) or p[x]>self.max(p1[x], p2[x]):
            return None
        if p[x]<self.min(p3[x], p4[x]) or p[x]>self.max(p3[x], p4[x]):
            return None
        if p[y]<self.min(p1[y], p2[y]) or p[y]>self.max(p1[y], p2[y]):
            return None
        if p[y]<self.min(p3[y], p4[y]) or p[y]>self.max(p3[y], p4[y]):
            return None

        # reject intersections on edges
        if (p[x]==p1[x] and p[y]==p1[y]) or (p[x]==p2[x] and p[y]==p2[y]) or (p[x]==p3[x] and p[y]==p3[y]) or (p[x]==p4[x] and p[y]==p4[y]):
            return None
        
        return p

    def PointInRect(self, p, p0, p1):
        x=0
        y=1

        if p[x]>=p0[x] and p[x]<=p1[x] and p[y]>=p0[y] and p[y]<=p1[y]:
            return True
        return False
    
    def Distance(self, p0, p1):
        dx = abs(p0[0]-p1[0])
        dy = abs(p0[1]-p1[1])
        return math.sqrt(dx*dx+dy*dy)
    
    # return a line array containing segments minus intersected zones
    # return None if segment inside pad
    def IntersectPad(self, line, pad, clearance, segments):
        padx = pad.GetBoundingBox().GetX()
        pady = pad.GetBoundingBox().GetY()
        padw = pad.GetBoundingBox().GetWidth()
        padh = pad.GetBoundingBox().GetHeight()
        
        p0 = [padx-clearance, pady-clearance]
        p1 = [padx+padw+clearance, pady-clearance]
        p2 = [padx+padw+clearance, pady+padh+clearance]
        p3 = [padx-clearance, pady+padh+clearance]

        x = 0
        y = 1

        # check if segment entirely in pad
        if self.PointInRect(line[0], p0, p2) and self.PointInRect(line[1], p0, p2):
            return True
        
        # get intersections with edges
        pi = []
        pi.append(self.IntersectSegments(line[0], line[1], p0, p1))
        pi.append(self.IntersectSegments(line[0], line[1], p1, p2))
        pi.append(self.IntersectSegments(line[0], line[1], p2, p3))
        pi.append(self.IntersectSegments(line[0], line[1], p3, p0))
        
        # check if no intersection
        if pi[0] is None and pi[1] is None and pi[2] is None and pi[3] is None:
            return False
        
        # there is one intersection, cut the line by removing the intersected part
        for pline in line:
            # test if point is in rectangle made by two diagonal oposites edges
            if self.PointInRect(pline, p0, p2)==False:
                dist = None
                cp = None
                # point is not inside pin so try to find the nearest intersection point
                for p in pi:
                    if not p is None:
                        if dist is None or self.Distance(pline, p)<dist:
                            dist = self.Distance(pline, p)
                            cp = p
                if not cp is None:
                    # add segment line[0] -> cp
                    segments.append([pline, cp])
        
        return True
    
    def RemovePadsIntersections(self, lines, clearance=pcbnew.FromMM(0.2), minlength=pcbnew.FromMM(0.2)):        
        # loop stops when no more intersection was found
        iline = 0
        while iline<len(lines):
            line = lines[iline]
            iline = iline+1
            for p in self.module.Pads():
                segments = []
                if self.IntersectPad(line, p, clearance, segments)==True:
                     # found an intersection, push it at the bottom of the list and rewind the loop from the beginning
                    lines.remove(line)
                    for s in segments:
                        lines.append(s)
                    iline = 0
                    break
        #=======================================================================
        # # remove standalone segments shorter then minlength
        # iline = 0
        # while iline<len(lines):
        #     line = lines[iline]
        #     iline = iline+1
        #     # check if line shares a common bound
        #     iline2 = 0
        #     share = False
        #     while iline2<len(lines):
        #         line2 = lines[iline2]
        #         iline2 = iline2+1
        #         if iline!=iline2 and (
        #                 (line[0][0]==line2[0][0] and line[0][1]==line2[0][1]) or
        #                 (line[0][0]==line2[0][0] and line[1][1]==line2[1][1]) or
        #                 (line[1][0]==line2[1][0] and line[1][1]==line2[1][1]) or
        #                 (line[1][0]==line2[1][0] and line[0][1]==line2[0][1])
        #             ):
        #             share = True
        #     if share==False and self.Distance(line[0], line[1])<minlength:
        #         # remove segment
        #         lines.remove(line)
        #         iline = 0
        #=======================================================================


    def BoxWithDiagonalAtCorner(self, x, y, w, h,
                                setback=pcbnew.FromMM(1.27), flip=flipNone, 
                                clearance=pcbnew.FromMM(0.2), minlength=pcbnew.FromMM(0.2)):
        """
        Draw a box with a diagonal at the top left corner
        """
        self.draw.TransformFlip(x, y, flip, push=True)

        pts = [[x - w/2 + setback, y - h/2],
               [x - w/2,           y - h/2 + setback],
               [x - w/2,           y + h/2],
               [x + w/2,           y + h/2],
               [x + w/2,           y - h/2]]

        lines = [[pts[0], pts[1]],
                 [pts[1], pts[2]],
                 [pts[2], pts[3]],
                 [pts[3], pts[4]],
                 [pts[4], pts[0]]]

        self.RemovePadsIntersections(lines, clearance, minlength)

        for l in lines:
            self.draw.Line(l[0][0], l[0][1], l[1][0], l[1][1])

        self.draw.PopTransform()
