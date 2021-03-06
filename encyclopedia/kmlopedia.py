# standard
import unittest
# internal
from nits.time import unix2str
from nits.cast import To, cast
from encyclopedia import Record, XML

class To_KML():

    def make_listmode(u=None):
        return 'check' if u is None else u

    def make_integer(i=None):
        try:
            return int(i)
        except (ValueError, TypeError) as e:
            return None

    listmode = cast(make_listmode)
    uid = cast(To.string, 'unknown')
    id = cast(To.string, '')
    fraction = cast(To.fraction, 1)
    sloppyint = cast(make_integer)

class KML(XML):
    '''
    An encyclopedia-ified version of the KML (Keyhole Markup Language) GIS format.
    In addtion to encyclopedia operations, KML supports the following features:

    - a draw function for ease in creating a KML geometries
    - records for managing KML styles and coordinates
    '''

    # KML type choices ...

    GEOMETRIES = ['Point', 'LineString', 'LinearRing', 'Polygon', 'Model', 'gx:Track']
    ALTITUDE_MODES = ['relativeToGround', 'absolute', 'clampToGround']

    # specific google earth images ...

    BLUE_ARROW = 'http://earth.google.com/images/kml-icons/track-directional/track-0.png'
    WHITE_PADDLE = 'http://maps.google.com/mapfiles/kml/paddle/wht-blank.png'

    # spacing for writing Coordinates in at least a semi-pretty fashion ...

    SPACER = '\n' + ' '*10

    Coordinate = Record({
        'uid':To_KML.uid, # track id, unique
        'id':To.string, # label, non-unique
        'pid':To_KML.uid, # polygonal grouping id
        'tick':To.numeric, # UNIX time
        'begin':To_KML.sloppyint, # UNIX time
        'end':To_KML.sloppyint, # UNIX time
        'lat':To.signed_degree_90,
        'lon':To.signed_degree,
        'alt':To.numeric,
        'description':To.string, # KML description
        'point':To.string,# KML point string goes here
        'time':To.string,# KML time string goes here
        }, autopopulate=True, restrict=False).instance()

    Style = Record({
        'id':str,
        'show.fields':list, # show these fields in description. TODO: change this name to show.description
        'show.data':list, # show these fields in extended data
        'label.red':To_KML.fraction,
        'label.blue':To_KML.fraction,
        'label.green':To_KML.fraction,
        'label.opacity':To_KML.fraction,
        'label.scale':cast(To.integer, 1),
        'label.color': To.string,
        'line.width':To.abs_numeric,
        'line.red':To_KML.fraction,
        'line.blue':To_KML.fraction,
        'line.green':To_KML.fraction,
        'line.opacity':To_KML.fraction,
        'line.width':To.abs_numeric,
        'line.color':To.string,
        'fill.red':To_KML.fraction,
        'fill.blue':To_KML.fraction,
        'fill.green':To_KML.fraction,
        'fill.opacity':To_KML.fraction,
        'fill.on':To.integer,
        'fill.outline':To.integer,
        'fill.color': To.string,
        'list.mode':To_KML.listmode,
        'list.red':To_KML.fraction,
        'list.blue':To_KML.fraction,
        'list.green':To_KML.fraction,
        'list.opacity':To_KML.fraction,
        'list.color': To.string,
        'icon.shape':To.string,
        'icon.red':To_KML.fraction,
        'icon.blue':To_KML.fraction,
        'icon.green':To_KML.fraction,
        'icon.opacity':To_KML.fraction,
        'icon.color': To.string,
        'icon.scale':cast(To.numeric, 1),
        'model.shape': To.string,
        'model.xscale': cast(To.numeric, 1),
        'model.yscale': cast(To.numeric, 1),
        'model.zscale': cast(To.numeric, 1),
        'model.heading': To.degree,
        'model.roll': To.signed_degree,
        'model.tilt': To.signed_degree,
        }, autopopulate=True).instance()

    # type conversion functions ...

    @staticmethod
    def feet2meter(feet=0):
        return str(float(feet) * 0.3048)

    @staticmethod
    def meter2feet(meter=0):
        return float(meter) / 0.3048

    @staticmethod
    def nm2meter(nm=0):
        return str(float(nm) * 1852)

    @staticmethod
    def styled(record):
        '''
        create a KML style
        '''
        style = KML.Style(record)
        for field in ['fill', 'line', 'icon', 'label', 'list']:
            style[field + '.color'] = ''.join([
                To.hex_string(style[field + '.opacity']),
                To.hex_string(style[field + '.blue']),
                To.hex_string(style[field + '.green']),
                To.hex_string(style[field + '.red'])
                ])
        return style

    @staticmethod
    def timestamped(tick):
        return unix2str(float(tick), '%Y-%m-%dT%H:%M:%S.%fZ')

    @staticmethod
    def coordinated(record, show_description=None, show_data=None, altitude_in_feet=True):
        '''
        create a KML coordinate
        '''
        coordinate = KML.Coordinate(record)
        if show_description is not None:
            coordinate['description'] = '\n'.join([i+': '+str(coordinate[i]) for i in show_description])
        if show_data is not None:
            coordinate['data'] = [(i, str(coordinate[i])) for i in show_data]
        coordinate['time'] = KML.timestamped(coordinate['tick'])
        if altitude_in_feet:
            coordinate['alt'] = KML.feet2meter(coordinate['alt'])
        if not coordinate['point']:
            coordinate['point'] = ','.join([str(coordinate['lon']), str(coordinate['lat']), str(coordinate['alt'])])
        return coordinate

    def __init__(self):
        XML.__init__(self)
        self += 'kml'
        self['kml'] = 'Document'

    def write(self,
            filename=None,
            doctype=None,
            mlns='http://www.opengis.net/kml/2.2',
            gxmlns='http://www.google.com/kml/ext/2.2'):

        '''
        write KML to a file
        '''
        if mlns is not None:
            self['kml'].set('xmlns', mlns)
        if gxmlns is not None:
            self['kml'].set('xmlns:gx', gxmlns)
        XML.write(self, filename, doctype)

    def stylize(self, record):
        '''
        create a KML style element
        '''
        style = KML.styled(record)
        style_folder = style['id'] + '/Style'
        self['Document'] = style_folder
        self[style_folder].set('id', style['id'])

        substyle = {}
        for kind in ['label', 'line', 'poly', 'icon', 'list']:
            self[style_folder] = substyle[kind] = style_folder + '/' + kind.capitalize() + 'Style'

        for kind in ['label', 'line', 'icon', 'list']:
            self[substyle[kind], 'color'] = style[kind + '.color']
        for kind in ['label', 'icon']:
            self[substyle[kind], 'scale'] = style[kind + '.scale']

        self[substyle['poly'], 'outline'] = style['fill.outline']
        self[substyle['poly'], 'fill'] = style['fill.on']
        if style['fill.on']:
            self[substyle['poly'], 'color'] = style['fill.color']
        else:
            self[substyle['poly'], 'color'] = style['line.color']

        self[substyle['line'], 'width'] = style['line.width']

        if style['icon.shape']:
            self[substyle['icon']] = substyle['icon'] + '/Icon'
            self[substyle['icon'] + '/Icon', 'href'] = style['icon.shape']
        self[substyle['list'], 'listItemType'] = style['list.mode']

        return style

    def _draw(self,
                folder,
                point, # single point
                visibility,
                geometry,
                extrude,
                style,
                tesselate,
                altitude):
        '''
        internal drawing function for (starting) a single geometry.
        Classes inheriting KML may choose to use this directly.
        '''
        if geometry == 'Model':
            assert style['model.shape'] is not None

        assert geometry in KML.GEOMETRIES
        assert altitude in KML.ALTITUDE_MODES

        self[folder] = placemark = self.unique('Placemark')
        self[placemark, 'name'] = point['id']
        self[placemark, 'visibility'] = visibility

        if 'data' in point and point['data']:
            self[placemark] = ed = self.unique('ExtendedData')
            for field, value in point['data']:
                self[ed] = edt = self.unique('Data')
                self[edt].attrib['name'] = field
                self[edt, 'value'] =value
        elif 'description' in point and point['description']:
            self[placemark, 'description'] = point['description']

        self[placemark, 'styleUrl'] = style['id']

        if 'begin' in point or 'end' in point:
            self[placemark] = timespan = self.unique('TimeSpan')
            for bound in ['begin', 'end']:
                if bound in point and point[bound] is not None:
                    self[timespan, bound] = KML.timestamped(point[bound])

        if geometry == 'Model':
            self[placemark] = track = placemark + '/gx:Track'
            self[track].set('id', point['id'])
            self[track] = model = self.unique('Model')
            self[model] = scaler = self.unique('Scale')
            self[scaler, 'x'] = style['model.xscale']
            self[scaler, 'y'] = style['model.yscale']
            self[scaler, 'z'] = style['model.zscale']
            self[model] = orientation = self.unique('Orientation')
            self[orientation, 'tilt'] = style['model.tilt']
            self[orientation, 'roll'] = style['model.roll']
            self[orientation, 'heading'] = style['model.heading']
            self[model] = link = self.unique('Link')
            self[link, 'href'] = style['model.shape']
            self[track, 'altitudeMode'] = altitude
            return track
        else:
            self[placemark] = geom = self.unique(geometry)
            self[geom].set('id', point['id'])
            self[geom, 'extrude'] = To.integer(extrude)
            self[geom, 'tesselate'] = To.integer(tesselate)
            self[geom, 'altitudeMode'] = altitude
            if geometry == 'Polygon':
                self[geom] = outer = self.unique('outerBoundaryIs')
                self[outer] = geom = self.unique('LinearRing')
            return geom

    def draw(self,
            points,
            folder,
            style,
            geometry='LineString',
            extrude=False, # connect geometry to ground
            visibility=True, # show on startup
            tesselate=None, # follow terrain
            altitude='absolute'):

        '''
        create a KML geometry in a specified folder using:

        - collection of KML drawing parameters
        - set of points

        points are provided as an iterated list of dictionaries with (at least) the following fields:

        - uid (Unique Identifier)
        - id (KML element label)
        - lat
        - lon
        - alt (in feet)
        - tick (UNIX time)

        Points will be plotted in the order they are occur in the stream
        Meta data (e.g. id) will only be taken from the first point in the stream

        if begin/end appears as fields:

        - begin (UNIX time)
        - end (UNIX time)

        will create a time block.  As with meta data, only the data on the first uid appearance is used
        '''

        def complete(element, coords, ticks):
            '''
            finish creating a geometric element
            '''
            if geometry in ['gx:Track', 'Model']:
                assert len(ticks) == len(coords)
                for tick in ticks:
                    self[element, 'when'] = tick
                for coord in coords:
                    self[element, 'gx:coord'] = coord.replace(',', ' ') # different syntax than coordinate  ... for whatever reason :-/
            else:
                self[element, 'coordinates'] = KML.SPACER + KML.SPACER.join(coords) # all in one element

        last = coords = ticks = None
        for p in points:
            point = KML.coordinated(p,
                show_description=style['show.fields'],
                show_data=style['show.data'])
            if point['uid'] == last:
                coords.append(point['point'])
                ticks.append(point['time'])
            else:
                if last is not None:
                    complete(drawn, coords, ticks)
                last = point['uid']
                drawn = self._draw(
                    folder,
                    point,
                    visibility=visibility,
                    geometry=geometry,
                    style=style,
                    extrude=extrude,
                    tesselate=tesselate,
                    altitude=altitude)

                coords = [point['point']]
                ticks = [point['time']]

        if coords is not None:
            complete(drawn, coords, ticks) # last one

class Test_KML(unittest.TestCase):

    def test_style(self):
        style = KML.styled(KML.Style())
        assert style['line.color'] == 'FFFFFFFF'
        assert style['fill.color'] == 'FFFFFFFF'

    def test_kml(self):
        KML()

    def test_colors(self):
        color = KML.Style()
        assert To.hex_string(color['line.red']) == 'FF'
        color['line.red'] = .5
        assert To.hex_string(color['line.red']) == '7F'
        assert color['icon.scale'] == 1

    def test_coordinates(self):
        coordinate = KML.Coordinate({'uid':11})
        assert coordinate['uid'] == '11'
        coordinate['lon'] = -182
        assert coordinate['lon'] == 178.
        coordinate['lon'] = coordinate['lon']
        assert coordinate['lon'] == 178.
        assert coordinate['pid'] == 'unknown'
        assert coordinate['id'] == ''
        coordinate = KML.coordinated(KML.Coordinate({'alt':0}))
        assert coordinate['point'] == '0.0,0.0,0.0'
        coordinate['id'] = 11
        assert coordinate['id'] == '11'

if __name__ == '__main__':
    unittest.main()
