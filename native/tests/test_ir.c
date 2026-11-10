#include "sambu/ir.h"

#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>

#define CHECK(condition) do { \
    if (!(condition)) { \
        (void)fprintf(stderr, "CHECK failed at %s:%d: %s\n", __FILE__, __LINE__, #condition); \
        return false; \
    } \
} while (0)

static bool test_arena_and_interner(void) {
    SambuArena arena;
    CHECK(sambu_arena_init(&arena, 128u) == SAMBU_IR_OK);
    void *aligned = sambu_arena_alloc(&arena, 37u, 64u);
    CHECK(aligned != NULL && ((uintptr_t)aligned % 64u) == 0u);

    SambuInterner interner;
    CHECK(sambu_interner_init(&interner) == SAMBU_IR_OK);
    const char *one = sambu_interner_intern(&interner, "sambu");
    const char *two = sambu_interner_intern(&interner, "sambu");
    CHECK(one != NULL && one == two && interner.length == 1u);
    for (unsigned i = 0u; i < 1000u; ++i) {
        char name[32];
        (void)snprintf(name, sizeof(name), "symbol_%u", i);
        CHECK(sambu_interner_intern(&interner, name) != NULL);
    }
    CHECK(interner.length == 1001u);
    sambu_interner_dispose(&interner);
    sambu_arena_dispose(&arena);
    return true;
}

static bool test_hir_mir_lir(void) {
    SambuArena arena;
    CHECK(sambu_arena_init(&arena, 512u) == SAMBU_IR_OK);
    const SambuSourceSpan span = {0u, 1u};
    const SambuHirExpr *six = sambu_hir_i64(&arena, 6, span);
    const SambuHirExpr *seven = sambu_hir_i64(&arena, 7, span);
    const SambuHirExpr *one = sambu_hir_i64(&arena, 1, span);
    CHECK(six != NULL && seven != NULL && one != NULL);
    const SambuHirExpr *product = sambu_hir_binary(&arena, SAMBU_HIR_MUL, six, seven, span);
    CHECK(product != NULL);
    const SambuHirExpr *sum = sambu_hir_binary(&arena, SAMBU_HIR_ADD, product, one, span);
    CHECK(sum != NULL && sum->type == SAMBU_TYPE_I64);

    SambuMirFunction *mir = NULL;
    CHECK(sambu_lower_hir_expression(&arena, "main", sum, &mir) == SAMBU_IR_OK);
    CHECK(mir != NULL && mir->block_count == 1u && mir->next_value == 5u);
    char error[160];
    CHECK(sambu_mir_verify(mir, error, sizeof(error)) == SAMBU_IR_OK);

    SambuLirFunction *lir = NULL;
    CHECK(sambu_lir_lower(&arena, mir, &lir) == SAMBU_IR_OK);
    CHECK(lir != NULL && lir->instruction_count == mir->blocks[0].instruction_count);
    CHECK(sambu_lir_verify(lir, error, sizeof(error)) == SAMBU_IR_OK);

    const SambuHirExpr *fraction = sambu_hir_f64(&arena, 0.5, span);
    CHECK(fraction != NULL);
    CHECK(sambu_hir_binary(&arena, SAMBU_HIR_ADD, six, fraction, span) == NULL);

    SambuValueId saved = mir->blocks[0].instructions[4].operand_a;
    mir->blocks[0].instructions[4].operand_a = 999u;
    CHECK(sambu_mir_verify(mir, error, sizeof(error)) == SAMBU_IR_INVALID_IR);
    mir->blocks[0].instructions[4].operand_a = saved;
    CHECK(sambu_mir_verify(mir, error, sizeof(error)) == SAMBU_IR_OK);
    sambu_arena_dispose(&arena);
    return true;
}

