#include "rcme.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>

int main(void) {
    double md[4] = {1,0,0,1}, ad[4] = {1,0,0,1}, bd[4] = {0,0,0,0};
    double od[4] = {0,0,0,0}, x[4] = {0,0,0,0}, y[4] = {0,0,0,0};
    double weights[8], measure = 0.0;
    rcme_matrix m={2,2,2,md}, a={2,2,2,ad}, b={2,2,2,bd};
    rcme_matrix out={2,2,2,od}, wa={2,2,2,x}, wb={2,2,2,y};
    rcme_status status = RCME_OK;
    double residual;

    assert(rcme_matrix_validate(&m) == RCME_OK);
    assert(rcme_multiply(&m, &a, &out) == RCME_OK);
    assert(od[0] == 1.0 && od[3] == 1.0);
    assert(rcme_recursive_step(&m,&a,&b,&out,&wa,&wb) == RCME_OK);
    assert(fabs(od[0] - 0.7071067811865475) < 1e-12);
    assert(fabs(od[3] - 0.7071067811865475) < 1e-12);
    residual = rcme_residual_l2(&out,&out,&status);
    assert(status == RCME_OK && residual == 0.0);\n    residual = rcme_residual_l2(&out, &b, &status);\n    assert(status == RCME_OK && fabs(residual - 1.0) < 1e-12);
    assert(rcme_domain_weights(weights,8) == RCME_OK);
    assert(rcme_domain_measure(&out,&measure) == RCME_OK);
    assert(isfinite(measure));
    assert(rcme_domain_name() != NULL);
    assert(rcme_domain_weights(NULL,4) == RCME_INVALID_ARGUMENT);
    puts("RCME native tests: PASS");
    return 0;
}
