#include <string>
#include <complex>
#include <memory>     // smart pointers (unique_ptr)
#include <pybind11/stl.h>
#include "armapy.hpp"


pyarray expit(pyarray &x) {
  arma::mat X = pymat(x);
    for (unsigned i=0; i < X.n_elem; i++) {
      double z = X(i);
      if (z >= 0) {
	X(i) = 1/(1+exp(-z));
      } else {
	z = exp(z);
	X(i) = z/(1+z);
      }
    }
  return matpy(X);
}


PYBIND11_MODULE(__kvaser_c__, m) {
  m.doc() = "Python bindings for the target C++ library";

  m.def("expit", &expit, "Sigmoid function (inverse logit)");

}
