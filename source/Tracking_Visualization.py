import numpy as np
import networkx as nx

from bokeh.plotting import figure
from bokeh.models import Range1d
from matplotlib.colors import LinearSegmentedColormap
from bokeh.io import curdoc, show
from bokeh.layouts import row, gridplot
from bokeh.models import ColumnDataSource, LabelSet
from bokeh.models.widgets import RangeSlider
from bokeh.io import output_notebook
from bokeh.application import Application
from bokeh.application.handlers import FunctionHandler

from bokeh.models import FreehandDrawTool, TapTool
import pandas as pd

from Tracking_Constants import *
from Tracking_Statistics import *
from Tracking_Filters import *

def draw_pitch(field_dimen = FIELD_DIMENSIONS,
               fig = None, 
               size = 7, 
               padding = 4, 
               pattern = "stripes", 
               noise = True,
               background_fill_color = "lightgreen",
               color_from = LOW_GRASS_COLOR,
               color_to = HIGH_GRASS_COLOR,
               grass_alpha = 1,
               line_color = "white",
               line_width = 2,
               noise_strength = 1000,
               paraboloid_gradient = True,
               paraboloid_strength = 1/5,
               stripes_number = 7,
               pixel_factor = 10,
               **kwargs):
    """
    Plot a custom football pitch on a Bokeh Figure and return it.
    
    Parameters
    -----------
        field_dimen: Tuple containing the dimensions of the field. Default: FIELD_DIMENSIONS = (length = 106, width = 60)
        fig:
        size:
        padding:
        pattern:
        noise:
        background_fill_color:
        color_from:
        color_to:
        grass_alpha:
        line_width:
        stripes_number: 
        noise_strength:
        paraboloid_gradient:
        paraboloid_strength:
        pixel_factor:
        
    Returns
    -----------
       bokeh Figure : Returns a figure with a football pitch drawn on it.

    """
    if fig is None:
        p = figure(width = int(field_dimen[0])*size,
                   height=int(field_dimen[1])*size,
                   background_fill_color = background_fill_color, 
                   **kwargs
                  )
        p.xgrid.grid_line_color = None
        p.ygrid.grid_line_color = None
        p.x_range = Range1d(-field_dimen[0]/2-padding, field_dimen[0]/2+padding)
        p.y_range = Range1d(-field_dimen[1]/2-padding, field_dimen[1]/2+padding)
        p.x_range.bounds = [-field_dimen[0]/2-padding,field_dimen[0]/2+padding]
        p.y_range.bounds = [-field_dimen[1]/2-padding,field_dimen[1]/2+padding]
        p.axis.minor_tick_line_color = None
        p.axis.visible = False
        p.toolbar.logo = None
        
    else:
        p = fig
    
    d = generate_grass_pattern( field_dimen,
                                padding,
                                pattern = pattern,
                                noise = noise,
                                stripes_number = stripes_number,
                                noise_strength = noise_strength,
                                paraboloid_gradient = paraboloid_gradient,
                                paraboloid_strength = paraboloid_strength,
                                pixel_factor = pixel_factor)
    p.image(image=[d],
            x=-field_dimen[0]/2-padding,
            y=-field_dimen[1]/2-padding,
            dw=field_dimen[0]+2*padding,
            dh=field_dimen[1]+2*padding,
            palette=linear_cmap(color_from = color_from, color_to = color_to),
            level="image",
            alpha = grass_alpha)
    
    # ALL DIMENSIONS IN m
    half_pitch_length = field_dimen[0]/2. # length of half pitch
    half_pitch_width = field_dimen[1]/2. # width of half pitch
    
    p.patch([-half_pitch_length,-half_pitch_length, half_pitch_length, half_pitch_length],
            [-half_pitch_width, half_pitch_width, half_pitch_width, -half_pitch_width],
            line_width=line_width,
            fill_color = None,
            line_color = line_color)
    
    p.segment(x0 = 0, y0 = -half_pitch_width, x1 = 0,
          y1= half_pitch_width, color=line_color, line_width=line_width)
    
    D_half_angle = np.arcsin(2*np.sqrt(CIRCLE_RADIUS**2-(AREA_LENGTH-PENALTY_SPOT)**2)/(2*CIRCLE_RADIUS))
    
    p.arc(x = [0,half_pitch_length-PENALTY_SPOT,-half_pitch_length+PENALTY_SPOT],
          y = [0,0,0],
          radius=CIRCLE_RADIUS,
          start_angle=[0,np.pi-D_half_angle,2*np.pi-D_half_angle],
          end_angle=[2*np.pi,np.pi+D_half_angle,D_half_angle],
          color=line_color,
          line_width = line_width)
    
    p.annulus(x = [0,half_pitch_length-PENALTY_SPOT,-half_pitch_length+PENALTY_SPOT],
          y = [0,0,0], outer_radius = 0.3, color=line_color)
    
    p.arc(x = [-half_pitch_length,half_pitch_length,-half_pitch_length,half_pitch_length],
          y = [half_pitch_width,half_pitch_width,-half_pitch_width,-half_pitch_width],
          radius=CORNER_RADIUS,
          start_angle=[np.pi*3/2,np.pi,0,np.pi/2],
          end_angle=[2*np.pi,np.pi*3/2,np.pi/2,np.pi],
          color=line_color,
          line_width = line_width)
    
    for s in [1,-1]:
        p.line([s*half_pitch_length, s*(half_pitch_length-AREA_LENGTH),
                s*(half_pitch_length-AREA_LENGTH), s*half_pitch_length,],
               [HALF_AREA_WIDTH, HALF_AREA_WIDTH, -HALF_AREA_WIDTH, -HALF_AREA_WIDTH],
               line_width=line_width,
               line_color = line_color)
        p.line([s*half_pitch_length, s*(half_pitch_length-BOX_LENGTH),
                s*(half_pitch_length-BOX_LENGTH), s*half_pitch_length,],
               [HALF_BOX_WIDTH, HALF_BOX_WIDTH, -HALF_BOX_WIDTH, -HALF_BOX_WIDTH],
               line_width=line_width,
               line_color = line_color)
        p.line([s*half_pitch_length, s*(half_pitch_length+1.5),
                s*(half_pitch_length+1.5), s*half_pitch_length],
               [HALF_GOAL_LINE, HALF_GOAL_LINE, -HALF_GOAL_LINE, -HALF_GOAL_LINE],
               line_width=line_width,
               line_color = line_color)
    
    
    return p

