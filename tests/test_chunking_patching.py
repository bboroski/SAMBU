from __future__ import annotations
import unittest
from sambu.chunking import chunked, plan_chunks
from sambu.patching import PatchConflict, PatchSet, TextPatch

class ChunkingTests(unittest.TestCase):
    def test_lazy_chunks_and_manifest(self):
        self.assertEqual(list(chunked(iter(range(7)),3)),[(0,1,2),(3,4,5),(6,)])
        plan=plan_chunks(17,5,max_in_flight=2)
        self.assertEqual((plan.chunk_count,plan.processing_waves,plan.final_chunk_size),(4,2,2))
    def test_limits(self):
        with self.assertRaises(ValueError): list(chunked(range(5),2,max_items=3))
        with self.assertRaises(ValueError): plan_chunks(1_000_001,1)

class PatchSetTests(unittest.TestCase):
    def test_apply_rollback_reapply(self):
        receipt=PatchSet("rename",(TextPatch(4,7,"cat","duck"),)).apply("the cat sat")
        self.assertEqual(receipt.updated,"the duck sat")
        self.assertEqual(receipt.rollback(receipt.updated),"the cat sat")
        self.assertEqual(receipt.reapply(receipt.original),"the duck sat")
    def test_stale_and_overlapping_rejected(self):
        with self.assertRaises(PatchConflict):
            PatchSet("stale",(TextPatch(0,3,"dog","fox"),)).apply("cat sat")
        overlap=PatchSet("overlap",(TextPatch(0,3,"the","a"),TextPatch(2,5,"e c","fox")))
        with self.assertRaises(PatchConflict): overlap.apply("the cat")

if __name__ == "__main__": unittest.main()
