#include "rcme.h"
#include <math.h>

const char *rcme_domain_name(void) { return "SAMBU: Scientific modeling and reproducible quantum-inspired numerical experiments"; }

rcme_status rcme_domain_weights(double *weights, size_t count) {
    static const double profile[4] = {1.00, 0.85, 1.15, 0.70};
    size_t i;
    if (weights == NULL || count == 0) return RCME_INVALID_ARGUMENT;
    for (i = 0; i < count; ++i) weights[i] = profile[i % 4];
    return RCME_OK;
}

rcme_status rcme_domain_measure(const rcme_matrix *matrix, double *measure) {
    double weights[4], sum = 0.0;
    size_t i;
    rcme_status status;
    if (measure == NULL) return RCME_INVALID_ARGUMENT;
    status = rcme_matrix_validate(matrix);
    if (status != RCME_OK) return status;
    if (matrix->rows != matrix->cols) return RCME_DIMENSION_MISMATCH;
    status = rcme_domain_weights(weights, 4);
    if (status != RCME_OK) return status;
    for (i = 0; i < matrix->rows; ++i) {
        double term = matrix->data[i * matrix->stride + i] * weights[i % 4];
        if (!isfinite(term) || !isfinite(sum + term)) return RCME_NUMERIC_OVERFLOW;
        sum += term;
    }
    *measure = sum / (double)matrix->rows;
    return isfinite(*measure) ? RCME_OK : RCME_NUMERIC_OVERFLOW;
}
