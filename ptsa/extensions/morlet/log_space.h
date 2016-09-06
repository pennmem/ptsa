//
// Created by Stas Busygin on 1/12/16.
//

#ifndef MORLET_LOG_SPACE_H
#define MORLET_LOG_SPACE_H

#include <cstring>
#include <cmath>
#include <vector>
#include <algorithm>
#include <iterator>


template<typename T>
class Logspace {
private:
   T curValue, base;

public:
   Logspace(T first, T base) : curValue(first), base(base) {}

   T operator()() {
      T retval = curValue;
      curValue *= base;
      return retval;
   }
};

inline std::vector<double> logspace(double start, double stop, size_t n, double base=10.0) {
   double real_start = pow(base, start);
   double real_base = pow(base, (stop-start)/(n-1));
   std::vector<double> retval;
   retval.reserve(n);
   std::generate_n(std::back_inserter(retval), n, Logspace<double>(real_start,real_base));
   return retval;
}


#endif //MORLET_LOG_SPACE_H
