# Script intended to gather dataframe filtering functions.

def time_window(tracking_dataframe, start, end, frame = False):

    if not frame:
        try:
            return tracking_dataframe[(tracking_dataframe['Time [s]'] <= end) & (tracking_dataframe['Time [s]'] >= start)]
        except:
            return tracking_dataframe[(tracking_dataframe['End Time [s]'] <= end) & (tracking_dataframe['Start Time [s]'] >= start)]
    else:
        try:
            return tracking_dataframe[(tracking_dataframe['Frame'] <= end) & (tracking_dataframe['Frame'] >= start)]
        except:
            return tracking_dataframe[(tracking_dataframe['End Frame'] <= end) & (tracking_dataframe['Start Frame'] >= start)]
    