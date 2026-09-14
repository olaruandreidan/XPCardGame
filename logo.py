"""Parametric vector monogram from the Marriage XP sketch.

Every visible edge is a filled path. Circular arcs use cubic Bezier segments
(maximum radial error < 0.028% per quarter-circle). No tracing or raster image.
Geometry uses a downward-y coordinate system, like SVG.
"""
import math
from pathlib import Path

ARM_RADIUS = 128.0
BOWL_RADIUS = 68.0
THICKNESS = 44.0
STEM_BOTTOM = 444.0
LEFT_CENTER = (26.0, 170.0)
BOWL_CENTER_Y = 244.0
VIEWBOX = (0, 0, 338, 468)

# Version 1b: version 1 with one radius shared by all four arm circles. The P
# circle sets that radius, so the three oversized arcs come down to meet it, and
# a straight section through the middle gives back the height the smaller arcs
# would otherwise lose. Each arc still joins the stem where its tangent is
# vertical, which is where a band is exactly THICKNESS wide, so every join stays
# flush and smooth. The four circle centres sit at (axis +/- radius) on the two
# junction rows; the lower right one runs the whole way round as the bowl.
V1B_RADIUS = 78.0
V1B_AXIS = LEFT_CENTER[0]+ARM_RADIUS
V1B_TOP = 20.0  # Top edge of the mark, and V1B_X_HEIGHT below it, as in version 1.
V1B_X_HEIGHT = 300.0
# Degrees each open arc carries on past the vertical end cap a quarter turn
# would give it. The extra sweep lengthens the three arms and tilts their cut
# ends; the closed bowl is unaffected.
V1B_ARC_EXTRA = 25.0
# The stem runs this far up underneath the arms. Their closing edge is a
# horizontal line exactly the stem's width, so butting the two leaves a
# composited hairline; above the junction the arms flare wider than the stem,
# which hides the overlap completely.
V1B_OVERLAP = THICKNESS/4
V1B_TOP_JOIN = V1B_TOP+V1B_RADIUS+THICKNESS/2
V1B_MIDDLE = V1B_X_HEIGHT-2*(V1B_RADIUS+THICKNESS/2)  # Straight run between the junctions.
V1B_STEM_BOTTOM = STEM_BOTTOM
# Breathing room around the mark for the loose viewBox. The tight box moves
# with the radius and the extra sweep, so the loose one is derived, not fixed.
V1B_PADDING = 26.0

# Version 2: raised loop, open crescent and outlined, upright stem.
V2_ARM_RADIUS = 92.0
V2_THICKNESS = 44.0
V2_LEFT_CENTER = (36.0, 132.0)
# One width governs every open stroke and every opening between them: the
# inner right ring, the outer ring, the stem outline, the crescent gap and the
# stem's hollow. The bowl's annular zone, from the circular opening out to the
# silhouette, is exactly the arm weight, so splitting that weight in three
# makes ring, gap and ring fill it edge to edge; the same third splits the stem
# into outline, hollow and outline.
V2_OUTLINE = V2_THICKNESS/3
V2_LOOP_THICKNESS = V2_OUTLINE
# The opening sits flush with the arm's inner edge, so it stays one clean
# circle across both the solid left half of the bowl and the open right half.
V2_COUNTER_RADIUS = V2_ARM_RADIUS-V2_THICKNESS/2
V2_LOOP_RADIUS = V2_COUNTER_RADIUS+V2_LOOP_THICKNESS/2
V2_CRESCENT_GAP = (V2_ARM_RADIUS+V2_THICKNESS/2
                   - V2_OUTLINE - V2_COUNTER_RADIUS - V2_LOOP_THICKNESS)
# 99 below the bowl, a little under half its diameter. The sketch runs longer,
# nearer 154; raise this to go back to it.
V2_STEM_BOTTOM = 345.0
# Zero keeps the stem plumb. Its axis is cx+V2_ARM_RADIUS, the waist where the
# two arm circles meet, so upright and centred on the junction are the same
# thing. A positive value leans the foot left; the geometry still holds.
V2_STEM_LEAN = 0.0
V2_VIEWBOX = (12, -6, 346, 430)

