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

int main(void) {
    if (!test_arena_and_interner() || !test_hir_mir_lir()) return 1;
    puts("SAMBU native IR tests passed");
    return 0;
}
