from __future__ import annotations

from pathlib import Path
import unittest

from sambu import execute


ROOT = Path(__file__).resolve().parents[1]


class PassageCurtainPatternTests(unittest.TestCase):
    def test_passage_opens_for_first_arrival_and_closes_after_last_exit(self):
        output: list[str] = []
        source = (ROOT / "examples" / "passage_curtain.sambu").read_text(encoding="utf-8")
        execute(source, output=output.append)
        self.assertEqual(
            output,
            ["opened", "already_open", "held_open", "closed", "false"],
        )

    def test_extra_exit_does_not_make_occupancy_negative(self):
        output: list[str] = []
        execute("""
class PassageCurtain {
  fn init(self) {
    self.occupants = 0
    self.is_open = false
  }
  fn leave(self) {
    if self.occupants > 0 {
      self.occupants = self.occupants - 1
    }
    if self.occupants == 0 {
      if self.is_open {
        self.is_open = false
        return "closed"
      }
      return "already_closed"
    }
    return "held_open"
  }
}
let curtain = PassageCurtain()
print(curtain.leave())
print(curtain.occupants)
""", output=output.append)
        self.assertEqual(output, ["already_closed", "0"])


if __name__ == "__main__":
    unittest.main()