# Version 3: a genuine capital P, tilted over the outlined diagonal of an X.
# The P's continuous stem is the other X diagonal. Its D-shaped bowl has a
# flat inner left edge and a circular right edge, all in the P's own frame.
# One weight governs the stem and the top, bottom and curved bowl strokes.
V3_THICKNESS = 56.0
V3_OUTLINE = 14.0
V3_TILT = 32.0  # Degrees clockwise from an upright P; X angles are mirrored.
V3_CROSSING = (170.0, 280.0)
V3_ARM_LENGTH = 200.0  # Equal centre-line distance from the crossing to all four ends.
V3_UPPER_ARM = V3_ARM_LENGTH
V3_LOWER_ARM = V3_ARM_LENGTH
V3_UPPER_STEM = V3_ARM_LENGTH
V3_CORNER_RADIUS = 14.0  # Round tips and counters; X crossing notches stay sharp.
V3_BOWL_RADIUS = 82.0  # Outer half-circle; the bowl is twice this tall.
V3_BOWL_STRAIGHT = 76.0  # Distance from the P's left edge to the arc centre.
V3_PADDING = 26.0


def arc(cx, cy, radius, start, end):
    count = max(1, math.ceil(abs(end-start)/90))
    result = []
    for i in range(count):
        a = math.radians(start+(end-start)*i/count)
        b = math.radians(start+(end-start)*(i+1)/count)
        k = 4/3*math.tan((b-a)/4)
        result.append(("C", cx+radius*(math.cos(a)-k*math.sin(a)),
                       cy+radius*(math.sin(a)+k*math.cos(a)),
                       cx+radius*(math.cos(b)+k*math.sin(b)),
                       cy+radius*(math.sin(b)-k*math.cos(b)),
                       cx+radius*math.cos(b), cy+radius*math.sin(b)))
    return result


def point(cx, cy, radius, angle):
    a = math.radians(angle)
    return cx+radius*math.cos(a), cy+radius*math.sin(a)


def band(cx, cy, radius, start, end, thickness=None):
    thickness = THICKNESS if thickness is None else thickness
    outer, inner = radius+thickness/2, radius-thickness/2
    return [("M", *point(cx, cy, outer, start)), *arc(cx, cy, outer, start, end),
            ("L", *point(cx, cy, inner, end)), *arc(cx, cy, inner, end, start), ("Z",)]


def bar(x0, y0, x1, y1, thickness, wall=None):
    """A straight bar along a centre line. A wall width hollows it out."""
    length = math.hypot(x1-x0, y1-y0)
    ux, uy = (x1-x0)/length, (y1-y0)/length
    nx, ny = -uy*thickness/2, ux*thickness/2
    path = [("M", x0+nx, y0+ny), ("L", x1+nx, y1+ny),
            ("L", x1-nx, y1-ny), ("L", x0-nx, y0-ny), ("Z",)]
    if wall:
        inset = 1-2*wall/thickness
        gx, gy = nx*inset, ny*inset
        ax, ay, bx, by = x0+ux*wall, y0+uy*wall, x1-ux*wall, y1-uy*wall
        # Opposite winding for the inner contour makes the bar genuinely hollow.
        path += [("M", ax+gx, ay+gy), ("L", ax-gx, ay-gy),
                 ("L", bx-gx, by-gy), ("L", bx+gx, by+gy), ("Z",)]
    return path


def geometry():
    cx, cy = LEFT_CENTER
    stem = cx+ARM_RADIUS
    half = THICKNESS/2
    if not 0 < THICKNESS < 2*BOWL_RADIUS < 2*ARM_RADIUS:
        raise ValueError("Use 0 < thickness < 2*bowl radius < 2*arm radius.")
    return [
        band(cx, cy, ARM_RADIUS, -90, 90),
        band(cx+2*ARM_RADIUS, cy, ARM_RADIUS, 180, 270),
        [("M", stem-half, cy), ("L", stem+half, cy),
         ("L", stem+half, STEM_BOTTOM), ("L", stem-half, STEM_BOTTOM), ("Z",)],
        band(stem+BOWL_RADIUS, BOWL_CENTER_Y, BOWL_RADIUS, 0, 360),
    ]


