from datetime import datetime
from bokeh.models import DatetimeTickFormatter, NumeralTickFormatter
from bokeh.plotting import figure, save
from bokeh.document import Document

class Plotter:
    def __init__(self):
        self.dates_array = []
        self.prices_array = []

    def add_date_price(self, date, price):
        if type(date) is str and type(price) is str:
            try:
                date = list(map(int, date.split('.')[::-1]))
                price = int(price)
                self.dates_array.append(datetime(*date))
                self.prices_array.append(price)
            except ValueError:
                return -1

        return 0

    def get_json_plot(self, plot_name):
        if type(plot_name) is not str:
            return ''

        if not self.dates_array or not self.prices_array or \
                len(self.dates_array) != len(self.dates_array):
            return ''

        plot = figure(
                title=plot_name,
                x_axis_type='datetime',
                sizing_mode='stretch_width',
                x_axis_label='days',
                y_axis_label='price'
        )

        slice_start_index = 0
        n_nones = self.prices_array.count(-1) # -1 means that price not found

        for i in range(n_nones):
            none_index = self.prices_array[slice_start_index:].index(-1) + slice_start_index
            plot.circle(
                    self.dates_array[slice_start_index:none_index],
                    self.prices_array[slice_start_index:none_index],
                    size=8
            )

            plot.line(
                    self.dates_array[slice_start_index:none_index],
                    self.prices_array[slice_start_index:none_index],
                    color='navy',
                    line_width=1
            )

            slice_start_index = none_index + 1

        plot.circle(
                self.dates_array[slice_start_index:],
                self.prices_array[slice_start_index:],
                size=8
        )

        plot.line(
                self.dates_array[slice_start_index:],
                self.prices_array[slice_start_index:],
                color='navy',
                line_width=1
        )

        plot.xaxis[0].formatter = DatetimeTickFormatter(days='%d/%b', months='%b %Y')
        plot.yaxis[0].formatter = NumeralTickFormatter(format='0,0')

        plot_document = Document()
        plot_document.add_root(plot)
        return plot_document.to_json_string()

#FILL_PLOT = \
#'''
#{"defs":[],"roots":{"references":[{"attributes":{},"id":"1007","type":"DataRange1d"},{"attributes":{"axis_label":"price","coordinates":null,"formatter":{"id":"1043"},"group":null,"major_label_policy":{"id":"1044"},"ticker":{"id":"1018"}},"id":"1017","type":"LinearAxis"},{"attributes":{},"id":"1044","type":"AllLabels"},{"attributes":{},"id":"1049","type":"Selection"},{"attributes":{"line_alpha":0.2,"line_color":"#1f77b4","x":{"field":"x"},"y":{"field":"y"}},"id":"1038","type":"Line"},{"attributes":{},"id":"1011","type":"LinearScale"},{"attributes":{"line_alpha":0.1,"line_color":"#1f77b4","x":{"field":"x"},"y":{"field":"y"}},"id":"1037","type":"Line"},{"attributes":{},"id":"1026","type":"HelpTool"},{"attributes":{},"id":"1021","type":"PanTool"},{"attributes":{"overlay":{"id":"1027"}},"id":"1023","type":"BoxZoomTool"},{"attributes":{},"id":"1024","type":"SaveTool"},{"attributes":{},"id":"1046","type":"BasicTickFormatter"},{"attributes":{},"id":"1025","type":"ResetTool"},{"attributes":{"line_color":"#1f77b4","x":{"field":"x"},"y":{"field":"y"}},"id":"1036","type":"Line"},{"attributes":{},"id":"1048","type":"UnionRenderers"},{"attributes":{"bottom_units":"screen","coordinates":null,"fill_alpha":0.5,"fill_color":"lightgrey","group":null,"left_units":"screen","level":"overlay","line_alpha":1.0,"line_color":"black","line_dash":[4,4],"line_width":2,"right_units":"screen","syncable":false,"top_units":"screen"},"id":"1027","type":"BoxAnnotation"},{"attributes":{"axis":{"id":"1017"},"coordinates":null,"dimension":1,"group":null,"ticker":null},"id":"1020","type":"Grid"},{"attributes":{},"id":"1018","type":"BasicTicker"},{"attributes":{"axis":{"id":"1013"},"coordinates":null,"group":null,"ticker":null},"id":"1016","type":"Grid"},{"attributes":{},"id":"1022","type":"WheelZoomTool"},{"attributes":{"source":{"id":"1035"}},"id":"1040","type":"CDSView"},{"attributes":{},"id":"1009","type":"LinearScale"},{"attributes":{"tools":[{"id":"1021"},{"id":"1022"},{"id":"1023"},{"id":"1024"},{"id":"1025"},{"id":"1026"}]},"id":"1028","type":"Toolbar"},{"attributes":{"coordinates":null,"group":null,"text":"Product name"},"id":"1003","type":"Title"},{"attributes":{},"id":"1047","type":"AllLabels"},{"attributes":{"axis_label":"date","coordinates":null,"formatter":{"id":"1046"},"group":null,"major_label_policy":{"id":"1047"},"ticker":{"id":"1014"}},"id":"1013","type":"LinearAxis"},{"attributes":{},"id":"1043","type":"BasicTickFormatter"},{"attributes":{},"id":"1005","type":"DataRange1d"},{"attributes":{},"id":"1014","type":"BasicTicker"},{"attributes":{"data":{"x":[],"y":[]},"selected":{"id":"1049"},"selection_policy":{"id":"1048"}},"id":"1035","type":"ColumnDataSource"},{"attributes":{"coordinates":null,"data_source":{"id":"1035"},"glyph":{"id":"1036"},"group":null,"hover_glyph":null,"muted_glyph":{"id":"1038"},"nonselection_glyph":{"id":"1037"},"view":{"id":"1040"}},"id":"1039","type":"GlyphRenderer"},{"attributes":{"below":[{"id":"1013"}],"center":[{"id":"1016"},{"id":"1020"}],"left":[{"id":"1017"}],"renderers":[{"id":"1039"}],"title":{"id":"1003"},"toolbar":{"id":"1028"},"x_range":{"id":"1005"},"x_scale":{"id":"1009"},"y_range":{"id":"1007"},"y_scale":{"id":"1011"}},"id":"1002","subtype":"Figure","type":"Plot"}],"root_ids":["1002"]},"title":"Bokeh Application","version":"2.4.2"}
#'''
