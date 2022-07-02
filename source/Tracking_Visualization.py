from turtle import update, width
import numpy as np
import networkx as nx

from bokeh.plotting import figure
from bokeh.models import Range1d, LinearAxis
from matplotlib.colors import LinearSegmentedColormap
from bokeh.io import curdoc, show
from bokeh.layouts import row, gridplot, column, widgetbox
from bokeh.models import ColumnDataSource, LabelSet, DataTable, TableColumn, Label
from bokeh.models.widgets import RangeSlider, Slider, Button, Spinner
from bokeh.io import output_notebook
from bokeh.application import Application
from bokeh.application.handlers import FunctionHandler

from bokeh.models import FreehandDrawTool, TapTool, CheckboxGroup
import pandas as pd

from Tracking_Constants import *
from Tracking_Statistics import *
from Tracking_Filters import *


def draw_pitch(field_dimen=FIELD_DIMENSIONS,
               fig=None,
               size=7,
               padding=4,
               pattern="stripes",
               noise=True,
               background_fill_color="lightgreen",
               color_from=LOW_GRASS_COLOR,
               color_to=HIGH_GRASS_COLOR,
               grass_alpha=1,
               line_color="white",
               line_width=2,
               noise_strength=1000,
               paraboloid_gradient=True,
               paraboloid_strength=1 / 5,
               stripes_number=7,
               pixel_factor=10,
               axis_visible=False,
               extra_padding = False,
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
        if not extra_padding:
            p = figure(width=int(field_dimen[0]) * size,
                       height=int(field_dimen[1]) * size,
                       background_fill_color=background_fill_color,
                       **kwargs
                       )
            p.y_range = Range1d(-field_dimen[1] / 2 - padding, field_dimen[1] / 2 + padding)
            p.y_range.bounds = [-field_dimen[1] / 2 - padding, field_dimen[1] / 2 + padding]
        else:
            p = figure(width=int(field_dimen[0]) * size,
                       height=int(field_dimen[1]+8) * size,
                       background_fill_color=background_fill_color,
                       **kwargs
                       )
            p.y_range = Range1d(-field_dimen[1] / 2 - padding -8, field_dimen[1] / 2 + padding)
            p.y_range.bounds = [-field_dimen[1] / 2 - padding -8, field_dimen[1] / 2 + padding]
        p.xgrid.grid_line_color = None
        p.ygrid.grid_line_color = None
        p.x_range = Range1d(-field_dimen[0] / 2 - padding, field_dimen[0] / 2 + padding)
        p.x_range.bounds = [-field_dimen[0] / 2 - padding, field_dimen[0] / 2 + padding]
        p.axis.minor_tick_line_color = None
        p.axis.visible = axis_visible
        p.toolbar.logo = None

    else:
        p = fig

    d = generate_grass_pattern(field_dimen,
                               padding,
                               pattern=pattern,
                               noise=noise,
                               stripes_number=stripes_number,
                               noise_strength=noise_strength,
                               paraboloid_gradient=paraboloid_gradient,
                               paraboloid_strength=paraboloid_strength,
                               pixel_factor=pixel_factor)
    p.image(image=[d],
            x=-field_dimen[0] / 2 - padding,
            y=-field_dimen[1] / 2 - padding,
            dw=field_dimen[0] + 2 * padding,
            dh=field_dimen[1] + 2 * padding,
            palette=linear_cmap(color_from=color_from, color_to=color_to),
            level="image",
            alpha=grass_alpha)

    # ALL DIMENSIONS IN m
    half_pitch_length = field_dimen[0] / 2.  # length of half pitch
    half_pitch_width = field_dimen[1] / 2.  # width of half pitch

    p.patch([-half_pitch_length, -half_pitch_length, half_pitch_length, half_pitch_length],
            [-half_pitch_width, half_pitch_width, half_pitch_width, -half_pitch_width],
            line_width=line_width,
            fill_color=None,
            line_color=line_color)

    p.segment(x0=0, y0=-half_pitch_width, x1=0,
              y1=half_pitch_width, color=line_color, line_width=line_width)

    D_half_angle = np.arcsin(2 * np.sqrt(CIRCLE_RADIUS ** 2 - (AREA_LENGTH - PENALTY_SPOT) ** 2) / (2 * CIRCLE_RADIUS))

    p.arc(x=[0, half_pitch_length - PENALTY_SPOT, -half_pitch_length + PENALTY_SPOT],
          y=[0, 0, 0],
          radius=CIRCLE_RADIUS,
          start_angle=[0, np.pi - D_half_angle, 2 * np.pi - D_half_angle],
          end_angle=[2 * np.pi, np.pi + D_half_angle, D_half_angle],
          color=line_color,
          line_width=line_width)

    p.annulus(x=[0, half_pitch_length - PENALTY_SPOT, -half_pitch_length + PENALTY_SPOT],
              y=[0, 0, 0], outer_radius=0.3, color=line_color)

    p.arc(x=[-half_pitch_length, half_pitch_length, -half_pitch_length, half_pitch_length],
          y=[half_pitch_width, half_pitch_width, -half_pitch_width, -half_pitch_width],
          radius=CORNER_RADIUS,
          start_angle=[np.pi * 3 / 2, np.pi, 0, np.pi / 2],
          end_angle=[2 * np.pi, np.pi * 3 / 2, np.pi / 2, np.pi],
          color=line_color,
          line_width=line_width)

    for s in [1, -1]:
        p.line([s * half_pitch_length, s * (half_pitch_length - AREA_LENGTH),
                s * (half_pitch_length - AREA_LENGTH), s * half_pitch_length, ],
               [HALF_AREA_WIDTH, HALF_AREA_WIDTH, -HALF_AREA_WIDTH, -HALF_AREA_WIDTH],
               line_width=line_width,
               line_color=line_color)
        p.line([s * half_pitch_length, s * (half_pitch_length - BOX_LENGTH),
                s * (half_pitch_length - BOX_LENGTH), s * half_pitch_length, ],
               [HALF_BOX_WIDTH, HALF_BOX_WIDTH, -HALF_BOX_WIDTH, -HALF_BOX_WIDTH],
               line_width=line_width,
               line_color=line_color)
        p.line([s * half_pitch_length, s * (half_pitch_length + 1.5),
                s * (half_pitch_length + 1.5), s * half_pitch_length],
               [HALF_GOAL_LINE, HALF_GOAL_LINE, -HALF_GOAL_LINE, -HALF_GOAL_LINE],
               line_width=line_width,
               line_color=line_color)

    return p


def generate_grass_pattern(field_dimen=FIELD_DIMENSIONS,
                           padding=5,
                           pattern="stripes",
                           noise=True,
                           noise_strength=1000,
                           paraboloid_gradient=True,
                           paraboloid_strength=1 / 5,
                           stripes_number=7,
                           pixel_factor=10):
    if pixel_factor > 50:
        raise ValueError('pixel_factor argument can\'t exceed 50')
    x = np.linspace(0, field_dimen[0], pixel_factor * int(field_dimen[0]))
    y = np.linspace(0, field_dimen[1], pixel_factor * int(field_dimen[1]))
    xx, yy = np.meshgrid(x, y)
    d = np.zeros(shape=xx.shape)

    if noise:
        d += np.random.randint(0, noise_strength, xx.shape)
    if paraboloid_gradient:
        d -= ((xx - field_dimen[0] / 2) ** 2 + 5 * (yy - field_dimen[1] / 2) ** 2) * paraboloid_strength

    if pattern is not None:
        pattern = pattern.split('_')
        stripes_width = field_dimen[0] / stripes_number

        if 'stripes' in pattern:
            if ('vertical' in pattern) or ('horizontal' not in pattern):
                d += 100 * np.sign(np.sin((xx - stripes_width / 2) * 2 * np.pi / stripes_width))
            if 'horizontal' in pattern:
                d += 100 * np.sign(np.sin((yy - stripes_width / 2) * 2 * np.pi / stripes_width))

        if 'circles' in pattern:
            d += 100 * np.sign(np.sin(
                (np.sqrt((yy - field_dimen[1] / 2) ** 2 + (xx - field_dimen[0] / 2) ** 2)) * 2 * np.pi / stripes_width))

    return d


def linear_cmap(color_from=LOW_GRASS_COLOR, color_to=HIGH_GRASS_COLOR):
    """ Create a linear gradient from one color to another.

    Returns
    -------
    cmap : List of HTML colors.
    """
    cmap = LinearSegmentedColormap.from_list('grass', [color_from, color_to], N=255)
    cmap = cmap(np.linspace(0, 1, 30))
    cmap = np.concatenate((cmap[:10][::-1], cmap))
    cmap = ["#%02x%02x%02x" % (int(r), int(g), int(b)) for r, g, b, _ in 255 * cmap]
    return cmap


def plot_sliding_window(match_object,
                        filtered_home_df=None,
                        filtered_away_df=None,
                        filtered_events=None,
                        normalized=None,
                        pass_graph=True,
                        scoreboard=True,
                        center_of_mass=True,
                        field_dimen=FIELD_DIMENSIONS,
                        **kwargs):
    # Set up plot
    if normalized:
        plot = figure(tools=('tap', 'pan', 'save'), toolbar_location='left')
        plot.xaxis.axis_label = r"$$\hat{x}$$"
        plot.yaxis.axis_label = r"$$\hat{y}$$"
    else:
        plot = draw_pitch(tools=('tap', 'pan', 'save'), toolbar_location='left',
                              field_dimen=field_dimen, extra_padding=False, **kwargs)
        plot.xaxis.axis_label = r"$$x[m]$$"
        plot.yaxis.axis_label = r"$$y[m]$$"
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
    LABELS = ["Pass Network Home", "Pass Network Away", "Covariant Ellipse Home", "Covariant Ellipse Away",
              "Away Circles", "Home Circles", "Ball", "CM"]

    checkbox_group = CheckboxGroup(labels=LABELS, active=[0, 1, 2, 3, 4, 5, 6, 7])

    ph = figure(toolbar_location=None, width=plot.width, height=150, x_range=plot.x_range, min_border=0,
                min_border_left=50, y_axis_location="left", x_axis_location='above')
    ph.yaxis.major_label_orientation = np.pi / 4
    ph.background_fill_color = "white"
    ph.yaxis.axis_label = r"$$\rho(x)$$"

    pv = figure(toolbar_location=None, width=150, height=plot.height,
                y_range=plot.y_range, min_border=0, y_axis_location="right", x_axis_location='below')
    pv.xaxis.major_label_orientation = np.pi / 4
    pv.background_fill_color = "white"
    pv.xaxis.axis_label = r"$$\rho(y)$$"

    if normalized:
        ph.yaxis.axis_label = r"$$\rho(\hat{x})$$"
        pv.xaxis.axis_label = r"$$\rho(\hat{y})$$"

    # Set up widgets
    home_time_window = RangeSlider(start=min(tracking_home['Time [s]']), end=max(tracking_home['Time [s]']),
                                   value=(min(tracking_home['Time [s]']), max(tracking_home['Time [s]'])), step=.4,
                                   format='00:00:00', show_value=False,
                                   bar_color=match_object.home_color, height=20)
    away_time_window = RangeSlider(start=min(tracking_away['Time [s]']), end=max(tracking_away['Time [s]']),
                                   value=(min(tracking_away['Time [s]']), max(tracking_away['Time [s]'])), step=.4,
                                   format='00:00:00', show_value=False,
                                   bar_color=match_object.away_color, height=20)
    ball_time_window = RangeSlider(start=min(tracking_home['Time [s]']), end=max(tracking_home['Time [s]']),
                                   value=(min(tracking_home['Time [s]']), max(tracking_home['Time [s]'])), step=.4,
                                   format='00:00:00', show_value=False,
                                   bar_color='black', height=20)
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
        ball_dist_stats = bivariate_normal_distribution(home_df, ball=True)
        if normalized == 'Home':
            home_x, home_y = histogram(home_df, match_object.home_players, density=True, normalised=True)
            away_x, away_y = histogram(home_df, match_object.away_players, density=True, normalised=True)
            home_dist_stats = bivariate_normal_distribution(home_df, match_object.home_players)
            away_dist_stats = bivariate_normal_distribution(home_df, match_object.away_players, against=True)
        elif normalized == 'Away':
            home_x, home_y = histogram(away_df, match_object.home_players, density=True, normalised=True)
            away_x, away_y = histogram(away_df, match_object.away_players, density=True, normalised=True)
            away_dist_stats = bivariate_normal_distribution(away_df, match_object.away_players)
            home_dist_stats = bivariate_normal_distribution(away_df, match_object.home_players, against=True)
        elif normalized == 'Both':
            home_x, home_y = histogram(home_df, match_object.home_players, density=True, normalised=True)
            away_x, away_y = histogram(away_df, match_object.away_players, density=True, normalised=True)
            away_dist_stats = bivariate_normal_distribution(away_df, match_object.away_players)
            home_dist_stats = bivariate_normal_distribution(home_df, match_object.home_players)
        norm_key = 'norm'
        norm_key_angle = 'norm_'
    else:
        ball_dist_stats = bivariate_normal_distribution(home_df, ball=True)
        home_dist_stats = bivariate_normal_distribution(home_df, match_object.home_players)
        away_dist_stats = bivariate_normal_distribution(away_df, match_object.away_players)
        home_x, home_y = histogram(home_df, match_object.home_players, density=False)
        away_x, away_y = histogram(away_df, match_object.away_players, density=False)
        norm_key = ''
        norm_key_angle = ''
    if pass_graph:
        passes_home = events_df[
            (events_df['Type'] == 'PASS') & (events_df["From"].str.split("_").str[0] == "Home")].groupby(['From',
                                                                                                          'To',
                                                                                                          'Start Time [s]',
                                                                                                          'End Time [s]',
                                                                                                          'Start X',
                                                                                                          'Start Y',
                                                                                                          'End X',
                                                                                                          'End Y']).size().reset_index(
            name="Freq")
        passes_home = passes_home.groupby(['From', 'To']).sum().reset_index()
        passes_home = passes_home.apply(lambda x: x / passes_home['Freq'] if x.name in ['Start Time [s]',
                                                                                        'End Time [s]',
                                                                                        'Start X',
                                                                                        'End X',
                                                                                        'Start Y',
                                                                                        'End Y',
                                                                                        ] else x)
        passes_home['Alpha'] = passes_home['Freq'] / passes_home['Freq'].max()
        max_passes_home = passes_home['Freq'].max()

        passes_home["Start X mean"] = [home_dist_stats.loc[home_dist_stats['player'] == player, f'{norm_key}x_mean'] for
                                       player in
                                       passes_home['From']]
        passes_home["Start Y mean"] = [home_dist_stats.loc[home_dist_stats['player'] == player, f'{norm_key}y_mean'] for
                                       player in
                                       passes_home['From']]
        passes_home["End X mean"] = [home_dist_stats.loc[home_dist_stats['player'] == player, f'{norm_key}x_mean'] for
                                     player in
                                     passes_home['To']]
        passes_home["End Y mean"] = [home_dist_stats.loc[home_dist_stats['player'] == player, f'{norm_key}y_mean'] for
                                     player in
                                     passes_home['To']]

        passes_away = events_df[
            (events_df['Type'] == 'PASS') & (events_df["From"].str.split("_").str[0] == "Away")].groupby(['From',
                                                                                                          'To',
                                                                                                          'Start Time [s]',
                                                                                                          'End Time [s]',
                                                                                                          'Start X',
                                                                                                          'Start Y',
                                                                                                          'End X',
                                                                                                          'End Y']).size().reset_index(
            name="Freq")
        passes_away = passes_away.groupby(['From', 'To']).sum().reset_index()
        passes_away = passes_away.apply(lambda x: x / passes_away['Freq'] if x.name in ['Start Time [s]',
                                                                                        'End Time [s]',
                                                                                        'Start X',
                                                                                        'End X',
                                                                                        'Start Y',
                                                                                        'End Y',
                                                                                        ] else x)

        passes_away['Alpha'] = passes_away['Freq'] / passes_away['Freq'].max()
        max_passes_away = passes_away['Freq'].max()

        passes_away["Start X mean"] = [away_dist_stats.loc[away_dist_stats['player'] == player, f'{norm_key}x_mean'] for
                                       player in
                                       passes_away['From']]
        passes_away["Start Y mean"] = [away_dist_stats.loc[away_dist_stats['player'] == player, f'{norm_key}y_mean'] for
                                       player in
                                       passes_away['From']]
        passes_away["End X mean"] = [away_dist_stats.loc[away_dist_stats['player'] == player, f'{norm_key}x_mean'] for
                                     player in
                                     passes_away['To']]
        passes_away["End Y mean"] = [away_dist_stats.loc[away_dist_stats['player'] == player, f'{norm_key}y_mean'] for
                                     player in
                                     passes_away['To']]

        max_passes = max(max_passes_home, max_passes_away)

        passes_home['Line_Width'] = 15 * passes_home['Freq'] / max_passes
        passes_away['Line_Width'] = 15 * passes_away['Freq'] / max_passes

        sources_home_passes = ColumnDataSource(data=passes_home)
        sources_away_passes = ColumnDataSource(data=passes_away)
        pass_network_home_renderer = plot.segment(x0="Start X mean", y0="Start Y mean", x1="End X mean",
                                                  y1="End Y mean", color=match_object.home_color,
                                                  line_width="Line_Width",
                                                  alpha="Alpha", source=sources_home_passes)
        pass_network_away_renderer = plot.segment(x0="Start X mean", y0="Start Y mean", x1="End X mean",
                                                  y1="End Y mean", color=match_object.away_color,
                                                  line_width="Line_Width",
                                                  alpha="Alpha", source=sources_away_passes)

    source_home_hist_x = ColumnDataSource(data=home_x)
    source_home_hist_y = ColumnDataSource(data=home_y)
    source_away_hist_x = ColumnDataSource(data=away_x)
    source_away_hist_y = ColumnDataSource(data=away_y)

    ph.quad(bottom='bottom_x', left='left_x', right='right_x', top='top_x', source=source_home_hist_x,
            color=match_object.home_color, line_color=match_object.home_color, alpha=0.5)
    pv.quad(left='left_y', bottom='bottom_y', top='top_y', right='right_y', source=source_home_hist_y,
            color=match_object.home_color, line_color=match_object.home_color, alpha=0.5)

    ph.quad(bottom='bottom_x', left='left_x', right='right_x', top='top_x', source=source_away_hist_x,
            color=match_object.away_color, line_color=match_object.away_color, alpha=0.5)
    pv.quad(left='left_y', bottom='bottom_y', top='top_y', right='right_y', source=source_away_hist_y,
            color=match_object.away_color, line_color=match_object.away_color, alpha=0.5)

    sources_home = ColumnDataSource(data=home_dist_stats.to_dict('series'))
    sources_home_inst = ColumnDataSource(data=dict(x=[], y=[]))
    sources_ball = ColumnDataSource(data=ball_dist_stats.to_dict('series'))
    sources_ball_inst = ColumnDataSource(data=dict(x=[], y=[]))
    sources_away = ColumnDataSource(data=away_dist_stats.to_dict('series'))
    sources_away_inst = ColumnDataSource(data=dict(x=[], y=[]))

    renderer1 = plot.circle(f'{norm_key}x_mean', f'{norm_key}y_mean', source=sources_away, alpha=0.5, size=15,
                            color=match_object.away_color)
    renderer2 = plot.circle(f'{norm_key}x_mean', f'{norm_key}y_mean', source=sources_home, alpha=0.5, size=15,
                            color=match_object.home_color)
    renderer3 = plot.circle(f'{norm_key}x_mean', f'{norm_key}y_mean', source=sources_ball, alpha=0.5, size=15,
                            color="black")

    renderer4 = plot.circle(0, 0, alpha=0, size=15,
                            color="yellow")
    renderer5 = plot.circle(0, 0, alpha=0, size=15,
                            color="yellow")
    if center_of_mass & (not normalized):
        cm_df = pd.concat([home_df[["team_meanx", "team_meany"]].agg(['mean']),
                           away_df[["team_meanx", "team_meany"]].agg(['mean'])])

        cm_series = np.sqrt((np.sqrt((away_df[["team_meanx", "team_meany"]]
                                      - home_df[["team_meanx", "team_meany"]]) ** 2) ** 2).sum(axis=1))
        cm_distance = cm_series.mean()
        std_distance = cm_series.std()
        cm_source = ColumnDataSource(cm_df.to_dict("series"))
        renderer4 = plot.circle(f'team_meanx', f'team_meany', source=cm_source, alpha=0.5, size=15,
                                color="yellow")
        renderer5 = plot.line('team_meanx', 'team_meany', source=cm_source, color='yellow', line_width=3)
        cm_distance_label = Label(x=0, y=-HALF_FIELD_HEIGHT - 2,
                                  text=f'd = ({cm_distance:.2f} ± {std_distance:.2f})m',
                                  text_color="yellow",
                                  text_baseline="middle", text_align="center")
        plot.add_layout(cm_distance_label)
    taptool.renderers = [renderer1, renderer2, renderer3, renderer4, renderer5]

    plot.multi_line('x', 'y', source=sources_home_inst, color=match_object.home_color)
    plot.multi_line('x', 'y', source=sources_away_inst, color=match_object.away_color)
    plot.line('x', 'y', source=sources_ball_inst, color='black')

    labels_home = LabelSet(x=f'{norm_key}x_mean', y=f'{norm_key}y_mean', text='player_number',
                           source=sources_home, text_color="white",
                           text_font_size="10px",
                           text_baseline="middle", text_align="center")
    labels_away = LabelSet(x=f'{norm_key}x_mean', y=f'{norm_key}y_mean', text='player_number',
                           source=sources_away, text_color="white",
                           text_font_size="10px", text_baseline="middle", text_align="center")
    away_ellipse_renderer = plot.ellipse(x=f'{norm_key}x_mean',
                                         y=f'{norm_key}y_mean',
                                         width=f'cov_{norm_key}x_std',
                                         height=f'cov_{norm_key}y_std',
                                         source=sources_away,
                                         fill_color=None,
                                         line_width=1,
                                         line_color=match_object.away_color,
                                         angle=f'cov_{norm_key_angle}angle')
    home_ellipse_renderer = plot.ellipse(x=f'{norm_key}x_mean',
                                         y=f'{norm_key}y_mean',
                                         width=f'cov_{norm_key}x_std',
                                         height=f'cov_{norm_key}y_std',
                                         source=sources_home,
                                         fill_color=None,
                                         line_width=1,
                                         line_color=match_object.home_color,
                                         angle=f'cov_{norm_key_angle}angle')
    ball_ellipse_renderer = plot.ellipse(x=f'{norm_key}x_mean',
                                         y=f'{norm_key}y_mean',
                                         width=f'cov_{norm_key}x_std',
                                         height=f'cov_{norm_key}y_std',
                                         source=sources_ball,
                                         fill_color=None,
                                         line_width=1,
                                         line_color="black",
                                         angle=f'cov_{norm_key_angle}angle')
    plot.add_layout(labels_home)
    plot.add_layout(labels_away)

    # Calculating score
    if scoreboard:
        home_goals = events_df[(events_df["Subtype"] == "ON TARGET-GOAL") & (events_df["Team"] == "Home")].shape[0]
        away_goals = events_df[(events_df["Subtype"] == "ON TARGET-GOAL") & (events_df["Team"] == "Away")].shape[0]

        scoreboard = Label(x=0, y=HALF_FIELD_HEIGHT + 2, text=f'{home_goals}:{away_goals}', text_color="white",
                                text_baseline="middle", text_align="center")

        plot.add_layout(scoreboard)

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

        home_events_df = time_window(events, c.value[0], c.value[1])

        home_dist_stats = bivariate_normal_distribution(home_df, match_object.home_players, against=flag)
        if pass_graph:
            if pass_network_home_renderer.visible:
                passes_home = home_events_df[
                    (home_events_df['Type'] == 'PASS') & (
                            home_events_df["From"].str.split("_").str[0] == "Home")].groupby(['From',
                                                                                              'To',
                                                                                              'Start Time [s]',
                                                                                              'End Time [s]',
                                                                                              'Start X',
                                                                                              'Start Y',
                                                                                              'End X',
                                                                                              'End Y']).size().reset_index(
                    name="Freq")
                passes_home = passes_home.groupby(['From', 'To']).sum().reset_index()
                passes_home = passes_home.apply(lambda x: x / passes_home['Freq'] if x.name in ['Start Time [s]',
                                                                                                'End Time [s]',
                                                                                                'Start X',
                                                                                                'End X',
                                                                                                'Start Y',
                                                                                                'End Y',
                                                                                                ] else x)

                passes_home['Alpha'] = passes_home['Freq'] / passes_home['Freq'].max()
                passes_home['Line_Width'] = 15 * passes_home['Freq'] / max_passes

                passes_home["Start X mean"] = [
                    home_dist_stats.loc[home_dist_stats['player'] == player, f'{norm_key}x_mean'] for
                    player in
                    passes_home['From']]
                passes_home["Start Y mean"] = [
                    home_dist_stats.loc[home_dist_stats['player'] == player, f'{norm_key}y_mean'] for
                    player in
                    passes_home['From']]
                passes_home["End X mean"] = [
                    home_dist_stats.loc[home_dist_stats['player'] == player, f'{norm_key}x_mean'] for
                    player in
                    passes_home['To']]
                passes_home["End Y mean"] = [
                    home_dist_stats.loc[home_dist_stats['player'] == player, f'{norm_key}y_mean'] for
                    player in
                    passes_home['To']]
                sources_home_passes.data = passes_home

        sources_home.data = home_dist_stats.to_dict(
            'series')
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
            source_home_hist_x.data, source_home_hist_y.data = histogram(home_df, players, density=True,
                                                                         normalised=flag)
        else:
            sources_home_inst.data = dict(x=[], y=[])
            source_home_hist_x.data, source_home_hist_y.data = histogram(home_df, match_object.home_players,
                                                                         density=True, normalised=flag)

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

        away_events_df = time_window(events, c.value[0], c.value[1])

        away_dist_stats = bivariate_normal_distribution(away_df, match_object.away_players, against=flag)
        if pass_graph:
            if pass_network_away_renderer.visible:
                passes_away = away_events_df[
                    (away_events_df['Type'] == 'PASS') & (
                            away_events_df["From"].str.split("_").str[0] == "Away")].groupby(
                    ['From',
                     'To',
                     'Start Time [s]',
                     'End Time [s]',
                     'Start X',
                     'Start Y',
                     'End X',
                     'End Y']).size().reset_index(
                    name="Freq")
                passes_away = passes_away.groupby(['From', 'To']).sum().reset_index()
                passes_away = passes_away.apply(lambda x: x / passes_away['Freq'] if x.name in ['Start Time [s]',
                                                                                                'End Time [s]',
                                                                                                'Start X',
                                                                                                'End X',
                                                                                                'Start Y',
                                                                                                'End Y',
                                                                                                ] else x)
                passes_away['Alpha'] = passes_away['Freq'] / passes_away['Freq'].max()
                passes_away['Line_Width'] = 15 * passes_away['Freq'] / max_passes

                passes_away["Start X mean"] = [
                    away_dist_stats.loc[away_dist_stats['player'] == player, f'{norm_key}x_mean'] for
                    player in
                    passes_away['From']]
                passes_away["Start Y mean"] = [
                    away_dist_stats.loc[away_dist_stats['player'] == player, f'{norm_key}y_mean'] for
                    player in
                    passes_away['From']]
                passes_away["End X mean"] = [
                    away_dist_stats.loc[away_dist_stats['player'] == player, f'{norm_key}x_mean'] for
                    player in
                    passes_away['To']]
                passes_away["End Y mean"] = [
                    away_dist_stats.loc[away_dist_stats['player'] == player, f'{norm_key}y_mean'] for
                    player in
                    passes_away['To']]
                sources_away_passes.data = passes_away

        sources_away.data = away_dist_stats.to_dict(
            'series')
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
            source_away_hist_x.data, source_away_hist_y.data = histogram(away_df, players, density=True,
                                                                         normalised=flag)
        else:
            sources_away_inst.data = dict(x=[], y=[])
            source_away_hist_x.data, source_away_hist_y.data = histogram(away_df, match_object.away_players,
                                                                         density=True, normalised=flag)

    def update_data_ball(attrname, old, new):
        # Get the current slider values
        c = ball_time_window
        home_time_window.value = c.value
        away_time_window.value = c.value
        home_df = time_window(tracking_home, c.value[0], c.value[1])
        away_df = time_window(tracking_away, c.value[0], c.value[1])
        events_df = time_window(events, c.value[0], c.value[1])
        sources_ball.data = bivariate_normal_distribution(home_df, ball=True).to_dict('series')
        if len(sources_ball.selected.indices) == 1:
            sources_ball_inst.data = dict(x=home_df[f"ball_{norm_key}x"],
                                          y=home_df[f"ball_{norm_key}y"])
        else:
            sources_ball_inst.data = dict(x=[], y=[])
        if center_of_mass & (not normalized):
            cm_df = pd.concat([home_df[["team_meanx", "team_meany"]].agg(['mean']),
                               away_df[["team_meanx", "team_meany"]].agg(['mean'])])
            cm_series = np.sqrt((np.sqrt((away_df[["team_meanx", "team_meany"]]
                                          - home_df[["team_meanx", "team_meany"]]) ** 2) ** 2).sum(axis=1))
            cm_distance = cm_series.mean()
            std_distance = cm_series.std()
            cm_distance_label.text = f'd = ({cm_distance:.2f} ± {std_distance:.2f})m'
            cm_source.data = cm_df.to_dict("series")
        if scoreboard:
            away_goals = events_df[
                    (events_df["Subtype"] == "ON TARGET-GOAL") & (events_df["Team"] == "Away")].shape[0]
            home_goals = events_df[
                (events_df["Subtype"] == "ON TARGET-GOAL") & (events_df["Team"] == "Home")].shape[0]
            scoreboard.text = f'{home_goals}:{away_goals}'

    def update_checkbox(attrname, old, new):
        pass_network_home_renderer.visible = (0 in checkbox_group.active)
        pass_network_away_renderer.visible = (1 in checkbox_group.active)
        home_ellipse_renderer.visible = (2 in checkbox_group.active)
        away_ellipse_renderer.visible = (3 in checkbox_group.active)
        renderer1.visible = (4 in checkbox_group.active)
        renderer2.visible = (5 in checkbox_group.active)
        renderer3.visible = (6 in checkbox_group.active)
        ball_ellipse_renderer.visible = (6 in checkbox_group.active)
        labels_home.visible = (5 in checkbox_group.active)
        labels_away.visible = (4 in checkbox_group.active)
        renderer4.visible = (7 in checkbox_group.active)
        renderer5.visible = (7 in checkbox_group.active)

    home_time_window.on_change('value', update_data_home)
    away_time_window.on_change('value', update_data_away)
    ball_time_window.on_change('value', update_data_ball)
    checkbox_group.on_change('active', update_checkbox)
    sources_home.selected.on_change('indices', update_data_home)
    sources_away.selected.on_change('indices', update_data_away)
    sources_ball.selected.on_change('indices', update_data_ball)

    # Set up layouts and add to document
    inputs = gridplot([[ph, checkbox_group],
                       [plot, pv],
                       [ball_time_window, None],
                       [home_time_window, None],
                       [away_time_window, None]], merge_tools=False)

    def modify_doc(doc):
        doc.add_root(row(inputs, width=800))

    handler = FunctionHandler(modify_doc)
    app = Application(handler)
    show(app)
    return inputs


def play_match(match_object,
               filtered_home_df=None,
               filtered_away_df=None,
               filtered_events=None,
               normalized=None,
               **kwargs):
    # Set up plot
    plot = draw_pitch(tools=('tap', 'pan'), toolbar_location='left', **kwargs)
    norm_plot_home = figure(toolbar_location=None, width=int(plot.width / 2), height=int(plot.width / 2),
                            x_range=[-3, 3], y_range=[-3, 3], min_border=0, min_border_left=50, y_axis_location="left",
                            x_axis_location='above')
    norm_plot_away = figure(toolbar_location=None, width=int(plot.width / 2), height=int(plot.width / 2),
                            x_range=[-3, 3], y_range=[-3, 3], min_border=0, min_border_left=50, y_axis_location="right",
                            x_axis_location='above')
    norm_plot_home.axis.major_tick_in = 10
    norm_plot_home.axis.major_tick_out = 0
    norm_plot_home.axis.minor_tick_in = 5
    norm_plot_home.axis.minor_tick_out = 0

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

    frame_home = match_object.tracking_home.iloc[[0]]
    frame_home.columns = frame_home.columns.str.rsplit(r'_', 1, expand=True)
    home_df = frame_home.stack(0).droplevel(0).filter(like="Home", axis=0)
    home_away_df = frame_home.stack(0).droplevel(0).filter(like="Away", axis=0)
    home_away_df['player'] = home_away_df.index.str.split("_").str[1]
    home_df['player'] = home_df.index.str.split("_").str[1]
    home_df['end_vx'] = home_df['vx'] + home_df['x']
    home_df['end_vy'] = home_df['vy'] + home_df['y']

    frame_away = match_object.tracking_away.iloc[[0]]
    frame_away.columns = frame_away.columns.str.rsplit(r'_', 1, expand=True)
    away_df = frame_away.stack(0).droplevel(0).filter(like="Away", axis=0)
    away_home_df = frame_away.stack(0).droplevel(0).filter(like="Home", axis=0)
    away_home_df['player'] = away_home_df.index.str.split("_").str[1]
    away_df['player'] = away_df.index.str.split("_").str[1]
    away_df['end_vx'] = away_df['vx'] + away_df['x']
    away_df['end_vy'] = away_df['vy'] + away_df['y']

    ball_home_df = frame_home.stack(0).droplevel(0).filter(like="ball", axis=0)
    ball_away_df = frame_away.stack(0).droplevel(0).filter(like="ball", axis=0)

    sources_home = ColumnDataSource(data=home_df.to_dict('series'))
    sources_away = ColumnDataSource(data=away_df.to_dict('series'))
    sources_home_away = ColumnDataSource(data=home_away_df.to_dict('series'))
    sources_away_home = ColumnDataSource(data=away_home_df.to_dict('series'))
    sources_home_ball = ColumnDataSource(data=ball_home_df.to_dict('series'))
    sources_away_ball = ColumnDataSource(data=ball_away_df.to_dict('series'))

    sources_events = ColumnDataSource(time_window(match_object.events, 0 - 200, 0 + 200, frame=True).to_dict("Series"))

    columns = [
        TableColumn(field="Team", title="Team"),
        TableColumn(field="Type", title="Type"),
        TableColumn(field="Subtype", title="Subtype"),
        TableColumn(field="From", title="From"),
        TableColumn(field="To", title="To"),
        TableColumn(field="Start Time [s]", title="Start Time [s]"),
        TableColumn(field="End Time [s]", title="End Time [s]")
    ]
    data_table = DataTable(source=sources_events, columns=columns, width=800, height=100)

    renderer1 = plot.circle('x', 'y', source=sources_away, alpha=0.5, size=15, color=match_object.away_color)
    renderer2 = plot.circle('x', 'y', source=sources_home, alpha=0.5, size=15, color=match_object.home_color)
    renderer3 = plot.circle('x', 'y', source=sources_home_ball, alpha=0.5, size=5, color="black")
    norm_home_render = norm_plot_home.circle('normx', 'normy', source=sources_home, alpha=0.5, size=15,
                                             color=match_object.home_color)
    norm_away_render = norm_plot_away.circle('normx', 'normy', source=sources_away, alpha=0.5, size=15,
                                             color=match_object.away_color)
    norm_home_away_render = norm_plot_home.circle('normx', 'normy', source=sources_home_away, alpha=0.5, size=15,
                                                  color=match_object.away_color)
    norm_away_home_render = norm_plot_away.circle('normx', 'normy', source=sources_away_home, alpha=0.5, size=15,
                                                  color=match_object.home_color)
    norm_ball_home_render = norm_plot_home.circle('normx', 'normy', source=sources_home_ball, alpha=0.5, size=15,
                                                  color="black")
    norm_ball_away_render = norm_plot_away.circle('normx', 'normy', source=sources_away_ball, alpha=0.5, size=15,
                                                  color="black")
    taptool.renderers = [renderer1, renderer2, renderer3, norm_home_render,
                         norm_away_render, norm_ball_home_render, norm_ball_away_render,
                         norm_home_away_render, norm_away_home_render]

    plot.segment(x0="x", y0="y", x1="end_vx", y1="end_vy", line_color=match_object.home_color, source=sources_home,
                 line_width=3)
    plot.segment(x0="x", y0="y", x1="end_vx", y1="end_vy", line_color=match_object.away_color, source=sources_away,
                 line_width=3)

    freq = Slider(title="Game Time", value=0, start=0, end=len(match_object.tracking_home), step=1, width_policy='max')

    labels_home = LabelSet(x='x', y='y', text='player',
                           source=sources_home, text_color="white",
                           text_font_size="10px",
                           text_baseline="middle", text_align="center")
    labels_away = LabelSet(x='x', y='y', text='player',
                           source=sources_away, text_color="white",
                           text_font_size="10px", text_baseline="middle", text_align="center")
    labels_home_norm = LabelSet(x='normx', y='normy', text='player',
                                source=sources_home, text_color="white",
                                text_font_size="10px",
                                text_baseline="middle", text_align="center")
    labels_away_norm = LabelSet(x='normx', y='normy', text='player',
                                source=sources_away, text_color="white",
                                text_font_size="10px", text_baseline="middle", text_align="center")
    labels_home_away_norm = LabelSet(x='normx', y='normy', text='player',
                                     source=sources_home_away, text_color="white",
                                     text_font_size="10px",
                                     text_baseline="middle", text_align="center")
    labels_away_home_norm = LabelSet(x='normx', y='normy', text='player',
                                     source=sources_away_home, text_color="white",
                                     text_font_size="10px", text_baseline="middle", text_align="center")
    plot.add_layout(labels_home)
    plot.add_layout(labels_away)
    norm_plot_home.add_layout(labels_home_norm)
    norm_plot_away.add_layout(labels_away_norm)
    norm_plot_home.add_layout(labels_home_away_norm)
    norm_plot_away.add_layout(labels_away_home_norm)

    def update_data(attrname, old, new):
        k = int(freq.value)

        frame_home = match_object.tracking_home.iloc[[k]]
        frame_home.columns = frame_home.columns.str.rsplit(r'_', 1, expand=True)
        home_df = frame_home.stack(0).droplevel(0).filter(like="Home", axis=0)
        home_away_df = frame_home.stack(0).droplevel(0).filter(like="Away", axis=0)
        home_away_df['player'] = home_away_df.index.str.split("_").str[1]
        home_df['player'] = home_df.index.str.split("_").str[1]
        home_df['end_vx'] = home_df['vx'] + home_df['x']
        home_df['end_vy'] = home_df['vy'] + home_df['y']

        frame_away = match_object.tracking_away.iloc[[k]]
        frame_away.columns = frame_away.columns.str.rsplit(r'_', 1, expand=True)
        away_df = frame_away.stack(0).droplevel(0).filter(like="Away", axis=0)
        away_home_df = frame_away.stack(0).droplevel(0).filter(like="Home", axis=0)
        away_home_df['player'] = away_home_df.index.str.split("_").str[1]
        away_df['player'] = away_df.index.str.split("_").str[1]
        away_df['end_vx'] = away_df['vx'] + away_df['x']
        away_df['end_vy'] = away_df['vy'] + away_df['y']

        ball_home_df = frame_home.stack(0).droplevel(0).filter(like="ball", axis=0)
        ball_away_df = frame_away.stack(0).droplevel(0).filter(like="ball", axis=0)

        sources_home.data = home_df.to_dict('series')
        sources_away.data = away_df.to_dict('series')
        sources_home_ball.data = ball_home_df.to_dict('series')
        sources_away_ball.data = ball_away_df.to_dict('series')
        sources_home_away.data = home_away_df.to_dict('series')
        sources_away_home.data = away_home_df.to_dict('series')

        time = int(frame_home['Time [s]'].iloc[0])

        sources_events.data = time_window(match_object.events, 0, time).to_dict("Series")

    freq.on_change('value', update_data)

    button = Button(label='►', width=60)
    forward_button = Button(label='▸▸', width=60)
    backward_button = Button(label='◂◂', width=60)

    global update_rate
    update_rate = 1

    def animate_update():
        frame = freq.value + update_rate
        if frame > len(match_object.tracking_home):
            frame = 0
        freq.value = frame

    def animate():
        global callback_id
        global update_rate
        if button.label == '►':
            button.label = '❚❚'
            update_rate = 1
            callback_id = curdoc().add_periodic_callback(animate_update, 40)
        else:
            button.label = '►'
            curdoc().remove_periodic_callback(callback_id)
            callback_id = None

    def forward_update():
        global update_rate
        update_rate *= 2

    def backward_update():
        global update_rate
        update_rate /= 2

    button.on_click(animate)
    forward_button.on_click(forward_update)
    backward_button.on_click(backward_update)

    def select_event(attr, old, new):
        selectionRowIndex = sources_events.selected.indices[0]
        freq.value = match_object.tracking_home['Time [s]'].sub(
            sources_events.data['Start Time [s]'][selectionRowIndex]).abs().idxmin()

    sources_events.selected.on_change('indices', select_event)

    inputs = gridplot([[row(norm_plot_home, norm_plot_away)], [plot], [data_table],
                       [row([backward_button, button, forward_button, freq])]], merge_tools=False)

    def modify_doc(doc):
        doc.add_root(row(inputs, width=800))

    handler = FunctionHandler(modify_doc)
    app = Application(handler)
    show(app)
    return inputs

def plot_sliding_window_spinner(match_object,
                        filtered_home_df=None,
                        filtered_away_df=None,
                        filtered_events=None,
                        normalized=None,
                        pass_graph=True,
                        scoreboard=True,
                        center_of_mass=True,
                        field_dimen=FIELD_DIMENSIONS,
                        **kwargs):
    # Set up plot
    if normalized:
        plot = figure(tools=('tap', 'pan', 'save'), toolbar_location='left')
    else:
        plot = draw_pitch(tools=('tap', 'pan', 'save'), toolbar_location='left',
                              field_dimen=field_dimen, extra_padding=False, **kwargs)
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
    LABELS = ["Pass Network Home", "Pass Network Away", "Covariant Ellipse Home", "Covariant Ellipse Away",
              "Away Circles", "Home Circles", "Ball", "CM"]

    checkbox_group = CheckboxGroup(labels=LABELS, active=[0, 1, 2, 3, 4, 5, 6, 7])

    ph = figure(toolbar_location=None, width=plot.width, height=150, x_range=plot.x_range, min_border=0,
                min_border_left=50, y_axis_location="left", x_axis_location='above')
    ph.yaxis.major_label_orientation = np.pi / 4
    ph.background_fill_color = "white"

    pv = figure(toolbar_location=None, width=150, height=plot.height,
                y_range=plot.y_range, min_border=0, y_axis_location="right", x_axis_location='below')
    pv.xaxis.major_label_orientation = np.pi / 4
    pv.background_fill_color = "white"

    # Set up widgets
    window_size = Spinner(title="Window size", low=0, step=1, value=5, width=80)
    home_time_window = RangeSlider(start=min(tracking_home['Time [s]']), end=max(tracking_home['Time [s]']),
                                   value=(min(tracking_home['Time [s]']), window_size.value), step=.4,
                                   format='00:00:00', show_value=False,
                                   bar_color=match_object.home_color, height=20)
    away_time_window = RangeSlider(start=min(tracking_away['Time [s]']), end=max(tracking_away['Time [s]']),
                                   value=(min(tracking_away['Time [s]']), window_size.value), step=.4,
                                   format='00:00:00', show_value=False,
                                   bar_color=match_object.away_color, height=20)

    ball_time_window = Slider(start=min(tracking_home['Time [s]']),
                              end=max(tracking_away['Time [s]']),
                              value=min(tracking_home['Time [s]']),
                              format='00:00:00',
                              show_value=False,
                              step=0.4)

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
        ball_dist_stats = bivariate_normal_distribution(home_df, ball=True)
        if normalized == 'Home':
            home_x, home_y = histogram(home_df, match_object.home_players, density=True, normalised=True)
            away_x, away_y = histogram(home_df, match_object.away_players, density=True, normalised=True)
            home_dist_stats = bivariate_normal_distribution(home_df, match_object.home_players)
            away_dist_stats = bivariate_normal_distribution(home_df, match_object.away_players, against=True)
        elif normalized == 'Away':
            home_x, home_y = histogram(away_df, match_object.home_players, density=True, normalised=True)
            away_x, away_y = histogram(away_df, match_object.away_players, density=True, normalised=True)
            away_dist_stats = bivariate_normal_distribution(away_df, match_object.away_players)
            home_dist_stats = bivariate_normal_distribution(away_df, match_object.home_players, against=True)
        elif normalized == 'Both':
            home_x, home_y = histogram(home_df, match_object.home_players, density=True, normalised=True)
            away_x, away_y = histogram(away_df, match_object.away_players, density=True, normalised=True)
            away_dist_stats = bivariate_normal_distribution(away_df, match_object.away_players)
            home_dist_stats = bivariate_normal_distribution(home_df, match_object.home_players)
        norm_key = 'norm'
        norm_key_angle = 'norm_'
    else:
        ball_dist_stats = bivariate_normal_distribution(home_df, ball=True)
        home_dist_stats = bivariate_normal_distribution(home_df, match_object.home_players)
        away_dist_stats = bivariate_normal_distribution(away_df, match_object.away_players)
        home_x, home_y = histogram(home_df, match_object.home_players, density=True)
        away_x, away_y = histogram(away_df, match_object.away_players, density=True)
        norm_key = ''
        norm_key_angle = ''
    if pass_graph:
        passes_home = events_df[
            (events_df['Type'] == 'PASS') & (events_df["From"].str.split("_").str[0] == "Home")].groupby(['From',
                                                                                                          'To',
                                                                                                          'Start Time [s]',
                                                                                                          'End Time [s]',
                                                                                                          'Start X',
                                                                                                          'Start Y',
                                                                                                          'End X',
                                                                                                          'End Y']).size().reset_index(
            name="Freq")
        passes_home = passes_home.groupby(['From', 'To']).sum().reset_index()
        passes_home = passes_home.apply(lambda x: x / passes_home['Freq'] if x.name in ['Start Time [s]',
                                                                                        'End Time [s]',
                                                                                        'Start X',
                                                                                        'End X',
                                                                                        'Start Y',
                                                                                        'End Y',
                                                                                        ] else x)
        passes_home['Alpha'] = passes_home['Freq'] / passes_home['Freq'].max()
        max_passes_home = passes_home['Freq'].max()

        passes_home["Start X mean"] = [home_dist_stats.loc[home_dist_stats['player'] == player, f'{norm_key}x_mean'] for
                                       player in
                                       passes_home['From']]
        passes_home["Start Y mean"] = [home_dist_stats.loc[home_dist_stats['player'] == player, f'{norm_key}y_mean'] for
                                       player in
                                       passes_home['From']]
        passes_home["End X mean"] = [home_dist_stats.loc[home_dist_stats['player'] == player, f'{norm_key}x_mean'] for
                                     player in
                                     passes_home['To']]
        passes_home["End Y mean"] = [home_dist_stats.loc[home_dist_stats['player'] == player, f'{norm_key}y_mean'] for
                                     player in
                                     passes_home['To']]

        passes_away = events_df[
            (events_df['Type'] == 'PASS') & (events_df["From"].str.split("_").str[0] == "Away")].groupby(['From',
                                                                                                          'To',
                                                                                                          'Start Time [s]',
                                                                                                          'End Time [s]',
                                                                                                          'Start X',
                                                                                                          'Start Y',
                                                                                                          'End X',
                                                                                                          'End Y']).size().reset_index(
            name="Freq")
        passes_away = passes_away.groupby(['From', 'To']).sum().reset_index()
        passes_away = passes_away.apply(lambda x: x / passes_away['Freq'] if x.name in ['Start Time [s]',
                                                                                        'End Time [s]',
                                                                                        'Start X',
                                                                                        'End X',
                                                                                        'Start Y',
                                                                                        'End Y',
                                                                                        ] else x)

        passes_away['Alpha'] = passes_away['Freq'] / passes_away['Freq'].max()
        max_passes_away = passes_away['Freq'].max()

        passes_away["Start X mean"] = [away_dist_stats.loc[away_dist_stats['player'] == player, f'{norm_key}x_mean'] for
                                       player in
                                       passes_away['From']]
        passes_away["Start Y mean"] = [away_dist_stats.loc[away_dist_stats['player'] == player, f'{norm_key}y_mean'] for
                                       player in
                                       passes_away['From']]
        passes_away["End X mean"] = [away_dist_stats.loc[away_dist_stats['player'] == player, f'{norm_key}x_mean'] for
                                     player in
                                     passes_away['To']]
        passes_away["End Y mean"] = [away_dist_stats.loc[away_dist_stats['player'] == player, f'{norm_key}y_mean'] for
                                     player in
                                     passes_away['To']]

        max_passes = max(max_passes_home, max_passes_away)

        passes_home['Line_Width'] = 15 * passes_home['Freq'] / max_passes
        passes_away['Line_Width'] = 15 * passes_away['Freq'] / max_passes

        sources_home_passes = ColumnDataSource(data=passes_home)
        sources_away_passes = ColumnDataSource(data=passes_away)
        pass_network_home_renderer = plot.segment(x0="Start X mean", y0="Start Y mean", x1="End X mean",
                                                  y1="End Y mean", color=match_object.home_color,
                                                  line_width="Line_Width",
                                                  alpha="Alpha", source=sources_home_passes)
        pass_network_away_renderer = plot.segment(x0="Start X mean", y0="Start Y mean", x1="End X mean",
                                                  y1="End Y mean", color=match_object.away_color,
                                                  line_width="Line_Width",
                                                  alpha="Alpha", source=sources_away_passes)

    source_home_hist_x = ColumnDataSource(data=home_x)
    source_home_hist_y = ColumnDataSource(data=home_y)
    source_away_hist_x = ColumnDataSource(data=away_x)
    source_away_hist_y = ColumnDataSource(data=away_y)

    ph.quad(bottom='bottom_x', left='left_x', right='right_x', top='top_x', source=source_home_hist_x,
            color=match_object.home_color, line_color=match_object.home_color, alpha=0.5)
    pv.quad(left='left_y', bottom='bottom_y', top='top_y', right='right_y', source=source_home_hist_y,
            color=match_object.home_color, line_color=match_object.home_color, alpha=0.5)

    ph.quad(bottom='bottom_x', left='left_x', right='right_x', top='top_x', source=source_away_hist_x,
            color=match_object.away_color, line_color=match_object.away_color, alpha=0.5)
    pv.quad(left='left_y', bottom='bottom_y', top='top_y', right='right_y', source=source_away_hist_y,
            color=match_object.away_color, line_color=match_object.away_color, alpha=0.5)

    sources_home = ColumnDataSource(data=home_dist_stats.to_dict('series'))
    sources_home_inst = ColumnDataSource(data=dict(x=[], y=[]))
    sources_ball = ColumnDataSource(data=ball_dist_stats.to_dict('series'))
    sources_ball_inst = ColumnDataSource(data=dict(x=[], y=[]))
    sources_away = ColumnDataSource(data=away_dist_stats.to_dict('series'))
    sources_away_inst = ColumnDataSource(data=dict(x=[], y=[]))

    renderer1 = plot.circle(f'{norm_key}x_mean', f'{norm_key}y_mean', source=sources_away, alpha=0.5, size=15,
                            color=match_object.away_color)
    renderer2 = plot.circle(f'{norm_key}x_mean', f'{norm_key}y_mean', source=sources_home, alpha=0.5, size=15,
                            color=match_object.home_color)
    renderer3 = plot.circle(f'{norm_key}x_mean', f'{norm_key}y_mean', source=sources_ball, alpha=0.5, size=15,
                            color="black")
    renderer4 = plot.circle(0, 0, alpha=0, size=1,
                                color="yellow")
    renderer5 = plot.circle(0, 0, alpha=0, size=1,
                            color="yellow")
    if center_of_mass & (not normalized):
        cm_df = pd.concat([home_df[["team_meanx", "team_meany"]].agg(['mean']),
                           away_df[["team_meanx", "team_meany"]].agg(['mean'])])

        cm_series = np.sqrt((np.sqrt((away_df[["team_meanx", "team_meany"]]
                                      - home_df[["team_meanx", "team_meany"]]) ** 2) ** 2).sum(axis=1))
        cm_distance = cm_series.mean()
        std_distance = cm_series.std()
        cm_source = ColumnDataSource(cm_df.to_dict("series"))
        renderer4 = plot.circle(f'team_meanx', f'team_meany', source=cm_source, alpha=0.5, size=15,
                                color="yellow")
        renderer5 = plot.line('team_meanx', 'team_meany', source=cm_source, color='yellow', line_width=3)
        cm_distance_label = Label(x=0, y=-HALF_FIELD_HEIGHT - 2,
                                  text=f'd = ({cm_distance:.2f} ± {std_distance:.2f})m',
                                  text_color="yellow",
                                  text_baseline="middle", text_align="center")
        plot.add_layout(cm_distance_label)
    taptool.renderers = [renderer1, renderer2, renderer3, renderer4, renderer5]

    plot.multi_line('x', 'y', source=sources_home_inst, color=match_object.home_color)
    plot.multi_line('x', 'y', source=sources_away_inst, color=match_object.away_color)
    plot.line('x', 'y', source=sources_ball_inst, color='black')

    labels_home = LabelSet(x=f'{norm_key}x_mean', y=f'{norm_key}y_mean', text='player_number',
                           source=sources_home, text_color="white",
                           text_font_size="10px",
                           text_baseline="middle", text_align="center")
    labels_away = LabelSet(x=f'{norm_key}x_mean', y=f'{norm_key}y_mean', text='player_number',
                           source=sources_away, text_color="white",
                           text_font_size="10px", text_baseline="middle", text_align="center")
    away_ellipse_renderer = plot.ellipse(x=f'{norm_key}x_mean',
                                         y=f'{norm_key}y_mean',
                                         width=f'cov_{norm_key}x_std',
                                         height=f'cov_{norm_key}y_std',
                                         source=sources_away,
                                         fill_color=None,
                                         line_width=1,
                                         line_color=match_object.away_color,
                                         angle=f'cov_{norm_key_angle}angle')
    home_ellipse_renderer = plot.ellipse(x=f'{norm_key}x_mean',
                                         y=f'{norm_key}y_mean',
                                         width=f'cov_{norm_key}x_std',
                                         height=f'cov_{norm_key}y_std',
                                         source=sources_home,
                                         fill_color=None,
                                         line_width=1,
                                         line_color=match_object.home_color,
                                         angle=f'cov_{norm_key_angle}angle')
    ball_ellipse_renderer = plot.ellipse(x=f'{norm_key}x_mean',
                                         y=f'{norm_key}y_mean',
                                         width=f'cov_{norm_key}x_std',
                                         height=f'cov_{norm_key}y_std',
                                         source=sources_ball,
                                         fill_color=None,
                                         line_width=1,
                                         line_color="black",
                                         angle=f'cov_{norm_key_angle}angle')
    plot.add_layout(labels_home)
    plot.add_layout(labels_away)

    # Calculating score
    if scoreboard:
        home_goals = events_df[(events_df["Subtype"] == "ON TARGET-GOAL") & (events_df["Team"] == "Home")].shape[0]
        away_goals = events_df[(events_df["Subtype"] == "ON TARGET-GOAL") & (events_df["Team"] == "Away")].shape[0]

        scoreboard = Label(x=0, y=HALF_FIELD_HEIGHT + 2, text=f'{home_goals}:{away_goals}', text_color="white",
                                text_baseline="middle", text_align="center")

        plot.add_layout(scoreboard)

    def update_data_home(attrname, old, new):
        # Get the current slider values
        c = home_time_window
        flag = False
        if isinstance(normalized, str):
            flag = True
            if normalized == 'Home' or normalized == 'Both':
                home_df = time_window(tracking_home, c.value[0], c.value[0] + window_size.value)
            elif normalized == 'Away':
                home_df = time_window(tracking_away, c.value[0], c.value[0] + window_size.value)
        else:
            home_df = time_window(tracking_home, c.value[0], c.value[0] + window_size.value)

        home_events_df = time_window(events, c.value[0], c.value[0] + window_size.value)

        home_dist_stats = bivariate_normal_distribution(home_df, match_object.home_players, against=flag)
        if pass_graph:
            if pass_network_home_renderer.visible:
                passes_home = home_events_df[
                    (home_events_df['Type'] == 'PASS') & (
                            home_events_df["From"].str.split("_").str[0] == "Home")].groupby(['From',
                                                                                              'To',
                                                                                              'Start Time [s]',
                                                                                              'End Time [s]',
                                                                                              'Start X',
                                                                                              'Start Y',
                                                                                              'End X',
                                                                                              'End Y']).size().reset_index(
                    name="Freq")
                passes_home = passes_home.groupby(['From', 'To']).sum().reset_index()
                passes_home = passes_home.apply(lambda x: x / passes_home['Freq'] if x.name in ['Start Time [s]',
                                                                                                'End Time [s]',
                                                                                                'Start X',
                                                                                                'End X',
                                                                                                'Start Y',
                                                                                                'End Y',
                                                                                                ] else x)

                passes_home['Alpha'] = passes_home['Freq'] / passes_home['Freq'].max()
                passes_home['Line_Width'] = 15 * passes_home['Freq'] / max_passes

                passes_home["Start X mean"] = [
                    home_dist_stats.loc[home_dist_stats['player'] == player, f'{norm_key}x_mean'] for
                    player in
                    passes_home['From']]
                passes_home["Start Y mean"] = [
                    home_dist_stats.loc[home_dist_stats['player'] == player, f'{norm_key}y_mean'] for
                    player in
                    passes_home['From']]
                passes_home["End X mean"] = [
                    home_dist_stats.loc[home_dist_stats['player'] == player, f'{norm_key}x_mean'] for
                    player in
                    passes_home['To']]
                passes_home["End Y mean"] = [
                    home_dist_stats.loc[home_dist_stats['player'] == player, f'{norm_key}y_mean'] for
                    player in
                    passes_home['To']]
                sources_home_passes.data = passes_home

        sources_home.data = home_dist_stats.to_dict(
            'series')
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
            source_home_hist_x.data, source_home_hist_y.data = histogram(home_df, players, density=True,
                                                                         normalised=flag)
        else:
            sources_home_inst.data = dict(x=[], y=[])
            source_home_hist_x.data, source_home_hist_y.data = histogram(home_df, match_object.home_players,
                                                                         density=True, normalised=flag)

    def update_data_away(attrname, old, new):
        # Get the current slider values
        c = away_time_window
        flag = False
        if isinstance(normalized, str):
            flag = True
            if normalized == 'Away' or normalized == 'Both':
                away_df = time_window(tracking_away, c.value[0], c.value[0] + window_size.value)
            elif normalized == 'Home':
                away_df = time_window(tracking_home, c.value[0], c.value[0] + window_size.value)
        else:
            away_df = time_window(tracking_away, c.value[0], c.value[0] + window_size.value)

        away_events_df = time_window(events, c.value[0], c.value[0] + window_size.value)

        away_dist_stats = bivariate_normal_distribution(away_df, match_object.away_players, against=flag)
        if pass_graph:
            if pass_network_away_renderer.visible:
                passes_away = away_events_df[
                    (away_events_df['Type'] == 'PASS') & (
                            away_events_df["From"].str.split("_").str[0] == "Away")].groupby(
                    ['From',
                     'To',
                     'Start Time [s]',
                     'End Time [s]',
                     'Start X',
                     'Start Y',
                     'End X',
                     'End Y']).size().reset_index(
                    name="Freq")
                passes_away = passes_away.groupby(['From', 'To']).sum().reset_index()
                passes_away = passes_away.apply(lambda x: x / passes_away['Freq'] if x.name in ['Start Time [s]',
                                                                                                'End Time [s]',
                                                                                                'Start X',
                                                                                                'End X',
                                                                                                'Start Y',
                                                                                                'End Y',
                                                                                                ] else x)
                passes_away['Alpha'] = passes_away['Freq'] / passes_away['Freq'].max()
                passes_away['Line_Width'] = 15 * passes_away['Freq'] / max_passes

                passes_away["Start X mean"] = [
                    away_dist_stats.loc[away_dist_stats['player'] == player, f'{norm_key}x_mean'] for
                    player in
                    passes_away['From']]
                passes_away["Start Y mean"] = [
                    away_dist_stats.loc[away_dist_stats['player'] == player, f'{norm_key}y_mean'] for
                    player in
                    passes_away['From']]
                passes_away["End X mean"] = [
                    away_dist_stats.loc[away_dist_stats['player'] == player, f'{norm_key}x_mean'] for
                    player in
                    passes_away['To']]
                passes_away["End Y mean"] = [
                    away_dist_stats.loc[away_dist_stats['player'] == player, f'{norm_key}y_mean'] for
                    player in
                    passes_away['To']]
                sources_away_passes.data = passes_away

        sources_away.data = away_dist_stats.to_dict(
            'series')
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
            source_away_hist_x.data, source_away_hist_y.data = histogram(away_df, players, density=True,
                                                                         normalised=flag)
        else:
            sources_away_inst.data = dict(x=[], y=[])
            source_away_hist_x.data, source_away_hist_y.data = histogram(away_df, match_object.away_players,
                                                                         density=True, normalised=flag)

    def update_data_ball(attrname, old, new):
        # Get the current slider values
        c = ball_time_window
        home_time_window.value = [c.value, c.value + window_size.value]
        away_time_window.value = [c.value, c.value + window_size.value]
        home_df = time_window(tracking_home, c.value, c.value + window_size.value)
        away_df = time_window(tracking_away, c.value, c.value + window_size.value)
        events_df = time_window(events, c.value, c.value + window_size.value)
        sources_ball.data = bivariate_normal_distribution(home_df, ball=True).to_dict('series')
        if len(sources_ball.selected.indices) == 1:
            sources_ball_inst.data = dict(x=home_df[f"ball_{norm_key}x"],
                                          y=home_df[f"ball_{norm_key}y"])
        else:
            sources_ball_inst.data = dict(x=[], y=[])
        if center_of_mass & (not normalized):
            cm_df = pd.concat([home_df[["team_meanx", "team_meany"]].agg(['mean']),
                               away_df[["team_meanx", "team_meany"]].agg(['mean'])])
            cm_series = np.sqrt((np.sqrt((away_df[["team_meanx", "team_meany"]]
                                          - home_df[["team_meanx", "team_meany"]]) ** 2) ** 2).sum(axis=1))
            cm_distance = cm_series.mean()
            std_distance = cm_series.std()
            cm_distance_label.text = f'd = ({cm_distance:.2f} ± {std_distance:.2f})m'
            cm_source.data = cm_df.to_dict("series")
        if scoreboard:
            away_goals = events_df[
                    (events_df["Subtype"] == "ON TARGET-GOAL") & (events_df["Team"] == "Away")].shape[0]
            home_goals = events_df[
                (events_df["Subtype"] == "ON TARGET-GOAL") & (events_df["Team"] == "Home")].shape[0]
            scoreboard.text = f'{home_goals}:{away_goals}'

    def update_checkbox(attrname, old, new):
        pass_network_home_renderer.visible = (0 in checkbox_group.active)
        pass_network_away_renderer.visible = (1 in checkbox_group.active)
        home_ellipse_renderer.visible = (2 in checkbox_group.active)
        away_ellipse_renderer.visible = (3 in checkbox_group.active)
        renderer1.visible = (4 in checkbox_group.active)
        renderer2.visible = (5 in checkbox_group.active)
        renderer3.visible = (6 in checkbox_group.active)
        ball_ellipse_renderer.visible = (6 in checkbox_group.active)
        labels_home.visible = (5 in checkbox_group.active)
        labels_away.visible = (4 in checkbox_group.active)
        renderer4.visible = (7 in checkbox_group.active)
        renderer5.visible = (7 in checkbox_group.active)

    home_time_window.on_change('value', update_data_home)
    away_time_window.on_change('value', update_data_away)
    ball_time_window.on_change('value', update_data_ball)
    checkbox_group.on_change('active', update_checkbox)
    sources_home.selected.on_change('indices', update_data_home)
    sources_away.selected.on_change('indices', update_data_away)
    sources_ball.selected.on_change('indices', update_data_ball)

    # Set up layouts and add to document
    inputs = gridplot([[ph, checkbox_group],
                       [plot, pv],
                       [ball_time_window, window_size],
                       [home_time_window, None],
                       [away_time_window, None]], merge_tools=False)

    def modify_doc(doc):
        doc.add_root(row(inputs, width=800))

    handler = FunctionHandler(modify_doc)
    app = Application(handler)
    show(app)
    return inputs
