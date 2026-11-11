#include "rcme.h"

#include <math.h>
#include <stdint.h>

rcme_status rcme_matrix_validate(const rcme_matrix *m) {
    size_t i, j;
    if (m == NULL || m->data == NULL || m->rows == 0 || m->cols == 0 ||
        m->stride < m->cols || m->rows > SIZE_MAX / m->stride)
        return RCME_INVALID_ARGUMENT;
    for (i = 0; i < m->rows; ++i)
        for (j = 0; j < m->cols; ++j)
            if (!isfinite(m->data[i * m->stride + j]))
                return RCME_NON_FINITE_VALUE;
    return RCME_OK;
}

static int same_shape(const rcme_matrix *a, const rcme_matrix *b) {
    return a->rows == b->rows && a->cols == b->cols;
}

rcme_status rcme_multiply(const rcme_matrix *a, const rcme_matrix *b,
                          rcme_matrix *out) {
    size_t i, j, k;
    rcme_status s;
    if ((s = rcme_matrix_validate(a)) != RCME_OK ||
        (s = rcme_matrix_validate(b)) != RCME_OK ||
        (s = rcme_matrix_validate(out)) != RCME_OK) return s;
    if (a->cols != b->rows || out->rows != a->rows || out->cols != b->cols)
        return RCME_DIMENSION_MISMATCH;
    if (out->data == a->data || out->data == b->data)
        return RCME_INVALID_ARGUMENT;
    for (i = 0; i < out->rows; ++i) {
        for (j = 0; j < out->cols; ++j) {
            double sum = 0.0;
            for (k = 0; k < a->cols; ++k) {
                double term = a->data[i*a->stride+k] * b->data[k*b->stride+j];
                if (!isfinite(term) || !isfinite(sum + term))
                    return RCME_NUMERIC_OVERFLOW;
                sum += term;
            }
            out->data[i*out->stride+j] = sum;
        }
    }
    return RCME_OK;
}

rcme_status rcme_transpose(const rcme_matrix *in, rcme_matrix *out) {
    size_t i, j;
    rcme_status s;
    if ((s = rcme_matrix_validate(in)) != RCME_OK ||
        (s = rcme_matrix_validate(out)) != RCME_OK) return s;
    if (out->rows != in->cols || out->cols != in->rows ||
        out->data == in->data) return RCME_DIMENSION_MISMATCH;
    for (i = 0; i < in->rows; ++i)
        for (j = 0; j < in->cols; ++j)
            out->data[j*out->stride+i] = in->data[i*in->stride+j];
    return RCME_OK;
}

rcme_status rcme_normalize_frobenius(rcme_matrix *m) {
    size_t i, j;
    double scale = 0.0, sum = 1.0;
    rcme_status s = rcme_matrix_validate(m);
    if (s != RCME_OK) return s;
    /* Scaled sum-of-squares avoids unnecessary intermediate overflow. */
    for (i = 0; i < m->rows; ++i) for (j = 0; j < m->cols; ++j) {
        double x = fabs(m->data[i*m->stride+j]);
        if (x != 0.0) {
            if (scale < x) { double q = scale / x; sum = 1.0 + sum*q*q; scale = x; }
            else { double q = x / scale; sum += q*q; }
        }
    }
    if (scale == 0.0) return RCME_OK;
    {
        double norm = scale * sqrt(sum);
        if (!isfinite(norm) || norm == 0.0) return RCME_NUMERIC_OVERFLOW;
        for (i = 0; i < m->rows; ++i) for (j = 0; j < m->cols; ++j)
            m->data[i*m->stride+j] /= norm;
    }
    return RCME_OK;
}

rcme_status rcme_recursive_step(const rcme_matrix *m,
                                const rcme_matrix *a,
                                const rcme_matrix *b,
                                rcme_matrix *out,
                                rcme_matrix *wa,
                                rcme_matrix *wb) {
    size_t i, j;
    rcme_status s;
    const rcme_matrix *all[] = {m, a, b, out, wa, wb};
    size_t n;
    for (i = 0; i < sizeof(all)/sizeof(all[0]); ++i)
        if ((s = rcme_matrix_validate(all[i])) != RCME_OK) return s;
    n = m->rows;
    for (i = 0; i < 6; ++i)
        if (all[i]->rows != n || all[i]->cols != n)
            return RCME_DIMENSION_MISMATCH;
    if (out->data == m->data || out->data == a->data ||
        out->data == b->data || out->data == wa->data ||
        out->data == wb->data || wa->data == wb->data)
        return RCME_INVALID_ARGUMENT;
    if ((s = rcme_multiply(m, a, wa)) != RCME_OK ||
        (s = rcme_transpose(m, wb)) != RCME_OK ||
        (s = rcme_multiply(wa, wb, out)) != RCME_OK) return s;
    for (i = 0; i < n; ++i) for (j = 0; j < n; ++j) {
        double v = out->data[i*out->stride+j] + b->data[i*b->stride+j];
        if (!isfinite(v)) return RCME_NUMERIC_OVERFLOW;
        out->data[i*out->stride+j] = v;
    }
    return rcme_normalize_frobenius(out);
}

double rcme_residual_l2(const rcme_matrix *a, const rcme_matrix *b,
                        rcme_status *status) {
    size_t i, j;
    double scale = 0.0, sum = 1.0;
    rcme_status s = rcme_matrix_validate(a);
    if (s == RCME_OK) s = rcme_matrix_validate(b);
    if (s != RCME_OK || !same_shape(a, b)) {
        if (status) *status = s == RCME_OK ? RCME_DIMENSION_MISMATCH : s;
        return NAN;
    }
    for (i = 0; i < a->rows; ++i) for (j = 0; j < a->cols; ++j) {
        double x = fabs(a->data[i*a->stride+j] - b->data[i*b->stride+j]);
        if (!isfinite(x)) { if(status) *status=RCME_NUMERIC_OVERFLOW; return NAN; }
        if (x != 0.0) {
            if (scale < x) { double q=scale/x; sum=1.0+sum*q*q; scale=x; }
            else { double q=x/scale; sum+=q*q; }
        }
    }
    if (status) *status = RCME_OK;
    return scale == 0.0 ? 0.0 : scale * sqrt(sum - 1.0);
}
