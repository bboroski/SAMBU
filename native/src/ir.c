#include "sambu/ir.h"

#include <stdalign.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

struct SambuArenaChunk {
    struct SambuArenaChunk *next;
    size_t capacity;
    size_t used;
    max_align_t alignment_anchor;
    unsigned char data[];
};

static bool power_of_two(size_t n) {
    return n != 0u && (n & (n - 1u)) == 0u;
}
static bool add_overflow(size_t a, size_t b, size_t *out) {
    if (a > SIZE_MAX - b) return true;
    *out = a + b;
    return false;
}
static void error_text(char *out, size_t capacity, const char *message) {
    if (out != NULL && capacity != 0u) (void)snprintf(out, capacity, "%s", message);
}

const char *sambu_type_name(SambuType type) {
    switch (type) {
        case SAMBU_TYPE_UNIT: return "unit";
        case SAMBU_TYPE_BOOL: return "bool";
        case SAMBU_TYPE_I64: return "i64";
        case SAMBU_TYPE_F64: return "f64";
        default: return "<invalid-type>";
    }
}
const char *sambu_ir_status_name(SambuIrStatus status) {
    switch (status) {
        case SAMBU_IR_OK: return "ok";
        case SAMBU_IR_INVALID_ARGUMENT: return "invalid argument";
        case SAMBU_IR_OUT_OF_MEMORY: return "out of memory";
        case SAMBU_IR_INVALID_TYPE: return "invalid type";
        case SAMBU_IR_INVALID_IR: return "invalid IR";
        case SAMBU_IR_UNSUPPORTED: return "unsupported";
        default: return "unknown status";
    }
}

SambuIrStatus sambu_arena_init(SambuArena *arena, size_t default_capacity) {
    if (arena == NULL) return SAMBU_IR_INVALID_ARGUMENT;
    arena->head = NULL;
    arena->default_capacity = default_capacity < 256u ? 256u : default_capacity;
    return SAMBU_IR_OK;
}
void sambu_arena_reset(SambuArena *arena) {
    if (arena == NULL) return;
    SambuArenaChunk *chunk = arena->head;
    while (chunk != NULL) {
        SambuArenaChunk *next = chunk->next;
        free(chunk);
        chunk = next;
    }
    arena->head = NULL;
}
void sambu_arena_dispose(SambuArena *arena) {
    if (arena == NULL) return;
    sambu_arena_reset(arena);
    arena->default_capacity = 0u;
}
void *sambu_arena_alloc(SambuArena *arena, size_t size, size_t alignment) {
    if (arena == NULL || arena->default_capacity == 0u) return NULL;
    if (size == 0u) size = 1u;
    if (alignment == 0u) alignment = alignof(max_align_t);
    if (!power_of_two(alignment)) return NULL;

    SambuArenaChunk *chunk = arena->head;
    if (chunk != NULL) {
        uintptr_t base = (uintptr_t)chunk->data;
        if (chunk->used <= UINTPTR_MAX - base) {
            uintptr_t current = base + chunk->used;
            if (current <= UINTPTR_MAX - (alignment - 1u)) {
                uintptr_t aligned = (current + alignment - 1u) & ~((uintptr_t)alignment - 1u);
                size_t offset = (size_t)(aligned - base);
                if (offset <= chunk->capacity && size <= chunk->capacity - offset) {
                    chunk->used = offset + size;
                    return (void *)aligned;
                }
            }
        }
    }

    size_t required = 0u, allocation_size = 0u;
    if (add_overflow(size, alignment - 1u, &required)) return NULL;
    size_t capacity = arena->default_capacity > required ? arena->default_capacity : required;
    if (add_overflow(sizeof(SambuArenaChunk), capacity, &allocation_size)) return NULL;
    chunk = (SambuArenaChunk *)malloc(allocation_size);
    if (chunk == NULL) return NULL;
    chunk->next = arena->head;
    chunk->capacity = capacity;
    chunk->used = 0u;
    arena->head = chunk;

    uintptr_t base = (uintptr_t)chunk->data;
    if (base > UINTPTR_MAX - (alignment - 1u)) return NULL;
    uintptr_t aligned = (base + alignment - 1u) & ~((uintptr_t)alignment - 1u);
    size_t offset = (size_t)(aligned - base);
    if (offset > capacity || size > capacity - offset) return NULL;
    chunk->used = offset + size;
    return (void *)aligned;
}
char *sambu_arena_copy_string(SambuArena *arena, const char *value) {
    if (arena == NULL || value == NULL) return NULL;
    size_t bytes = 0u;
    if (add_overflow(strlen(value), 1u, &bytes)) return NULL;
    char *copy = (char *)sambu_arena_alloc(arena, bytes, alignof(char));
    if (copy != NULL) memcpy(copy, value, bytes);
    return copy;
}

