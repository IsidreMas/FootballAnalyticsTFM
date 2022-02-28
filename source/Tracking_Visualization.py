import numpy as np
from bokeh.plotting import figure
from matplotlib.colors import LinearSegmentedColormap
from Tracking_Constants import LOW_GRASS_COLOR, HIGH_GRASS_COLOR

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

def generate_grass_pattern(field_dimen,
                           padding,
                           pattern = "stripes_circles",
                           noise = True, 
                           stripes_number = 7):
    N = 1000
    x = np.linspace(0, field_dimen[0], N)
    y = np.linspace(0, field_dimen[1], N)
    xx, yy = np.meshgrid(x, y)
    d = np.zeros(shape= xx.shape)
    
    if pattern is not None:
        pattern = pattern.split('_')

        if noise:
            d += np.random.randint(0, 1000, xx.shape)
            d -= ((xx-field_dimen[0]/2)**2+5*(yy-field_dimen[1]/2)**2)/5

        if 'stripes'in pattern:       
            stripes_width = field_dimen[0]/stripes_number
            if ('vertical' in pattern) or ('horizontal' not in pattern):
                d += 100*np.sign(np.sin((xx - stripes_width/2)*2*np.pi/stripes_width))
            if 'horizontal' in pattern:
                d += 100*np.sign(np.sin((yy - stripes_width/2)*2*np.pi/stripes_width))
        
        if 'circles' in pattern:
            d += 100*np.sign(np.sin((np.sqrt((yy- field_dimen[1]/2)**2+(xx - field_dimen[0]/2)**2))*2*np.pi/stripes_width))
    
    return d

def draw_pitch(field_dimen = (106.,60.),
               fig = None, 
               size = 7, 
               padding = 4, 
               pattern = "stripes_circles_horizontal_vertical", 
               noise = True):
    if fig is None:
        p = figure(width = int(field_dimen[0])*size,
                   height=int(field_dimen[1])*size,
                   background_fill_color = "lightgreen"
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
    
    d = generate_grass_pattern(field_dimen, padding, pattern = pattern, noise = noise)
    p.image(image=[d], x=-field_dimen[0]/2-padding, y=-field_dimen[1]/2-padding, dw=field_dimen[0]+2*padding, dh=field_dimen[1]+2*padding, palette=linear_cmap(), level="image", alpha = 0.6)
    
    # ALL DIMENSIONS IN m
    meters_per_yard = 0.9144 # unit conversion from yards to meters
    half_pitch_length = field_dimen[0]/2. # length of half pitch
    half_pitch_width = field_dimen[1]/2. # width of half pitch
    signs = [-1,1] 
    # Soccer field dimensions typically defined in yards, so we need to convert to meters
    half_goal_line = 8*meters_per_yard/2
    box_width = 20*meters_per_yard
    box_length = 6*meters_per_yard
    area_width = 44*meters_per_yard
    area_length = 18*meters_per_yard
    penalty_spot = 12*meters_per_yard
    corner_radius = 1*meters_per_yard
    D_pos = 12*meters_per_yard
    centre_circle_radius = 10*meters_per_yard
    
    p.patch([-half_pitch_length,-half_pitch_length, half_pitch_length, half_pitch_length],
            [-half_pitch_width, half_pitch_width, half_pitch_width, -half_pitch_width],
            line_width=2,
            fill_color = None,
            line_color = "white")
    
    p.segment(x0 = 0, y0 = -half_pitch_width, x1 = 0,
          y1= half_pitch_width, color="white", line_width=2)
    
    D_half_angle = np.arcsin(2*np.sqrt(centre_circle_radius**2-(area_length-D_pos)**2)/(2*centre_circle_radius))
    
    p.arc(x = [0,half_pitch_length-D_pos,-half_pitch_length+D_pos],
          y = [0,0,0],
          radius=centre_circle_radius,
          start_angle=[0,np.pi-D_half_angle,2*np.pi-D_half_angle],
          end_angle=[2*np.pi,np.pi+D_half_angle,D_half_angle],
          color="white",
          line_width = 2)
    
    p.annulus(x = [0,half_pitch_length-D_pos,-half_pitch_length+D_pos],
          y = [0,0,0], outer_radius = 0.3, color="white")
    
    p.arc(x = [-half_pitch_length,half_pitch_length,-half_pitch_length,half_pitch_length],
          y = [half_pitch_width,half_pitch_width,-half_pitch_width,-half_pitch_width],
          radius=corner_radius,
          start_angle=[np.pi*3/2,np.pi,0,np.pi/2],
          end_angle=[2*np.pi,np.pi*3/2,np.pi/2,np.pi],
          color="white",
          line_width = 2)
    
    for s in [1,-1]:
        p.line([s*half_pitch_length, s*(half_pitch_length-area_length),
                s*(half_pitch_length-area_length), s*half_pitch_length,],
               [area_width/2, area_width/2, -area_width/2, -area_width/2],
               line_width=2,
               line_color = "white")
        p.line([s*half_pitch_length, s*(half_pitch_length-box_length),
                s*(half_pitch_length-box_length), s*half_pitch_length,],
               [box_width/2, box_width/2, -box_width/2, -box_width/2],
               line_width=2,
               line_color = "white")
        p.line([s*half_pitch_length, s*(half_pitch_length+1.5),
                s*(half_pitch_length+1.5), s*half_pitch_length],
               [half_goal_line, half_goal_line, -half_goal_line, -half_goal_line],
               line_width=2,
               line_color = "white")
    
    
    return p