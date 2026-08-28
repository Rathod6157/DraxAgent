import time

from .visual_agent import visual_agent


class VisualBridge:
    """
    Connects Drax's normal command system
    to the closed-loop visual agent.

    Flow:

        Drax command
            ↓
        task / intent
            ↓
        VisualBridge
            ↓
        Observe → Act → Verify
    """

    def __init__(self):
        self.agent = visual_agent

    # ============================================================
    # CLICK
    # ============================================================

    def click(self, target):
        """
        Find a visible UI element and click it using vision.
        """

        if not target:
            return {
                "success": False,
                "error": "No visual target supplied."
            }

        print()
        print("👁️ DRAX VISUAL BRIDGE")
        print("Target:", target)

        result = self.agent.click(target)

        return result

    # ============================================================
    # RUN VISUAL TASK
    # ============================================================

    def run(self, instruction, target=None):
        """
        Run a closed-loop visual task.
        """

        if not instruction:
            return {
                "success": False,
                "error": "No visual instruction supplied."
            }

        print()
        print("👁️ DRAX VISUAL BRIDGE")
        print("Instruction:", instruction)

        result = self.agent.run(
            instruction,
            target=target
        )

        return result

    # ============================================================
    # OBSERVE
    # ============================================================

    def observe(self, instruction=None):
        """
        Capture and understand the current desktop.
        """

        return self.agent.observe(
            instruction=instruction
        )


# ================================================================
# SHARED INSTANCE
# ================================================================

visual_bridge = VisualBridge()