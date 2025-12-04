from itertools import permutations

from geometor.pappus import *
from geometor.render import *
from geometor.utils import *

from geometor.model import *

sp.init_printing()

BUILD = True
ANALYZE = True


NAME = "kepler"
NAME += input(f"\nsession name: {NAME}")
log_init(NAME)
start_time = timer()

print_log(f"\nMODEL: {NAME}")
# add starting points
pt_a = add_point(point(0, 0))
pt_b = add_point(point(1, 0))
# this point should be constructed eventually
pt_c = add_point(point(0, sp.sqrt(phi)))

triangle = add_polygon(polygon([pt_a, pt_b, pt_c]))

bisector(pt_a, pt_b)
bisector(pt_a, pt_c)
bisector(pt_b, pt_c)

# midpoint circle
c = add_element(circle(pts[30], pt_a))

circle = add_element(circle(pt_a, pt_c))
poly_pts = []
poly_pts.append(point(-1, -1))
poly_pts.append(point(-1, 1))
poly_pts.append(point(1, 1))
poly_pts.append(point(1, -1))
square = add_polygon(polygon(poly_pts))

model_summary(NAME, start_time)

# ANALYZE ***************************
if ANALYZE:
    print_log(f"\nANALYZE: {NAME}")
    goldens, groups = analyze_model()

    analyze_summary(NAME, start_time, goldens, groups)

# PLOT *********************************
print_log(f"\nPLOT: {NAME}")
limx, limy = get_limits_from_points(pts, margin=0.25)
limx, limy = adjust_lims(limx, limy)
bounds = set_bounds(limx, limy)
print_log()
print_log(f"limx: {limx}")
print_log(f"limy: {limy}")

#  plt.ion()
fig, (ax, ax_btm) = plt.subplots(2, 1, gridspec_kw={"height_ratios": [10, 1]})
ax_btm.axis("off")
ax.axis("off")
ax.set_aspect("equal")
plt.tight_layout()

title = f"G E O M E T O R"
fig.suptitle(title, fontdict={"color": "#960", "size": "small"})

print_log("\nPlot Summary")
xlabel = f"elements: {len(elements)} | points: {len(pts)}"
ax_prep(ax, ax_btm, bounds, xlabel)
plot_sequence(ax, history, bounds)
snapshot(NAME, "sequences/summary.png")

if BUILD:
    print_log("\nPlot Build")
    build_sequence(NAME, ax, ax_btm, history, bounds)

if ANALYZE:
    print_log("\nPlot Goldens")

    bounds = get_bounds_from_sections(goldens)

    plot_sections(NAME, ax, ax_btm, history, goldens, bounds)

    print_log("\nPlot Golden Groups")
    plot_all_groups(NAME, ax, ax_btm, history, groups, bounds)

    plot_all_sections(NAME, ax, ax_btm, history, goldens, bounds)

    complete_summary(NAME, start_time, goldens, groups)

else:
    model_summary(NAME, start_time)


plt.show()
