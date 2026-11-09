from __future__ import annotations

import math
import unittest

from sambu.interpreter import execute
from sambu.runtime import SambuRuntimeError


class LanguageV020Tests(unittest.TestCase):
    def run_sambu(self, source: str):
        output: list[str] = []
        result = execute(source, output=output.append)
        return result, output

    def test_user_functions_and_return(self):
        result, output = self.run_sambu('''fn square(x) { return x * x }
print(square(9))''')
        self.assertEqual(result, 81)
        self.assertEqual(output, ["81"])


    def test_lexical_binding_can_shadow_standard_function(self):
        _, output = self.run_sambu('''fn calculate(max) { return max + 1 }
print(calculate(4))''')
        self.assertEqual(output, ["5"])

    def test_recursive_function(self):
        _, output = self.run_sambu('''fn factorial(n) {
  if (n <= 1) { return 1 }
  else { return n * factorial(n - 1) }
}
print(factorial(6))''')
        self.assertEqual(output, ["720"])

    def test_if_else_and_block_scope(self):
        _, output = self.run_sambu('''let x = 5
if (x > 3) { let local = "large"; print(local) }
else { print("small") }
print(x)''')
        self.assertEqual(output, ["large", "5"])
        with self.assertRaises(SambuRuntimeError):
            execute('''if (true) { let hidden = 1 }
print(hidden)''')

    def test_for_range_sum_and_comprehension_style_accumulation(self):
        _, output = self.run_sambu('''let squares = []
for i in range(1, 5) { print(i * i) }
print(sum([1, 2, 3, 4]))
print(min([7, 2, 5]))
print(max([7, 2, 5]))''')
        self.assertEqual(output, ["1", "4", "9", "16", "10", "2", "7"])

    def test_network_metrics_and_influence(self):
        _, output = self.run_sambu('''let graph = network(["a", "b", "c"], [["a", "b", 0.9], ["b", "c", 0.8]])
let metrics = network_metrics(graph)
let signal = influence(graph, ["a"], 2, 0.8)
print(metrics.edge_count)
print(metrics.density)
print(signal.scores[2])''')
        self.assertEqual(output, ["2", "0.33333333", "0.4608"])

    def test_network_rejects_unknown_node(self):
        with self.assertRaises(ValueError):
            execute('let graph = network(["a"], [["a", "missing"]])')

    def test_negotiation_zone(self):
        _, output = self.run_sambu('''let z = negotiate(10, 30, 25, 40)
print(z.possible)
print(z.lower)
print(z.upper)
print(z.midpoint)''')
        self.assertEqual(output, ["true", "25", "30", "27.5"])

    def test_quantity_negotiation_preserves_units(self):
        _, output = self.run_sambu('''let z = negotiate(10 * J, 30 * J, 25 * J, 40 * J)
print(z.midpoint)''')
        self.assertEqual(output, ["27.5 J"])

    def test_funnel_and_ab_test(self):
        _, output = self.run_sambu('''let f = funnel([1000, 400, 100])
let test = ab_test(200, 40, 200, 60)
print(f.overall_conversion)
print(f.step_conversion[0])
print(test.absolute_lift)
print(test.p_value < 0.05)''')
        self.assertEqual(output[:3], ["0.1", "0.4", "0.1"])
        self.assertEqual(output[3], "true")

    def test_weekly_schedule_and_capacity(self):
        _, output = self.run_sambu('''let calendar = weekly_schedule([["Friday", "19:00", "Tea", 12], ["Monday", "18:00", "Yoga", 16]])
let room = attendance(16, 12)
print(calendar.session_count)
print(calendar.active_weekdays)
print(room.fill_rate)
print(room.remaining)''')
        self.assertEqual(output, ["2", "[Monday, Friday]", "0.75", "4"])

    def test_tower_capture_and_allocation(self):
        _, output = self.run_sambu('''let shares = allocate(100, [0.5, 0.25, 0.25])
let result = capture_tower(40, shares[0])
print(shares)
print(result.captured)
print(result.overflow)''')
        self.assertEqual(output, ["[50, 25, 25]", "true", "10"])

    def test_invalid_funnel_and_schedule_rejected(self):
        with self.assertRaises(ValueError):
            execute('let f = funnel([100, 110, 20])')
        with self.assertRaises(ValueError):
            execute('let s = weekly_schedule([["Monday", "18:00", "Yoga"], ["Monday", "18:00", "Tea"]])')


    def test_multiline_array_and_calls(self):
        _, output = self.run_sambu('''let values = [
  1,
  2,
  3
]
print(sum(values))''')
        self.assertEqual(output, ["6"])

    def test_range_requires_integer_arguments(self):
        with self.assertRaises(ValueError):
            execute("print(range(2.5))")
        with self.assertRaises(ValueError):
            execute("print(range(100001))")


    def test_channel_metrics_and_package_pricing(self):
        _, output = self.run_sambu('''let channel = channel_metrics(180, 12000, 240, 36)
let package = package_pricing(30, 200, 8)
print(channel.cost_per_customer)
print(channel.lead_rate)
print(package.effective_session_price)
print(package.discount_rate)''')
        self.assertEqual(output, ["5", "0.02", "25", "0.16666667"])

    def test_unit_economics_and_channel_validation(self):
        _, output = self.run_sambu('''let economics = unit_economics(100, 35, 20)
print(economics.contribution_after_acquisition)''')
        self.assertEqual(output, ["45"])
        with self.assertRaises(ValueError):
            execute("let channel = channel_metrics(50, 100, 30, 31)")

    def test_return_outside_function_rejected(self):
        with self.assertRaises(SambuRuntimeError):
            execute("return 42")


    def test_commerce_queue_profile_and_dead_letter_route(self):
        _, output = self.run_sambu('''let queue = queue_profile("heavy_orders", 4, 8, 3, true)
print(queue.max_in_flight)
print(queue.max_attempts)
print(queue.dead_letter_queue)''')
        self.assertEqual(output, ["32", "4", "heavy_orders.dlq"])

    def test_commerce_retry_schedule_and_idempotency_key(self):
        _, output = self.run_sambu('''let delays = retry_schedule(5, 2, 2, 10)
print(delays)
print(idempotency_key("checkout", "cart-42"))''')
        self.assertEqual(output, ["[2, 4, 8, 10]", "checkout:cart-42"])

    def test_commerce_queue_primitives_reject_unsafe_configuration(self):
        with self.assertRaises(ValueError):
            execute('queue_profile("Bad Queue", 4, 8, 3, true)')
        with self.assertRaises(ValueError):
            execute("retry_schedule(4, 2, 0.5, 10)")
        with self.assertRaises(ValueError):
            execute('idempotency_key("checkout", "")')


