"""JSON 提取与记忆管理的测试。

两处都是"LLM 输出不可信"的重灾区：模型会在 JSON 前后写废话、
把工具结果塞得超长、把历史消息裁剪出孤儿 tool 消息。
"""

from __future__ import annotations

import json
import os
import unittest

from cra.jsonutil import extract_json_array, extract_json_object
from cra.memory import Memory, SessionStore
from tests.support import TempDirTestCase


class TestJsonExtraction(unittest.TestCase):
    def test_plain_object(self) -> None:
        self.assertEqual(extract_json_object('{"a": 1}'), {"a": 1})

    def test_fenced_object(self) -> None:
        text = '这是结果：\n```json\n{"summary": "ok", "findings": []}\n```\n希望有帮助'
        data = extract_json_object(text)
        self.assertEqual(data["summary"], "ok")

    def test_braces_inside_strings(self) -> None:
        text = 'prefix {"detail": "代码里有 { 花括号 } 和 } 反括号", "ok": true} suffix'
        data = extract_json_object(text)
        self.assertTrue(data["ok"])
        self.assertIn("花括号", data["detail"])

    def test_trailing_comma_repair(self) -> None:
        self.assertEqual(extract_json_object('{"a": 1,}'), {"a": 1})

    def test_garbage_returns_none(self) -> None:
        self.assertIsNone(extract_json_object("完全没有 JSON"))

    def test_array_extraction(self) -> None:
        items = extract_json_array('说明\n[{"title": "x"}, {"title": "y"}]\n结束')
        self.assertEqual(len(items), 2)


class TestMemory(unittest.TestCase):
    def test_system_prompt_is_kept_first(self) -> None:
        memory = Memory(system_prompt="SYS")
        memory.add_user("hello")
        self.assertEqual(memory.to_messages()[0], {"role": "system", "content": "SYS"})

    def test_trim_keeps_recent_and_drops_old(self) -> None:
        memory = Memory(system_prompt="SYS", max_chars=200, keep_recent=2)
        for index in range(20):
            memory.add_user("x" * 50 + str(index))
        messages = memory.to_messages()
        self.assertLessEqual(len(messages), 21)
        self.assertGreater(memory.trimmed_count, 0)
        self.assertIn("19", messages[-1]["content"])

    def test_trim_never_leaves_orphan_tool_message(self) -> None:
        memory = Memory(system_prompt="SYS", max_chars=300, keep_recent=1)
        for index in range(6):
            memory.add_assistant("思考", [{"id": f"c{index}", "type": "function",
                                           "function": {"name": "read_file", "arguments": "{}"}}])
            memory.add_tool_result(f"c{index}", "read_file", "y" * 80)
        messages = memory.to_messages()
        self.assertNotEqual(messages[0]["role"], "tool")
        self.assertNotEqual(messages[1]["role"] if len(messages) > 1 else "", "tool")

    def test_session_payload_is_json_serializable(self) -> None:
        memory = Memory(system_prompt="SYS")
        memory.add_user("你好")
        json.dumps(memory.to_messages(), ensure_ascii=False)  # 不应抛异常


class TestSessionStore(TempDirTestCase):
    def test_session_store_roundtrip(self) -> None:
        store = SessionStore(os.path.join(self.root, "sessions"))
        session_id = store.new_id("chat")
        path = store.save(session_id, messages=[{"role": "user", "content": "hi"}], meta={"root": self.root})
        self.assertTrue(os.path.isfile(path))
        loaded = store.load(session_id)
        self.assertEqual(loaded["messages"][0]["content"], "hi")
        self.assertEqual(store.list_sessions(), [session_id])

    def test_missing_session_returns_none(self) -> None:
        store = SessionStore(os.path.join(self.root, "sessions"))
        self.assertIsNone(store.load("not-exist"))


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