def geometry_v1b():
    radius, half = V1B_RADIUS, THICKNESS/2
    axis, top = V1B_AXIS, V1B_TOP_JOIN
    low, extra = top+V1B_MIDDLE, V1B_ARC_EXTRA
    if not 0 < THICKNESS < 2*radius:
        raise ValueError("Version 1b needs a band thinner than the arm circles.")
    if V1B_MIDDLE < 0 or V1B_STEM_BOTTOM <= low:
        raise ValueError("Version 1b needs a straight middle and a stem below it.")
    # The overlap has to stay under the arms: past this depth the two upper
    # outer edges no longer reach each other and the stem would show through.
    if not 0 <= V1B_OVERLAP < math.sqrt((radius+half)**2-radius**2):
        raise ValueError("V1B_OVERLAP must stay within the arms' overlap above the junction.")
    if not 0 <= extra < 90:
        raise ValueError("V1B_ARC_EXTRA must be at least 0 and under 90 degrees.")
    return [
        band(axis-radius, top, radius, -90-extra, 0),
        band(axis+radius, top, radius, 180, 270+extra),
        band(axis-radius, low, radius, 0, 90+extra),
        band(axis+radius, low, radius, 0, 360),
        [("M", axis-half, top-V1B_OVERLAP), ("L", axis+half, top-V1B_OVERLAP),
         ("L", axis+half, V1B_STEM_BOTTOM), ("L", axis-half, V1B_STEM_BOTTOM), ("Z",)],
    ]


def geometry_v2():
    cx, cy = V2_LEFT_CENTER
    radius, weight = V2_ARM_RADIUS, V2_THICKNESS
    stem = cx+radius
    loop = cx+2*radius
    outer_radius = V2_LOOP_RADIUS+V2_LOOP_THICKNESS/2+V2_CRESCENT_GAP+V2_OUTLINE/2
    if not (0 < V2_OUTLINE < weight/2 and 0 < V2_LOOP_THICKNESS < 2*V2_LOOP_RADIUS
            and V2_STEM_BOTTOM > cy+2*V2_OUTLINE):
        raise ValueError("Version 2 requires positive loop/stem openings and enough stem length.")
    def left(y):
        return stem-weight/2-V2_STEM_LEAN*(y-cy)/(V2_STEM_BOTTOM-cy)
    bottom = V2_STEM_BOTTOM
    inset = V2_OUTLINE
    # Compensate for the lean so the perpendicular side thickness is exact.
    side_inset = inset*math.sqrt(1+(V2_STEM_LEAN/(bottom-cy))**2)
    # Opposite winding for the inner contour makes the stem genuinely hollow.
    stem_path = [("M", left(cy), cy), ("L", left(cy)+weight, cy),
                 ("L", left(bottom)+weight, bottom), ("L", left(bottom), bottom), ("Z",),
                 ("M", left(cy+inset)+side_inset, cy+inset),
                 ("L", left(bottom-inset)+side_inset, bottom-inset),
                 ("L", left(bottom-inset)+weight-side_inset, bottom-inset),
                 ("L", left(cy+inset)+weight-side_inset, cy+inset), ("Z",)]
    return [
        stem_path,
        band(cx, cy, radius, -90, 90, weight),
        band(loop, cy, radius, 90, 270, weight),
        band(loop, cy, V2_LOOP_RADIUS, 0, 360, V2_LOOP_THICKNESS),
        # Slight overlap with the solid left half prevents rasterizer hairlines.
        band(loop, cy, outer_radius, -90.25, 90.25, V2_OUTLINE),
    ]


def v3_transform(x, y):
    """Rotate a point in the upright P frame about the crossing."""
    angle = math.radians(V3_TILT)
    cosine, sine = math.cos(angle), math.sin(angle)
    cx, cy = V3_CROSSING
    x, y = x-V3_THICKNESS/2, y-V3_UPPER_STEM
    return cx+cosine*x-sine*y, cy+sine*x+cosine*y