def generate_grass_pattern(field_dimen = FIELD_DIMENSIONS,
                           padding = 5,
                           pattern = "stripes",
                           noise = True,
                           noise_strength = 1000,
                           paraboloid_gradient = True,
                           paraboloid_strength = 1/5,
                           stripes_number = 7,
                           pixel_factor = 10):
    if pixel_factor > 50:
        raise ValueError('pixel_factor argument can\'t exceed 50')
    x = np.linspace(0, field_dimen[0], pixel_factor*int(field_dimen[0]))
    y = np.linspace(0, field_dimen[1], pixel_factor*int(field_dimen[1]))
    xx, yy = np.meshgrid(x, y)
    d = np.zeros(shape= xx.shape)
    
    if noise:
        d += np.random.randint(0, noise_strength, xx.shape)
    if paraboloid_gradient:
        d -= ((xx-field_dimen[0]/2)**2+5*(yy-field_dimen[1]/2)**2)*paraboloid_strength

    if pattern is not None:
        pattern = pattern.split('_')
        stripes_width = field_dimen[0]/stripes_number

        if 'stripes'in pattern:       
            if ('vertical' in pattern) or ('horizontal' not in pattern):
                d += 100*np.sign(np.sin((xx - stripes_width/2)*2*np.pi/stripes_width))
            if 'horizontal' in pattern:
                d += 100*np.sign(np.sin((yy - stripes_width/2)*2*np.pi/stripes_width))
        
        if 'circles' in pattern:
            d += 100*np.sign(np.sin((np.sqrt((yy- field_dimen[1]/2)**2+(xx - field_dimen[0]/2)**2))*2*np.pi/stripes_width))
    
    return d

def linear_cmap(color_from = LOW_GRASS_COLOR, color_to = HIGH_GRASS_COLOR):
    """ Create a linear gradient from one color to another.

    Returns
    -------
    cmap : List of HTML colors.
    """
    cmap = LinearSegmentedColormap.from_list('grass', [color_from, color_to], N=255)
    cmap = cmap(np.linspace(0, 1, 30))
    cmap = np.concatenate((cmap[:10][::-1], cmap))
    cmap = ["#%02x%02x%02x" % (int(r), int(g), int(b)) for r, g, b, _ in 255*cmap]
    return cmap