static uint64_t string_hash(const char *value) {
    uint64_t hash = UINT64_C(14695981039346656037);
    const unsigned char *p = (const unsigned char *)value;
    while (*p != 0u) {
        hash ^= (uint64_t)*p++;
        hash *= UINT64_C(1099511628211);
    }
    return hash == 0u ? UINT64_C(1) : hash;
}
static SambuIrStatus interner_resize(SambuInterner *interner, size_t capacity) {
    if (capacity < 16u || !power_of_two(capacity) ||
        capacity > SIZE_MAX / sizeof(SambuInternSlot)) return SAMBU_IR_OUT_OF_MEMORY;
    SambuInternSlot *slots = (SambuInternSlot *)calloc(capacity, sizeof(*slots));
    if (slots == NULL) return SAMBU_IR_OUT_OF_MEMORY;
    for (size_t i = 0u; i < interner->capacity; ++i) {
        SambuInternSlot old = interner->slots[i];
        if (old.value == NULL) continue;
        size_t at = (size_t)(old.hash & (uint64_t)(capacity - 1u));
        while (slots[at].value != NULL) at = (at + 1u) & (capacity - 1u);
        slots[at] = old;
    }
    free(interner->slots);
    interner->slots = slots;
    interner->capacity = capacity;
    return SAMBU_IR_OK;
}
SambuIrStatus sambu_interner_init(SambuInterner *interner) {
    if (interner == NULL) return SAMBU_IR_INVALID_ARGUMENT;
    interner->slots = NULL;
    interner->capacity = 0u;
    interner->length = 0u;
    return interner_resize(interner, 16u);
}
const char *sambu_interner_intern(SambuInterner *interner, const char *value) {
    if (interner == NULL || value == NULL) return NULL;
    if (interner->capacity == 0u && interner_resize(interner, 16u) != SAMBU_IR_OK) return NULL;
    if (interner->length >= (interner->capacity * 7u) / 10u) {
        if (interner->capacity > SIZE_MAX / 2u ||
            interner_resize(interner, interner->capacity * 2u) != SAMBU_IR_OK) return NULL;
    }
    uint64_t hash = string_hash(value);
    size_t at = (size_t)(hash & (uint64_t)(interner->capacity - 1u));
    while (interner->slots[at].value != NULL) {
        if (interner->slots[at].hash == hash &&
            strcmp(interner->slots[at].value, value) == 0) return interner->slots[at].value;
        at = (at + 1u) & (interner->capacity - 1u);
    }
    size_t bytes = 0u;
    if (add_overflow(strlen(value), 1u, &bytes)) return NULL;
    char *copy = (char *)malloc(bytes);
    if (copy == NULL) return NULL;
    memcpy(copy, value, bytes);
    interner->slots[at].hash = hash;
    interner->slots[at].value = copy;
    interner->length += 1u;
    return copy;
}
void sambu_interner_dispose(SambuInterner *interner) {
    if (interner == NULL) return;
    for (size_t i = 0u; i < interner->capacity; ++i) free(interner->slots[i].value);
    free(interner->slots);
    interner->slots = NULL;
    interner->capacity = 0u;
    interner->length = 0u;
}

