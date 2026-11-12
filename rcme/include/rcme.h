#ifndef RCME_H
#define RCME_H

#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

#define RCME_ABI_VERSION 1u

typedef enum {
    RCME_OK = 0,
    RCME_INVALID_ARGUMENT,
    RCME_DIMENSION_MISMATCH,
    RCME_NON_FINITE_VALUE,
    RCME_NUMERIC_OVERFLOW
} rcme_status;

typedef struct {
    size_t rows;
    size_t cols;
    size_t stride;
    double *data;
} rcme_matrix;

/* Matrix views are caller-owned. No allocation, global state, or hidden I/O. */
rcme_status rcme_matrix_validate(const rcme_matrix *matrix);
rcme_status rcme_multiply(const rcme_matrix *left, const rcme_matrix *right,
                          rcme_matrix *output);
rcme_status rcme_transpose(const rcme_matrix *input, rcme_matrix *output);
rcme_status rcme_normalize_frobenius(rcme_matrix *matrix);

/*
 * One bounded RCME iteration:
 * output = normalize_frobenius(M * A * transpose(M) + B).
 * All matrices must be square with equal dimensions. scratch_a and scratch_b
 * are caller-provided, distinct workspaces; output must not alias an input.
 */
rcme_status rcme_recursive_step(const rcme_matrix *matrix,
                                const rcme_matrix *transform,
                                const rcme_matrix *bias,
                                rcme_matrix *output,
                                rcme_matrix *scratch_a,
                                rcme_matrix *scratch_b);

double rcme_residual_l2(const rcme_matrix *left, const rcme_matrix *right,
                        rcme_status *status);

/* Implemented by the repository-specific adapter. */
const char *rcme_domain_name(void);
rcme_status rcme_domain_weights(double *weights, size_t count);
rcme_status rcme_domain_measure(const rcme_matrix *matrix, double *measure);

#ifdef __cplusplus
}
#endif
#endif