def plot_sliding_window(match_object, 
                        filtered_home_df=None, 
                        filtered_away_df=None,
                        filtered_events=None, 
                        normalized = None):
    # Set up plot
    if normalized:
        plot = figure(tools = ('tap','pan'), toolbar_location = 'left')
    else:
        plot = draw_pitch(tools = ('tap','pan'), toolbar_location = 'left')
    if isinstance(filtered_home_df, pd.DataFrame):
        tracking_home = filtered_home_df
    else:
        tracking_home = match_object.tracking_home
    if isinstance(filtered_away_df, pd.DataFrame):
        tracking_away = filtered_away_df
    else:
       tracking_away = match_object.tracking_away
    if isinstance(filtered_events, pd.DataFrame):
        events = filtered_events
    else:
       events = match_object.events

    renderer = plot.multi_line([], [], line_width=3, alpha=0.4, color='black')
    draw_tool = FreehandDrawTool(renderers=[renderer])
    plot.add_tools(draw_tool)
    plot.toolbar.active_drag = draw_tool
    taptool = plot.select(type=TapTool)[0]

    ph = figure(toolbar_location=None, width=plot.width, height=150, x_range=plot.x_range, min_border=0, min_border_left=50, y_axis_location="left", x_axis_location = 'above')
    ph.yaxis.major_label_orientation = np.pi/4
    ph.background_fill_color = "white"

    pv = figure(toolbar_location=None, width=150, height=plot.height,
                y_range=plot.y_range, min_border=0, y_axis_location="right", x_axis_location = 'below')
    pv.xaxis.major_label_orientation = np.pi/4
    pv.background_fill_color = "white"

    # Set up widgets
    home_time_window = RangeSlider(start=0, end=max(tracking_home['Time [s]']), 
                                    value=(1,20), step=.4,
                                    format = '00:00:00', show_value = False,
                                    bar_color = match_object.home_color, height = 10)
    away_time_window = RangeSlider(start=0, end=max(tracking_away['Time [s]']),
                                    value=(1,20), step=.4,
                                    format = '00:00:00', show_value = False,
                                    bar_color = match_object.away_color, height = 10)
    ball_time_window = RangeSlider(start=0, end=max(tracking_home['Time [s]']),
                                    value=(1,20), step=.4,
                                    format = '00:00:00', show_value = False,
                                    bar_color = 'black', height = 10)
    # Set up data
    home_df = time_window(tracking_home, 
                          home_time_window.value[0], 
                          home_time_window.value[1])
    away_df = time_window(tracking_away, 
                          away_time_window.value[0], 
                          away_time_window.value[1])
    events_df = time_window(events, 
                            away_time_window.value[0], 
                            away_time_window.value[1])
    if isinstance(normalized, str):
        ball_dist_stats = bivariate_normal_distribution(home_df, ball = True)
        if normalized == 'Home':
            home_x, home_y = histogram(home_df, match_object.home_players, density = True, normalised=True)
            away_x, away_y = histogram(home_df, match_object.away_players, density = True, normalised=True)
            home_dist_stats = bivariate_normal_distribution(home_df, match_object.home_players)
            away_dist_stats = bivariate_normal_distribution(home_df, match_object.away_players, against=True)
        elif normalized == 'Away':
            home_x, home_y = histogram(away_df, match_object.home_players, density = True, normalised=True)
            away_x, away_y = histogram(away_df, match_object.away_players, density = True, normalised=True)
            away_dist_stats = bivariate_normal_distribution(away_df, match_object.away_players)
            home_dist_stats = bivariate_normal_distribution(away_df, match_object.home_players, against=True)
        elif normalized == 'Both':
            home_x, home_y = histogram(home_df, match_object.home_players, density = True, normalised=True)
            away_x, away_y = histogram(away_df, match_object.away_players, density = True, normalised=True)
            away_dist_stats = bivariate_normal_distribution(away_df, match_object.away_players)
            home_dist_stats = bivariate_normal_distribution(home_df, match_object.home_players)
        norm_key = 'norm'
        norm_key_angle = 'norm_'
    else:
        ball_dist_stats = bivariate_normal_distribution(home_df, ball = True)
        home_dist_stats = bivariate_normal_distribution(home_df, match_object.home_players)
        away_dist_stats = bivariate_normal_distribution(away_df, match_object.away_players)
        home_x, home_y = histogram(home_df, match_object.home_players, density = True)
        away_x, away_y = histogram(away_df, match_object.away_players, density = True)
        norm_key = ''
        norm_key_angle = 'norm_'
    source_home_hist_x = ColumnDataSource(data=home_x)
    source_home_hist_y = ColumnDataSource(data=home_y)
    source_away_hist_x = ColumnDataSource(data=away_x)
    source_away_hist_y = ColumnDataSource(data=away_y)

    ph.quad(bottom='bottom_x', left='left_x', right='right_x', top='top_x', source=source_home_hist_x, color=match_object.home_color, line_color=match_object.home_color, alpha = 0.5)
    pv.quad(left='left_y', bottom='bottom_y', top='top_y', right='right_y', source=source_home_hist_y, color=match_object.home_color, line_color=match_object.home_color, alpha = 0.5)

    ph.quad(bottom='bottom_x', left='left_x', right='right_x', top='top_x', source=source_away_hist_x, color=match_object.away_color, line_color=match_object.away_color, alpha = 0.5)
    pv.quad(left='left_y', bottom='bottom_y', top='top_y', right='right_y', source=source_away_hist_y, color=match_object.away_color, line_color=match_object.away_color, alpha = 0.5)

    
    
    sources_home = ColumnDataSource(data=home_dist_stats.to_dict('series'))
    sources_home_inst = ColumnDataSource(data=dict(x=[],y=[]))
    sources_ball = ColumnDataSource(data=ball_dist_stats.to_dict('series'))
    sources_ball_inst = ColumnDataSource(data=dict(x=[],y=[]))
    sources_away = ColumnDataSource(data=away_dist_stats.to_dict('series'))
    sources_away_inst = ColumnDataSource(data=dict(x=[],y=[]))

    renderer1 = plot.circle(f'{norm_key}x_mean', f'{norm_key}y_mean', source=sources_away, alpha=0.5, size = 15, color = match_object.away_color)
    renderer2 = plot.circle(f'{norm_key}x_mean', f'{norm_key}y_mean', source=sources_home, alpha=0.5, size = 15, color = match_object.home_color)
    renderer3 = plot.circle(f'{norm_key}x_mean', f'{norm_key}y_mean', source=sources_ball, alpha=0.5, size = 15, color = "black")
    taptool.renderers = [renderer1, renderer2, renderer3]

    plot.multi_line('x','y', source=sources_home_inst, color = match_object.home_color)
    plot.multi_line('x','y', source=sources_away_inst, color = match_object.away_color)
    plot.line('x','y', source=sources_ball_inst, color = 'black')

    labels_home = LabelSet(x=f'{norm_key}x_mean', y=f'{norm_key}y_mean', text='player_number',
                            source=sources_home, text_color = "white",
                            text_font_size = "10px",
                            text_baseline="middle", text_align="center")
    labels_away = LabelSet(x=f'{norm_key}x_mean', y=f'{norm_key}y_mean', text='player_number',
                            source=sources_away, text_color = "white",
                            text_font_size = "10px", text_baseline="middle", text_align="center")
    plot.ellipse(x=f'{norm_key}x_mean', 
                y=f'{norm_key}y_mean', 
                width=f'cov_{norm_key}x_std', 
                height=f'cov_{norm_key}y_std',
                source = sources_away,
                fill_color = None,
                line_width = 1,
                line_color = match_object.away_color,
                angle = f'cov_{norm_key_angle}angle')
    plot.ellipse(x=f'{norm_key}x_mean', 
                y=f'{norm_key}y_mean', 
                width=f'cov_{norm_key}x_std', 
                height=f'cov_{norm_key}y_std',
                source = sources_home,
                fill_color = None,
                line_width = 1,
                line_color = match_object.home_color,
                angle = f'cov_{norm_key_angle}angle')
    plot.ellipse(x=f'{norm_key}x_mean', 
                y=f'{norm_key}y_mean', 
                width=f'cov_{norm_key}x_std', 
                height=f'cov_{norm_key}y_std',
                source = sources_ball,
                fill_color = None,
                line_width = 1,
                line_color = "black",
                angle = f'cov_{norm_key_angle}angle')
    plot.add_layout(labels_home)
    plot.add_layout(labels_away)

    def update_data_home(attrname, old, new):
        # Get the current slider values
        c = home_time_window
        flag = False
        if isinstance(normalized, str):
            flag = True
            if normalized == 'Home' or normalized == 'Both':
                home_df = time_window(tracking_home, c.value[0], c.value[1])
            elif normalized == 'Away':
                home_df = time_window(tracking_away, c.value[0], c.value[1])
        else:
            home_df = time_window(tracking_home, c.value[0], c.value[1])
        sources_home.data = bivariate_normal_distribution(home_df, match_object.home_players, against=flag).to_dict('series')
        if len(sources_home.selected.indices) >= 1:
            x = []
            y = []
            players = []
            for indice in sources_home.selected.indices:
                player = str(sources_home.data['player'][indice])
                x.append(home_df[f"{player}_{norm_key}x"])
                y.append(home_df[f"{player}_{norm_key}y"])
                players.append(player)
            sources_home_inst.data = dict(x=x, y=y)
            source_home_hist_x.data, source_home_hist_y.data = histogram(home_df, players, density = True, normalised=flag)
        else:
            sources_home_inst.data = dict(x=[],y=[])
            source_home_hist_x.data, source_home_hist_y.data = histogram(home_df, match_object.home_players, density = True, normalised=flag)

    def update_data_away(attrname, old, new):
        # Get the current slider values
        c = away_time_window
        flag = False
        if isinstance(normalized, str):
            flag = True
            if normalized == 'Away' or normalized == 'Both':
                away_df = time_window(tracking_away, c.value[0], c.value[1])
            elif normalized == 'Home':
                away_df = time_window(tracking_home, c.value[0], c.value[1])
        else:
            away_df = time_window(tracking_away, c.value[0], c.value[1])
        sources_away.data = bivariate_normal_distribution(away_df, match_object.away_players, against=flag).to_dict('series')
        if len(sources_away.selected.indices) >= 1:
            x = []
            y = []
            players = []
            for indice in sources_away.selected.indices:
                player = str(sources_away.data['player'][indice])
                x.append(away_df[f"{player}_{norm_key}x"])
                y.append(away_df[f"{player}_{norm_key}y"])
                players.append(player)
            sources_away_inst.data = dict(x=x, y=y)
            source_away_hist_x.data, source_away_hist_y.data = histogram(away_df, players, density = True, normalised=flag)
        else:
            sources_away_inst.data = dict(x=[],y=[])
            source_away_hist_x.data, source_away_hist_y.data = histogram(away_df, match_object.away_players, density = True, normalised=flag)

    def update_data_ball(attrname, old, new):
        # Get the current slider values
        c = ball_time_window
        home_time_window.value = c.value
        away_time_window.value = c.value
        home_df = time_window(tracking_home, c.value[0], c.value[1])
        sources_ball.data = bivariate_normal_distribution(home_df, ball = True).to_dict('series')
        if len(sources_ball.selected.indices) == 1:
            sources_ball_inst.data = dict(x=home_df[f"ball_{norm_key}x"],
                                        y=home_df[f"ball_{norm_key}y"])
        else:
            sources_ball_inst.data = dict(x=[],y=[])
        
            
    home_time_window.on_change('value', update_data_home)
    away_time_window.on_change('value', update_data_away)
    ball_time_window.on_change('value', update_data_ball)
    sources_home.selected.on_change('indices', update_data_home)
    sources_away.selected.on_change('indices', update_data_away)
    sources_ball.selected.on_change('indices', update_data_ball)


    # Set up layouts and add to document
    inputs = gridplot([[ph, None],
                        [plot, pv],
                        [ball_time_window, None],
                        [home_time_window, None], 
                        [away_time_window, None]], merge_tools=False)

    def modify_doc(doc):
        doc.add_root(row(inputs, width=800))


    handler = FunctionHandler(modify_doc)
    app = Application(handler)
    show(app)