static bool numeric(SambuType type) {
    return type == SAMBU_TYPE_I64 || type == SAMBU_TYPE_F64;
}
static SambuHirExpr *new_hir(
    SambuArena *arena, SambuHirKind kind, SambuType type, SambuSourceSpan span
) {
    if (arena == NULL || span.end < span.start) return NULL;
    SambuHirExpr *node = (SambuHirExpr *)sambu_arena_alloc(
        arena, sizeof(*node), alignof(SambuHirExpr)
    );
    if (node == NULL) return NULL;
    memset(node, 0, sizeof(*node));
    node->kind = kind;
    node->type = type;
    node->span = span;
    return node;
}
SambuHirExpr *sambu_hir_bool(SambuArena *a, bool v, SambuSourceSpan s) {
    SambuHirExpr *n = new_hir(a, SAMBU_HIR_BOOL_LITERAL, SAMBU_TYPE_BOOL, s);
    if (n != NULL) n->as.boolean = v;
    return n;
}
SambuHirExpr *sambu_hir_i64(SambuArena *a, int64_t v, SambuSourceSpan s) {
    SambuHirExpr *n = new_hir(a, SAMBU_HIR_I64_LITERAL, SAMBU_TYPE_I64, s);
    if (n != NULL) n->as.i64 = v;
    return n;
}
SambuHirExpr *sambu_hir_f64(SambuArena *a, double v, SambuSourceSpan s) {
    SambuHirExpr *n = new_hir(a, SAMBU_HIR_F64_LITERAL, SAMBU_TYPE_F64, s);
    if (n != NULL) n->as.f64 = v;
    return n;
}
SambuHirExpr *sambu_hir_binary(
    SambuArena *arena, SambuHirBinaryOp op,
    const SambuHirExpr *left, const SambuHirExpr *right, SambuSourceSpan span
) {
    if (left == NULL || right == NULL || left->type != right->type ||
        !numeric(left->type) || op < SAMBU_HIR_ADD || op > SAMBU_HIR_LT) return NULL;
    SambuType result_type = (op == SAMBU_HIR_EQ || op == SAMBU_HIR_LT)
        ? SAMBU_TYPE_BOOL : left->type;
    SambuHirExpr *n = new_hir(arena, SAMBU_HIR_BINARY, result_type, span);
    if (n != NULL) {
        n->as.binary.op = op;
        n->as.binary.left = left;
        n->as.binary.right = right;
    }
    return n;
}

