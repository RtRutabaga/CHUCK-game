"""Small dialogue edits requested after the browser-readiness pass."""

from src.systems.dialogue import DialogueSystem


def test_collided_desert_banner_is_only_a_visual_description() -> None:
    assert DialogueSystem().get("examine_castle_banner") == [
        "A red and gold banner."]


if __name__ == "__main__":
    test_collided_desert_banner_is_only_a_visual_description()
    print("All requested polish dialogue tests passed.")
