#include <iostream>
#include <utility>
#include <fstream>
#include <eigen3/Eigen/Core>

using namespace std;
using namespace Eigen;

// Constants
double MU_E = 398600.4418;  // km^3/s^2

struct State
{
  Vector3d position;
  Vector3d velocity;
  //Quaternion attitude;
  //rate;
};

State operator+(const State &a, const State &b)
{
  State c;
  c.position = a.position + b.position;
  c.velocity = a.velocity + b.velocity;
  return c;
}

State operator-(const State &a, const State &b)
{
  State c;
  c.position = a.position - b.position;
  c.velocity = a.velocity - b.velocity;
  return c;
}


State operator*(const double &a, const State &b)
{
  State c;
  c.position = a*b.position;
  c.velocity = a*b.velocity;
  return c;
}

double norm(State s)
{
  // L2 Norm of the state.
  //
  // This norm is used to calculate the integration error during propogation.
  // You cannot arbitrarily combine the position and velocity errors here without
  // some kind of scaling to match the magnitudes of their errors.
  // Instead of bothering with that, I am simply defining the error as the error
  // of the position, and the velocity is ignored. Thus the accuracy now has
  // a physical meaning.
  return s.position.norm();
  //return sqrt(s.position.dot(s.position) + s.velocity.dot(s.velocity));
}

struct Config
{
  State initial_state;
  int start, stop;
};


State System(double time, State state)
{
  Vector3d acceleration = -state.position*MU_E/pow(state.position.norm(),3);

  State dstate; 
  dstate.position = state.velocity;
  dstate.velocity = acceleration;

  return dstate;
}

// Butcher tableau for RKCK
const double A1[] = { 1./5};
const double A2[] = {3./40,          9./40};
const double A3[] = {3./10,         -9./10,        6./5};
const double A4[] = {-11./54,         5./2,      -70./27,        35./27};
const double A5[] = {1631./55296, 175./512,   575./13824, 44275./110592,  253./4096};

const double B5[] = {37./378,            0,     250./621,      125./594,           0, 512./1771};
const double B4[] = {2825./27648,        0, 18575./48384,  13525./55296,  277./14336,      1./4};

const double C[]  = {0,               1./5,        3./10,          3./5,           1,      7./8};

pair< vector<double>, vector<State> > PropogateRKCK(Config c)
{
  // Runge-Kutta Cash Karp (adaptive and variable order)
  State k0, k1, k2, k3, k4, k5, 
        y4, y5;

  double SF       = 0.9; // Safety factor;
  double accuracy = 1.0; // Accuracy between RK5 and RK4 results
  double h        = 0.1; // Initial time step

  State y         = c.initial_state;
  double t        = c.start; // Initial time
  double end_time = c.stop;
  double duration = 0.01*(c.stop - c.start);

  // Output
  vector<State> states;
  vector<double> times;

  while (t <= end_time)
  {
    // Save calculate time and state state
    states.push_back(y);
    times.push_back(t); 

    // This method requires six function calls
    k0 = System(t,          y);
    k1 = System(t + C[1]*h, y + h*(A1[0]*k0));
    k2 = System(t + C[2]*h, y + h*(A2[0]*k0 + A2[1]*k1));
    k3 = System(t + C[3]*h, y + h*(A3[0]*k0 + A3[1]*k1 + A3[2]*k2));
    k4 = System(t +      h, y + h*(A4[0]*k0 + A4[1]*k1 + A4[2]*k2 + A4[3]*k3));
    k5 = System(t + C[5]*h, y + h*(A5[0]*k0 + A5[1]*k1 + A5[2]*k2 + A5[3]*k3 + A5[4]*k4));

    y5 = y + h*(B5[0]*k0 + B5[2]*k2 + B5[3]*k3            + B5[6]*k5);
    y4 = y + h*(B4[0]*k0 + B4[2]*k2 + B4[3]*k3 + B4[4]*k4 + B4[6]*k5);

    // Update timestep h, and next state y
    h = SF*h*pow(accuracy/norm(y5-y4), 0.2);
    t = t + h;
    y = y5;

    cout << "p:" << (t - c.start) / duration << endl;
    cout << "h, err " << h << ", " << norm(y5 - y4) << endl;
  }

  // Currently ignoring the final calculation.
  // When I move to a interpolated results system, I
  // may use the final calculation

  return make_pair(times, states);
}

Config LoadConfig(string filename)
{
  //cout << "LoadConfig " << filename << endl;

  ifstream file;
  file.open(filename);

  if (!file.is_open())
  {
    cout << "Unable to open file" << endl;
    throw;
  }

  vector<double> v;
  double n;
  while (file >> n)
    v.push_back(n);

  file.close();

  Config c;
  c.start = v[0];
  c.stop  = v[1];
  c.initial_state.position = Vector3d(v[2], v[3], v[4]);
  c.initial_state.velocity = Vector3d(v[5], v[6], v[7]);

  return c;
}


int main(int argc, char* argv[])
{
  Config config = LoadConfig(argv[1]);

  pair< vector<double>, vector<State> > output = PropogateRKCK(config);

  // Save the state
  ofstream myfile(argv[2]);
  for (auto state : output.second)
  {
    myfile << state.position.x() << '\t' 
           << state.position.y() << '\t'
           << state.position.z() << '\t' 
           << state.velocity.x() << '\t'
           << state.velocity.y() << '\t'
           << state.velocity.z() << endl;
  }
  myfile.close();

  return 0;
}


