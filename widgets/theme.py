"""
DraxAgent UI Theme
==================

Central visual system for the Drax desktop application.

This file contains visual constants only.
No application logic belongs here.

Design goals:
    Clean
    Restrained
    Modern
    Consistent
    Smooth
    Professional
"""

# ============================================================
# WINDOW
# ============================================================

WINDOW_BACKGROUND = "#17181C"
WINDOW_SURFACE = "#1B1D22"
WINDOW_SURFACE_ALT = "#202228"

WINDOW_RADIUS = 18


# ============================================================
# ACCENT
# ============================================================

ACCENT = "#4C8DFF"
ACCENT_HOVER = "#69A0FF"
ACCENT_PRESSED = "#3978E8"

ACCENT_SOFT = "#263653"
ACCENT_GLOW = "#4C8DFF"


# ============================================================
# SEMANTIC COLORS
# ============================================================

SUCCESS = "#59D98E"
ERROR = "#FF6B6B"
WARNING = "#F7C948"
INFO = "#4C8DFF"


# ============================================================
# TEXT
# ============================================================

TEXT = "#FFFFFF"
TEXT_PRIMARY = "#F5F6F8"

TEXT_SECONDARY = "#A6ABB5"
TEXT_MUTED = "#6F7582"
TEXT_DISABLED = "#4F535C"


# ============================================================
# CHAT
# ============================================================

CHAT_BACKGROUND = "#17181C"

CHAT_SURFACE = "#1C1E23"
CHAT_SURFACE_HOVER = "#21242A"

USER_BUBBLE = "#3478F6"
USER_BUBBLE_HOVER = "#3D82FF"
USER_TEXT = "#FFFFFF"

DRAX_BUBBLE = "#26282E"
DRAX_BUBBLE_HOVER = "#2B2E35"
DRAX_TEXT = "#F2F2F2"

STATUS_BUBBLE = "#20242B"


# ============================================================
# CONVERSATION LAYOUT
# ============================================================

# The conversation should use most of the available window
# without becoming edge-to-edge.
#
# Previous value:
#     1180
#
# New value:
#     1500
#
# This dramatically reduces the excessive empty space on
# large/maximized windows while keeping the conversation
# centered and visually contained.

CONVERSATION_MAX_WIDTH = 1500

# Inner breathing room between the conversation column
# and the actual message rows.

CONVERSATION_SIDE_PADDING = 24


# ============================================================
# CHAT MESSAGE WIDTHS
# ============================================================

USER_BUBBLE_MIN_WIDTH = 260
USER_BUBBLE_MAX_WIDTH = 620

DRAX_BUBBLE_MIN_WIDTH = 420
DRAX_BUBBLE_MAX_WIDTH = 720


# ============================================================
# CHAT BUBBLES
# ============================================================

BUBBLE_RADIUS = 18

BUBBLE_PADDING = 12

BUBBLE_MARGIN = 8

MAX_BUBBLE_WIDTH = 720

BUBBLE_VERTICAL_PADDING = 8
BUBBLE_HORIZONTAL_PADDING = 18


# ============================================================
# MESSAGE METADATA
# ============================================================

TIMESTAMP_COLOR = "#6F7582"

TIMESTAMP_SIZE = 10

CHAT_SIZE = 14

CHAT_LINE_HEIGHT = 1.25


# ============================================================
# STATUS BAR
# ============================================================

STATUS_BACKGROUND = "#22252C"
STATUS_BORDER = "#333844"

STATUS_HOVER = "#292C34"

STATUS_SIZE = 13


# ============================================================
# INPUT BAR
# ============================================================

INPUT_BACKGROUND = "#22252C"
INPUT_BACKGROUND_FOCUS = "#252932"

INPUT_BORDER = "#393E49"
INPUT_BORDER_HOVER = "#464C59"
INPUT_FOCUS = "#4C8DFF"

INPUT_TEXT = "#FFFFFF"
PLACEHOLDER = "#8A909A"

