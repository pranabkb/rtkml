import sys
import argparse

try:
    import requests
    import simplekml
    import polyline
except ModuleNotFoundError:
    yn = input('It looks like you are missing the required libraries. Would you like to install them now? [Y|n] ')
    if yn.lower().startswith('y') or len(yn) == 0:
        import pip
        print('Installing required libraries...')
        pip.main(['install', '-r', 'requirements.txt'])
        print('Libraries installed.\n\n')
    else:
        sys.exit(0)

URL = 'https://maps.roadtrippers.com/api/v2/trips/%s'

def export(trip_ids, no_waypoints=False, no_paths=False):
    import requests
    import simplekml
    import polyline
    kml = simplekml.Kml()
    for id in trip_ids:
        try:
            resp = requests.get(URL % id)
            if resp.status_code == 404:
                print('Error 404\nCould not find trip %s' % id)
                continue
            if resp.status_code != 200:
                print('Error %s trying to find trip %s' % (resp.status_code, id))
                continue
            data = resp.json()
            trip = data['trip']
            waypoints = trip['waypoints']
            legs = trip['legs']
            if not no_paths:
                for leg in legs:
                    ls = kml.newlinestring()
                    ls.coords = [(c[1], c[0], 0.0) for c in polyline.decode(leg['encoded_polyline'])]
                    ls.extrude = 1
                    ls.altitudemode = simplekml.AltitudeMode.clamptoground
                    ls.style.linestyle.width = 5
                    ls.style.linestyle.color = simplekml.Color.cornflowerblue
            if not no_waypoints:
                for waypoint in waypoints:
                    kml.newpoint(name=waypoint['name'], coords=[(waypoint['start_location'][0], waypoint['start_location'][1])])
                    if waypoint['start_location'][0] != waypoint['end_location'][0] or waypoint['start_location'][1] != waypoint['end_location'][1]:
                        kml.newpoint(name=waypoint['name'], coords=[(waypoint['end_location'][0], waypoint['end_location'][1])])
        except:
            print('Error parsing trip %s' % id)
    fn = '-'.join(trip_ids) + '.kml'
    kml.save(fn)
    print('KML file save to %s' % fn)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('trip_id', nargs='+', help='The ID(s) of the trip(s) you want to export.')
    parser.add_argument('--no-waypoints', action='store_true', help='Omit waypoints from the KML.')
    parser.add_argument('--no-paths', action='store_true', help='Omit paths from the KML.')
    args = parser.parse_args()
    export(args.trip_id, args.no_waypoints, args.no_paths)