static SambuIrStatus reserve_blocks(SambuMirFunction *f, size_t needed) {
    if (needed <= f->block_capacity) return SAMBU_IR_OK;
    size_t cap = f->block_capacity == 0u ? 2u : f->block_capacity;
    while (cap < needed) {
        if (cap > SIZE_MAX / 2u) return SAMBU_IR_OUT_OF_MEMORY;
        cap *= 2u;
    }
    if (cap > SIZE_MAX / sizeof(SambuMirBlock)) return SAMBU_IR_OUT_OF_MEMORY;
    SambuMirBlock *p = (SambuMirBlock *)sambu_arena_alloc(
        f->arena, cap * sizeof(*p), alignof(SambuMirBlock)
    );
    if (p == NULL) return SAMBU_IR_OUT_OF_MEMORY;
    if (f->blocks != NULL) memcpy(p, f->blocks, f->block_count * sizeof(*p));
    f->blocks = p;
    f->block_capacity = cap;
    return SAMBU_IR_OK;
}
static SambuIrStatus reserve_instructions(SambuMirFunction *f, SambuMirBlock *b) {
    if (b->instruction_count < b->instruction_capacity) return SAMBU_IR_OK;
    size_t cap = b->instruction_capacity == 0u ? 8u : b->instruction_capacity;
    if (cap > SIZE_MAX / 2u) return SAMBU_IR_OUT_OF_MEMORY;
    cap *= 2u;
    if (cap > SIZE_MAX / sizeof(SambuMirInst)) return SAMBU_IR_OUT_OF_MEMORY;
    SambuMirInst *p = (SambuMirInst *)sambu_arena_alloc(
        f->arena, cap * sizeof(*p), alignof(SambuMirInst)
    );
    if (p == NULL) return SAMBU_IR_OUT_OF_MEMORY;
    if (b->instructions != NULL) {
        memcpy(p, b->instructions, b->instruction_count * sizeof(*p));
    }
    b->instructions = p;
    b->instruction_capacity = cap;
    return SAMBU_IR_OK;
}
SambuMirFunction *sambu_mir_function_new(SambuArena *arena, const char *name, SambuType ret) {
    if (arena == NULL || name == NULL ||
        (!numeric(ret) && ret != SAMBU_TYPE_BOOL && ret != SAMBU_TYPE_UNIT)) return NULL;
    SambuMirFunction *f = (SambuMirFunction *)sambu_arena_alloc(
        arena, sizeof(*f), alignof(SambuMirFunction)
    );
    if (f == NULL) return NULL;
    memset(f, 0, sizeof(*f));
    f->arena = arena;
    f->name = sambu_arena_copy_string(arena, name);
    f->return_type = ret;
    return f->name == NULL ? NULL : f;
}
SambuIrStatus sambu_mir_add_block(SambuMirFunction *f, const char *name, uint32_t *id) {
    if (f == NULL || name == NULL || id == NULL) return SAMBU_IR_INVALID_ARGUMENT;
    if (f->block_count >= UINT32_MAX) return SAMBU_IR_OUT_OF_MEMORY;
    SambuIrStatus status = reserve_blocks(f, f->block_count + 1u);
    if (status != SAMBU_IR_OK) return status;
    SambuMirBlock *b = &f->blocks[f->block_count];
    memset(b, 0, sizeof(*b));
    b->id = (uint32_t)f->block_count;
    b->name = sambu_arena_copy_string(f->arena, name);
    if (b->name == NULL) return SAMBU_IR_OUT_OF_MEMORY;
    *id = b->id;
    f->block_count++;
    return SAMBU_IR_OK;
}
static SambuMirBlock *block_at(SambuMirFunction *f, uint32_t id) {
    return f != NULL && id < f->block_count ? &f->blocks[id] : NULL;
}
static SambuIrStatus append_inst(
    SambuMirFunction *f, SambuMirBlock *b, const SambuMirInst *inst
) {
    if (b->instruction_count != 0u &&
        b->instructions[b->instruction_count - 1u].opcode == SAMBU_MIR_RETURN) {
        return SAMBU_IR_INVALID_IR;
    }
    SambuIrStatus status = reserve_instructions(f, b);
    if (status != SAMBU_IR_OK) return status;
    b->instructions[b->instruction_count++] = *inst;
    return SAMBU_IR_OK;
}
static bool value_type_before(
    const SambuMirBlock *b, size_t before, SambuValueId id, SambuType *type
) {
    for (size_t i = 0u; i < before; ++i) {
        if (b->instructions[i].result == id) {
            *type = b->instructions[i].type;
            return true;
        }
    }
    return false;
}
static SambuIrStatus emit_constant(
    SambuMirFunction *f, uint32_t block_id, SambuMirOpcode op,
    SambuType type, const void *value, SambuValueId *result
) {
    if (f == NULL || value == NULL || result == NULL) return SAMBU_IR_INVALID_ARGUMENT;
    if (f->next_value == SAMBU_VALUE_NONE) return SAMBU_IR_OUT_OF_MEMORY;
    SambuMirBlock *b = block_at(f, block_id);
    if (b == NULL) return SAMBU_IR_INVALID_ARGUMENT;
    SambuMirInst inst;
    memset(&inst, 0, sizeof(inst));
    inst.opcode = op;
    inst.result = f->next_value;
    inst.operand_a = SAMBU_VALUE_NONE;
    inst.operand_b = SAMBU_VALUE_NONE;
    inst.type = type;
    if (op == SAMBU_MIR_CONST_BOOL) inst.immediate.boolean = *(const bool *)value;
    else if (op == SAMBU_MIR_CONST_I64) inst.immediate.i64 = *(const int64_t *)value;
    else inst.immediate.f64 = *(const double *)value;
    SambuIrStatus status = append_inst(f, b, &inst);
    if (status != SAMBU_IR_OK) return status;
    *result = f->next_value++;
    return SAMBU_IR_OK;
}
SambuIrStatus sambu_mir_emit_bool(
    SambuMirFunction *f, uint32_t b, bool v, SambuValueId *r
) {
    return emit_constant(f, b, SAMBU_MIR_CONST_BOOL, SAMBU_TYPE_BOOL, &v, r);
}
SambuIrStatus sambu_mir_emit_i64(
    SambuMirFunction *f, uint32_t b, int64_t v, SambuValueId *r
) {
    return emit_constant(f, b, SAMBU_MIR_CONST_I64, SAMBU_TYPE_I64, &v, r);
}
SambuIrStatus sambu_mir_emit_f64(
    SambuMirFunction *f, uint32_t b, double v, SambuValueId *r
) {
    return emit_constant(f, b, SAMBU_MIR_CONST_F64, SAMBU_TYPE_F64, &v, r);
}