class NeoModernBlueprintTests(unittest.TestCase):
    def run_sambu(self, source: str):
        output: list[str] = []
        result = execute(source, output=output.append)
        return result, output

    def test_audio_profile_captures_production_constraints(self):
        _, output = self.run_sambu('''let mix = audio_profile("Neo Modern Diplomat", 150, 60, 15, -0.3, true, true, true, true, true)
print(mix.bpm)
print(mix.immediate_entry)
print(mix.stereo_mastering)
print(mix.mix_ceiling_is_below_full_scale)''')
        self.assertEqual(output, ["150", "true", "true", "true"])

    def test_audio_profile_rejects_unsafe_values_and_non_boolean_flags(self):
        with self.assertRaises(ValueError):
            execute('audio_profile("bad", 150, 60, 15, 0.2, true, true, true, true, true)')
        with self.assertRaises(TypeError):
            execute('audio_profile("bad", 150, 60, 15, -0.3, "yes", true, true, true, true)')

    def test_studio_offer_checks_intro_conversion_and_package_economics(self):
        _, output = self.run_sambu('''let offer = studio_offer(200, 60, 0.30, 30, 200, 8)
print(offer.intro_conversion)
print(offer.target_met)
print(offer.effective_session_price)
print(offer.package_savings)
print(offer.package_discount_rate)''')
        self.assertEqual(output, ["0.3", "true", "25", "40", "0.16666667"])

    def test_studio_offer_handles_zero_visitors_and_rejects_impossible_counts(self):
        _, output = self.run_sambu('''let offer = studio_offer(0, 0, 0.30, 30, 200, 8)
print(offer.target_met)''')
        self.assertEqual(output, ["false"])
        with self.assertRaises(ValueError):
            execute("studio_offer(10, 11, 0.3, 30, 200, 8)")

    def test_capture_node_transfers_owner_only_after_resistance_is_depleted(self):
        _, output = self.run_sambu('''let partial = capture_node("rival", "diplomat", 40, 25)
let captured = capture_node("rival", "diplomat", 40, 55)
print(partial.captured)
print(partial.owner_after)
print(partial.resistance_after)
print(captured.captured)
print(captured.owner_after)
print(captured.overflow)''')
        self.assertEqual(output, ["false", "rival", "15", "true", "diplomat", "15"])

    def test_capture_node_rejects_same_faction_and_negative_pressure(self):
        with self.assertRaises(ValueError):
            execute('capture_node("diplomat", "diplomat", 10, 20)')
        with self.assertRaises(ValueError):
            execute('capture_node("rival", "diplomat", 10, -1)')

    def test_order_pipeline_accepts_safe_outbox_and_acknowledgement_plan(self):
        _, output = self.run_sambu('''let queue = queue_profile("heavy_orders_queue", 4, 8, 3, true)
let flow = order_pipeline(queue, true, true, true, true, true, true)
print(flow.invariants_satisfied)
print(flow.delivery_semantics)
print(flow.acknowledgement_boundary)
print(flow.max_in_flight)
print(count(flow.blockers))''')
        self.assertEqual(output, ["true", "at_least_once", "after_order_state_commit", "32", "0"])

    def test_order_pipeline_reports_missing_safety_invariants(self):
        _, output = self.run_sambu('''let queue = queue_profile("orders", 2, 4, 2, false)
let flow = order_pipeline(queue, false, true, true, true, false, true)
print(flow.invariants_satisfied)
print(count(flow.blockers))''')
        self.assertEqual(output, ["false", "3"])

    def test_order_pipeline_requires_a_queue_profile(self):
        with self.assertRaises(TypeError):
            execute('order_pipeline("orders", true, true, true, true, true, true)')



if __name__ == "__main__":
    unittest.main()
