import sys
sys.path.append("./source")

from source.Match_Analytics import Match
from source.Tracking_Visualization import draw_pitch

from bokeh.plotting import show
p = draw_pitch()
show(p)