static SambuMirOpcode mir_binary_opcode(SambuHirBinaryOp op, SambuType type) {
    if (type == SAMBU_TYPE_I64) {
        switch (op) {
            case SAMBU_HIR_ADD: return SAMBU_MIR_ADD_I64;
            case SAMBU_HIR_SUB: return SAMBU_MIR_SUB_I64;
            case SAMBU_HIR_MUL: return SAMBU_MIR_MUL_I64;
            case SAMBU_HIR_DIV: return SAMBU_MIR_DIV_I64;
            case SAMBU_HIR_EQ: return SAMBU_MIR_EQ_I64;
            case SAMBU_HIR_LT: return SAMBU_MIR_LT_I64;
            default: break;
        }
    } else if (type == SAMBU_TYPE_F64) {
        switch (op) {
            case SAMBU_HIR_ADD: return SAMBU_MIR_ADD_F64;
            case SAMBU_HIR_SUB: return SAMBU_MIR_SUB_F64;
            case SAMBU_HIR_MUL: return SAMBU_MIR_MUL_F64;
            case SAMBU_HIR_DIV: return SAMBU_MIR_DIV_F64;
            case SAMBU_HIR_EQ: return SAMBU_MIR_EQ_F64;
            case SAMBU_HIR_LT: return SAMBU_MIR_LT_F64;
            default: break;
        }
    }
    return SAMBU_MIR_RETURN;
}
static bool comparison_mir(SambuMirOpcode op) {
    return op == SAMBU_MIR_EQ_I64 || op == SAMBU_MIR_LT_I64 ||
        op == SAMBU_MIR_EQ_F64 || op == SAMBU_MIR_LT_F64;
}
SambuIrStatus sambu_mir_emit_binary(
    SambuMirFunction *f, uint32_t block_id, SambuHirBinaryOp op,
    SambuValueId left, SambuValueId right, SambuValueId *result
) {
    if (f == NULL || result == NULL || op < SAMBU_HIR_ADD || op > SAMBU_HIR_LT) {
        return SAMBU_IR_INVALID_ARGUMENT;
    }
    SambuMirBlock *b = block_at(f, block_id);
    if (b == NULL) return SAMBU_IR_INVALID_ARGUMENT;
    SambuType lt, rt;
    if (!value_type_before(b, b->instruction_count, left, &lt) ||
        !value_type_before(b, b->instruction_count, right, &rt) ||
        lt != rt || !numeric(lt)) return SAMBU_IR_INVALID_TYPE;
    if (f->next_value == SAMBU_VALUE_NONE) return SAMBU_IR_OUT_OF_MEMORY;
    SambuMirInst inst;
    memset(&inst, 0, sizeof(inst));
    inst.opcode = mir_binary_opcode(op, lt);
    inst.result = f->next_value;
    inst.operand_a = left;
    inst.operand_b = right;
    inst.type = comparison_mir(inst.opcode) ? SAMBU_TYPE_BOOL : lt;
    SambuIrStatus status = append_inst(f, b, &inst);
    if (status != SAMBU_IR_OK) return status;
    *result = f->next_value++;
    return SAMBU_IR_OK;
}
SambuIrStatus sambu_mir_emit_return(SambuMirFunction *f, uint32_t block_id, SambuValueId value) {
    if (f == NULL) return SAMBU_IR_INVALID_ARGUMENT;
    SambuMirBlock *b = block_at(f, block_id);
    if (b == NULL) return SAMBU_IR_INVALID_ARGUMENT;
    SambuType type;
    if (!value_type_before(b, b->instruction_count, value, &type) || type != f->return_type) {
        return SAMBU_IR_INVALID_TYPE;
    }
    SambuMirInst inst;
    memset(&inst, 0, sizeof(inst));
    inst.opcode = SAMBU_MIR_RETURN;
    inst.result = SAMBU_VALUE_NONE;
    inst.operand_a = value;
    inst.operand_b = SAMBU_VALUE_NONE;
    inst.type = SAMBU_TYPE_UNIT;
    return append_inst(f, b, &inst);
}