def rounded_contour(commands, radius, overrides=None):
    """Round line/line corners with tangent circular cubic fillets.

    Existing curved edges stay intact. Short adjacent edges limit the radius
    locally so neighbouring fillets cannot overlap. Works for either winding.
    """
    edges = []
    current = first = None
    for op, *v in commands:
        if op == "M":
            current = first = tuple(v)
        elif op == "L":
            end = tuple(v)
            if math.dist(current, end) > 1e-9:
                edges.append(("L", current, end))
            current = end
        elif op == "C":
            end = tuple(v[4:])
            edges.append(("C", current, tuple(v[:2]), tuple(v[2:4]), end))
            current = end
        elif op == "Z" and math.dist(current, first) > 1e-9:
            edges.append(("L", current, first))
    corners = []
    for i, edge in enumerate(edges):
        previous, point = edges[i-1], edge[1]
        before = after = point
        controls = None
        r = (overrides or {}).get(point, radius)
        if previous[0] == edge[0] == "L" and r > 0:
            la, lb = math.dist(previous[1],point), math.dist(point,edge[-1])
            ua = tuple((point[j]-previous[1][j])/la for j in (0,1))
            ub = tuple((edge[-1][j]-point[j])/lb for j in (0,1))
            angle = math.acos(max(-1,min(1,sum(ua[j]*ub[j] for j in (0,1)))))
            if 1e-7 < angle < math.pi-1e-7:
                trim = min(r*math.tan(angle/2),la*.45,lb*.45)
                actual = trim/math.tan(angle/2)
                handle = 4/3*math.tan(angle/4)*actual
                before = tuple(point[j]-ua[j]*trim for j in (0,1))
                after = tuple(point[j]+ub[j]*trim for j in (0,1))
                controls = (*[before[j]+ua[j]*handle for j in (0,1)],
                            *[after[j]-ub[j]*handle for j in (0,1)], *after)
        corners.append((before,after,controls))
    result = [("M",*corners[0][0])]
    for i, edge in enumerate(edges):
        before, after, controls = corners[i]
        if controls:
            result.append(("C",*controls))
        destination = corners[(i+1)%len(edges)][0]
        if edge[0] == "C":
            result.append(("C",*edge[2],*edge[3],*destination))
        else:
            result.append(("L",*destination))
    return result+[("Z",)]


def polygon_contour(points):
    return [("M",*points[0]), *[("L",*p) for p in points[1:]], ("Z",)]


def clip_vertical(points, boundary, keep_left):
    """Clip a convex slot against the left or right edge of the P stem."""
    result = []
    inside = lambda p: p[0] <= boundary if keep_left else p[0] >= boundary
    for a,b in zip(points[-1:]+points[:-1],points):
        if inside(a) != inside(b):
            t = (boundary-a[0])/(b[0]-a[0])
            result.append((boundary,a[1]+t*(b[1]-a[1])))
        if inside(b):
            result.append(b)
    return result


def transform_v3_contour(contour):
    result = []
    for op,*values in contour:
        coords = []
        for i in range(0,len(values),2):
            coords.extend(v3_transform(values[i],values[i+1]))
        result.append((op,*coords))
    return result


