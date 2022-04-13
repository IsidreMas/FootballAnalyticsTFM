# Template to start creating an interactive dashboard.
# Run with: bokeh serve dashboard.py

import sys
sys.path.append("../source")

from Tracking_Visualization import draw_pitch

from bokeh.plotting import curdoc
p = draw_pitch()
curdoc().add_root(p)
curdoc().title = "Empty Pitch"