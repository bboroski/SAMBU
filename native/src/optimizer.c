#include "sambu/ir.h"

#include <math.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

typedef struct FoldValue {
    bool known;
    SambuType type;
    union {
        bool boolean;
        int64_t i64;
        double f64;
    } value;
} FoldValue;

static bool add_i64(int64_t a, int64_t b, int64_t *out)
{
    if ((b > 0 && a > INT64_MAX - b) ||
        (b < 0 && a < INT64_MIN - b)) return false;
    *out = a + b;
    return true;
}

static bool sub_i64(int64_t a, int64_t b, int64_t *out)
{
    if ((b < 0 && a > INT64_MAX + b) ||
        (b > 0 && a < INT64_MIN + b)) return false;
    *out = a - b;
    return true;
}

static bool mul_i64(int64_t a, int64_t b, int64_t *out)
{
    if (a == 0 || b == 0) {
        *out = 0;
        return true;
    }
    if (a > 0) {
        if ((b > 0 && a > INT64_MAX / b) ||
            (b < 0 && b < INT64_MIN / a)) return false;
    } else {
        if ((b > 0 && a < INT64_MIN / b) ||
            (b < 0 && b < INT64_MAX / a)) return false;
    }
    *out = a * b;
    return true;
}

static void write_constant(SambuMirInst *inst, SambuMirOpcode opcode,
                           SambuType type, const FoldValue *value)
{
    inst->opcode = opcode;
    inst->operand_a = SAMBU_VALUE_NONE;
    inst->operand_b = SAMBU_VALUE_NONE;
    inst->type = type;
    memset(&inst->immediate, 0, sizeof(inst->immediate));
    if (type == SAMBU_TYPE_BOOL) inst->immediate.boolean = value->value.boolean;
    else if (type == SAMBU_TYPE_I64) inst->immediate.i64 = value->value.i64;
    else inst->immediate.f64 = value->value.f64;
}

static bool fold_binary(const SambuMirInst *inst,
                        const FoldValue *left, const FoldValue *right,
                        FoldValue *out, SambuMirOpcode *constant_opcode)
{
    int64_t integer_result = 0;
    double float_result = 0.0;

    if (!left->known || !right->known || left->type != right->type)
        return false;

    memset(out, 0, sizeof(*out));
    if (left->type == SAMBU_TYPE_I64) {
        const int64_t a = left->value.i64;
        const int64_t b = right->value.i64;
        switch (inst->opcode) {
            case SAMBU_MIR_ADD_I64:
                if (!add_i64(a, b, &integer_result)) return false;
                out->type = SAMBU_TYPE_I64;
                out->value.i64 = integer_result;
                *constant_opcode = SAMBU_MIR_CONST_I64;
                break;
            case SAMBU_MIR_SUB_I64:
                if (!sub_i64(a, b, &integer_result)) return false;
                out->type = SAMBU_TYPE_I64;
                out->value.i64 = integer_result;
                *constant_opcode = SAMBU_MIR_CONST_I64;
                break;
            case SAMBU_MIR_MUL_I64:
                if (!mul_i64(a, b, &integer_result)) return false;
                out->type = SAMBU_TYPE_I64;
                out->value.i64 = integer_result;
                *constant_opcode = SAMBU_MIR_CONST_I64;
                break;
            case SAMBU_MIR_DIV_I64:
                if (b == 0 || (a == INT64_MIN && b == -1)) return false;
                out->type = SAMBU_TYPE_I64;
                out->value.i64 = a / b;
                *constant_opcode = SAMBU_MIR_CONST_I64;
                break;
            case SAMBU_MIR_EQ_I64:
                out->type = SAMBU_TYPE_BOOL;
                out->value.boolean = (a == b);
                *constant_opcode = SAMBU_MIR_CONST_BOOL;
                break;
            case SAMBU_MIR_LT_I64:
                out->type = SAMBU_TYPE_BOOL;
                out->value.boolean = (a < b);
                *constant_opcode = SAMBU_MIR_CONST_BOOL;
                break;
            default:
                return false;
        }
    } else if (left->type == SAMBU_TYPE_F64) {
        const double a = left->value.f64;
        const double b = right->value.f64;
        if (!isfinite(a) || !isfinite(b)) return false;
        switch (inst->opcode) {
            case SAMBU_MIR_ADD_F64:
                float_result = a + b;
                break;
            case SAMBU_MIR_SUB_F64:
                float_result = a - b;
                break;
            case SAMBU_MIR_MUL_F64:
                float_result = a * b;
                break;
            case SAMBU_MIR_DIV_F64:
                if (b == 0.0) return false;
                float_result = a / b;
                break;
            case SAMBU_MIR_EQ_F64:
                out->type = SAMBU_TYPE_BOOL;
                out->value.boolean = (a == b);
                *constant_opcode = SAMBU_MIR_CONST_BOOL;
                out->known = true;
                return true;
            case SAMBU_MIR_LT_F64:
                out->type = SAMBU_TYPE_BOOL;
                out->value.boolean = (a < b);
                *constant_opcode = SAMBU_MIR_CONST_BOOL;
                out->known = true;
                return true;
            default:
                return false;
        }
        if (!isfinite(float_result)) return false;
        out->type = SAMBU_TYPE_F64;
        out->value.f64 = float_result;
        *constant_opcode = SAMBU_MIR_CONST_F64;
    } else {
        return false;
    }

    out->known = true;
    return true;
}