def v3_paths(combined=True):
    if not 0 < V3_OUTLINE < V3_THICKNESS/2:
        raise ValueError("Version 3 needs an outline under half the bar width.")
    if not (0 < V3_THICKNESS < V3_BOWL_RADIUS and V3_BOWL_STRAIGHT > V3_THICKNESS):
        raise ValueError("Version 3 needs a bowl radius and straight run larger than its stroke.")
    if not (0 < V3_TILT < 60 and V3_UPPER_STEM > 2*V3_BOWL_RADIUS
            and V3_UPPER_ARM > V3_THICKNESS and V3_LOWER_ARM > V3_THICKNESS):
        raise ValueError("Version 3 needs a 0..60-degree tilt and distinct arms below the bowl.")
    if not V3_OUTLINE/2 < V3_CORNER_RADIUS < V3_THICKNESS/2:
        raise ValueError("V3_CORNER_RADIUS must be between half the outline and half the stem width.")
    w, r, straight = V3_THICKNESS, V3_BOWL_RADIUS, V3_BOWL_STRAIGHT
    stem_bottom = V3_UPPER_STEM+V3_LOWER_ARM
    corner, wall = V3_CORNER_RADIUS,V3_OUTLINE
    # Build both letters in the upright P frame. The other diagonal turns by
    # twice the tilt here; the final transform restores the mirrored X angles.
    angle = math.radians(2*V3_TILT)
    ux,uy = math.sin(angle),math.cos(angle)
    cx,cy = w/2,V3_UPPER_STEM
    def rectangle(upper,lower,half):
        a=(cx-ux*upper,cy-uy*upper)
        b=(cx+ux*lower,cy+uy*lower)
        return [(a[0]-uy*half,a[1]+ux*half),
                (b[0]-uy*half,b[1]+ux*half),
                (b[0]+uy*half,b[1]-ux*half),
                (a[0]+uy*half,a[1]-ux*half)]
    a,b,c,d = rectangle(V3_UPPER_ARM,V3_LOWER_ARM,w/2)
    slot = rectangle(V3_UPPER_ARM-wall,V3_LOWER_ARM-wall,w/2-wall)
    counter = rounded_contour(
        [("M",w,w),("L",w,2*r-w),("L",straight,2*r-w),
         *arc(straight,r,r-w,90,-90),("L",w,w),("Z",)],corner)
    if not combined:
        outline = rounded_contour(polygon_contour([a,b,c,d]),corner+wall/2)
        outline += rounded_contour(polygon_contour(list(reversed(slot))),corner-wall/2)
        p = rounded_contour(
            [("M",0,0),("L",straight,0),*arc(straight,r,r,-90,90),
             ("L",w,2*r),("L",w,stem_bottom),("L",0,stem_bottom),("Z",)],corner)
        return [transform_v3_contour(outline),transform_v3_contour(p+counter)]
    def edge_y(x,sign):
        return cy+(x-cx)*uy/ux+sign*w/(2*ux)
    if edge_y(w,-1) <= 2*r:
        raise ValueError("The P bowl needs space above the crossing; increase V3_ARM_LENGTH or reduce its bowl.")
    # Keep the four inward corners of the X crisp while rounding its tips.
    outer = [("M",0,0),("L",straight,0),*arc(straight,r,r,-90,90),
             ("L",w,2*r),("L",w,edge_y(w,-1)),("L",*c),("L",*b),
             ("L",w,edge_y(w,1)),("L",w,stem_bottom),("L",0,stem_bottom),
             ("L",0,edge_y(0,1)),("L",*a),("L",*d),("L",0,edge_y(0,-1)),("Z",)]
    radii = {p:corner+wall/2 for p in (a,b,c,d)}
    radii.update({(x,edge_y(x,sign)):0 for x in (0,w) for sign in (-1,1)})
    compound = rounded_contour(outer,corner,radii)
    for keep_left,boundary in [(True,0),(False,w)]:
        # Counterclockwise holes reveal the real background, with no masks.
        hole = clip_vertical(slot,boundary,keep_left)
        compound += rounded_contour(polygon_contour(hole),corner-wall/2)
    compound += counter
    return [transform_v3_contour(compound)]


def geometry_v3():
    return v3_paths(combined=True)


def path_bounds(contours):
    """Tight bounds from line endpoints and exact cubic Bezier extrema."""
    points = []
    for contour in contours:
        current = (0, 0)
        for op, *v in contour:
            if op in ("M", "L"):
                current = (v[0], v[1])
                points.append(current)
            elif op == "C":
                p0, p1, p2, p3 = current, tuple(v[:2]), tuple(v[2:4]), tuple(v[4:6])
                times = {0.0, 1.0}
                for dim in (0, 1):
                    a = -p0[dim]+3*p1[dim]-3*p2[dim]+p3[dim]
                    b = 2*(p0[dim]-2*p1[dim]+p2[dim])
                    c = p1[dim]-p0[dim]
                    if abs(a) < 1e-10:
                        roots = [-c/b] if abs(b) > 1e-10 else []
                    else:
                        d = b*b-4*a*c
                        roots = [(-b+math.sqrt(d))/(2*a),(-b-math.sqrt(d))/(2*a)] if d >= 0 else []
                    times.update(t for t in roots if 0 < t < 1)
                for t in times:
                    points.append(tuple((1-t)**3*p0[j]+3*(1-t)**2*t*p1[j]
                                        +3*(1-t)*t*t*p2[j]+t**3*p3[j] for j in (0, 1)))
                current = p3
    xs, ys = zip(*points)
    return min(xs), min(ys), max(xs)-min(xs), max(ys)-min(ys)


GEOMETRY = {1: geometry, "1b": geometry_v1b, 2: geometry_v2, 3: geometry_v3}


