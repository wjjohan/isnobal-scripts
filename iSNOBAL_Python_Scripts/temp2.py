import sys
from datetime import datetime, time, timedelta
import ephem

def hour_angle(dt, longit, latit, elev):
    obs = ephem.Observer()
    obs.date = dt.strftime('%Y/%m/%d %H:%M:%S')
    obs.lon = longit
    obs.lat = latit
    obs.elevation = elev
    sun = ephem.Sun()
    sun.compute(obs)
    # get right ascention
    ra = ephem.degrees(sun.g_ra)

    # get sidereal time at greenwich (AA ch12)
    jd = ephem.julian_date(dt)
    t = (jd - 2451545.0) / 36525
    theta = 280.46061837 + 360.98564736629 * (jd - 2451545) \
            + .000387933 * t**2 - t**3 / 38710000

    # hour angle (AA ch13)
    ha = (theta + longit - ra * 180 / ephem.pi) % 360
    return ha

def main():
    if len(sys.argv) != 6:
        print 'Usage: hour_angle.py [YYYY/MM/DD] [HH:MM:SS] [longitude] [latitude] [elev]'
        sys.exit()
    else:
        dt = datetime.strptime(sys.argv[1] + ' ' + sys.argv[2], '%Y/%m/%d %H:%M:%S')
        longit = float(sys.argv[3])
        latit = float(sys.argv[4])
        elev = float(sys.argv[5])

    # get hour angle
    ha = hour_angle(dt, longit, latit, elev)

    # convert hour angle to timedelta from noon
    days = ha / 360
    if days > 0.5:
        days -= 0.5
    td = timedelta(days=days)

    # make solar time
    solar_time = datetime.combine(dt.date(), time(12)) + td
    print solar_time

if __name__ == '__main__':
    main()