SambuIrStatus sambu_mir_fold_constants(SambuMirFunction *function,
                                       size_t *folded_count)
{
    FoldValue *values;
    SambuMirBlock *block;
    size_t capacity;
    size_t folded = 0u;
    SambuIrStatus status;

    if (folded_count != NULL) *folded_count = 0u;
    if (function == NULL) return SAMBU_IR_INVALID_ARGUMENT;

    status = sambu_mir_verify(function, NULL, 0u);
    if (status != SAMBU_IR_OK) return status;

    if ((uint64_t)function->next_value >
        (uint64_t)(SIZE_MAX / sizeof(*values))) return SAMBU_IR_OUT_OF_MEMORY;
    capacity = function->next_value == 0u ? 1u : (size_t)function->next_value;
    values = (FoldValue *)calloc(capacity, sizeof(*values));
    if (values == NULL) return SAMBU_IR_OUT_OF_MEMORY;

    block = &function->blocks[0];
    for (size_t i = 0u; i < block->instruction_count; ++i) {
        SambuMirInst *inst = &block->instructions[i];
        FoldValue *destination;

        if (inst->opcode == SAMBU_MIR_RETURN) continue;
        if ((size_t)inst->result >= capacity) {
            free(values);
            return SAMBU_IR_INVALID_IR;
        }
        destination = &values[inst->result];

        switch (inst->opcode) {
            case SAMBU_MIR_CONST_BOOL:
                destination->known = true;
                destination->type = SAMBU_TYPE_BOOL;
                destination->value.boolean = inst->immediate.boolean;
                break;
            case SAMBU_MIR_CONST_I64:
                destination->known = true;
                destination->type = SAMBU_TYPE_I64;
                destination->value.i64 = inst->immediate.i64;
                break;
            case SAMBU_MIR_CONST_F64:
                destination->known = true;
                destination->type = SAMBU_TYPE_F64;
                destination->value.f64 = inst->immediate.f64;
                break;
            default: {
                FoldValue result;
                SambuMirOpcode constant_opcode = SAMBU_MIR_CONST_I64;
                if (inst->operand_a >= capacity || inst->operand_b >= capacity)
                    continue;
                if (fold_binary(inst, &values[inst->operand_a],
                                &values[inst->operand_b], &result,
                                &constant_opcode)) {
                    write_constant(inst, constant_opcode, result.type, &result);
                    *destination = result;
                    ++folded;
                }
                break;
            }
        }
    }

    free(values);
    status = sambu_mir_verify(function, NULL, 0u);
    if (status != SAMBU_IR_OK) return status;
    if (folded_count != NULL) *folded_count = folded;
    return SAMBU_IR_OK;
}