def plot_match(match_object, 
                        filtered_home_df=None, 
                        filtered_away_df=None,
                        filtered_events=None, 
                        normalized = None):
    # Set up plot
    if normalized:
        plot = figure(tools = ('tap','pan'), toolbar_location = 'left')
        plot2 = figure(tools = ('tap','pan'), toolbar_location = 'left')
        plot3 = figure(tools = ('tap','pan'), toolbar_location = 'left')
    else:
        plot = draw_pitch(tools = ('tap','pan'), toolbar_location = 'left')
        plot2 = draw_pitch(tools = ('tap','pan'), toolbar_location = 'left')
        plot3 = draw_pitch(tools = ('tap','pan'), toolbar_location = 'left')

    if isinstance(filtered_home_df, pd.DataFrame):
        tracking_home = filtered_home_df
    else:
        tracking_home = match_object.tracking_home
    if isinstance(filtered_away_df, pd.DataFrame):
        tracking_away = filtered_away_df
    else:
       tracking_away = match_object.tracking_away
    if isinstance(filtered_events, pd.DataFrame):
        events = filtered_events
    else:
       events = match_object.events

    def modify_doc(doc):
        doc.add_root(row(plot, width=800))


    handler = FunctionHandler(modify_doc)
    app = Application(handler)
    show(app)