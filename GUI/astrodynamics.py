'''
Library of useful Astrodynamics stuff

Most of these come from my orbital dynamics class notes

'''

from numpy import *

X = array([1, 0, 0])
Y = array([0, 1, 0])
Z = array([0, 0, 1])

# Earth's gravitational parameter
mu = 398600.4418;  # km^3/s^2

# Orbital Parameters
# ------------------

def cartesian_to_keplarian(r, v):

    # Distance
    R = norm(r)

    # Orbital Energy
    epsilon = 0.5*dot(v, v) - mu/R
    
    # Semi-major Axis
    a = -0.5*mu/epsilon

    # Angular Velocity
    h = cross(r, v)

    # Eccentricity
    evec = cross(v, h)/mu - r/R
    e = norm(evec)

    # Inclination
    i = arccos(dot(h, Z)/norm(h))

    # RAAN
    n = cross(Z, h)     # n points to the ascneding node
    if norm(n) == 0:
        n = array([1, 0, 0])    # If t
    else:
        n = n/norm(n)   # Normalize

    RAAN = arccos(dot(n, X))
    if dot(n, Y) < 0:
        RAAN = 2*pi - RAAN

    # Argument of perigee
    if e == 0:
        omega = 0   # By convention
    else:
        omega = arccos(dot(n, evec)/e)
        if dot(evec, Z) < 0:
            omega = 2*pi - omega

    # Argument of latitude
    u = arccos(dot(n,r)/R)
    if dot(r, Z) < 0:
        u = 2*pi - u

    # True Anomaly
    theta = u - omega

    # Eccentric anomaly
    #E = 2*arctan(sqrt((1-e)/(1+e))*tan(theta/2))

    # Time of Perigee Passage
    #t0 = t - (E - e*sin(E))*sqrt(a**3/mu)

    return a, e, i, RAAN, omega, theta

def keplerian_to_cartesian(a, e, i, RAAN, omega, theta):

    # Mean motion
    #n = sqrt(mu/a**3)

    # Mean Anomaly
    #M = n*(t-t0)

    # Eccentric Anomaly
    #from scipy.optimize import brentq
    #E = brentq(lambda E: E - e*sin(E) - M, 0, 2*pi)

    # True Anomaly
    #theta = 2*arctan(sqrt((1+e)/(1-e))*tan(0.5*E))

    # Perifocal to ECI transformation
    C_Gp = array([[cos(RAAN)*cos(omega) - sin(RAAN)*cos(i)*sin(omega), -cos(RAAN)*sin(omega) - sin(RAAN)*cos(i)*cos(omega),  sin(RAAN)*sin(i)],
                  [sin(RAAN)*cos(omega) + cos(RAAN)*cos(i)*sin(omega), -sin(RAAN)*sin(omega) + cos(RAAN)*cos(i)*cos(omega), -cos(RAAN)*sin(i)],
                  [                                 sin(i)*sin(omega),                                   sin(i)*cos(omega),            cos(i)]])


    # Distance
    R = a*(1-e**2)/(1+e*cos(theta))

    # Cartesian Position    
    r_p = array([R*cos(theta), R*sin(theta), 0])
    r_G = dot(C_Gp, r_p)

    # Cartesian Velocity
    T2 = sqrt(mu/(a*(1-e**2)))
    v_p = array([-T2*sin(theta), T2*(e+cos(theta)), 0])
    v_G = dot(C_Gp, v_p)

    return r_G, v_G


# Time
# ----

def utc2jd(utc):
    """
    Convert UTC to Julian date.
    """
    
    y   = float(utc.year)
    m   = float(utc.month)
    d   = float(utc.day)
    hr  = utc.hour
    min = utc.minute
    sec = utc.second

    mterm = int((m-14)/12)
    aterm = int((1461*(y+4800+mterm))/4)
    bterm = int((367*(m-2-12*mterm))/12)
    cterm = int((3*int((y+4900+mterm)/100))/4)

    j     = aterm + bterm - cterm + d
    j    -= 32075
    # Offset to start of day
    j    -= 0.5

    # Apply the time
    jd = j + (hr + (min + (sec/60.0))/60.0)/24.0

    return jd

# Earth Orientation Model
# -----------------------

#r_gcrf = [x, y, z]
#r_itrf = [x, y, z]

''' Work in progress
def R1(a) = 1, 0, 0
            0, cos(a), -sin(a),
            0, sin(a),  cos(a)
def R2(a) = cos(a),  0, sin(a),
            0,       1, 0,
            -sin(a), 0, cos(a)

def R3(a) = cos(a), -sin(a), 0
            sin(a),  cos(a), 0
            0,       0,      1

def PolarMotion(t_i):
     aka W_CIO
    xp and yp come from tables
    

    #s' = - 47 mas (t - 51544.5) / 36525   where t is expressed in modified Julian days (MJD).
    s_prime = 47 uas per century
    xp
    yp from tables

    return R3(-s_prime)*R2(xp)*r1(yp)

def SiderealRotation(a_ERA):
    
    #a_ERA comes from?
    

    return R3(-a_ERA)

def BiasPrecessionNutation(t_i):
    # aka BPN_CIO
    X, Y, and s come from tables at t_i
    

    X = f(t_i)
    Y = f(t_i)
    s = f(t_i)

    Z = sqrt(1 - X**2 + Y**2)
    a = 1./(1. + Z)
    a = 0.5 + 0.125*(X**2 + Y**2)

    A = 1 - a*X**2,   -a*X*Y, X
            -a*X*Y, 1-a*Y**2, Y
                -X,       -X, 1-a*(X**2 + Y**2)

    return A*R3(s)

# Tu is (UT1) days since JD 2451545.0
# input: thedate

Tu = utc2jd(thedate) - 2451545.0
a_ERA = 2*pi*(0.779057273264 + 1.00273781191135448*Tu)

r_gcrf = BiasPrecessionNutation(X, Y, s)*SiderealRotation(a_ERA)*PolarMotion(xp, yp)*r_itrf
'''

