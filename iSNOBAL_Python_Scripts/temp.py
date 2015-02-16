import sys
from datetime import datetime, time, timedelta
import ephem

fmt = '%Y/%m/%d'
s = '2008/3/1'
dt = datetime.strptime(s,fmt)

tt = dt.timetuple()
tt.tm_yday
#print(tt.tm_yday)



d = ephem.Date('1984/05/30 16:23:45.12')
#print(d)

def solartime(observer, sun=ephem.Sun()):
    sun.compute(observer)
    hour_angle = observer.sidereal_time() - sun.ra
    return ephem.hours(hour_angle + ephem.hours('12:00')).norm


o = ephem.Observer()
o.date = datetime(2008,3,1,19,0,0)
o.long = -120

#print(solartime(o))


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

dt = datetime.strptime('2014/11/7 12:00:00', '%Y/%m/%d %H:%M:%S')
longit = -112.4473
latit = 42.8752
elev = 1360

ha = hour_angle(dt,longit,latit,elev)

days = ha / 360
if days > 0.5:
    days -= 0.5
td = timedelta(days=days)

# make solar time
solar_time = datetime.combine(dt.date(), time(12)) + td
print solar_time