static bool valid_mir_binary(
    SambuMirOpcode op, SambuType input, SambuType output
) {
    switch (op) {
        case SAMBU_MIR_ADD_I64:
        case SAMBU_MIR_SUB_I64:
        case SAMBU_MIR_MUL_I64:
        case SAMBU_MIR_DIV_I64:
            return input == SAMBU_TYPE_I64 && output == SAMBU_TYPE_I64;
        case SAMBU_MIR_EQ_I64:
        case SAMBU_MIR_LT_I64:
            return input == SAMBU_TYPE_I64 && output == SAMBU_TYPE_BOOL;
        case SAMBU_MIR_ADD_F64:
        case SAMBU_MIR_SUB_F64:
        case SAMBU_MIR_MUL_F64:
        case SAMBU_MIR_DIV_F64:
            return input == SAMBU_TYPE_F64 && output == SAMBU_TYPE_F64;
        case SAMBU_MIR_EQ_F64:
        case SAMBU_MIR_LT_F64:
            return input == SAMBU_TYPE_F64 && output == SAMBU_TYPE_BOOL;
        default:
            return false;
    }
}
SambuIrStatus sambu_mir_verify(
    const SambuMirFunction *f, char *error, size_t error_capacity
) {
    if (f == NULL || f->name == NULL || f->block_count != 1u || f->blocks == NULL) {
        error_text(error, error_capacity, "MIR v1 requires one named function block");
        return SAMBU_IR_INVALID_IR;
    }
    const SambuMirBlock *b = &f->blocks[0];
    if (b->id != 0u || b->name == NULL || b->instruction_count == 0u ||
        b->instructions == NULL) {
        error_text(error, error_capacity, "MIR entry block is empty or malformed");
        return SAMBU_IR_INVALID_IR;
    }
    uint32_t definitions = 0u;
    bool returned = false;
    for (size_t i = 0u; i < b->instruction_count; ++i) {
        const SambuMirInst *inst = &b->instructions[i];
        if (inst->opcode == SAMBU_MIR_RETURN) {
            SambuType type;
            if (i + 1u != b->instruction_count || returned ||
                inst->operand_a >= definitions ||
                !value_type_before(b, i, inst->operand_a, &type) ||
                type != f->return_type) {
                error_text(error, error_capacity, "MIR return must be final and match the function type");
                return SAMBU_IR_INVALID_IR;
            }
            returned = true;
            continue;
        }
        if (inst->result != definitions || inst->result == SAMBU_VALUE_NONE) {
            error_text(error, error_capacity, "MIR SSA results must be unique and densely numbered");
            return SAMBU_IR_INVALID_IR;
        }
        if (inst->opcode == SAMBU_MIR_CONST_BOOL) {
            if (inst->type != SAMBU_TYPE_BOOL) goto bad_constant;
        } else if (inst->opcode == SAMBU_MIR_CONST_I64) {
            if (inst->type != SAMBU_TYPE_I64) goto bad_constant;
        } else if (inst->opcode == SAMBU_MIR_CONST_F64) {
            if (inst->type != SAMBU_TYPE_F64) goto bad_constant;
        } else {
            SambuType lt, rt;
            if (inst->operand_a >= definitions || inst->operand_b >= definitions ||
                !value_type_before(b, i, inst->operand_a, &lt) ||
                !value_type_before(b, i, inst->operand_b, &rt) ||
                lt != rt || !valid_mir_binary(inst->opcode, lt, inst->type)) {
                error_text(error, error_capacity, "MIR operation has invalid operands or result type");
                return SAMBU_IR_INVALID_IR;
            }
        }
        definitions++;
    }
    if (!returned || definitions != f->next_value) {
        error_text(error, error_capacity, "MIR function has no valid return or inconsistent value count");
        return SAMBU_IR_INVALID_IR;
    }
    error_text(error, error_capacity, "");
    return SAMBU_IR_OK;

bad_constant:
    error_text(error, error_capacity, "MIR constant opcode and type disagree");
    return SAMBU_IR_INVALID_IR;
}

static SambuIrStatus lower_hir_node(
    SambuMirFunction *f, uint32_t block, const SambuHirExpr *expr, SambuValueId *result
) {
    if (expr == NULL || result == NULL) return SAMBU_IR_INVALID_ARGUMENT;
    switch (expr->kind) {
        case SAMBU_HIR_BOOL_LITERAL:
            return sambu_mir_emit_bool(f, block, expr->as.boolean, result);
        case SAMBU_HIR_I64_LITERAL:
            return sambu_mir_emit_i64(f, block, expr->as.i64, result);
        case SAMBU_HIR_F64_LITERAL:
            return sambu_mir_emit_f64(f, block, expr->as.f64, result);
        case SAMBU_HIR_BINARY: {
            SambuValueId left, right;
            SambuIrStatus status = lower_hir_node(f, block, expr->as.binary.left, &left);
            if (status != SAMBU_IR_OK) return status;
            status = lower_hir_node(f, block, expr->as.binary.right, &right);
            if (status != SAMBU_IR_OK) return status;
            return sambu_mir_emit_binary(f, block, expr->as.binary.op, left, right, result);
        }
        default:
            return SAMBU_IR_UNSUPPORTED;
    }
}
SambuIrStatus sambu_lower_hir_expression(
    SambuArena *arena, const char *name, const SambuHirExpr *expr,
    SambuMirFunction **out_function
) {
    if (arena == NULL || name == NULL || expr == NULL || out_function == NULL) {
        return SAMBU_IR_INVALID_ARGUMENT;
    }
    *out_function = NULL;
    SambuMirFunction *f = sambu_mir_function_new(arena, name, expr->type);
    if (f == NULL) return SAMBU_IR_OUT_OF_MEMORY;
    uint32_t entry = 0u;
    SambuIrStatus status = sambu_mir_add_block(f, "entry", &entry);
    if (status != SAMBU_IR_OK) return status;
    SambuValueId value;
    status = lower_hir_node(f, entry, expr, &value);
    if (status != SAMBU_IR_OK) return status;
    status = sambu_mir_emit_return(f, entry, value);
    if (status != SAMBU_IR_OK) return status;
    status = sambu_mir_verify(f, NULL, 0u);
    if (status == SAMBU_IR_OK) *out_function = f;
    return status;
}