INPUT_RADIUS = 18


# ============================================================
# BUTTONS
# ============================================================

BUTTON_BACKGROUND = ACCENT
BUTTON_HOVER = ACCENT_HOVER
BUTTON_PRESSED = ACCENT_PRESSED

BUTTON_TEXT = "#FFFFFF"

BUTTON_DISABLED = "#343840"


# ============================================================
# SIDEBAR / PANELS
# ============================================================

PANEL_BACKGROUND = "#1B1D22"
PANEL_SURFACE = "#202228"

PANEL_BORDER = "#2D3037"

PANEL_HOVER = "#252830"

PANEL_ACTIVE = "#29344A"


# ============================================================
# DIVIDERS
# ============================================================

DIVIDER = "#292C33"
DIVIDER_STRONG = "#333740"


# ============================================================
# ACTIVITY CARD
# ============================================================

ACTIVITY_BACKGROUND = "#20242B"
ACTIVITY_BORDER = "#333844"

ACTIVITY_TITLE = TEXT
ACTIVITY_SECONDARY = TEXT_SECONDARY

ACTIVITY_MUTED = TEXT_MUTED


# ============================================================
# WINDOW TITLE / HEADER
# ============================================================

TITLE_SIZE = 28
SUBTITLE_SIZE = 12

HEADER_HEIGHT = 64


# ============================================================
# SPACING
# ============================================================

WINDOW_PADDING = 18

SECTION_SPACING = 12

CHAT_SPACING = 8

HEADER_SPACING = 8

INPUT_SPACING = 12


# ============================================================
# LOGO / IDENTITY
# ============================================================

# Drax's visual identity.
#
# The actual logo artwork is supplied by the UI/logo widget.

LOGO_SIZE = 34
LOGO_SMALL_SIZE = 26
LOGO_LARGE_SIZE = 48

LOGO_RADIUS = 10

LOGO_BACKGROUND = ACCENT

LOGO_GLOW = ACCENT_SOFT

APP_NAME = "Drax"

APP_SUBTITLE = "Your desktop AI companion"


# ============================================================
# ICONS
# ============================================================

# Drax uses the actual geometric logo asset.
# No robot emoji.

DRAX_ICON = "assets/drax_logo.png"

USER_ICON = "👤"

SUCCESS_ICON = "✓"
ERROR_ICON = "!"
WARNING_ICON = "!"
STATUS_ICON = "●"

THINKING_ICON = ""


# ============================================================
# THINKING / ACTIVITY
# ============================================================

THINKING_TEXT = "Drax is thinking"

THINKING_DOT_INTERVAL = 420

THINKING_PULSE_DURATION = 1100

THINKING_OPACITY_MIN = 0.45
THINKING_OPACITY_MAX = 1.0


# ============================================================
# ANIMATION
# ============================================================

FADE_DURATION = 180

FADE_FAST = 120
FADE_NORMAL = 180
FADE_SLOW = 260

SLIDE_DURATION = 200

SLIDE_FAST = 140
SLIDE_NORMAL = 200
SLIDE_SLOW = 280

HOVER_DURATION = 120

PANEL_DURATION = 180


# ============================================================
# WELCOME SCREEN
# ============================================================

WELCOME_TITLE_SIZE = 24

WELCOME_SUBTITLE_SIZE = 14

WELCOME_SUGGESTION_SIZE = 13

WELCOME_SPACING = 10


# ============================================================
# SCROLLING
# ============================================================

SCROLL_SINGLE_STEP = 24

SCROLL_ANIMATION_DURATION = 180


# ============================================================
# FONT WEIGHTS
# ============================================================

FONT_NORMAL = 400
FONT_MEDIUM = 500
FONT_SEMIBOLD = 600
FONT_BOLD = 700


# ============================================================
# THEME IDENTITY
# ============================================================

THEME_NAME = "Drax Dark"

THEME_VERSION = "2.1"