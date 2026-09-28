# -*- coding: utf-8 -*-
"""משימות: בתחילת כל שלב (אם אין משימה פתוחה) מקבלים משימה עם שעון.

מצליחים בזמן - מקבלים כסף ונקודות דרגה. נגמר הזמן - המשימה נכשלת, ובשלב הבא יש חדשה.
משימה לא נגמרת כשעוברים שלב: אפשר להמשיך לאסוף לה גם בשלב הבא, כל עוד יש זמן.
"""

import random

from ..models import GameState, Mission, MissionKind
from . import ranks

MINUTE_MS = 60_000

# מה כתוב על כל סוג משימה (בשורה על המסך)
TEXTS = {
    MissionKind.KILL: "חסל %d אויבים",
    MissionKind.HARVEST: "אסוף %d משאבים",
    MissionKind.CRATES: "פתח %d תיבות",
    MissionKind.EXIT: "סיים את השלב",
}


def mission_text(mission: Mission) -> str:
    text = TEXTS[mission.kind]
    return text % mission.goal if "%d" in text else text


def time_left(state: GameState) -> int:
    """כמה מילישניות נשארו למשימה (0 אם אין משימה)."""
    return max(0, state.mission.deadline - state.now) if state.mission else 0


def assign(state: GameState) -> None:
    """משימה חדשה לשלב - רק אם אין כבר משימה פתוחה. ככל שהשלב גבוה, המשימה גדולה יותר."""
    if state.mission is not None:
        return
    n = state.level.number
    kind = random.choice(list(MissionKind))
    match kind:
        case MissionKind.KILL:
            goal = min(3 + n // 2, 10)
            minutes = 4 + goal
        case MissionKind.HARVEST:
            goal = min(3 + n // 3, 8)
            minutes = 3 + goal
        case MissionKind.CRATES:
            goal = min(2 + n // 3, 5)
            minutes = 3 + goal
        case _:
            goal = 1
            minutes = 4 + n // 2
    state.mission = Mission(kind=kind, goal=goal, deadline=state.now + minutes * MINUTE_MS,
                            money=40 * goal + 20 * n + (60 if kind == MissionKind.EXIT else 0),
                            points=8 * goal + 2 * n + (10 if kind == MissionKind.EXIT else 0))


def progress(state: GameState, kind: MissionKind) -> None:
    """קרה משהו שנחשב למשימה (אויב חוסל, משאב נאסף...). אם המשימה הושלמה - מקבלים פרס."""
    mission = state.mission
    if mission is None or mission.kind != kind or state.now > mission.deadline:
        return
    mission.progress += 1
    if mission.progress < mission.goal:
        return
    state.mission = None
    state.inventory.money += mission.money
    promoted = ranks.add_points(state, mission.points)
    state.play("level")
    state.say("השלמת את המשימה! +%d כסף +%d נקודות" % (mission.money, mission.points))
    if promoted:
        ranks.announce_promotion(state, promoted)


def update(state: GameState) -> None:
    """כל פריים: האם נגמר הזמן."""
    if state.mission is not None and state.now > state.mission.deadline:
        state.mission = None
        state.play("no")
        state.say("נגמר הזמן - המשימה נכשלה. בשלב הבא תקבל משימה חדשה")
