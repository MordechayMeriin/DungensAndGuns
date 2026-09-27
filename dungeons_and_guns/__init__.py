# -*- coding: utf-8 -*-
"""מבוך ונשק - משחק מבוך דו-ממדי מלמעלה.

Package layout (logic never imports pygame; only ``ui``, ``audio`` and ``app`` do):

    config.py   - screen size, tile size, FPS
    models/     - pydantic models: catalog items, world entities, game state
    data/       - the actual content (weapons, ammo, gear, tools, ...) as a validated Catalog
    world/      - maze generation and level building
    systems/    - game rules operating on GameState (combat, shop, crates, wheel, ...)
    ui/         - everything drawn on screen (icons, world, HUD, shop, overlays)
    audio/      - synthesized sound effects
    app.py      - pygame window, input mapping and the main loop
"""