static bool test_mir_constant_folding(void) {
    SambuArena arena;
    CHECK(sambu_arena_init(&arena, 512u) == SAMBU_IR_OK);
    const SambuSourceSpan span = {0u, 1u};
    const SambuHirExpr *six = sambu_hir_i64(&arena, 6, span);
    const SambuHirExpr *seven = sambu_hir_i64(&arena, 7, span);
    const SambuHirExpr *one = sambu_hir_i64(&arena, 1, span);
    CHECK(six != NULL && seven != NULL && one != NULL);
    const SambuHirExpr *product = sambu_hir_binary(&arena, SAMBU_HIR_MUL, six, seven, span);
    const SambuHirExpr *sum = product != NULL
        ? sambu_hir_binary(&arena, SAMBU_HIR_ADD, product, one, span) : NULL;
    CHECK(sum != NULL);

    SambuMirFunction *mir = NULL;
    CHECK(sambu_lower_hir_expression(&arena, "folded", sum, &mir) == SAMBU_IR_OK);
    size_t folded = 0u;
    CHECK(sambu_mir_fold_constants(mir, &folded) == SAMBU_IR_OK);
    CHECK(folded == 2u);
    CHECK(mir->blocks[0].instructions[2].opcode == SAMBU_MIR_CONST_I64);
    CHECK(mir->blocks[0].instructions[2].immediate.i64 == 42);
    CHECK(mir->blocks[0].instructions[4].opcode == SAMBU_MIR_CONST_I64);
    CHECK(mir->blocks[0].instructions[4].immediate.i64 == 43);
    CHECK(sambu_mir_verify(mir, NULL, 0u) == SAMBU_IR_OK);
    CHECK(sambu_mir_fold_constants(mir, &folded) == SAMBU_IR_OK);
    CHECK(folded == 0u);

    SambuLirFunction *lir = NULL;
    CHECK(sambu_lir_lower(&arena, mir, &lir) == SAMBU_IR_OK);
    CHECK(sambu_lir_verify(lir, NULL, 0u) == SAMBU_IR_OK);

    const SambuHirExpr *maximum = sambu_hir_i64(&arena, INT64_MAX, span);
    const SambuHirExpr *overflow = sambu_hir_binary(&arena, SAMBU_HIR_ADD,
                                                     maximum, one, span);
    CHECK(overflow != NULL);
    SambuMirFunction *overflow_mir = NULL;
    CHECK(sambu_lower_hir_expression(&arena, "overflow", overflow,
                                     &overflow_mir) == SAMBU_IR_OK);
    CHECK(sambu_mir_fold_constants(overflow_mir, &folded) == SAMBU_IR_OK);
    CHECK(folded == 0u);
    CHECK(overflow_mir->blocks[0].instructions[2].opcode == SAMBU_MIR_ADD_I64);

    const SambuHirExpr *zero = sambu_hir_i64(&arena, 0, span);
    const SambuHirExpr *division = sambu_hir_binary(&arena, SAMBU_HIR_DIV,
                                                     one, zero, span);
    CHECK(division != NULL);
    SambuMirFunction *division_mir = NULL;
    CHECK(sambu_lower_hir_expression(&arena, "division", division,
                                     &division_mir) == SAMBU_IR_OK);
    CHECK(sambu_mir_fold_constants(division_mir, &folded) == SAMBU_IR_OK);
    CHECK(folded == 0u);
    CHECK(division_mir->blocks[0].instructions[2].opcode == SAMBU_MIR_DIV_I64);

    sambu_arena_dispose(&arena);
    return true;
}

static bool test_unit_returns(void) {
    SambuArena arena;
    CHECK(sambu_arena_init(&arena, 256u) == SAMBU_IR_OK);

    SambuMirFunction *mir = sambu_mir_function_new(&arena, "procedure", SAMBU_TYPE_UNIT);
    CHECK(mir != NULL);
    uint32_t entry = 0u;
    CHECK(sambu_mir_add_block(mir, "entry", &entry) == SAMBU_IR_OK);
    CHECK(sambu_mir_emit_return_unit(mir, entry) == SAMBU_IR_OK);

    char error[160];
    CHECK(sambu_mir_verify(mir, error, sizeof(error)) == SAMBU_IR_OK);

    SambuLirFunction *lir = NULL;
    CHECK(sambu_lir_lower(&arena, mir, &lir) == SAMBU_IR_OK);
    CHECK(lir != NULL && lir->instruction_count == 1u);
    CHECK(lir->instructions[0].source_a == SAMBU_VALUE_NONE);
    CHECK(lir->instructions[0].source_b == SAMBU_VALUE_NONE);
    CHECK(sambu_lir_verify(lir, error, sizeof(error)) == SAMBU_IR_OK);

    lir->instructions[0].source_a = 0u;
    CHECK(sambu_lir_verify(lir, error, sizeof(error)) == SAMBU_IR_INVALID_IR);
    lir->instructions[0].source_a = SAMBU_VALUE_NONE;

    mir->blocks[0].instructions[0].operand_a = 0u;
    CHECK(sambu_mir_verify(mir, error, sizeof(error)) == SAMBU_IR_INVALID_IR);
    mir->blocks[0].instructions[0].operand_a = SAMBU_VALUE_NONE;
    CHECK(sambu_mir_verify(mir, error, sizeof(error)) == SAMBU_IR_OK);

    CHECK(sambu_mir_emit_return_unit(mir, entry) == SAMBU_IR_INVALID_IR);

    SambuMirFunction *value_function =
        sambu_mir_function_new(&arena, "value_function", SAMBU_TYPE_I64);
    CHECK(value_function != NULL);
    uint32_t value_entry = 0u;
    CHECK(sambu_mir_add_block(value_function, "entry", &value_entry) == SAMBU_IR_OK);
    CHECK(sambu_mir_emit_return_unit(value_function, value_entry) == SAMBU_IR_INVALID_TYPE);

    sambu_arena_dispose(&arena);
    return true;
}

int main(void) {
    if (!test_arena_and_interner() || !test_hir_mir_lir() || !test_mir_constant_folding() || !test_unit_returns()) return 1;
    puts("SAMBU native IR tests passed");
    return 0;
}
