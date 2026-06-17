"""Tests for the remote-LLM move suggestion in :mod:`game2048.llm`.

These never hit the network: the Anthropic client is replaced with a fake whose
``messages.create`` returns canned content blocks. This lets us exercise the
parsing and validation logic deterministically.
"""

import pytest
from anthropic.types import TextBlock

from game2048 import llm
from game2048.llm import LLMError, suggest_move_llm

BOARD = [
    [2, 4, 8, 16],
    [None, 4, 8, 32],
    [2, None, 16, 64],
    [4, 8, 32, 128],
]
VALID_MOVES = ['left', 'right', 'up', 'down']


def _install_fake_anthropic(monkeypatch, content_blocks):
    """Replace ``llm.Anthropic`` with a fake returning the given content blocks."""

    class FakeMessages:
        def create(self, **kwargs):
            return type('FakeMessage', (), {'content': content_blocks})()

    class FakeAnthropic:
        def __init__(self, *args, **kwargs):
            self.messages = FakeMessages()

    monkeypatch.setenv('ANTHROPIC_API_KEY', 'test-key')
    monkeypatch.setattr(llm, 'Anthropic', FakeAnthropic)


def _text_block(text: str) -> TextBlock:
    """Build a real ``TextBlock`` (so the module's isinstance check passes)."""
    return TextBlock(type='text', text=text)


def test_suggest_move_returns_valid_direction(monkeypatch):
    _install_fake_anthropic(monkeypatch, [_text_block('{"direction": "left"}')])
    assert suggest_move_llm(BOARD, VALID_MOVES) == 'left'


def test_suggest_move_skips_non_text_blocks(monkeypatch):
    # A leading non-text block (e.g. a thinking block) must be ignored.
    thinking_block = type('FakeThinkingBlock', (), {'type': 'thinking'})()
    _install_fake_anthropic(
        monkeypatch,
        [thinking_block, _text_block('{"direction": "up"}')],
    )
    assert suggest_move_llm(BOARD, VALID_MOVES) == 'up'


def test_unparseable_response_raises(monkeypatch):
    _install_fake_anthropic(monkeypatch, [_text_block('not json at all')])
    with pytest.raises(LLMError):
        suggest_move_llm(BOARD, VALID_MOVES)


def test_missing_direction_key_raises(monkeypatch):
    _install_fake_anthropic(monkeypatch, [_text_block('{"move": "left"}')])
    with pytest.raises(LLMError):
        suggest_move_llm(BOARD, VALID_MOVES)


def test_illegal_direction_is_rejected(monkeypatch):
    # The model returns a syntactically valid but illegal move for this board.
    _install_fake_anthropic(monkeypatch, [_text_block('{"direction": "down"}')])
    with pytest.raises(LLMError):
        suggest_move_llm(BOARD, ['left', 'right'])


def test_no_text_block_raises(monkeypatch):
    thinking_block = type('FakeThinkingBlock', (), {'type': 'thinking'})()
    _install_fake_anthropic(monkeypatch, [thinking_block])
    with pytest.raises(LLMError):
        suggest_move_llm(BOARD, VALID_MOVES)
