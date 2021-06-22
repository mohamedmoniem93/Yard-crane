# -*- coding: utf-8 -*-

from bokeh.plotting import figure, show

def draw_graph(x, y):
    # create a new plot with a title and axis labels
    p = figure(title="Simple line example", x_axis_label='x', y_axis_label='y')
    # add a line renderer with legend and line thickness to the plot
    p.line(x, y, name="Temp.", line_width=2)
    # show the results
    show(p)


if __name__ == "__main__":
    x = [1, 2, 3, 4, 5]
    y = [6, 7, 2, 4, 5]
    draw_graph(x, y)