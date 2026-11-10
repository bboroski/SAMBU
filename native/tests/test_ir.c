#include "sambu/ir.h"

#include <assert.h>
#include <stdint.h>
#include <stdio.h>

static void test_arena_and_interner(void) {
    SambuArena arena;
    assert(sambu_arena_init(&arena, 128u) == SAMBU_IR_OK);
    void *aligned = sambu_arena_alloc(&arena, 37u, 64u);
    assert(aligned != NULL && ((uintptr_t)aligned % 64u) == 0u);

    SambuInterner interner;
    assert(sambu_interner_init(&interner) == SAMBU_IR_OK);
    const char *one = sambu_interner_intern(&interner, "sambu");
    const char *two = sambu_interner_intern(&interner, "sambu");
    assert(one != NULL && one == two && interner.length == 1u);
    for (unsigned i = 0u; i < 1000u; ++i) {
        char name[32];
        (void)snprintf(name, sizeof(name), "symbol_%u", i);
        assert(sambu_interner_intern(&interner, name) != NULL);
    }
    assert(interner.length == 1001u);
    sambu_interner_dispose(&interner);
    sambu_arena_dispose(&arena);
}

static void test_hir_mir_lir(void) {
    SambuArena arena;
    assert(sambu_arena_init(&arena, 512u) == SAMBU_IR_OK);
    const SambuSourceSpan span = {0u, 1u};
    const SambuHirExpr *six = sambu_hir_i64(&arena, 6, span);
    const SambuHirExpr *seven = sambu_hir_i64(&arena, 7, span);
    const SambuHirExpr *one = sambu_hir_i64(&arena, 1, span);
    assert(six != NULL && seven != NULL && one != NULL);
    const SambuHirExpr *product = sambu_hir_binary(&arena, SAMBU_HIR_MUL, six, seven, span);
    const SambuHirExpr *sum = sambu_hir_binary(&arena, SAMBU_HIR_ADD, product, one, span);
    assert(product != NULL && sum != NULL && sum->type == SAMBU_TYPE_I64);

    SambuMirFunction *mir = NULL;
    assert(sambu_lower_hir_expression(&arena, "main", sum, &mir) == SAMBU_IR_OK);
    assert(mir != NULL && mir->block_count == 1u && mir->next_value == 5u);
    char error[160];
    assert(sambu_mir_verify(mir, error, sizeof(error)) == SAMBU_IR_OK);

    SambuLirFunction *lir = NULL;
    assert(sambu_lir_lower(&arena, mir, &lir) == SAMBU_IR_OK);
    assert(lir != NULL && lir->instruction_count == mir->blocks[0].instruction_count);
    assert(sambu_lir_verify(lir, error, sizeof(error)) == SAMBU_IR_OK);

    const SambuHirExpr *fraction = sambu_hir_f64(&arena, 0.5, span);
    assert(fraction != NULL);
    assert(sambu_hir_binary(&arena, SAMBU_HIR_ADD, six, fraction, span) == NULL);

    SambuValueId saved = mir->blocks[0].instructions[4].operand_a;
    mir->blocks[0].instructions[4].operand_a = 999u;
    assert(sambu_mir_verify(mir, error, sizeof(error)) == SAMBU_IR_INVALID_IR);
    mir->blocks[0].instructions[4].operand_a = saved;
    assert(sambu_mir_verify(mir, error, sizeof(error)) == SAMBU_IR_OK);
    sambu_arena_dispose(&arena);
}

int main(void) {
    test_arena_and_interner();
    test_hir_mir_lir();
    puts("SAMBU native IR tests passed");
    return 0;
}
