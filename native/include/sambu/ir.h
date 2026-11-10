#ifndef SAMBU_IR_H
#define SAMBU_IR_H

/* Backend-independent native compiler foundation; no Python ABI in this API. */
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define SAMBU_IR_VERSION 1u
#define SAMBU_VALUE_NONE UINT32_MAX

typedef enum SambuIrStatus {
    SAMBU_IR_OK = 0,
    SAMBU_IR_INVALID_ARGUMENT,
    SAMBU_IR_OUT_OF_MEMORY,
    SAMBU_IR_INVALID_TYPE,
    SAMBU_IR_INVALID_IR,
    SAMBU_IR_UNSUPPORTED
} SambuIrStatus;

typedef struct SambuSourceSpan {
    uint32_t start;
    uint32_t end;
} SambuSourceSpan;

typedef enum SambuType {
    SAMBU_TYPE_UNIT = 0,
    SAMBU_TYPE_BOOL,
    SAMBU_TYPE_I64,
    SAMBU_TYPE_F64
} SambuType;

const char *sambu_type_name(SambuType type);

typedef struct SambuArenaChunk SambuArenaChunk;
typedef struct SambuArena {
    SambuArenaChunk *head;
    size_t default_capacity;
} SambuArena;

SambuIrStatus sambu_arena_init(SambuArena *arena, size_t default_capacity);
void sambu_arena_reset(SambuArena *arena);
void sambu_arena_dispose(SambuArena *arena);
void *sambu_arena_alloc(SambuArena *arena, size_t size, size_t alignment);
char *sambu_arena_copy_string(SambuArena *arena, const char *value);

typedef struct SambuInternSlot {
    uint64_t hash;
    char *value;
} SambuInternSlot;

typedef struct SambuInterner {
    SambuInternSlot *slots;
    size_t capacity;
    size_t length;
} SambuInterner;

SambuIrStatus sambu_interner_init(SambuInterner *interner);
const char *sambu_interner_intern(SambuInterner *interner, const char *value);
void sambu_interner_dispose(SambuInterner *interner);

typedef enum SambuHirBinaryOp {
    SAMBU_HIR_ADD = 0,
    SAMBU_HIR_SUB,
    SAMBU_HIR_MUL,
    SAMBU_HIR_DIV,
    SAMBU_HIR_EQ,
    SAMBU_HIR_LT
} SambuHirBinaryOp;

typedef enum SambuHirKind {
    SAMBU_HIR_BOOL_LITERAL = 0,
    SAMBU_HIR_I64_LITERAL,
    SAMBU_HIR_F64_LITERAL,
    SAMBU_HIR_BINARY
} SambuHirKind;

typedef struct SambuHirExpr SambuHirExpr;
struct SambuHirExpr {
    SambuHirKind kind;
    SambuType type;
    SambuSourceSpan span;
    union {
        bool boolean;
        int64_t i64;
        double f64;
        struct {
            SambuHirBinaryOp op;
            const SambuHirExpr *left;
            const SambuHirExpr *right;
        } binary;
    } as;
};

SambuHirExpr *sambu_hir_bool(SambuArena *arena, bool value, SambuSourceSpan span);
SambuHirExpr *sambu_hir_i64(SambuArena *arena, int64_t value, SambuSourceSpan span);
SambuHirExpr *sambu_hir_f64(SambuArena *arena, double value, SambuSourceSpan span);
SambuHirExpr *sambu_hir_binary(
    SambuArena *arena, SambuHirBinaryOp op,
    const SambuHirExpr *left, const SambuHirExpr *right,
    SambuSourceSpan span
);

typedef uint32_t SambuValueId;

typedef enum SambuMirOpcode {
    SAMBU_MIR_CONST_BOOL = 0,
    SAMBU_MIR_CONST_I64,
    SAMBU_MIR_CONST_F64,
    SAMBU_MIR_ADD_I64,
    SAMBU_MIR_SUB_I64,
    SAMBU_MIR_MUL_I64,
    SAMBU_MIR_DIV_I64,
    SAMBU_MIR_EQ_I64,
    SAMBU_MIR_LT_I64,
    SAMBU_MIR_ADD_F64,
    SAMBU_MIR_SUB_F64,
    SAMBU_MIR_MUL_F64,
    SAMBU_MIR_DIV_F64,
    SAMBU_MIR_EQ_F64,
    SAMBU_MIR_LT_F64,
    SAMBU_MIR_RETURN
} SambuMirOpcode;