def mark_bounds(version=1, tight=False):
    if version not in GEOMETRY:
        raise ValueError(f"LOGO_VERSION must be one of {tuple(GEOMETRY)}.")
    if not tight:
        # Versions whose extents move with their parameters derive the loose
        # box from the tight one, so it cannot go stale and clip the mark.
        pad = {"1b": V1B_PADDING, 3: V3_PADDING}.get(version)
        if pad is not None:
            vx, vy, vw, vh = mark_bounds(version, True)
            return vx-pad, vy-pad, vw+2*pad, vh+2*pad
        return {1: VIEWBOX, 2: V2_VIEWBOX}[version]
    if version == 3:
        return path_bounds(geometry_v3())
    if version == "1b":
        radius, half = V1B_RADIUS, THICKNESS/2
        # The left arms are quarter circles on the right of their own centres,
        # so the mark starts at those centres, where their end caps are cut.
        # The extra sweep carries the left arms past their circle centres; the
        # top and bottom still fall on the plain quarter-turn points.
        vx = V1B_AXIS-radius-(radius+half)*math.sin(math.radians(V1B_ARC_EXTRA))
        vy = V1B_TOP_JOIN-radius-half
        right = V1B_AXIS+2*radius+half  # Bowl centre at axis+radius, plus its outer edge.
        bottom = max(V1B_STEM_BOTTOM, V1B_TOP_JOIN+V1B_MIDDLE+radius+half)
        return vx, vy, right-vx, bottom-vy
    if version == 2:
        cx, cy = V2_LEFT_CENTER
        outer = V2_LOOP_RADIUS+V2_LOOP_THICKNESS/2+V2_CRESCENT_GAP+V2_OUTLINE
        x0 = min(cx, cx+V2_ARM_RADIUS-V2_THICKNESS/2-V2_STEM_LEAN)
        y0 = cy-max(V2_ARM_RADIUS+V2_THICKNESS/2, outer)
        right = cx+2*V2_ARM_RADIUS+outer
        bottom = max(V2_STEM_BOTTOM, cy+V2_ARM_RADIUS+V2_THICKNESS/2, cy+outer)
        return x0, y0, right-x0, bottom-y0
    cx, cy = LEFT_CENTER
    half = THICKNESS/2
    vx, vy = cx, cy-ARM_RADIUS-half
    right = max(cx+2*ARM_RADIUS, cx+ARM_RADIUS+2*BOWL_RADIUS+half)
    bottom = max(STEM_BOTTOM, cy+ARM_RADIUS+half, BOWL_CENTER_Y+BOWL_RADIUS+half)
    return vx, vy, right-vx, bottom-vy


def draw_mark(canvas, x, y, width, height, tight=False, version=1):
    """Fit the mark in a points-based rectangle, keeping aspect ratio and color."""
    vx, vy, vw, vh = mark_bounds(version, tight)
    scale = min(width/vw, height/vh)
    canvas.saveState()
    canvas.translate(x+(width-vw*scale)/2, y+(height+vh*scale)/2)
    canvas.scale(scale, -scale)
    canvas.translate(-vx, -vy)
    for contour in GEOMETRY[version]():
        p = canvas.beginPath()
        for op, *values in contour:
            {"M":p.moveTo, "L":p.lineTo, "C":p.curveTo, "Z":p.close}[op](*values)
        canvas.drawPath(p, stroke=0, fill=1, fillMode=1)
    canvas.restoreState()


def export_svg(path, fill="#000000", version=1):
    bounds = " ".join(str(value) for value in mark_bounds(version))
    paths = []
    for contour in GEOMETRY[version]():
        d = " ".join(op+" "+" ".join(f"{n:.6f}".rstrip("0").rstrip(".") for n in values)
                     for op, *values in contour)
        paths.append(f'  <path d="{d}"/>')
    Path(path).write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{bounds}" '
        'role="img" aria-label="Marriage XP monogram">\n'
        f'  <title>Marriage XP - geometric monogram, version {version}</title>\n'
        f'<g fill="{fill}" fill-rule="nonzero">\n'+"\n".join(paths)+'\n</g>\n</svg>\n',
        encoding="utf-8")


def draw_logo(canvas, x, y, width, height, config):
    # Controlled by game_config.py; the generator draws the game name below it.
    if not getattr(config, "USE_VECTOR_LOGO", False):
        return False
    draw_mark(canvas, x, y, width, height, tight=True, version=getattr(config, "LOGO_VERSION", 1))
    return True
