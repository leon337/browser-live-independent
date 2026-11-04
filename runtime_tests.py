"""Offline regression of cancellation, serialization and durable task recovery."""
import asyncio
import json
import tempfile
import unittest
from pathlib import Path
import app

class RuntimeTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix="browser-live-tests-")
        self.original_state=app.STATE
        app.STATE=Path(self.tmp.name)

    async def asyncTearDown(self):
        app.STATE=self.original_state
        self.tmp.cleanup()

    async def test_restart_marks_unfinished_task(self):
        item={"id":"test","objective":"teste local","state":"running","steps":1}
        (app.STATE/"task.json").write_text(json.dumps(item))
        runtime=app.Runtime()
        self.assertEqual(runtime.current["state"],"interrupted_after_restart")
        disk=json.loads((app.STATE/"task.json").read_text())
        self.assertEqual(disk["state"],"interrupted_after_restart")

    async def test_only_one_task_and_stop_allows_next(self):
        runtime=app.Runtime()
        async def suspended(_objective,_generation):
            await asyncio.sleep(3600)
        runtime.run=suspended
        first=await runtime.start("tarefa inicial")
        self.assertTrue(first["ok"])
        second=await runtime.start("tarefa simultânea")
        self.assertFalse(second["ok"])
        stopped=await runtime.stop()
        self.assertTrue(stopped["ok"])
        self.assertEqual(stopped["task"]["state"],"stopped")
        self.assertEqual(json.loads((app.STATE/"task.json").read_text())["state"],"stopped")
        next_task=await runtime.start("tarefa posterior")
        self.assertTrue(next_task["ok"])
        await runtime.stop()
        self.assertNotEqual(first["id"],next_task["id"])

if __name__=="__main__":
    unittest.main(verbosity=2)