static bool map_opcode(SambuMirOpcode m, SambuLirOpcode *l) {
    switch (m) {
        case SAMBU_MIR_CONST_BOOL: *l = SAMBU_LIR_LOAD_BOOL; return true;
        case SAMBU_MIR_CONST_I64: *l = SAMBU_LIR_LOAD_I64; return true;
        case SAMBU_MIR_CONST_F64: *l = SAMBU_LIR_LOAD_F64; return true;
        case SAMBU_MIR_ADD_I64: *l = SAMBU_LIR_ADD_I64; return true;
        case SAMBU_MIR_SUB_I64: *l = SAMBU_LIR_SUB_I64; return true;
        case SAMBU_MIR_MUL_I64: *l = SAMBU_LIR_MUL_I64; return true;
        case SAMBU_MIR_DIV_I64: *l = SAMBU_LIR_DIV_I64; return true;
        case SAMBU_MIR_EQ_I64: *l = SAMBU_LIR_EQ_I64; return true;
        case SAMBU_MIR_LT_I64: *l = SAMBU_LIR_LT_I64; return true;
        case SAMBU_MIR_ADD_F64: *l = SAMBU_LIR_ADD_F64; return true;
        case SAMBU_MIR_SUB_F64: *l = SAMBU_LIR_SUB_F64; return true;
        case SAMBU_MIR_MUL_F64: *l = SAMBU_LIR_MUL_F64; return true;
        case SAMBU_MIR_DIV_F64: *l = SAMBU_LIR_DIV_F64; return true;
        case SAMBU_MIR_EQ_F64: *l = SAMBU_LIR_EQ_F64; return true;
        case SAMBU_MIR_LT_F64: *l = SAMBU_LIR_LT_F64; return true;
        case SAMBU_MIR_RETURN: *l = SAMBU_LIR_RETURN; return true;
        default: return false;
    }
}
SambuIrStatus sambu_lir_lower(
    SambuArena *arena, const SambuMirFunction *mir, SambuLirFunction **out_function
) {
    if (arena == NULL || mir == NULL || out_function == NULL) return SAMBU_IR_INVALID_ARGUMENT;
    *out_function = NULL;
    SambuIrStatus status = sambu_mir_verify(mir, NULL, 0u);
    if (status != SAMBU_IR_OK) return status;
    const SambuMirBlock *b = &mir->blocks[0];
    SambuLirFunction *f = (SambuLirFunction *)sambu_arena_alloc(
        arena, sizeof(*f), alignof(SambuLirFunction)
    );
    if (f == NULL) return SAMBU_IR_OUT_OF_MEMORY;
    memset(f, 0, sizeof(*f));
    f->name = sambu_arena_copy_string(arena, mir->name);
    f->return_type = mir->return_type;
    f->instruction_count = b->instruction_count;
    if (f->name == NULL || f->instruction_count > SIZE_MAX / sizeof(SambuLirInst)) {
        return SAMBU_IR_OUT_OF_MEMORY;
    }
    f->instructions = (SambuLirInst *)sambu_arena_alloc(
        arena, f->instruction_count * sizeof(SambuLirInst), alignof(SambuLirInst)
    );
    if (f->instructions == NULL) return SAMBU_IR_OUT_OF_MEMORY;
    for (size_t i = 0u; i < f->instruction_count; ++i) {
        const SambuMirInst *src = &b->instructions[i];
        SambuLirInst *dst = &f->instructions[i];
        memset(dst, 0, sizeof(*dst));
        if (!map_opcode(src->opcode, &dst->opcode)) return SAMBU_IR_UNSUPPORTED;
        dst->destination = src->result;
        dst->source_a = src->operand_a;
        dst->source_b = src->operand_b;
        dst->type = src->type;
        if (src->opcode == SAMBU_MIR_CONST_BOOL) dst->immediate.boolean = src->immediate.boolean;
        else if (src->opcode == SAMBU_MIR_CONST_I64) dst->immediate.i64 = src->immediate.i64;
        else if (src->opcode == SAMBU_MIR_CONST_F64) dst->immediate.f64 = src->immediate.f64;
    }
    status = sambu_lir_verify(f, NULL, 0u);
    if (status == SAMBU_IR_OK) *out_function = f;
    return status;
}
static bool lir_value_type(
    const SambuLirFunction *f, SambuValueId id, size_t before, SambuType *type
) {
    for (size_t i = 0u; i < before; ++i) {
        if (f->instructions[i].destination == id) {
            *type = f->instructions[i].type;
            return true;
        }
    }
    return false;
}
static bool valid_lir_binary(SambuLirOpcode op, SambuType input, SambuType output) {
    switch (op) {
        case SAMBU_LIR_ADD_I64:
        case SAMBU_LIR_SUB_I64:
        case SAMBU_LIR_MUL_I64:
        case SAMBU_LIR_DIV_I64:
            return input == SAMBU_TYPE_I64 && output == SAMBU_TYPE_I64;
        case SAMBU_LIR_EQ_I64:
        case SAMBU_LIR_LT_I64:
            return input == SAMBU_TYPE_I64 && output == SAMBU_TYPE_BOOL;
        case SAMBU_LIR_ADD_F64:
        case SAMBU_LIR_SUB_F64:
        case SAMBU_LIR_MUL_F64:
        case SAMBU_LIR_DIV_F64:
            return input == SAMBU_TYPE_F64 && output == SAMBU_TYPE_F64;
        case SAMBU_LIR_EQ_F64:
        case SAMBU_LIR_LT_F64:
            return input == SAMBU_TYPE_F64 && output == SAMBU_TYPE_BOOL;
        default:
            return false;
    }
}
SambuIrStatus sambu_lir_verify(
    const SambuLirFunction *f, char *error, size_t error_capacity
) {
    if (f == NULL || f->name == NULL || f->instructions == NULL || f->instruction_count == 0u) {
        error_text(error, error_capacity, "LIR function is empty or malformed");
        return SAMBU_IR_INVALID_IR;
    }
    uint32_t definitions = 0u;
    bool returned = false;
    for (size_t i = 0u; i < f->instruction_count; ++i) {
        const SambuLirInst *inst = &f->instructions[i];
        if (inst->opcode == SAMBU_LIR_RETURN) {
            SambuType type;
            if (i + 1u != f->instruction_count || returned ||
                inst->source_a >= definitions ||
                !lir_value_type(f, inst->source_a, i, &type) || type != f->return_type) {
                error_text(error, error_capacity, "LIR return must be final and match the function type");
                return SAMBU_IR_INVALID_IR;
            }
            returned = true;
            continue;
        }
        if (inst->destination != definitions || inst->destination == SAMBU_VALUE_NONE) {
            error_text(error, error_capacity, "LIR virtual registers must be densely defined");
            return SAMBU_IR_INVALID_IR;
        }
        if (inst->opcode == SAMBU_LIR_LOAD_BOOL) {
            if (inst->type != SAMBU_TYPE_BOOL) goto bad_lir_type;
        } else if (inst->opcode == SAMBU_LIR_LOAD_I64) {
            if (inst->type != SAMBU_TYPE_I64) goto bad_lir_type;
        } else if (inst->opcode == SAMBU_LIR_LOAD_F64) {
            if (inst->type != SAMBU_TYPE_F64) goto bad_lir_type;
        } else {
            SambuType lt, rt;
            if (inst->source_a >= definitions || inst->source_b >= definitions ||
                !lir_value_type(f, inst->source_a, i, &lt) ||
                !lir_value_type(f, inst->source_b, i, &rt) ||
                lt != rt || !valid_lir_binary(inst->opcode, lt, inst->type)) {
                error_text(error, error_capacity, "LIR operation has invalid registers or types");
                return SAMBU_IR_INVALID_IR;
            }
        }
        definitions++;
    }
    if (!returned) {
        error_text(error, error_capacity, "LIR function has no final return");
        return SAMBU_IR_INVALID_IR;
    }
    error_text(error, error_capacity, "");
    return SAMBU_IR_OK;

bad_lir_type:
    error_text(error, error_capacity, "LIR load opcode and type disagree");
    return SAMBU_IR_INVALID_IR;
}
