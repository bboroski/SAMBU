from __future__ import annotations
import unittest
from sambu.jiu_jitsu import DualActionButton, JiuJitsu, JiuJitsuError, Role, RoleManager, ViewController, ViewDefinition, ViewNode

class DualActionButtonTests(unittest.TestCase):
    def test_button_serializes_actions(self):
        node=DualActionButton("save","Save / Preview","save","preview",primary_label="Save",secondary_label="Preview").to_node()
        self.assertEqual(node.kind,"dual_action_button")
        self.assertEqual(node.props["actions"]["primary"]["name"],"save")
        self.assertEqual(node.props["actions"]["secondary"]["name"],"preview")
    def test_dispatch_requires_explicit_intent(self):
        roles=RoleManager()
        roles.add_role(Role("operator",grants=frozenset({"save:run","preview:run"})))
        roles.assign("alice","operator")
        app=JiuJitsu.app("alice",roles)
        app.register_view(ViewDefinition("/home","Home",ViewNode("home","page")))
        controller=ViewController("home").dual_action(
            "save-or-preview",lambda c,p:"saved",lambda c,p:"previewed",
            primary_permission="save:run",secondary_permission="preview:run",
        )
        app.register_controller("/home",controller); app.navigate("/home")
        with self.assertRaises(JiuJitsuError): app.dispatch("save-or-preview",{})
        self.assertEqual(app.dispatch("save-or-preview",{"intent":"primary"}),"saved")
        self.assertEqual(app.dispatch("save-or-preview",{"intent":"secondary"}),"previewed")

if __name__ == "__main__": unittest.main()