typedef struct SambuMirInst {
    SambuMirOpcode opcode;
    SambuValueId result;
    SambuValueId operand_a;
    SambuValueId operand_b;
    SambuType type;
    union {
        bool boolean;
        int64_t i64;
        double f64;
    } immediate;
} SambuMirInst;

typedef struct SambuMirBlock {
    uint32_t id;
    const char *name;
    SambuMirInst *instructions;
    size_t instruction_count;
    size_t instruction_capacity;
} SambuMirBlock;

typedef struct SambuMirFunction {
    SambuArena *arena;
    const char *name;
    SambuType return_type;
    SambuMirBlock *blocks;
    size_t block_count;
    size_t block_capacity;
    SambuValueId next_value;
} SambuMirFunction;

SambuMirFunction *sambu_mir_function_new(
    SambuArena *arena, const char *name, SambuType return_type
);
SambuIrStatus sambu_mir_add_block(
    SambuMirFunction *function, const char *name, uint32_t *block_id
);
SambuIrStatus sambu_mir_emit_bool(
    SambuMirFunction *function, uint32_t block_id, bool value, SambuValueId *result
);
SambuIrStatus sambu_mir_emit_i64(
    SambuMirFunction *function, uint32_t block_id, int64_t value, SambuValueId *result
);
SambuIrStatus sambu_mir_emit_f64(
    SambuMirFunction *function, uint32_t block_id, double value, SambuValueId *result
);
SambuIrStatus sambu_mir_emit_binary(
    SambuMirFunction *function, uint32_t block_id, SambuHirBinaryOp op,
    SambuValueId left, SambuValueId right, SambuValueId *result
);
SambuIrStatus sambu_mir_emit_return(
    SambuMirFunction *function, uint32_t block_id, SambuValueId value
);
SambuIrStatus sambu_mir_emit_return_unit(
    SambuMirFunction *function, uint32_t block_id
);

/* MIR v1 accepts one block. CFG dominance and phi nodes are later milestones. */
SambuIrStatus sambu_mir_verify(
    const SambuMirFunction *function, char *error, size_t error_capacity
);
/* Folds safe local constant expressions in place; overflow and invalid divisions stay intact. */
SambuIrStatus sambu_mir_fold_constants(
    SambuMirFunction *function, size_t *folded_count
);
SambuIrStatus sambu_lower_hir_expression(
    SambuArena *arena, const char *function_name,
    const SambuHirExpr *expression, SambuMirFunction **out_function
);

typedef enum SambuLirOpcode {
    SAMBU_LIR_LOAD_BOOL = 0,
    SAMBU_LIR_LOAD_I64,
    SAMBU_LIR_LOAD_F64,
    SAMBU_LIR_ADD_I64,
    SAMBU_LIR_SUB_I64,
    SAMBU_LIR_MUL_I64,
    SAMBU_LIR_DIV_I64,
    SAMBU_LIR_EQ_I64,
    SAMBU_LIR_LT_I64,
    SAMBU_LIR_ADD_F64,
    SAMBU_LIR_SUB_F64,
    SAMBU_LIR_MUL_F64,
    SAMBU_LIR_DIV_F64,
    SAMBU_LIR_EQ_F64,
    SAMBU_LIR_LT_F64,
    SAMBU_LIR_RETURN
} SambuLirOpcode;

/* LIR virtual registers are target-neutral; physical registers belong to backends. */
typedef struct SambuLirInst {
    SambuLirOpcode opcode;
    SambuValueId destination;
    SambuValueId source_a;
    SambuValueId source_b;
    SambuType type;
    union {
        bool boolean;
        int64_t i64;
        double f64;
    } immediate;
} SambuLirInst;

typedef struct SambuLirFunction {
    const char *name;
    SambuType return_type;
    SambuLirInst *instructions;
    size_t instruction_count;
} SambuLirFunction;

SambuIrStatus sambu_lir_lower(
    SambuArena *arena, const SambuMirFunction *mir, SambuLirFunction **out_function
);
SambuIrStatus sambu_lir_verify(
    const SambuLirFunction *function, char *error, size_t error_capacity
);

const char *sambu_ir_status_name(SambuIrStatus status);

#ifdef __cplusplus
}
#endif
#endif
