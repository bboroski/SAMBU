import unittest

from sambu.platforms import detect_target, is_native_e2k_linux, normalize_architecture


class PlatformDetectionTests(unittest.TestCase):
    def test_e2k_aliases_normalize(self):
        for name in ("e2k", "E2K", "Elbrus", "mcst-elbrus"):
            self.assertEqual(normalize_architecture(name), "e2k")

    def test_e2k_linux_contract_is_64_bit_little_endian(self):
        result = detect_target(machine="e2k", pointer_bits=64, byteorder="little", system="Linux")
        self.assertEqual(result["architecture"], "e2k")
        self.assertEqual(result["elf_machine"], 175)
        self.assertTrue(result["native_e2k_userspace"])
        self.assertFalse(result["bare_metal_support"])

    def test_wrong_word_size_or_endian_is_not_qualified(self):
        self.assertFalse(detect_target(machine="e2k", pointer_bits=32)["native_e2k_userspace"])
        self.assertFalse(detect_target(machine="e2k", pointer_bits=64, byteorder="big")["native_e2k_userspace"])

    def test_x86_host_is_not_e2k(self):
        result = detect_target(machine="x86_64", pointer_bits=64, byteorder="little")
        self.assertEqual(result["architecture"], "x86_64")
        self.assertIsNone(result["elf_machine"])
        self.assertFalse(result["native_e2k_userspace"])

    def test_invalid_pointer_width_is_rejected(self):
        with self.assertRaises(ValueError):
            detect_target(machine="e2k", pointer_bits=48)

    def test_current_host_probe_is_boolean(self):
        self.assertIsInstance(is_native_e2k_linux(), bool)


if __name__ == "__main__":
    unittest.main()
