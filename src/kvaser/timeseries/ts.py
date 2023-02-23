# -*- coding: utf-8 -*-
#
# Time series utilities
# Copyright (c) 2019-2023 Klaus K. Holst.  All rights reserved.

import datetime
import pytz
import math
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def now(tz='Europe/Copenhagen'):
    if tz is None:
        for i in pytz.common_timezones:
            print(i)
        return None
    return pd.to_datetime(datetime.datetime.now()).tz_localize(tz)


def ts(x, index=None, tz='Europe/Copenhagen'):
    if not isinstance(x, (pd.Series, pd.DataFrame)):
        try:
            x = pd.DataFrame(x)
        except Exception as ex:
            raise TypeError("Pandas type expected") from ex
    if index is None:
        index = x.index
    else:
        index = pd.to_datetime(index)
        if index.dt.tz is None:
            index = index.dt.tz_localize(tz)
        else:
            index = index.dt.tz_convert(tz)
        x.index = index
    return x


def plot(y, upper=None, lower=None,
         interval_text='Prediction interval',
         highlight_start=None, highlight_text="",
         highlight_color="MediumPurple", highlight_fill="Gray",
         line_shape="hvh",
         select_fraction=0.2,
         title=None):
    r"""Plot time series

    See Also
    ----------
    plotly.express.scatter

    Returns
    ----------
    plotly.graph_objs._figure.Figure
        plotly object

    Parameters
    ----------
    y: pandas.Series
        Series or DataFrame with time series in each column
    upper: pandas.Series
        Upper prediction limit (single series)
    lower: pandas.Series
        Lower prediction limit (single series)
    interval_text: str
    highlight_start: str
    highlight_text: str
    highlight_color: str
    highlight_fill: str
    line_shape: str
    select_fraction: float
    title: str
    """

    if not isinstance(y, (pd.Series, pd.DataFrame)):
        try:
            y = pd.DataFrame(y)
        except Exception as ex:
            raise TypeError("Pandas type expected") from ex
    time = y.index
    first = min(time)
    last = max(time)
    if isinstance(y, pd.Series):
        fig = px.line(x=time, y=y,
                      title=title)
    else:
        fig = px.line(y, x=time, y=y.columns,
                      render_mode='auto',
                      title=title)
    if upper is not None and lower is not None:
        fig.add_traces([go.Scatter(x=time, y=upper,
                                   mode='lines', line_color='rgba(0,0,0,0)',
                                   showlegend=False),
                        go.Scatter(x=time, y=lower,
                                   mode='lines', line_color='rgba(0,0,0,0)',
                                   name=interval_text,
                                   fill='tonexty', fillcolor='rgba(0, 0, 255, 0.2)')])

    if highlight_start is not None:
        fig.update_layout(shapes=[dict(type='line',
                                       yref='paper', y0=0, y1=1,
                                       xref='x', x0=highlight_start, x1=highlight_start,
                                       line=dict(color=highlight_color,
                                                 width=3,
                                                 dash="dot")
                                    )])
        fig.add_vrect(x0=first, x1=highlight_start,
                      fillcolor=highlight_fill, opacity=0.2, line_width=0)
        fig.add_vrect(x0=highlight_start, x1=last,
                      annotation_text=highlight_text, annotation_position="top left",
                      annotation_font_size=11,
                      annotation_font_color=highlight_color,
                      line_width=0)
    fig.update_traces(line_shape=line_shape)
    select_visible = False
    if select_fraction > 0:
        sel_index = math.floor(len(time)*(1-select_fraction))
        select_visible = True
        fig.update_xaxes(
            range=[time[sel_index], last],
            rangeslider=dict(visible=True,
                             range=[first, last]),
            rangeselector={
                'visible': select_visible,
            })
    return fig
