# המשחק שלי

היי! זה הקובץ שבו אתה מתאר לי (קלוד) איזה משחק מחשב אתה רוצה שאני אבנה לך.

אתה לא צריך לדעת קוד ולא צריך לדעת אנגלית - פשוט תכתוב כאן בעברית, בשפה שלך, מה שאתה רוצה שיהיה במשחק. תוכל לכתוב חופשי, לא חייבים למלא הכל, וזה גם בסדר אם משהו לא ברור - פשוט תכתוב כמה שאתה יודע ואני אשאל אותך שאלות על מה שחסר.

טיפ: תכתוב כאילו אתה מסביר למישהו שמעולם לא ראה את המשחק שבראש שלך.

---

## איך מפעילים את המשחק?

לחיצה כפולה על הקובץ **הפעל את המשחק.bat** בתיקייה. נפתח חלון של המשחק, ובו קודם מסך הוראות (לוחצים על מקש כלשהו כדי להמשיך לתפריט).

**מקשים:** חצים = תזוזה | רווח = להשתמש במה שנבחר בשורת המספרים (לירות / לשתות / לאכול) | 1-9 ו-0, Z/X או גלגלת העכבר = לבחור משבצת בשורה | E = התיק (כל מה שיש לך; גוררים עם העכבר לשורת המספרים) | Q = איסוף משאב/פתיחת תיבה/פתיחת שער (צריך מפתח)/מעבר לשלב הבא | T = שתיית תרופה | F = לאכול | Y = חנות וסדנה (קונים בכסף, או מכינים מחומרים שאספת תחמושת, ציוד, אוכל, מפתחות ותנור, ומבשלים בתנור - בלחיצת עכבר) | M = להדליק/לכבות קולות | R אחרי מוות = להתחיל מחדש | Esc = תפריט ראשי (משחק חדש, שמירה, טעינה, יציאה)

### Code structure (for Claude — keep to it)

`game.py` is only a launcher; all code lives in the `dungeons_and_guns/` package:

- `models/` — pydantic models. Catalog items (`Weapon`, `Gear`, ...) are frozen; world entities and `GameState` are mutable. Entities carry a `uid` so equal-looking objects stay distinct.
- `data/` — game content (weapons, ammo, gear, tools, resources + the material each one drops, workshop recipes, ranks, wheel). New items go here; `Catalog` validates cross-references at startup.
- `world/` — maze generation and level building.
- `systems/` — game rules as functions over `GameState`. **Must not import pygame.** Feedback goes through `state.say()` / `state.play()`; time comes from `state.now`.
- `ui/` — all drawing (world, HUD, shop, wheel, overlays, item icons). Reads state, never changes game rules.
- `saves.py` — save slots: `GameState` ↔ JSON in `saves/` (gitignored). Bump `SAVE_VERSION` when a `GameState` change breaks old files. All timestamps use the game clock `state.now` (advanced by the app, frozen in menus), never wall-clock ticks, so they survive save/load.
- `audio/` — synthesized sounds. `app.py` — window, screens (menu / save-load slots / game), input → `PlayerInput`, main loop. `controls.py` — key bindings.

Run tests with `python -m pytest tests` after changing rules; add a test for new systems logic.

---

## על מה המשחק?

*(למשל: משחק הרפתקאות, משחק ירי, משחק פתרון חידות, משחק מירוץ...)*
 המסלול הוא מבוך שאמור להיות לא קשה מדי, יש שם תיבות, ואויבים עם כלי נשק ברמות שונות של מרחק וסיכויי פגיעה בעזרת הקוביה

---

## איך המשחק נראה?

*(האם זה משחק דו-ממדי (כמו משחקים ישנים, מהצד) או תלת-ממדי? יש דמויות? אילו צבעים? יש רקע כמו יער, מבוך, חלל?)*
המשחק הוא דו מימדי מלמעלה אין דמויות יש איש אחד שקונה חפצים וכלי נשק הרקע הוא מבוך אבל זה לא רק רקע האיש הולך בתוך   המבוך ולא יכול לעבור בקירות
---

## מי הדמות הראשית?

*(איך קוראים לה? איך היא נראית? יש לה כוחות מיוחדים?)*
איש רגיל
---

## מה השחקן עושה במשחק?

*(איך זזים? קופצים? יורים? אוספים דברים? נלחמים באויבים?)*
זזים עם החיצים שבמקלדת יורים עם המקש רווח ולכל כלי נשק יש אחוז שונה של דיוק
 אם רוצים לאסוף משאבים פשוט לוחצים על CONTROL    ונאסף, חלק מהמשאבים צריכים כלי מיוחד לאסוף. למשל, עץ צריך מסור, וכל המכרות צריכים מקוש



## מי האויבים או המכשולים?

*(יש מפלצות? מלכודות? זמן שאוזל?)*
גם אנשים עם כל מיני כלי נשק
---

## איך מנצחים? איך מפסידים?

*(יש "חיים"? יש שלבים? מה קורה כשמגיעים לסוף?)*
יש קו מעל כל אויב/שחקן עם חיים.כלי נשק שונים מורידים כמות שונה של חיים. כשמסיימים את המבוך מסיימים שלב ועוברים למבוך - שלב - הבא.
---

## עוד רעיונות או דברים חשובים לי

*(כל דבר נוסף שחשוב לך שיהיה במשחק - כתוב כאן חופשי)*
במקש שיפט יהיה את החנות בחנות יהיה כלי נשק שונים אקדחים, רובי סער, תתי מקלע, מקלעים כבדים, רובי צלפים, ועוד. מכל סוג יהיו כמה כלים לדוגמה גלוק 19, M16 וכולי. בחנות יהיו גם גדלים שונים של תרופות להעלאת החיים.

---

כשתסיים לכתוב (גם אם רק חלק), תגיד לי "קרא את הקובץ" ואני אתחיל לבנות לך את המשחק, שלב אחרי שלב, ואסביר לך בעברית פשוטה מה אני עושה בדרך.
