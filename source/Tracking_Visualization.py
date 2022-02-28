import numpy as np
from bokeh.plotting import figure
from matplotlib.colors import LinearSegmentedColormap
from Tracking_Constants import *

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
               stripes_number = 7):

    if fig is None:
        p = figure(width = int(field_dimen[0])*size,
                   height=int(field_dimen[1])*size,
                   background_fill_color = background_fill_color
                  )
        p.xgrid.grid_line_color = None
        p.ygrid.grid_line_color = None
        p.x_range.range_padding = 0
        p.y_range.range_padding = 0
        p.x_range.bounds = [-field_dimen[0]/2-padding,field_dimen[0]/2+padding]
        p.y_range.bounds = [-field_dimen[1]/2-padding,field_dimen[1]/2+padding]
        p.axis.minor_tick_line_color = None
        p.axis.visible = False
        
    else:
        p = fig
    
    d = generate_grass_pattern(field_dimen, padding, pattern = pattern, noise = noise, stripes_number = stripes_number)
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
                           stripes_number = 7):
    N = 1000
    x = np.linspace(0, field_dimen[0], N)
    y = np.linspace(0, field_dimen[1], N)
    xx, yy = np.meshgrid(x, y)
    d = np.zeros(shape= xx.shape)
    
    if pattern is not None:
        pattern = pattern.split('_')
        stripes_width = field_dimen[0]/stripes_number
        if noise:
            d += np.random.randint(0, 1000, xx.shape)
            d -= ((xx-field_dimen[0]/2)**2+5*(yy-field_dimen[1]/2)**2)/5

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
    cmap = LinearSegmentedColormap.from_list('grass', [color_from, color_to], N=30)
    cmap = cmap(np.linspace(0, 1, 30))
    cmap = np.concatenate((cmap[:10][::-1], cmap))
    cmap = ["#%02x%02x%02x" % (int(r), int(g), int(b)) for r, g, b, _ in 255*cmap]
    return cmap