#!/usr/bin/env python3
"""
NERV // MAGI SUPERCOMPUTER SYSTEM v8.0
GEHIRN / NERV TOKYO-3 — CLASSIFIED LEVEL 5
"""
import curses,time,random,threading,math,textwrap
from collections import deque
from datetime import datetime

# ══ COLORS ══════════════════════════════════════════════════════════════════
C_ORANGE=1;C_DIM=2;C_AMBER=3;C_RED=4;C_GREEN=5
C_CYAN=6;C_WHITE=7;C_MAGENTA=8;C_ORANGE_BG=9;C_RED_BG=10

lock=threading.Lock()
run=True

# ══ WEAPON CATALOGUE ════════════════════════════════════════════════════════
WEAPON_CATALOGUE={
    "PALLET RIFLE":   {"dmg":(8,14), "acc":75,"rng":5,"ammo":24, "type":"RANGED", "desc":"Standard rifle. Reliable at range."},
    "PROG KNIFE":     {"dmg":(15,25),"acc":90,"rng":1,"ammo":99, "type":"MELEE",  "desc":"Progressive blade. High melee DMG."},
    "PROG SPEAR":     {"dmg":(20,35),"acc":70,"rng":2,"ammo":99, "type":"MELEE",  "desc":"Long-reach lance. Piercing."},
    "SHIELD":         {"dmg":(0,0),  "acc":100,"rng":0,"ammo":99,"type":"DEFENSE","desc":"AT field amplifier. Blocks 40%."},
    "POSITRON RIFLE": {"dmg":(40,60),"acc":55,"rng":8,"ammo":3,  "type":"RANGED", "desc":"Sniper. Pierces AT field."},
    "UMBILICAL":      {"dmg":(0,0),  "acc":100,"rng":0,"ammo":99,"type":"UTILITY","desc":"Power cable. Unlimited battery."},
    "N2 MINE":        {"dmg":(50,80),"acc":100,"rng":3,"ammo":1, "type":"BOMB",   "desc":"Area blast. Ignores AT field."},
    "GATLING GUN":    {"dmg":(5,10), "acc":65,"rng":4,"ammo":400,"type":"RANGED", "desc":"High fire rate. Burns ammo fast."},
    "PROG HAMMER":    {"dmg":(25,40),"acc":60,"rng":1,"ammo":99, "type":"MELEE",  "desc":"Slow but devastating."},
    "DUMMY PLUG":     {"dmg":(18,28),"acc":85,"rng":1,"ammo":99, "type":"SPECIAL","desc":"No hesitation. +20% ATK."},
}
WEP_KEYS=list(WEAPON_CATALOGUE.keys())

# ══ PILOTS ══════════════════════════════════════════════════════════════════
PILOTS={
    "IKARI SHINJI": {"sync_base":94.0,"personality":"HESITANT","color":C_GREEN,
                     "stat_atk":0.9,"stat_def":1.0,"note":"Berserk risk at >97% sync."},
    "AYANAMI REI":  {"sync_base":71.0,"personality":"STOIC",   "color":C_AMBER,
                     "stat_atk":0.85,"stat_def":1.2,"note":"High DEF. Quiet but resilient."},
    "SORYU ASUKA":  {"sync_base":82.0,"personality":"FIERCE",  "color":C_RED,
                     "stat_atk":1.3, "stat_def":0.8,"note":"30% more ATK. Fragile."},
    "NAGISA KAWORU":{"sync_base":99.9,"personality":"CALM",    "color":C_CYAN,
                     "stat_atk":1.1, "stat_def":1.1,"note":"Balanced. High sync base."},
    "IKARI YUI":    {"sync_base":99.9,"personality":"UNKNOWN", "color":C_WHITE,
                     "stat_atk":1.5, "stat_def":1.5,"note":"CLASSIFIED. All stats max."},
}
PILOT_KEYS=list(PILOTS.keys())

# ══ EVA UNITS ═══════════════════════════════════════════════════════════════
eva_units={
    "EVA-00":{"pilot":"AYANAMI REI",  "status":"STANDBY","unit_col":C_AMBER,
              "sync":71.2,"pwr":88.0,"atf":65.0,"armor":91.0,"lcl":100.0,
              "pos":(5,8),"deployed":False,
              "loadout":["PROG SPEAR","SHIELD","PROG KNIFE"],
              "ammo":{"PROG SPEAR":99,"SHIELD":99,"PROG KNIFE":99},
              "active_weapon":0,"battle_hp":100,"battle_max_hp":100,
              "note":"Prototype. Restraints nominal."},
    "EVA-01":{"pilot":"IKARI SHINJI","status":"ACTIVE", "unit_col":C_GREEN,
              "sync":98.4,"pwr":61.0,"atf":79.0,"armor":74.0,"lcl":100.0,
              "pos":(12,8),"deployed":True,
              "loadout":["PALLET RIFLE","PROG KNIFE","UMBILICAL"],
              "ammo":{"PALLET RIFLE":24,"PROG KNIFE":99,"UMBILICAL":99},
              "active_weapon":0,"battle_hp":100,"battle_max_hp":100,
              "note":"Test-type. Berserk risk ELEVATED."},
    "EVA-02":{"pilot":"SORYU ASUKA", "status":"CRITICAL","unit_col":C_RED,
              "sync":23.1,"pwr":18.0,"atf": 8.0,"armor":22.0,"lcl":74.0,
              "pos":(19,8),"deployed":False,
              "loadout":["GATLING GUN","PROG KNIFE"],
              "ammo":{"GATLING GUN":400,"PROG KNIFE":99},
              "active_weapon":0,"battle_hp":40,"battle_max_hp":100,
              "note":"!! CORE BREACH RISK. Eject pilot."},
}
EVA_KEYS=list(eva_units.keys())

FIELD_W=32;FIELD_H=16
TERRAIN={(10,12):"▓",(11,12):"▓",(12,12):"▓",(18,10):"▓",(19,10):"▓",
         (5,14):"░",(6,14):"░",(7,14):"░",(0,15):"~",(1,15):"~",
         (28,15):"~",(29,15):"~",(30,15):"~",(31,15):"~"}

magi_votes={"CASPAR":  {"vote":"YES","role":"SCIENTIST","desc":"Logic / Science"},
            "MELCHIOR":{"vote":"YES","role":"MOTHER",   "desc":"Emotion / Instinct"},
            "BALTHASAR":{"vote":"WAIT","role":"WOMAN",  "desc":"Ethics / Morality"}}
magi_cycle=["YES","NO","WAIT"]; magi_names=["CASPAR","MELCHIOR","BALTHASAR"]
selected_magi=0

# ══ ANGELS ══════════════════════════════════════════════════════════════════
ANGELS=[
    {"class":"SACHIEL","pattern":"BLUE","hp":120,"max_hp":120,"atk_min":8,"atk_max":18,
     "atf":60,"desc":"Third Angel. Energy blasts, core regen.",
     "abilities":["ENERGY_BLAST","AT_FIELD","CORE_REGEN"]},
    {"class":"SHAMSHEL","pattern":"BLUE","hp":100,"max_hp":100,"atk_min":12,"atk_max":22,
     "atf":40,"desc":"Fourth Angel. Whip tentacles. Fast.",
     "abilities":["WHIP_LASH","DOUBLE_STRIKE","AT_FIELD"]},
    {"class":"RAMIEL","pattern":"BLUE","hp":200,"max_hp":200,"atk_min":30,"atk_max":50,
     "atf":90,"desc":"Fifth Angel. Particle cannon. Stationary.",
     "abilities":["PARTICLE_CANNON","AT_FIELD","DRILL"]},
    {"class":"GAGHIEL","pattern":"BLUE","hp":150,"max_hp":150,"atk_min":15,"atk_max":30,
     "atf":55,"desc":"Sixth Angel. Sea-based. Aquatic.",
     "abilities":["BITE_ATTACK","WATER_SLAM","AT_FIELD","DOUBLE_STRIKE"]},
]
angel_idx=0
angel={**ANGELS[0],"alive":True,"bearing":247,"range_km":2.4,
       "pos":(24,4),"status_effect":None,"charge":0,"angel_stun":0}

alerts=deque([("CRIT","ANGEL PATTERN BLUE CONFIRMED"),
              ("CRIT","EVA-02 SYNC CRITICAL — 23.1%"),
              ("WARN","BALTHASAR: ANOMALY DETECTED"),
              ("OK","EVA-01 ACTIVE ON FIELD"),
              ("INFO","MAGI CONSENSUS: 2/3 ACHIEVED")],maxlen=30)
alert_pool=[("CRIT","CORE BREACH IMMINENT"),("WARN","N2 MINE AUTHORIZED"),
            ("INFO","UMBILICAL CABLE LIMIT"),("OK","S/R RISING"),
            ("WARN","PWR RESERVE 3 MIN"),("CRIT","AT FIELD EVOLVING"),
            ("INFO","SEELE COMM INCOMING"),("WARN","LCL CONTAMINATION"),
            ("OK","NERV SHIELD ACTIVE"),("CRIT","DUMMY SYSTEM ARMED"),
            ("WARN","BERSERK THRESHOLD NEAR"),("CRIT","3RD IMPACT: 34%"),
            ("OK","AT FIELD NEUTRALIZED"),("CRIT","PATTERN BLUE — NEW"),
            ("WARN","ADAM SIGNAL DETECTED"),("INFO","GEHIRN PURGE"),
            ("WARN","PILOT PSYCHOLOGICAL EVALUATION OVERDUE"),
            ("INFO","GEHIRN ARCHIVE ACCESS: LEVEL 4"),
            ("CRIT","EVANGELION UNIT GOING BERSERK"),
            ("WARN","TERMINAL DOGMA: UNAUTHORIZED ACCESS"),
            ("OK","CASPAR CONSENSUS CONFIRMED"),
            ("INFO","MAGI NETWORK SYNC: 99.9%"),
            ("CRIT","ANGEL CORE DETECTED IN GRID SECTOR 7"),
            ("WARN","UMBILICAL BRIDGE: PARTIAL DAMAGE"),
            ("OK","EVA DEPLOYMENT ELEVATOR: READY"),
            ("INFO","DR AKAGI: MAGI CALIBRATION COMPLETE"),
]

# ── NERV Alert Level (like the show) ─────────────────────────────────────
ALERT_LEVEL=1  # 1=normal, 2=standby, 3=battle stations
ALERT_NAMES={1:"NORMAL",2:"STAND BY",3:"BATTLE STATIONS"}

# ── Pilot battle quotes ────────────────────────────────────────────────────
PILOT_QUOTES={
    "IKARI SHINJI":{
        "attack":["I... I can do this.","Don't think. Just fight!","For everyone's sake!"],
        "hit":   ["Ugh! EVA-01 taking damage!","H-hold on!","I won't give up!"],
        "win":   ["I... I did it?","It stopped moving.","Is it over...?"],
        "berserk":["I can't... I can't stop it!","Unit 01 is moving on its own!"],
    },
    "AYANAMI REI":{
        "attack":["Initiating attack sequence.","Engaging target.","AT field penetrated."],
        "hit":   ["...","Armor integrity falling.","Pain is irrelevant."],
        "win":   ["Target neutralized.","Mission complete.","..."],
        "berserk":["...I feel something."],
    },
    "SORYU ASUKA":{
        "attack":["Out of my way!","I'll show you what a real pilot can do!","AMAZING!"],
        "hit":   ["What?! My EVA got hit?!","Don't underestimate me!","AAAUGH!"],
        "win":   ["Of course I won. Did you expect anything less?","Too easy!","Anta baka?"],
        "berserk":["Mama... mama look at me..."],
    },
    "NAGISA KAWORU":{
        "attack":["This is the will of man.","Interesting.","As calculated."],
        "hit":   ["Acceptable.","The outcome was foreseen.","Curious."],
        "win":   ["I return to you now, Lilith.","This ends as it must.","..."],
        "berserk":["The AT field... the wall of the heart."],
    },
    "IKARI YUI":{
        "attack":["I will protect everyone.","Shinji... I'm here.","Don't be afraid."],
        "hit":   ["...","This pain... I can bear it.","I won't fall here."],
        "win":   ["It's alright now.","This is what I chose.","Shinji... grow up."],
        "berserk":["I am always with you."],
    },
}
comm_log=deque([
    ("MISATO","Shinji, advance on the angel now!"),
    ("SHINJI","Y-yes ma'am... I'll try."),
    ("RITSUKO","AT field holding at 80%."),
    ("MISATO","Asuka — status report!"),
    ("ASUKA","EVA-02 IS DOWN! Can't move!"),
    ("RITSUKO","Sync rate dropping. Stand by."),
    ("GENDO","Proceed as planned.")],maxlen=40)

CMD_DB={
    "help":[("MAGI","━━ NERV COMMAND SYSTEM ━━"),
            ("MAGI","UNITS: deploy/recall/eject <unit>"),
            ("MAGI","       pilot <unit> <n>  swap <u1> <u2>"),
            ("MAGI","       repair/boost <unit>"),
            ("MAGI","COMBAT: fire/advance/move <unit>"),
            ("MAGI","        kill angel / revive angel"),
            ("MAGI","        bearing <deg>  range <km>"),
            ("MAGI","INTEL:  status report quote pilots angels"),
            ("MAGI","        seele adam lilith third"),
            ("MAGI","        kaji rei asuka impact berserk"),
            ("MAGI","ALERT:  alert <1/2/3>  emergency  dummy"),
            ("MAGI","        sync up  lcl self"),
            ("MAGI","GAMES:  game attack / sync / nerv"),
            ("MAGI","MISC:   clear"),
            ("MAGI","━━━━━━━━━━━━━━━━━━━━━━━━━━")],
    "status":[("RITSUKO","All MAGI online. EVA-01 active."),
              ("RITSUKO","EVA-02 critical. Eject recommended."),
              ("MISATO","Angel: 2.4km bearing 247 closing.")],
    "report":[("HYUGA","MAGI uptime 99.97%. All nominal."),
              ("IBUKI","EVA-01 exceeding sync thresholds."),
              ("FUYUTSUKI","SEELE filed another inquiry."),
              ("RITSUKO","Dummy System ready. Don't use it."),
              ("HYUGA","Angel ETA: 4 minutes.")],
    "quote":[("SHINJI","I mustn't run away..."),
             ("ASUKA","How pathetic. I'll do it myself."),
             ("KAWORU","I love you, Shinji."),
             ("GENDO","You are here because I called for you."),
             ("SEELE","Man fears the darkness..."),
             ("REI","I am not a doll."),
             ("RITSUKO","Science has no heart.")],
    "seele":[("SEELE","SOUND ONLY."),
             ("SEELE","The scenario proceeds on schedule."),
             ("SEELE","Third Impact must not be impeded."),
             ("GENDO","Understood."),("MAGI","** SEELE COMM LOGGED **")],
    "lcl":[("RITSUKO","LCL nominal in EVA-00/01."),
           ("RITSUKO","EVA-02 LCL at 74%. Contamination?"),
           ("MISATO","Eject Asuka if it drops below 60.")],
    "self":[("MAGI","CASPAR    — 100%. Normal."),
            ("MAGI","MELCHIOR  — 100%. Normal."),
            ("MAGI","BALTHASAR — minor deviation flagged.")],
    "impact":[("RITSUKO","Third Impact probability: 34.7%"),
              ("MAGI","CASPAR: Acceptable."),
              ("MAGI","MELCHIOR: Acceptable."),
              ("MAGI","BALTHASAR: NOT acceptable."),("GENDO","...")],
    "berserk":[("MAGI","!! BERSERK THRESHOLD ANALYSIS:"),
               ("RITSUKO","EVA-01 sync 98.4% — boundary."),
               ("RITSUKO","Personality contamination possible."),
               ("MISATO","It'll fight alone. I know."),
               ("RITSUKO","That's what worries me.")],
    "kaji":[("KAJI","Hey Misato. Long time no see."),
            ("MISATO","Kaji... what are you doing here?"),
            ("KAJI","Adam is secured. For now."),
            ("MAGI","** KAJI COMM FLAGGED BY CASPAR **")],
    "rei":[("REI","..."),("REI","I am not a doll."),
           ("REI","What would you like me to say?"),
           ("RITSUKO","Rei, please respond."),("REI","...Understood.")],
    "asuka":[("ASUKA","I am the best pilot NERV has!"),
             ("ASUKA","Stupid Shinji. Always in the way."),
             ("ASUKA","Fine! I'll do it alone!"),
             ("ASUKA","Mama... look at me, mama..."),
             ("MISATO","Asuka — focus. Please.")],
    "n2":[("MAGI","N2 MINE: AUTHORIZED."),
          ("MISATO","Buys 7 mins."),
          ("RITSUKO","EVA-01 must close in that window.")],
    "abort":[("MAGI","ABORT REQUIRES COMMANDER AUTH."),
             ("RITSUKO","Ikari-san hasn't responded."),("MISATO","Typical.")],
    "game attack":[("MAGI","COMBAT SIM: LAUNCHING"),("MAGI","WASD=move SPACE=fire F=power Z=shield")],
    "game sync":  [("MAGI","SYNC CALIB: LAUNCHING"),("MAGI","HOLD SPACE to raise sync")],
    "game nerv":  [("MAGI","TRIVIA: LAUNCHING"),("MAGI","Test your NERV knowledge")],
    "alert":      [("MAGI","CURRENT ALERT LEVEL:"),
                   ("HYUGA","Monitoring all sectors."),
                   ("IBUKI","MAGI tracking angel approach."),
                   ("MAGI","TYPE: alert 1/2/3 TO SET LEVEL")],
    "pilots":     [("RITSUKO","PILOT ROSTER:"),
                   ("RITSUKO","SHINJI  — EVA-01  SYNC~94%  HESITANT"),
                   ("RITSUKO","REI     — EVA-00  SYNC~71%  STOIC"),
                   ("RITSUKO","ASUKA   — EVA-02  SYNC~82%  FIERCE"),
                   ("RITSUKO","KAWORU  — ANY     SYNC~99%  CALM"),
                   ("RITSUKO","YUI     — ANY     SYNC~99%  CLASSIFIED")],
    "angels":     [("RITSUKO","KNOWN ANGEL ROSTER:"),
                   ("RITSUKO","SACHIEL  #03 — Energy blasts, core regen"),
                   ("RITSUKO","SHAMSHEL #04 — Whip tentacles, double strike"),
                   ("RITSUKO","RAMIEL   #05 — Particle cannon, EXTREMELY dangerous"),
                   ("RITSUKO","GAGHIEL  #06 — Aquatic, bite/water slam"),
                   ("MAGI","TYPE: revive angel to cycle to next angel")],
    "dummy":      [("GENDO","Activate the Dummy System."),
                   ("RITSUKO","Commander... are you certain?"),
                   ("GENDO","Do it."),
                   ("RITSUKO","...Yes, Commander."),
                   ("MAGI","DUMMY PLUG: ARMED"),
                   ("MAGI","WARNING: PILOT OVERRIDE IN EFFECT")],
    "adam":       [("KAJI","Adam... the first Angel. The source of all life."),
                   ("RITSUKO","It was discovered in Antarctica 15 years ago."),
                   ("RITSUKO","Contact with Adam caused Second Impact."),
                   ("GENDO","Adam's soul is contained within EVA-01."),
                   ("MAGI","** CLASSIFIED: LEVEL 5 CLEARANCE **")],
    "lilith":     [("RITSUKO","Lilith... the second Angel. Our true progenitor."),
                   ("RITSUKO","Crucified in Terminal Dogma. Has been there since—"),
                   ("GENDO","That's enough, Dr. Akagi."),
                   ("RITSUKO","...Of course, Commander."),
                   ("MAGI","** TERMINAL DOGMA ACCESS DENIED **")],
    "third":      [("RITSUKO","Third Impact would mean the end of humanity."),
                   ("RITSUKO","The merging of all souls into one."),
                   ("GENDO","Instrumentality."),
                   ("MAGI","PROBABILITY: 34.7% — RISING")],
    "sync up":    [("RITSUKO","Boosting sync ratios for all units."),
                   ("IBUKI","EVA-00: +5% EVA-01: +8% EVA-02: +3%"),
                   ("RITSUKO","Careful — EVA-01 is already near threshold.")],
    "emergency":  [("MAGI","!! EMERGENCY PROTOCOL ACTIVATED !!"),
                   ("HYUGA","All personnel to battle stations!"),
                   ("MISATO","This is not a drill! EVA units — launch!"),
                   ("MAGI","ALERT LEVEL 3 — BATTLE STATIONS")],
}

# ══ RUNTIME STATE ═══════════════════════════════════════════════════════════
cmd_buffer=""; cmd_history=[]; hist_idx=-1
reticle_ang=0; tick=0; run_time=0
seele_mode=False
game_mode=None   # None|"attack"|"sync"|"nerv"|"battle"
focus="comm"
FOCUS_ORDER=["comm","magi","field"]
field_sel=0
view_mode="main"  # "main"|"field"|"angel"
views=["main","field","angel"]   # V cycles only these; loadout/deploy entered separately

# ── deploy ────────────────────────────────────────────────────────────────
deploy_sel=0
deploy_choices={k:False for k in EVA_KEYS}
deploy_choices["EVA-01"]=True  # default

# ── loadout editor ────────────────────────────────────────────────────────
loadout_unit_idx=0   # index into EVA_KEYS
loadout_slot_sel=0   # slot 0-2
loadout_wep_sel=0    # index into WEP_KEYS

# ── battle ────────────────────────────────────────────────────────────────
battle={"active":False,"phase":"PLAYER_TURN","eva_party":[],
        "active_eva":0,"cursor":0,
        "actions":["ATTACK","AT FIELD","ITEM","SWITCH","FLEE"],
        "log":[],"turn":0,"anim_frames":0,
        "shield_turns":0,"sub_menu":None,"item_sel":0,
        "items":{"N2 MINE":1,"REPAIR KIT":2,"LCL BOOST":2}}

# ── attack arcade ─────────────────────────────────────────────────────────
atk={"cx":20,"cy":8,"angel_x":30.0,"angel_y":6.0,"angel_vx":1.2,"angel_vy":0.8,
     "shots":[],"score":0,"hits":0,"misses":0,"ammo":20,"hp":5,"eva_hp":100,
     "flash":0,"eva_flash":0,"msg":"WASD=move  SPACE=fire  F=power  Z=shield",
     "phase":"play","time_left":90,"xmax":55,"ymax":16,
     "power_shots":3,"shield_on":False,"shield_turns":0,"angel_charge":0,"level":1}

# ── sync calibration ──────────────────────────────────────────────────────
syn={"target":50.0,"current":50.0,"velocity":0.0,"wave_phase":0.0,
     "score":0,"streak":0,"best_streak":0,"rounds":0,"max_rounds":12,
     "msg":"Hold SPACE to raise sync. Match the target!",
     "phase":"play","history":[],"tolerance":8.0,"zone_ticks":0}

# ── trivia ────────────────────────────────────────────────────────────────
TRIVIA_QS=[
    ("NERV's motto?","GOD'S IN HIS HEAVEN",
     ["AT FIELD ABSOLUTE","GOD'S IN HIS HEAVEN","THIRD IMPACT NOW","MAGI CONSENSUS"]),
    ("Pilot of EVA-00?","AYANAMI REI",
     ["SORYU ASUKA","IKARI SHINJI","AYANAMI REI","NAGISA KAWORU"]),
    ("MAGI based on?","DR NAOKO AKAGI",
     ["GEHIRN AI","DR NAOKO AKAGI","ADAM DNA","LILITH SOUL"]),
    ("Angel #3 name?","SACHIEL",
     ["SHAMSHEL","SACHIEL","RAMIEL","GAGHIEL"]),
    ("Organization above NERV?","SEELE",
     ["GEHIRN","SEELE","UN SEC COUNCIL","WILLE"]),
    ("EVA-01 main color?","PURPLE",
     ["GREEN","RED","PURPLE","WHITE"]),
    ("Who says I mustn't run away?","SHINJI",
     ["ASUKA","SHINJI","REI","MISATO"]),
    ("Angel AT field type?","ABSOLUTE",
     ["RELATIVE","PARTIAL","ABSOLUTE","NONE"]),
    ("NERV HQ location?","TOKYO-3",
     ["TOKYO-1","TOKYO-3","TOKYO-2","MATSUSHIRO"]),
    ("Adam was found in?","ANTARCTIC",
     ["ANTARCTIC","ARCTIC","PACIFIC","TOKYO-2"]),
    ("Ritsuko's mother built?","MAGI",
     ["EVANGELION","MAGI","GEHIRN","LCL SYSTEM"]),
    ("SEELE monolith count?","12",
     ["7","9","12","15"]),
]
trv={"q_idx":0,"score":0,"answered":False,"selected":0,"result":"","phase":"play",
     "shuffled_qs":random.sample(TRIVIA_QS,len(TRIVIA_QS))}

# ══ HOSPITAL EASTER EGG — Episode 26 "video" player ═══════════════════════
# Renders ASCII-art "frames" + subtitles like a VHS tape playing in terminal.
# Each SCENE has: (duration_ticks, frame_fn, subtitle_lines, sfx)
# sfx: None | "static" | "flash" | "glitch"

# ── ASCII art frame builders ─────────────────────────────────────────────────
# Each returns list of (text_str, curses_attr) — one per row, exactly H rows.

def _make_rows(H,W,bg_attr=0):
    """Create H blank rows with given attribute."""
    return [[" "*(W-2), bg_attr] for _ in range(H)]

def _draw_str(rows,y,x,s,attr,W):
    """Safely draw string s into rows[y] at column x."""
    if y<0 or y>=len(rows):return
    row=rows[y][0]
    s=s[:max(0,W-2-x)]
    rows[y][0]=row[:x]+s+row[x+len(s):]

def _frame_static(H,W):
    chars="░▒▓ ▒░▒▓"
    attr=curses.color_pair(C_DIM)
    return [("".join(random.choice(chars) for _ in range(W-2)),attr) for _ in range(H)]

def _frame_black(H,W):
    return [(" "*(W-2), 0) for _ in range(H)]

def _frame_scanline(H,W):
    rows=[]
    for r in range(H):
        if r%3==0: rows.append(("─"*(W-2), curses.color_pair(C_DIM)|curses.A_DIM))
        else:      rows.append((" "*(W-2), 0))
    return rows

def _frame_void(H,W):
    """Pure white void."""
    attr=curses.color_pair(C_WHITE)|curses.A_REVERSE
    rows=[(" "*(W-2), attr) for _ in range(H)]
    # tiny center dot
    cr=H//2; cc=(W-2)//2
    row_txt=rows[cr][0]
    rows[cr]=(row_txt[:cc]+"·"+row_txt[cc+1:], attr)
    return rows

def _frame_classroom(H,W):
    """School classroom — blackboard + desks."""
    attr=curses.color_pair(C_DIM)
    rows=_make_rows(H,W-2,attr)  # use list for mutability
    w=W-2
    # Blackboard
    bw=min(40,w-8); bh=5; bx=(w-bw)//2; by=2
    if bx>=0 and by+bh<H:
        _draw_str(rows,by,  bx,"╔"+"═"*(bw-2)+"╗",attr,w)
        _draw_str(rows,by+bh,bx,"╚"+"═"*(bw-2)+"╝",attr,w)
        for r in range(by+1,by+bh):
            _draw_str(rows,r,bx,"║",attr,w)
            _draw_str(rows,r,bx+bw-1,"║",attr,w)
        msg="NERV PSYCHOLOGICAL EVALUATION"
        _draw_str(rows,by+2,bx+(bw-len(msg))//2,msg,curses.color_pair(C_AMBER)|curses.A_BOLD,w)
    # Desks
    step=max(8,w//5)
    for dx in range(3,w-6,step):
        dy=by+bh+3
        if dy+2<H:
            _draw_str(rows,dy,  dx,"┌───┐",attr,w)
            _draw_str(rows,dy+1,dx,"│   │",attr,w)
            _draw_str(rows,dy+2,dx,"└───┘",attr,w)
        if dy-2>=0:
            _draw_str(rows,dy-2,dx+2,"○",attr,w)
            _draw_str(rows,dy-1,dx+2,"│",attr,w)
    return [(r[0],r[1]) for r in rows]

def _frame_hospital_bed(H,W):
    """Hospital room with bed and figure."""
    attr=curses.color_pair(C_DIM)
    rows=_make_rows(H,W-2,attr)
    w=W-2
    # Room walls
    _draw_str(rows,0,0,"┌"+"─"*(w-2)+"┐",attr,w)
    _draw_str(rows,H-1,0,"└"+"─"*(w-2)+"┘",attr,w)
    for r in range(1,H-1):
        _draw_str(rows,r,0,"│",attr,w)
        _draw_str(rows,r,w-1,"│",attr,w)
    # Window top-right
    wx=w-14; wh=4
    if wx>0:
        _draw_str(rows,2,wx,"┌──────┐",attr,w)
        _draw_str(rows,2+wh,wx,"└──────┘",attr,w)
        for r in range(3,2+wh):
            _draw_str(rows,r,wx,"│ ░░░░ │",attr,w)
    # Bed
    bw=min(36,w-10); bx=(w-bw)//2; by=H//2-3; bh=6
    if by>1 and bx>1 and by+bh<H-1:
        _draw_str(rows,by,bx,"╔"+"═"*(bw-2)+"╗",attr,w)
        _draw_str(rows,by+bh,bx,"╚"+"═"*(bw-2)+"╝",attr,w)
        for r in range(by+1,by+bh):
            _draw_str(rows,r,bx,"║",attr,w)
            _draw_str(rows,r,bx+bw-1,"║",attr,w)
        # Pillow
        _draw_str(rows,by+1,bx+2,"[ pillow ]",attr,w)
        # Figure
        fa=curses.color_pair(C_AMBER)|curses.A_BOLD
        _draw_str(rows,by+2,bx+2,"  ○  ──────────────",fa,w)
        _draw_str(rows,by+3,bx+2," ╔╩╗ ███████████████",fa,w)
        _draw_str(rows,by+4,bx+2,"  ┴  ═══════════════",fa,w)
    # IV stand
    ivx=bx+bw+2
    if ivx<w-2:
        for r in range(by,by+4):
            _draw_str(rows,r,ivx,"│",attr,w)
        _draw_str(rows,by,ivx,"┬",attr,w)
        _draw_str(rows,by+4,ivx,"⊕",attr,w)
    return [(r[0],r[1]) for r in rows]

def _frame_silhouettes(H,W):
    """Three standing silhouettes on white background."""
    attr=curses.color_pair(C_WHITE)|curses.A_REVERSE
    rows=_make_rows(H,W-2,attr)
    w=W-2
    positions=[w//5, w//2, 4*w//5]
    for px in positions:
        if px<2 or px>=w-3:continue
        hy=H//2-4
        # Head
        _draw_str(rows,hy,px-1," ○ ",curses.color_pair(C_DIM)|curses.A_BOLD,w)
        # Body
        for ry in range(hy+1,min(H-3,hy+5)):
            _draw_str(rows,ry,px,"│",curses.color_pair(C_DIM),w)
        # Arms
        if hy+2<H-1:
            _draw_str(rows,hy+2,max(0,px-2),"─┤├─",curses.color_pair(C_DIM),w)
        # Legs
        if hy+5<H-1:
            _draw_str(rows,hy+5,max(0,px-1),"/ "+chr(92),curses.color_pair(C_DIM),w)
    return [(r[0],r[1]) for r in rows]

def _frame_congratulations(H,W,phase=0):
    """CONGRATULATIONS!"""
    attr=curses.color_pair(C_WHITE)|curses.A_REVERSE
    rows=_make_rows(H,W-2,attr)
    w=W-2
    msg_lines=["╔════════════════════════════════╗",
                "║  C O N G R A T U L A T I O N S  ║",
                "╚════════════════════════════════╝"]
    col=curses.color_pair(C_RED)|curses.A_BOLD if phase%4<2 else curses.color_pair(C_AMBER)|curses.A_BOLD
    by=H//2-2
    for i,ml in enumerate(msg_lines):
        bx=max(0,(w-len(ml))//2)
        _draw_str(rows,by+i,bx,ml,col,w)
    # Sparkles
    for fx in range(4,w-4,w//8):
        fy=random.randint(1,max(2,by-2))
        if fy<H-1:
            _draw_str(rows,fy,fx,"✦",curses.color_pair(C_AMBER)|curses.A_BOLD,w)
    return [(r[0],r[1]) for r in rows]

def _frame_end(H,W):
    """END OF EVANGELION title card."""
    attr=0
    rows=_make_rows(H,W-2,attr)
    w=W-2
    lines=["","[ END OF EVANGELION ]","",
           "  新世紀エヴァンゲリオン  ","",
           "  Neon Genesis Evangelion  "]
    sy=(H-len(lines))//2
    for i,ln in enumerate(lines):
        ry=sy+i
        if 0<ry<H-1 and ln:
            bx=max(0,(w-len(ln))//2)
            col=curses.color_pair(C_AMBER)|curses.A_BOLD if i==1 else curses.color_pair(C_DIM)|curses.A_BOLD
            _draw_str(rows,ry,bx,ln,col,w)
    return [(r[0],r[1]) for r in rows]

def _frame_glitch(H,W):
    """Glitch frame."""
    rows=[]
    for r in range(H):
        roll=random.random()
        if roll<0.25:
            s="".join(random.choice("▓▒░│─╬█") for _ in range(W-2))
            rows.append((s, curses.color_pair(random.choice([C_RED,C_DIM,C_CYAN]))))
        elif roll<0.4:
            rows.append(("█"*(W-2), curses.color_pair(C_DIM)|curses.A_DIM))
        else:
            rows.append((" "*(W-2), 0))
    return rows


# ── Scene list ────────────────────────────────────────────────────────────────
HOSP_SCENES=[
    # (duration_ticks, frame_fn_name, sfx)
    # sfx: "vhs"|"glitch"|"scanline"|"clean"|"done"
    (18,"static",    "vhs"),
    (12,"scanline",  "vhs"),
    (14,"static",    "vhs"),
    (10,"scanline",  "vhs"),
    (6, "black",     "clean"),
    (22,"void",      "clean"),
    (8, "glitch",    "glitch"),
    (24,"void",      "clean"),
    (20,"void",      "clean"),
    (6, "black",     "clean"),
    (5, "static",    "vhs"),
    (35,"classroom", "scanline"),
    (35,"classroom", "scanline"),
    (35,"classroom", "scanline"),
    (35,"classroom", "scanline"),
    (8, "black",     "clean"),
    (5, "static",    "vhs"),
    (35,"hospital_bed","scanline"),
    (35,"hospital_bed","scanline"),
    (35,"hospital_bed","scanline"),
    (8, "glitch",    "glitch"),
    (35,"silhouettes","clean"),
    (35,"silhouettes","clean"),
    (35,"silhouettes","clean"),
    (8, "black",     "clean"),
    (24,"void",      "clean"),
    (24,"void",      "clean"),
    (8, "black",     "clean"),
    (5, "flash",     "flash"),
    (28,"congrats",  "clean"),
    (5, "flash",     "flash"),
    (28,"congrats",  "clean"),
    (5, "flash",     "flash"),
    (8, "black",     "clean"),
    (24,"void",      "clean"),
    (8, "black",     "clean"),
    (5, "static",    "vhs"),
    (60,"end",       "clean"),
    (8, "black",     "clean"),
    (0, "end",       "done"),
]

hospital={"active":False,"scene":0,"tick":0,"phase":0,"done":False}


# ══ HOSPITAL RENDERER ════════════════════════════════════════════════════════
def draw_hospital(win,H,W):
    h=hospital
    win.erase()

    if h["scene"]>=len(HOSP_SCENES):
        h["done"]=True
        for r in range(H):sh(win,r,0," ",W,curses.color_pair(C_WHITE)|curses.A_REVERSE)
        msg="[ END OF EVANGELION — PRESS ANY KEY ]"
        sa(win,H//2,max(0,(W-len(msg))//2),msg,curses.color_pair(C_DIM))
        return

    dur,fname,sfx=HOSP_SCENES[h["scene"]]
    p=h["phase"]

    # Build frame
    BUILDERS={"static":_frame_static,"black":_frame_black,"scanline":_frame_scanline,
               "void":_frame_void,"classroom":_frame_classroom,
               "hospital_bed":_frame_hospital_bed,"silhouettes":_frame_silhouettes,
               "end":_frame_end,"glitch":_frame_glitch}
    if fname=="congrats": frame=_frame_congratulations(H,W,p)
    elif fname=="flash":
        fa=curses.color_pair(C_RED)|curses.A_REVERSE if p%2==0 else curses.color_pair(C_WHITE)|curses.A_REVERSE
        frame=[(" "*(W-2),fa)]*H
    elif fname in BUILDERS: frame=BUILDERS[fname](H,W)
    else: frame=[(" "*(W-2),0)]*H

    # Render each row cleanly
    for row in range(min(H-1,len(frame))):
        text,attr=frame[row]
        # Fill background
        sh(win,row,0," ",W,attr)
        # Draw text on top with same attr
        sa(win,row,0,text[:W-1],attr)

    # VHS overlay noise
    if sfx=="vhs":
        for _ in range(random.randint(2,6)):
            nr=random.randint(0,H-2)
            noise="".join(random.choice("▒░ ") for _ in range(random.randint(3,10)))
            nx=random.randint(0,max(0,W-len(noise)-1))
            try:win.addstr(nr,nx,noise,curses.color_pair(C_DIM)|curses.A_DIM)
            except:pass
    elif sfx=="glitch":
        for _ in range(random.randint(3,8)):
            gr=random.randint(0,H-2); gx=random.randint(0,max(0,W-8))
            gc=random.choice([C_RED,C_CYAN,C_AMBER])
            s="█"*random.randint(2,8)
            try:win.addstr(gr,gx,s,curses.color_pair(gc)|curses.A_BOLD)
            except:pass
    elif sfx=="scanline":
        for row in range(0,H-1,2):
            try:win.chgat(row,0,W-1,curses.A_DIM)
            except:pass

    # Progress bar at very bottom row
    total=len(HOSP_SCENES); cur=h["scene"]
    pct=int(cur/total*100)
    bw=min(48,W-16)
    bar="█"*int(bw*pct//100)+"░"*(bw-int(bw*pct//100))
    hud=f"▶ {bar} {pct:3d}% SPACE=skip ESC=exit"
    try:win.addstr(H-1,1,hud[:W-2],curses.color_pair(C_DIM)|curses.A_DIM)
    except:pass
    # Play indicator
    pi=" ▶ " if sfx!="done" else " ■ "
    pc=curses.color_pair(C_GREEN if sfx!="done" else C_RED)|curses.A_BOLD|curses.A_REVERSE
    try:win.addstr(0,0,pi,pc)
    except:pass
    ts=f"{cur:02d}:{h['tick']%60:02d}"
    try:win.addstr(0,4,ts,curses.color_pair(C_AMBER)|curses.A_BOLD|curses.A_REVERSE)
    except:pass


def tick_hospital():
    h=hospital
    if not h["active"] or h["done"]:return
    if h["scene"]>=len(HOSP_SCENES):
        h["done"]=True;return
    h["tick"]+=1
    h["phase"]=(h["phase"]+1)%256
    dur,fname,sfx=HOSP_SCENES[h["scene"]]
    if sfx=="done" or dur==0:return   # wait for keypress
    if h["tick"]>=dur:
        h["tick"]=0
        h["scene"]+=1
        if h["scene"]>=len(HOSP_SCENES):h["done"]=True


# ══ HELPERS ═════════════════════════════════════════════════════════════════
def sa(win,y,x,s,attr=0):
    try:
        h,w=win.getmaxyx()
        if y<0 or y>=h or x<0 or x>=w:return
        avail=w-x-1
        if avail<=0:return
        win.addstr(y,x,s[:avail],attr)
    except curses.error:pass

def sh(win,y,x,ch,n,attr=0):
    try:
        h,w=win.getmaxyx()
        if y<0 or y>=h or x>=w:return
        n=min(n,w-x-1)
        if n>0:win.addstr(y,x,ch*n,attr)
    except curses.error:pass

def cp(c,bold=False,dim=False):
    a=curses.color_pair(c)
    if bold:a|=curses.A_BOLD
    if dim:a|=curses.A_DIM
    return a

def mkbar(val,w,hi="█",lo="░"):
    f=max(0,min(w,int(val/100.0*w)))
    return hi*f+lo*(w-f)

def val_col(v):
    return C_GREEN if v>60 else C_AMBER if v>30 else C_RED

def magi_consensus():
    votes=[magi_votes[m]["vote"] for m in magi_names]
    yes=votes.count("YES");no=votes.count("NO")
    if yes>=2:return f"APPROVED {yes}/3",C_GREEN
    if no>=2:return f"REJECTED {no}/3",C_RED
    return "DEADLOCK 1/3",C_AMBER

def dist(ax,ay,bx,by):
    return math.sqrt((ax-bx)**2+(ay-by)**2)

def wlog(msg):
    """Add to battle log + comm"""
    battle["log"].append(msg)
    comm_log.append(("MAGI",msg))

# ══ BOX STYLES ══════════════════════════════════════════════════════════════
BS_HEAVY=("╔","╗","╚","╝","═","║")
BS_LIGHT=("┌","┐","└","┘","─","│")
BS_SEELE=("╔","╗","╚","╝","━","┃")
BS_GAME =("▛","▜","▙","▟","▀","▌")
BS_THIN =("╭","╮","╰","╯","─","│")   # rounded light

def box(win,y,x,h,w,title="",style=BS_HEAVY,tcol=C_ORANGE,bcol=C_DIM,sel=False):
    if w<3 or h<2:return
    TL,TR,BL,BR,HZ,VT=style
    bc=C_ORANGE if sel else bcol
    ba=cp(bc,bold=sel)
    sa(win,y,x,TL,ba);sa(win,y,x+w-1,TR,ba)
    sa(win,y+h-1,x,BL,ba);sa(win,y+h-1,x+w-1,BR,ba)
    sa(win,y,x+1,HZ*(w-2),ba);sa(win,y+h-1,x+1,HZ*(w-2),ba)
    for i in range(1,h-1):
        sa(win,y+i,x,VT,ba);sa(win,y+i,x+w-1,VT,ba)
    if title:
        t=f" {title} "
        tx=x+2
        sa(win,y,tx,t,cp(tcol,bold=True))
        # corner accents when selected
        if sel:
            sa(win,y,x,"◈",cp(C_ORANGE,bold=True))
            sa(win,y,x+w-1,"◈",cp(C_ORANGE,bold=True))

def sec(win,y,x,w,label,col=C_DIM):
    total=w-4
    if total<len(label)+2:return
    ll=(total-len(label)-2)//2
    rl=total-ll-len(label)-2
    sa(win,y,x+1,"─"*ll+f" {label} "+"─"*rl,cp(col))

def hp_bar(win,y,x,w,current,maximum,label=""):
    """Draw a compact health bar with percentage"""
    if maximum<=0:return
    pct=current/maximum*100
    bw=max(1,w-len(label)-8)
    vc=val_col(pct)
    if label:sa(win,y,x,label,cp(C_DIM))
    sa(win,y,x+len(label),mkbar(pct,bw),cp(vc))
    sa(win,y,x+len(label)+bw+1,f"{current:3d}/{maximum}",cp(vc,bold=True))

# ══ TOPBAR ══════════════════════════════════════════════════════════════════
def draw_topbar(win,W):
    win.erase()
    # Full-width orange background strip — like the real NERV UI
    sh(win,0,0," ",W,cp(C_ORANGE_BG))
    now=datetime.now().strftime("%H:%M:%S")
    date=datetime.now().strftime("%Y.%m.%d")
    berserks=[u for u,d in eva_units.items() if d.get("status")=="BERSERK"]

    # Left: NERV logo
    if berserks:
        sa(win,0,1,f"!! {berserks[0]} BERSERK !!",cp(C_RED,bold=True)|curses.A_BLINK)
    elif game_mode:
        sa(win,0,1,f"NERV // {game_mode.upper()} MODE",cp(C_WHITE,bold=True))
    else:
        sa(win,0,1,"NERV // MAGI v8 // GEHIRN // TOKYO-3",cp(C_WHITE,bold=True))

    # Center: MAGI status indicators (like image 1 — colored status blocks)
    cx2=W//2-15
    for name in magi_names:
        if cx2>=W-20:break
        v=magi_votes[name]["vote"]
        col=C_GREEN if v=="YES" else C_RED if v=="NO" else C_AMBER
        short=name[:3]
        # Draw as colored block
        sa(win,0,cx2,f"[{short}:{v[:1]}]",cp(col,bold=True))
        cx2+=9

    # View mode tag
    vm=f"[{view_mode.upper()}]"
    sa(win,0,cx2+2,vm,cp(C_WHITE,bold=True))

    # Alert level indicator
    al_col={1:C_GREEN,2:C_AMBER,3:C_RED}.get(ALERT_LEVEL,C_DIM)
    al_txt=f" LVL:{ALERT_LEVEL} {ALERT_NAMES.get(ALERT_LEVEL,'')} "
    al_x=max(cx2+12,W-len(al_txt)-len(f" {now} ")-2)
    sa(win,0,al_x,al_txt,cp(al_col,bold=True)|curses.A_REVERSE)
    # Right: time
    right=f" {now} "
    sa(win,0,W-len(right)-1,right,cp(C_WHITE,bold=True))

# ══ STATUSBAR ═══════════════════════════════════════════════════════════════
def draw_statusbar(win,W):
    win.erase()
    # Orange background strip matching topbar
    sh(win,0,0," ",W,cp(C_ORANGE_BG))

    if game_mode=="battle" and battle["eva_party"]:
        ek=battle["eva_party"][battle["active_eva"]];d=eva_units[ek]
        sa(win,0,0,
           f" !! BATTLE:{angel['class']} HP:{angel['hp']}/{angel['max_hp']}"
           f" | {ek} HP:{d['battle_hp']}/{d['battle_max_hp']}"
           f" | T:{battle['turn']} | ↑↓:action 1/2/3:weapon ENTER:go",
           cp(C_WHITE,bold=True));return
    if game_mode=="attack":
        sa(win,0,0,
           f" ARCADE | HP:{atk['eva_hp']}%  AMM:{atk['ammo']}"
           f"  SCORE:{atk['score']}  T:{atk['time_left']}s  PWR:{atk['power_shots']}  | ESC:exit",
           cp(C_WHITE,bold=True));return
    if game_mode=="sync":
        sa(win,0,0,
           f" SYNC | SCORE:{syn['score']} STREAK:{syn['streak']}"
           f" ROUND:{syn['rounds']}/{syn['max_rounds']} | SPACE:raise ESC:exit",
           cp(C_WHITE,bold=True));return
    if game_mode=="nerv":
        sa(win,0,0,
           f" TRIVIA | {trv['score']}/{len(trv['shuffled_qs'])}"
           f" | ↑↓:select ENTER:confirm ESC:exit",
           cp(C_WHITE,bold=True));return
    # Normal — show focus-specific controls
    focus_hints={
        "comm": "ENTER:send  ↑↓:hist  ESC:clear  TAB→MAGI  — V:cycle-view works always",
        "magi": "◄►/WASD:pick  ENTER/SPC:vote  S:seele  V:view  TAB→FIELD  Q:quit",
        "field":"WASD:move  SPACE:fire  B:deploy  L:loadout  []:unit  V:view  TAB→COMM  Q:quit",
    }
    threat="◈ "+angel["class"] if angel["alive"] else "CLEAR"
    tcol=C_WHITE  # white on orange bg
    hint=focus_hints.get(focus,"")
    ang_col=C_WHITE  # all white on orange bg
    sa(win,0,1,f"THREAT:{threat} ",cp(C_WHITE,bold=True))
    sep=9+len(threat)
    sa(win,0,sep,f"| [{focus.upper()}] {hint}",cp(C_WHITE,bold=False))

# ══ EVA PANEL ═══════════════════════════════════════════════════════════════
def draw_eva_panel(win,H,W):
    win.erase()
    box(win,0,0,H,W,"EVA UNITS",bcol=C_ORANGE)
    y=1
    for unit,d in eva_units.items():
        if y>=H-1:break
        scol={"ACTIVE":C_GREEN,"STANDBY":C_AMBER,"CRITICAL":C_RED,
              "BERSERK":C_RED}.get(d["status"],C_ORANGE)
        # header row
        dep="▶" if d["deployed"] else "·"
        badge=d["status"][:7]
        sa(win,y,1,f"{dep} {unit}",cp(d["unit_col"],bold=True))
        sa(win,y,W-len(badge)-2,f"[{badge}]",cp(scol,bold=True));y+=1
        if y>=H-1:break
        # pilot
        pc=PILOTS.get(d["pilot"],{}).get("color",C_DIM)
        sa(win,y,3,d["pilot"][:W-4],cp(pc));y+=1
        bw=max(4,W-14)
        # sync bar
        if y<H-1:
            v=d["sync"];vc=val_col(v)
            sa(win,y,2,"SYN",cp(C_DIM))
            sa(win,y,6,mkbar(v,bw),cp(vc))
            sa(win,y,6+bw+1,f"{v:5.1f}%",cp(vc,bold=True));y+=1
        # HP bar (battle)
        if y<H-1:
            hpv=d["battle_hp"]/d["battle_max_hp"]*100;vc=val_col(hpv)
            sa(win,y,2,"HP ",cp(C_DIM))
            sa(win,y,6,mkbar(hpv,bw),cp(vc))
            sa(win,y,6+bw+1,f"{d['battle_hp']:3d}/{d['battle_max_hp']}",cp(vc,bold=True));y+=1
        # ATF bar
        if y<H-1:
            v=d["atf"];vc=val_col(v)
            sa(win,y,2,"ATF",cp(C_DIM))
            sa(win,y,6,mkbar(v,bw),cp(vc))
            sa(win,y,6+bw+1,f"{v:5.1f}%",cp(vc,bold=True));y+=1
        # active weapon
        if y<H-1:
            aw=d["active_weapon"] if d["active_weapon"]<len(d["loadout"]) else 0
            wn=d["loadout"][aw] if d["loadout"] else "NONE"
            ammo=d["ammo"].get(wn,0)
            ammo_s="∞" if ammo>=99 else str(ammo)
            sa(win,y,2,f"▸ {wn[:W-10]} x{ammo_s}",cp(C_AMBER));y+=1
        # divider
        if y<H-1:sh(win,y,1,"─",W-2,cp(C_DIM));y+=1

# ══ MAGI PANEL ══════════════════════════════════════════════════════════════
# Inspired by the real NERV UI: concentric green dot rings, red/orange MAGI slabs
# Layout from show: CASPAR-3 (left), MELCHIOR-1 (right), BALTHASAR-2 (top)
def draw_magi_panel(win,H,W):
    win.erase()
    foc=focus=="magi"
    box(win,0,0,H,W,"MAGI SUPERCOMPUTER — CENTRAL DOGMA",
        bcol=C_ORANGE if foc else C_DIM,tcol=C_AMBER,sel=foc)
    cy=H//2;cx=W//2

    # ── Concentric dot rings (like image 4 — green dot pattern) ──────────────
    for r_chars,r_y,density in [
        (int(cx*0.9), int(cy*0.85), 12),
        (int(cx*0.65),int(cy*0.65),18),
        (int(cx*0.40),int(cy*0.45),28),
    ]:
        for deg in range(0,360,density):
            a=math.radians(deg)
            xo=int(cx+r_chars*math.cos(a))
            yo=int(cy+r_y*math.sin(a)*0.5)
            if 1<=yo<H-2 and 1<=xo<W-2:
                # Outer rings green (show aesthetic), inner orange
                col=C_GREEN if r_chars>cx*0.5 else C_DIM
                sa(win,yo,xo,"●" if r_chars>cx*0.7 else "·",cp(col,dim=True))

    # ── Rotating scan line (orange) ───────────────────────────────────────────
    scan_len=min(cx-2, int(cy*0.7))
    for r in range(1,scan_len):
        a=math.radians(reticle_ang)
        xr=int(cx+r*math.cos(a))
        yr=int(cy+r*math.sin(a)*0.45)
        if 1<=yr<H-2 and 1<=xr<W-2:
            fade=C_ORANGE if r>scan_len*0.7 else C_DIM
            sa(win,yr,xr,"░" if r<scan_len*0.5 else "▒",cp(fade,dim=(r<scan_len*0.5)))

    # ── Center crosshair ──────────────────────────────────────────────────────
    for dy,dx_,ch in[(-1,0,"│"),(1,0,"│"),(0,-2,"─"),(0,-1,"─"),(0,1,"─"),(0,2,"─")]:
        if 1<=cy+dy<H-2 and 1<=cx+dx_<W-2:sa(win,cy+dy,cx+dx_,ch,cp(C_DIM))
    pulse_ch="◆" if (tick//5)%2==0 else "◈"
    sa(win,cy,cx,pulse_ch,cp(C_ORANGE,bold=True))

    # ── MAGI computer slabs ───────────────────────────────────────────────────
    # Real layout from show: BALTHASAR top-center, CASPAR bottom-left, MELCHIOR bottom-right
    # Each is a parallelogram/diamond but we fake it with angled box labels
    cons_text,cons_col=magi_consensus()

    # Slab dimensions
    sw=min(20,W//4);sh2=6
    # Positions: BALTHASAR top-center, CASPAR bottom-left, MELCHIOR bottom-right
    # Order MUST match magi_names = ["CASPAR","MELCHIOR","BALTHASAR"]
    # so selected_magi index maps correctly to visual highlight
    slabs=[
        # (name,          center_x,                    y_top,     )
        ("CASPAR",    max(sw//2+2,cx-W//4),         H-sh2-3   ),
        ("MELCHIOR",  min(W-sw//2-3,cx+W//4),       H-sh2-3   ),
        ("BALTHASAR", cx,                            2         ),
    ]

    for i,(name,hx,hy) in enumerate(slabs):
        d=magi_votes[name];v=d["vote"]
        vcol=C_GREEN if v=="YES" else C_RED if v=="NO" else C_AMBER
        sel=(i==selected_magi and foc)
        bx=max(1,hx-sw//2);bw=min(sw,W-bx-2)
        hy=max(1,min(hy,H-sh2-2))

        # Box border style — heavy+orange when selected, light otherwise
        bc=C_ORANGE if sel else C_DIM
        TL,TR,BL,BR,HZ,VT=BS_HEAVY if sel else BS_LIGHT
        ba=cp(bc,bold=sel)
        # Draw the slab
        sa(win,hy,bx,TL,ba);sa(win,hy,bx+bw-1,TR,ba)
        sa(win,hy+sh2-1,bx,BL,ba);sa(win,hy+sh2-1,bx+bw-1,BR,ba)
        if bw>2:sa(win,hy,bx+1,HZ*(bw-2),ba)
        if bw>2:sa(win,hy+sh2-1,bx+1,HZ*(bw-2),ba)
        for row in range(1,sh2-1):
            sa(win,hy+row,bx,VT,ba)
            sa(win,hy+row,bx+bw-1,VT,ba)

        # Corner accent for selected
        if sel:
            sa(win,hy,bx,"◈",cp(C_ORANGE,bold=True))
            sa(win,hy,bx+bw-1,"◈",cp(C_ORANGE,bold=True))

        mid=bx+bw//2
        # Magi number (like MAGI 01, 02, 03)
        magi_num={"BALTHASAR":"02","CASPAR":"03","MELCHIOR":"01"}[name]
        num_label=f"MAGI {magi_num}"
        sa(win,hy+1,mid-len(num_label)//2,num_label,cp(C_ORANGE,bold=True))
        sa(win,hy+2,mid-len(name)//2,name,cp(C_AMBER if sel else C_DIM,bold=sel))
        sa(win,hy+3,mid-len(d["role"])//2,d["role"],cp(C_DIM,dim=True))
        # Vote display — pulse when YES
        pulse=(v=="YES" and (tick//7)%2==0)
        vd=f"◈{v}◈" if pulse else f"[{v}]"
        sa(win,hy+4,mid-len(vd)//2,vd,cp(vcol,bold=True))

        # Connector lines from slabs to center
        # Draw a line of dots toward center
        slab_cx=bx+bw//2; slab_cy=hy+sh2//2
        steps=6
        for step in range(1,steps):
            lx=int(slab_cx+(cx-slab_cx)*step/steps)
            ly=int(slab_cy+(cy-slab_cy)*step/steps)
            if 1<=ly<H-2 and 1<=lx<W-2:
                sa(win,ly,lx,"·",cp(C_DIM,dim=True))

    # ── Consensus readout — center bottom ─────────────────────────────────────
    dec=f" {cons_text} "
    dec_y=H-3; dx=max(1,cx-len(dec)//2)
    box(win,dec_y-1,dx-1,3,len(dec)+2,style=BS_LIGHT,bcol=cons_col)
    sa(win,dec_y,dx,dec,cp(cons_col,bold=True))

    # ── Hint ─────────────────────────────────────────────────────────────────
    if foc:
        sa(win,H-1,2,"◄►/WASD:select slab  ENTER/SPACE:vote  TAB:next focus",cp(C_DIM,dim=True))

# ══ FIELD PANEL ═════════════════════════════════════════════════════════════
# Real NERV tactical display — inspired by the show's defense line layout
# TOKYO-3 defense sectors with hex-style grid
SECTOR_LABELS={
    # y_row: (x_start, label, color)
    0:  (1,"SUPPORT LINE",C_DIM),
    3:  (1,"1ST DEFENSE LINE",C_AMBER),
    6:  (1,"MAIN BARRIER",C_ORANGE),
    9:  (1,"2ND DEFENSE LINE",C_AMBER),
    12: (1,"3RD DEFENSE LINE",C_RED),
}

def draw_field_panel(win,H,W):
    win.erase()
    foc=focus=="field"
    box(win,0,0,H,W,
        "TOKYO-3 TACTICAL DISPLAY" if not foc else "TOKYO-3 TACTICAL ◈ ACTIVE",
        bcol=C_ORANGE if foc else C_DIM,
        tcol=C_AMBER if not foc else C_ORANGE,sel=foc)

    # Layout: grid ~65%, info ~35%
    grid_cols=min(FIELD_W,max(10,(W-24)//2))
    grid_w=grid_cols*2+2
    info_x=grid_w+2
    info_w=max(1,W-info_x-1)

    # ── Sector lines across grid (like image 1 — SUPPORT LINE, MAIN BARRIER etc) ──
    sector_rows={
        0: (C_DIM,  "SUPPORT LINE"),
        3: (C_AMBER,"1ST DEFENSE LINE"),
        6: (C_ORANGE,"MAIN BARRIER"),
        9: (C_AMBER,"2ND DEFENSE LINE"),
        12:(C_RED,  "3RD DEFENSE LINE"),
    }
    for row,(col,label) in sector_rows.items():
        sy=1+row
        if sy<H-2:
            sh(win,sy,1,"╌",grid_w-1,cp(col,dim=True))
            # Draw sector label at right edge of grid
            if len(label)<grid_w-2:
                sa(win,sy,max(1,grid_w-len(label)-1),label,cp(col,dim=True))

    # ── Draw terrain cells ────────────────────────────────────────────────────
    EVA_ICONS={"EVA-00":"00","EVA-01":"01","EVA-02":"02"}
    # Build occupancy map for collision detection
    eva_positions={}
    for uk in EVA_KEYS:
        d=eva_units[uk]
        if d["deployed"]:
            eva_positions[d["pos"]]=uk

    for gy in range(FIELD_H):
        for gx in range(grid_cols):
            sx=1+gx*2; sy=1+gy
            if sy>=H-2 or sx+1>=grid_w:break
            ch=TERRAIN.get((gx,gy),"·")
            if ch not in("·",):
                if ch=="~":   sa(win,sy,sx,"≈",cp(C_CYAN,dim=True))
                elif ch=="▓": sa(win,sy,sx,"▓",cp(C_AMBER,dim=True))
                elif ch=="░": sa(win,sy,sx,"░",cp(C_DIM,dim=True))
            else:
                # Hex-style grid dot pattern
                if gx%3==0 and gy%2==0:
                    sa(win,sy,sx,"·",cp(C_DIM,dim=True))

    # ── ANGEL on grid — distinctive red pulsing diamond ──────────────────────
    if angel["alive"]:
        ax,ay=angel["pos"]
        if ax<grid_cols:
            sx=1+ax*2; sy=1+ay
            if 1<=sy<H-2 and 1<=sx<grid_w:
                # Angel is a RED pulsing cross/diamond — unmistakable
                blink=(tick//3)%4
                ang_chars=["◈","◇","◈","✦"]
                sa(win,sy,sx,ang_chars[blink],cp(C_RED,bold=True))
                # Danger halo — 1-cell ring in red
                for ddx,ddy in[(0,-1),(0,1),(-1,0),(1,0)]:
                    hx2=sx+ddx*2; hy2=sy+ddy
                    if 1<=hy2<H-2 and 1<=hx2<grid_w:
                        sa(win,hy2,hx2,"·",cp(C_RED,dim=True))
                # Label below
                lbl=angel["class"][:4]
                if sy+1<H-2:
                    sa(win,sy+1,max(1,sx-1),lbl,cp(C_RED,dim=True))

    # ── EVA units on grid — green/amber/red triangles with unit ID ───────────
    for ei,uk in enumerate(EVA_KEYS):
        d=eva_units[uk]
        if not d["deployed"]:continue
        ex,ey=d["pos"]
        if ex>=grid_cols:continue
        sx=1+ex*2; sy=1+ey
        if 0<sy<H-2 and 0<sx<grid_w:
            is_sel=(ei==field_sel and foc)
            col=d["unit_col"]
            # EVA = solid filled upward triangle + 2-char ID
            # Use reverse video for selected
            eva_ch="▲"
            tag=uk[-2:]  # "00","01","02"
            if is_sel:
                sa(win,sy,sx,eva_ch,cp(col,bold=True)|curses.A_REVERSE)
                sa(win,sy,sx+1,tag,cp(col,bold=True)|curses.A_REVERSE)
            else:
                sa(win,sy,sx,eva_ch,cp(col,bold=True))
                sa(win,sy,sx+1,tag,cp(col,dim=True))

    # ── Grid divider ──────────────────────────────────────────────────────────
    for gy in range(H-1):
        sa(win,gy,grid_w,"║",cp(C_DIM))

    # ── Info panel (right side) ───────────────────────────────────────────────
    if info_x<W-2 and info_w>=8:
        uk=EVA_KEYS[field_sel]
        d=eva_units[uk]
        y2=1
        lbl=f"◀ {uk} ▶" if foc else uk
        sa(win,y2,info_x,lbl,cp(d["unit_col"],bold=True));y2+=1
        pc=PILOTS.get(d["pilot"],{}).get("color",C_DIM)
        sa(win,y2,info_x,d["pilot"][:info_w],cp(pc,bold=True));y2+=1
        scol={"ACTIVE":C_GREEN,"STANDBY":C_AMBER,"CRITICAL":C_RED,
              "BERSERK":C_RED}.get(d["status"],C_ORANGE)
        sa(win,y2,info_x,d["status"],cp(scol,bold=True));y2+=1
        ex2,ey2=d["pos"];dep="FIELD" if d["deployed"] else "HANGAR"
        sa(win,y2,info_x,f"({ex2},{ey2}) {dep}",cp(C_GREEN if d["deployed"] else C_DIM));y2+=2

        # Vitals
        sec(win,y2,info_x-1,info_w+1,"VITALS");y2+=1
        bw2=max(2,info_w-10)
        hp_pct=d["battle_hp"]/d["battle_max_hp"]*100
        for val,label,extra in[
            (hp_pct,   "HP  ",f"{d['battle_hp']}/{d['battle_max_hp']}"),
            (d["sync"],"SYN ",f"{d['sync']:.0f}%"),
            (d["atf"], "ATF ",f"{d['atf']:.0f}%"),
        ]:
            if y2>=H-6:break
            vc=val_col(val)
            sa(win,y2,info_x,label,cp(C_DIM))
            sa(win,y2,info_x+4,mkbar(val,bw2),cp(vc))
            sa(win,y2,info_x+4+bw2+1,extra,cp(vc,bold=True));y2+=1

        # Loadout
        if y2<H-5:
            y2+=1;sec(win,y2,info_x-1,info_w+1,"LOADOUT");y2+=1
        for wi,wn in enumerate(d["loadout"]):
            if y2>=H-4:break
            active=wi==d.get("active_weapon",0)
            ammo=d["ammo"].get(wn,0)
            ammo_s="∞" if ammo>=99 else str(ammo)
            sa(win,y2,info_x,("▶ " if active else "  ")+wn[:info_w-6],
               cp(C_AMBER if active else C_DIM,bold=active))
            sa(win,y2,info_x+info_w-4,f"x{ammo_s}",cp(C_DIM));y2+=1

        # Angel info
        if angel["alive"] and y2<H-4:
            y2+=1
            ax3,ay3=angel["pos"]; d_ang=dist(ex2,ey2,ax3,ay3)
            ang_col=C_RED if d_ang<=2 else C_AMBER if d_ang<=5 else C_DIM
            sa(win,y2,info_x,f"◈ANGEL {d_ang:.1f}cells",cp(ang_col,bold=True));y2+=1
            if d_ang<=2:
                sa(win,y2,info_x,"ENGAGE! B=squad",cp(C_RED,bold=True))

        # Legend at very bottom
        y2=H-2
        sa(win,y2,info_x,"B:deploy []:EVA",cp(C_DIM,dim=True))

    # ── Bottom legend in grid area ────────────────────────────────────────────
    sa(win,H-1,1,"▲=EVA  ◈=ANGEL  ≈=water  ▓=building  ╌=sector",
       cp(C_DIM,dim=True))

    # Info panel (right side)
    if info_x<W-2 and info_w>=8:
        uk=EVA_KEYS[field_sel]
        d=eva_units[uk]
        y2=1
        # Header
        lbl=f"◀ {uk} ▶" if foc else uk
        sa(win,y2,info_x,lbl,cp(d["unit_col"],bold=True));y2+=1
        pc=PILOTS.get(d["pilot"],{}).get("color",C_DIM)
        sa(win,y2,info_x,d["pilot"][:info_w],cp(pc,bold=True));y2+=1
        scol={"ACTIVE":C_GREEN,"STANDBY":C_AMBER,"CRITICAL":C_RED,
              "BERSERK":C_RED}.get(d["status"],C_ORANGE)
        sa(win,y2,info_x,d["status"],cp(scol,bold=True));y2+=1
        ex2,ey2=d["pos"];dep="FIELD" if d["deployed"] else "HANGAR"
        sa(win,y2,info_x,f"({ex2},{ey2}) {dep}",
           cp(C_GREEN if d["deployed"] else C_DIM));y2+=2

        # Vitals
        sec(win,y2,info_x-1,info_w+1,"VITALS");y2+=1
        bw2=max(2,info_w-10)
        hp_pct=d["battle_hp"]/d["battle_max_hp"]*100
        for val,label,key in[
            (hp_pct,"HP ",None),
            (d["sync"],"SYN",None),
            (d["atf"],"ATF",None)]:
            if y2>=H-6:break
            vc=val_col(val)
            sa(win,y2,info_x,label,cp(C_DIM))
            sa(win,y2,info_x+3,mkbar(val,bw2),cp(vc))
            if label=="HP ":
                sa(win,y2,info_x+3+bw2+1,f"{d['battle_hp']}/{d['battle_max_hp']}",cp(vc,bold=True))
            else:
                sa(win,y2,info_x+3+bw2+1,f"{val:.0f}%",cp(vc,bold=True))
            y2+=1

        # Loadout
        if y2<H-5:
            y2+=1;sec(win,y2,info_x-1,info_w+1,"LOADOUT");y2+=1
        for wi,wn in enumerate(d["loadout"]):
            if y2>=H-4:break
            active=wi==d.get("active_weapon",0)
            ammo=d["ammo"].get(wn,0)
            ammo_s="∞" if ammo>=99 else str(ammo)
            prefix="▶ " if active else "  "
            sa(win,y2,info_x,
               prefix+wn[:info_w-6],
               cp(C_AMBER if active else C_DIM,bold=active))
            sa(win,y2,info_x+info_w-4,f"x{ammo_s}",cp(C_DIM));y2+=1

        # Angel distance
        if angel["alive"] and y2<H-3:
            y2+=1
            ax3,ay3=angel["pos"]
            d_ang=dist(ex2,ey2,ax3,ay3)
            ang_col=C_RED if d_ang<=2 else C_AMBER if d_ang<=5 else C_DIM
            sa(win,y2,info_x,f"ANGEL:{d_ang:.1f}",cp(ang_col,bold=True))
            if d_ang<=2:
                y2+=1
                sa(win,y2,info_x,"ENGAGE! SPACE",cp(C_RED,bold=True))

        # Controls
        y2=H-3
        if foc:
            sa(win,y2,info_x,"WASD:move",cp(C_DIM,dim=True));y2+=1
            sa(win,y2,info_x,"B:deploy []:EVA",cp(C_DIM,dim=True))

    sa(win,H-1,1,"▲=EVA  ◉=ANGEL  ≈=water  ▓=building",cp(C_DIM,dim=True))


# ══ ANGEL PANEL ══════════════════════════════════════════════════════════════
def draw_angel_panel(win,H,W):
    """Angel tracking radar — live bearing, range, threat analysis."""
    win.erase()
    box(win,0,0,H,W,"ANGEL TRACKING — PATTERN BLUE",bcol=C_RED,tcol=C_RED)
    cy=H//2; cx=W//2
    ang=angel

    # Radar rings
    for r in [8,5,3]:
        for deg in range(0,360,15):
            a=math.radians(deg)
            xo=int(cx+r*math.cos(a)*2.0)
            yo=int(cy+r*math.sin(a)*0.6)
            if 1<=yo<H-2 and 1<=xo<W-2:
                sa(win,yo,xo,"·",cp(C_DIM,dim=True))

    # Rotating sweep arm
    scan_len=min(8,cx-2,cy-2)
    for r in range(1,scan_len):
        a=math.radians(reticle_ang)
        xr=int(cx+r*math.cos(a)*2.0)
        yr=int(cy+r*math.sin(a)*0.6)
        if 1<=yr<H-2 and 1<=xr<W-2:
            sa(win,yr,xr,"▒" if r>scan_len*0.6 else "░",
               cp(C_GREEN if ang["alive"] else C_DIM,dim=(r<scan_len*0.6)))

    # NERV base at center
    sa(win,cy,cx,"╋",cp(C_ORANGE,bold=True))

    # Angel blip on radar
    if ang["alive"]:
        bear=math.radians(ang.get("bearing",0)-90)
        rng_norm=min(1.0,ang.get("range_km",5)/6.0)
        bx=int(cx+rng_norm*scan_len*math.cos(bear)*2.0)
        by_=int(cy+rng_norm*scan_len*math.sin(bear)*0.6)
        if 1<=by_<H-2 and 1<=bx<W-2:
            blip="◈" if (tick//4)%2==0 else "◇"
            sa(win,by_,bx,blip,cp(C_RED,bold=True))

    # Info panel right side
    ix=cx+min(cx-2,11)+3; iw=max(1,W-ix-2)
    y=2
    sa(win,y,ix,"THREAT ANALYSIS",cp(C_RED,bold=True));y+=1
    sh(win,y,ix,"─",iw,cp(C_DIM));y+=1
    if ang["alive"]:
        sa(win,y,ix,f"CLASS: {ang['class']}",cp(C_ORANGE,bold=True));y+=1
        sa(win,y,ix,f"PATTERN: {ang.get('pattern','BLUE')}",cp(C_RED));y+=1
        sa(win,y,ix,f"RANGE: {ang.get('range_km',0):.1f}km",cp(C_AMBER,bold=True));y+=1
        sa(win,y,ix,f"BEARING: {ang.get('bearing',0)}°",cp(C_AMBER));y+=1
        sa(win,y,ix,f"ATF LVL: {ang.get('atf',0)}%",cp(C_RED,bold=True));y+=1
        hp_pct=ang["hp"]/ang["max_hp"]*100
        sa(win,y,ix,f"HP: {ang['hp']}/{ang['max_hp']}",cp(val_col(hp_pct),bold=True));y+=1
        sa(win,y,ix,mkbar(hp_pct,min(iw-2,16)),cp(val_col(hp_pct)));y+=2
        sa(win,y,ix,"ABILITIES:",cp(C_DIM));y+=1
        for ab in ang.get("abilities",[]):
            sa(win,y,ix,f" ▸ {ab}",cp(C_AMBER));y+=1
            if y>=H-4:break
    else:
        sa(win,y,ix,"STATUS: NEUTRALIZED",cp(C_GREEN,bold=True));y+=1
        sa(win,y,ix,"PATTERN BLUE: GONE",cp(C_GREEN));y+=1
        sa(win,y+2,ix,"TYPE: revive angel",cp(C_DIM,dim=True))

    # Bottom: MAGI consensus on angel threat
    cons,ccol=magi_consensus()
    sa(win,H-2,2,f"MAGI DECISION: {cons}",cp(ccol,bold=True))

# ══ DEPLOY PANEL ════════════════════════════════════════════════════════════
def draw_deploy_panel(win,H,W):
    win.erase()
    box(win,0,0,H,W,"SQUAD DEPLOYMENT",bcol=C_AMBER,tcol=C_AMBER)
    sa(win,2,3,"Choose EVAs for the angel encounter.",cp(C_DIM))
    sa(win,3,3,"↑↓:select  SPACE:toggle  ENTER:launch battle",cp(C_DIM))
    sh(win,4,2,"─",W-4,cp(C_DIM))
    y=6
    for i,uk in enumerate(EVA_KEYS):
        if y>=H-5:break
        d=eva_units[uk]
        chosen=deploy_choices.get(uk,False)
        sel=(i==deploy_sel)
        scol={"ACTIVE":C_GREEN,"STANDBY":C_AMBER,"CRITICAL":C_RED}.get(d["status"],C_DIM)
        pc=PILOTS.get(d["pilot"],{}).get("color",C_DIM)
        # Row highlight
        if sel:sh(win,y,1," ",W-2,cp(C_ORANGE_BG))
        chk="[✓]" if chosen else "[ ]"
        sa(win,y,2,("▶" if sel else " ")+" "+chk,cp(C_ORANGE if sel else C_DIM,bold=sel))
        sa(win,y,8,uk,cp(d["unit_col"],bold=True))
        sa(win,y,15,d["pilot"][:16],cp(pc))
        sa(win,y,W-11,f"[{d['status'][:8]}]",cp(scol));y+=1
        # Stats
        bw3=min(20,W//4)
        hp_pct=d["battle_hp"]/d["battle_max_hp"]*100
        sa(win,y,8,
           f"SYNC:{mkbar(d['sync'],8)}{d['sync']:.0f}%  "
           f"HP:{mkbar(hp_pct,8)}{d['battle_hp']}/{d['battle_max_hp']}",
           cp(val_col(d["sync"])));y+=1
        # Loadout
        weps=" | ".join(d["loadout"][:3])
        sa(win,y,8,f"▸ {weps[:W-12]}",cp(C_DIM,dim=True));y+=2
    sh(win,H-4,2,"─",W-4,cp(C_DIM))
    chosen_list=[uk for uk in EVA_KEYS if deploy_choices.get(uk)]
    if chosen_list:
        sa(win,H-3,2,f"SQUAD: {' + '.join(chosen_list)}",cp(C_GREEN,bold=True))
        sa(win,H-2,2,"ENTER=launch battle",cp(C_AMBER,bold=True))
    else:
        sa(win,H-3,2,"No units selected.",cp(C_RED))
        sa(win,H-2,2,"SPACE to toggle.",cp(C_DIM))

# ══ LOADOUT PANEL ═══════════════════════════════════════════════════════════
def draw_loadout_panel(win,H,W):
    win.erase()
    box(win,0,0,H,W,"WEAPON LOADOUT EDITOR",bcol=C_AMBER,tcol=C_AMBER)

    uk=EVA_KEYS[loadout_unit_idx % len(EVA_KEYS)]
    d=eva_units[uk]

    # EVA tabs
    sa(win,2,2,"↑↓:weapon  ←→:slot  []:prev-EVA  ]:next-EVA  ENTER:equip  V/ESC:exit",cp(C_DIM))
    tab_x=2
    for i,u in enumerate(EVA_KEYS):
        sel=(i==loadout_unit_idx % len(EVA_KEYS))
        ud=eva_units[u]
        label=f"[{u}]" if sel else f" {u} "
        sa(win,3,tab_x,label,cp(ud["unit_col"],bold=sel))
        tab_x+=len(label)+1
    sh(win,4,2,"─",W-4,cp(C_DIM))

    # Split: left=loadout, right=catalogue
    half=max(20,(W-4)//2)
    lx=2;rx=half+3

    # Left: current loadout
    sa(win,5,lx,"CURRENT LOADOUT",cp(C_ORANGE,bold=True))
    pc=PILOTS.get(d["pilot"],{}).get("color",C_DIM)
    sa(win,6,lx,f"Pilot: {d['pilot']}",cp(pc))
    y=8
    for si in range(3):
        if y>=H-6:break
        wn=d["loadout"][si] if si<len(d["loadout"]) else "── EMPTY ──"
        sel=(si==loadout_slot_sel)
        attr=cp(C_ORANGE if sel else C_DIM,bold=sel)
        prefix="▶ " if sel else "  "
        sa(win,y,lx,f"{prefix}SLOT {si+1}:",attr)
        sa(win,y,lx+9,wn[:half-10],attr)
        if wn in WEAPON_CATALOGUE and sel:
            wd=WEAPON_CATALOGUE[wn]
            ammo=d["ammo"].get(wn,0)
            sa(win,y+1,lx+3,
               f"DMG:{wd['dmg'][0]}-{wd['dmg'][1]} ACC:{wd['acc']}% RNG:{wd['rng']}",
               cp(C_DIM,dim=True))
            sa(win,y+2,lx+3,
               f"TYPE:{wd['type']}  AMMO:{'∞' if ammo>=99 else ammo}",
               cp(C_DIM,dim=True))
            y+=3
        else:
            y+=2

    # Vertical divider
    for gy in range(5,H-1):sa(win,gy,half+2,"│",cp(C_DIM))

    # Right: weapon catalogue
    sa(win,5,rx,"WEAPON CATALOGUE",cp(C_CYAN,bold=True))
    vis_start=max(0,loadout_wep_sel-4)
    cy2=7
    for wi in range(vis_start,min(len(WEP_KEYS),vis_start+H-9)):
        if cy2>=H-3:break
        wn=WEP_KEYS[wi]
        sel=(wi==loadout_wep_sel)
        wd=WEAPON_CATALOGUE[wn]
        attr=cp(C_AMBER if sel else C_DIM,bold=sel)
        prefix="▶ " if sel else "  "
        sa(win,cy2,rx,prefix+wn[:W-rx-4],attr)
        if sel:
            cy2+=1
            sa(win,cy2,rx+2,wd["desc"][:W-rx-4],cp(C_DIM,dim=True))
            cy2+=1
            col={"RANGED":C_CYAN,"MELEE":C_RED,"DEFENSE":C_GREEN,
                 "BOMB":C_ORANGE,"SPECIAL":C_MAGENTA,"UTILITY":C_DIM}.get(wd["type"],C_DIM)
            sa(win,cy2,rx+2,
               f"DMG:{wd['dmg'][0]}-{wd['dmg'][1]}  ACC:{wd['acc']}%  RNG:{wd['rng']}",
               cp(col))
            cy2+=2
        else:
            cy2+=1

    sa(win,H-2,2,f"Equipping to: {uk} SLOT {loadout_slot_sel+1}",cp(C_AMBER,bold=True))

# ══ ALERT PANEL ═════════════════════════════════════════════════════════════
def draw_alert_panel(win,H,W):
    win.erase()
    # Check if any CRIT alert — if so, use red border (image 2 style)
    crits=[a for a in alerts if a[0]=="CRIT"]
    has_crit=len(crits)>0
    box(win,0,0,H,W,"SYSTEM ALERTS",
        bcol=C_RED if has_crit else C_DIM,
        tcol=C_RED if has_crit else C_ORANGE)
    col_map={"CRIT":C_RED,"WARN":C_AMBER,"OK":C_GREEN,"INFO":C_CYAN}
    # Image 2 style: WARNING / ERROR banners
    tag_map={"CRIT":"▶▶","WARN":"▷▷","OK":"OK","INFO":"--"}
    y=1
    for level,msg in list(alerts):
        if y>=H-1:break
        col=col_map.get(level,C_ORANGE)
        tag=tag_map.get(level,"--")
        bold=(level=="CRIT")
        # Flash the very newest CRIT
        if level=="CRIT" and y==1:
            flash=(tick//3)%2==0
            if flash:sh(win,y,1," ",W-2,cp(C_RED_BG))
        sa(win,y,1,tag,cp(col,bold=True))
        lines=textwrap.wrap(msg,W-5) or[msg[:W-5]]
        sa(win,y,4,lines[0],cp(col,bold=bold));y+=1
        for extra in lines[1:]:
            if y>=H-1:break
            sa(win,y,4,extra,cp(col));y+=1

# ══ COMM PANEL ══════════════════════════════════════════════════════════════
def draw_comm_panel(win,H,W):
    win.erase()
    foc=(focus=="comm")
    box(win,0,0,H,W,"COMM // TERMINAL",
        bcol=C_ORANGE if foc else C_DIM,sel=foc)
    sp_col={"MISATO":C_AMBER,"RITSUKO":C_CYAN,"SHINJI":C_GREEN,
            "ASUKA":C_RED,"GENDO":C_WHITE,"AYANAMI":C_AMBER,
            "SEELE":C_MAGENTA,"MAGI":C_ORANGE,"YOU":C_GREEN,
            "REI":C_AMBER,"KAWORU":C_CYAN,"KAJI":C_AMBER,
            "HYUGA":C_GREEN,"IBUKI":C_AMBER,"FUYUTSUKI":C_WHITE}
    rendered=[]
    for speaker,msg in list(comm_log):
        col=sp_col.get(speaker,C_DIM)
        avail=max(1,W-12)
        lines=textwrap.wrap(msg,avail) or[msg[:avail]]
        rendered.append((speaker,lines[0],col))
        for extra in lines[1:]:rendered.append((None,extra,col))
    vis_h=H-4
    vis=rendered[-vis_h:] if len(rendered)>vis_h else rendered
    y=1
    for speaker,text,col in vis:
        if y>=H-3:break
        if speaker:sa(win,y,1,f"{speaker:<9}",cp(col,bold=True))
        sa(win,y,10,text,cp(C_DIM));y+=1
    sh(win,H-3,1,"─",W-2,cp(C_DIM))
    prompt="CMD > "
    sa(win,H-2,1,prompt,cp(C_ORANGE if foc else C_DIM,bold=foc))
    buf_area=W-len(prompt)-3
    disp=cmd_buffer[-buf_area:] if len(cmd_buffer)>buf_area else cmd_buffer
    sa(win,H-2,1+len(prompt),disp,cp(C_GREEN if foc else C_DIM))
    cx2=1+len(prompt)+len(disp)
    if foc and(tick//5)%2==0:
        sa(win,H-2,cx2,"█",cp(C_GREEN,bold=True))
    hint="ENTER:send  ↑↓:history  help=cmds" if foc else "TAB to focus"
    sa(win,H-1,1,hint,cp(C_DIM,dim=True))

# ══ BATTLE PANEL ════════════════════════════════════════════════════════════
def draw_battle_panel(win,H,W):
    b=battle
    if not b["eva_party"]:return
    eva_key=b["eva_party"][b["active_eva"]]
    d=eva_units[eva_key]
    ang=angel
    win.erase()
    box(win,0,0,H,W,f"COMBAT — {ang['class']}",style=BS_GAME,bcol=C_RED,tcol=C_RED)

    ang_half=H//2-2
    # ── Angel area ───────────────────────────────────────────────────────────
    # Angel ASCII sprite (changes with HP)
    if ang["alive"]:
        hp_ratio=ang["hp"]/ang["max_hp"]
        if hp_ratio>0.6:
            sprite=["  ◈◈◈◈◈  ","◈ ╬◉╬◉╬ ◈","◈  ╬╬╬  ◈","  ║║║║║  "]
        elif hp_ratio>0.3:
            sprite=["  ◌◌◌◌◌  ","◌ ╬◌╬◌╬ ◌","◌  ╬╬╬  ◌","  ╎╎╎╎╎  "]
        else:
            sprite=["  ○○○○○  "," ○ ╎○╎ ○ ","  ○ ○ ○  ","  ╎ ╎ ╎  "]
        anim_hit=b.get("anim_frames",0)>0
        sc=C_WHITE if anim_hit else C_RED
        for li,ln in enumerate(sprite):
            yr=2+li
            if yr>=ang_half:break
            xr=W//2-len(ln)//2
            sa(win,yr,xr,ln,cp(sc,bold=True))
        # Stun indicator
        if ang.get("angel_stun",0)>0:
            sa(win,2,4,f"STUNNED x{ang['angel_stun']}",cp(C_AMBER,bold=True))
        # Status effect
        if ang.get("status_effect"):
            sa(win,3,4,f"STATUS: {ang['status_effect']}",cp(C_MAGENTA,bold=True))
        # Angel HP / ATF
        bar_w=min(40,W-20)
        sa(win,1,3,ang["class"],cp(C_RED,bold=True))
        hp_pct=ang["hp"]/ang["max_hp"]*100
        sa(win,1,3+len(ang["class"])+2,
           f"HP:{mkbar(hp_pct,bar_w)}{ang['hp']}/{ang['max_hp']}",
           cp(val_col(hp_pct),bold=True))
        sa(win,2,3,f"ATF:{ang['atf']}%  {ang['desc'][:W-16]}",cp(C_DIM))
    else:
        sa(win,ang_half//2,W//2-9,"-- NEUTRALIZED --",cp(C_GREEN,bold=True))

    sh(win,ang_half+1,1,"─",W-2,cp(C_DIM))

    # ── EVA party bars ────────────────────────────────────────────────────────
    py=ang_half+2
    for i,ek in enumerate(b["eva_party"]):
        if py>=H-8:break
        ed=eva_units[ek]
        active=(i==b["active_eva"])
        hp_pct=ed["battle_hp"]/ed["battle_max_hp"]*100
        vc=val_col(hp_pct)
        marker="▶" if active else " "
        bw4=min(14,W//6)
        pinfo=f"{marker}{ek[-2:]} {mkbar(hp_pct,bw4)}{ed['battle_hp']:3d}/{ed['battle_max_hp']}"
        if active:py_x=2
        else:py_x=2+i*22
        sa(win,py,py_x,pinfo,cp(ed["unit_col"],bold=active))
    py+=2

    # EVA ASCII sprite (active)
    eva_sprite={
        "EVA-00":["  ▲▲  "," ▲║▲ "," ║║║ "," ╫ ╫ "],
        "EVA-01":["  ▲▲▲ "," ▲╬╬▲"," ║╬║ "," ╫ ╫ "],
        "EVA-02":["  ▲▲  "," ▲╋╋▲"," ║╋║ "," ╫ ╫ "],
    }
    sprite=eva_sprite.get(eva_key,["  ▲  "," ▲▲▲ "," ║║║ "," ╫ ╫ "])
    ef=(b.get("anim_frames",0)>0 and b.get("last_action","")!="ATTACK")
    for li,ln in enumerate(sprite):
        yr=ang_half+2+li
        if yr>=H-7:break
        sa(win,W-12,yr,ln,cp(C_AMBER if ef else d["unit_col"],bold=True))

    # ── Battle log ────────────────────────────────────────────────────────────
    log_y=py
    log_lines=b["log"][-4:] if len(b["log"])>4 else b["log"]
    for li,ln in enumerate(log_lines):
        if log_y+li>=H-6:break
        age=len(b["log"])-(len(b["log"])-4+li if len(b["log"])>4 else li)-1
        col=C_ORANGE if li==len(log_lines)-1 else C_DIM
        sa(win,log_y+li,2,ln[:W-4],cp(col))

    sh(win,H-7,1,"─",W-2,cp(C_DIM))

    # ── Action menu ───────────────────────────────────────────────────────────
    if b["phase"] in("PLAYER_TURN","SELECT"):
        if b["sub_menu"]=="item":
            sa(win,H-6,2,"ITEMS:",cp(C_AMBER,bold=True))
            items=list(b["items"].items())
            ix=10
            for ii,(iname,cnt) in enumerate(items):
                if ix>=W-4:break
                sel=(ii==b["item_sel"])
                sa(win,H-6,ix,
                   f"{'▶' if sel else ' '}{iname}(x{cnt})",
                   cp(C_AMBER if sel else C_DIM,bold=sel))
                ix+=len(iname)+8
            sa(win,H-5,2,"←→:select  ENTER:use  ESC:back",cp(C_DIM,dim=True))
        elif b["sub_menu"]=="switch":
            sa(win,H-6,2,"SWITCH TO:",cp(C_CYAN,bold=True))
            sx=13
            for ii,ek in enumerate(b["eva_party"]):
                if ii==b["active_eva"]:continue
                if sx>=W-4:break
                ed=eva_units[ek]
                sel=(ii==b["item_sel"])
                sa(win,H-6,sx,
                   f"{'▶' if sel else ' '}{ek[-2:]} HP:{ed['battle_hp']}",
                   cp(ed["unit_col"] if sel else C_DIM,bold=sel))
                sx+=16
            sa(win,H-5,2,"←→:select  ENTER:switch  ESC:back",cp(C_DIM,dim=True))
        else:
            # Main action menu in a clean row
            mx=2
            for ai,act in enumerate(b["actions"]):
                sel=(ai==b["cursor"])
                extra=""
                if act=="ATTACK":
                    aw=d.get("active_weapon",0)
                    wn=d["loadout"][aw] if d["loadout"] else "?"
                    extra=f"[{wn[:8]}]"
                elif act=="AT FIELD":
                    extra=f"[{d['atf']:.0f}%]"
                elif act=="ITEM":
                    extra=f"[x{sum(b['items'].values())}]"
                label=f"{'▶' if sel else ' '}{act} {extra}"
                sa(win,H-6,mx,label,cp(C_ORANGE if sel else C_DIM,bold=sel))
                mx+=len(label)+2
                if mx>=W-5:break
            # Weapon row
            sa(win,H-5,2,"WEP: ",cp(C_DIM))
            wx=7
            for wi,wn in enumerate(d["loadout"]):
                if wx>=W-5:break
                sel=(wi==d.get("active_weapon",0))
                sa(win,H-5,wx,f"[{wi+1}]{wn[:8]}",cp(C_AMBER if sel else C_DIM,bold=sel))
                wx+=len(wn)+5
            # Pilot / sync info
            pdata=PILOTS.get(d["pilot"],{})
            sa(win,H-4,2,
               f"PILOT:{d['pilot']}  SYN:{d['sync']:.0f}%  "
               f"ATK:{pdata.get('stat_atk',1):.1f}x  DEF:{pdata.get('stat_def',1):.1f}x",
               cp(C_DIM))
            sa(win,H-3,2,
               "↑↓:action  1/2/3:weapon  ENTER:go  ESC:flee",
               cp(C_DIM,dim=True))

    elif b["phase"]=="WIN":
        msg=f"ANGEL {ang['class']} NEUTRALIZED! {b['turn']} turns."
        sa(win,H//2,max(1,W//2-len(msg)//2),msg,cp(C_GREEN,bold=True))
        sa(win,H//2+2,W//2-6,"ESC to return",cp(C_DIM))
    elif b["phase"]=="LOSE":
        msg="ALL EVAS DEFEATED — MISSION FAILED"
        sa(win,H//2,max(1,W//2-len(msg)//2),msg,cp(C_RED,bold=True))
        sa(win,H//2+2,W//2-6,"ESC to return",cp(C_DIM))

# ══ ARCADE ATTACK GAME ══════════════════════════════════════════════════════
def draw_game_attack(win,H,W):
    a=atk
    atk["xmax"]=W-5;atk["ymax"]=H-8
    win.erase()
    box(win,0,0,H,W,"AT FIELD BREACH — ARCADE",style=BS_GAME,bcol=C_RED,tcol=C_RED)
    px1,py1,px2,py2=1,1,W-2,H-7
    if a["phase"]=="play":
        # Shots
        for sx,sy,age,ptype in list(a["shots"]):
            if px1<=sx<=px2 and py1<=sy<=py2:
                ch="★" if ptype=="power" else("*" if age<2 else "·")
                col=C_AMBER if ptype=="power" else C_GREEN
                sa(win,sy,sx,ch,cp(col,bold=(age<2)))
        # Angel
        ax2,ay2=int(a["angel_x"]),int(a["angel_y"])
        if px1<=ax2<=px2 and py1<=ay2<=py2:
            flash=a["flash"]>0
            hp=a["hp"]
            ch="◉" if hp>3 else("◎" if hp>1 else "○")
            sa(win,ay2,ax2,ch,cp(C_WHITE if flash else C_RED,bold=True))
            hp_bar_str=f"{'█'*hp}{'░'*(5-hp)}"
            sa(win,max(1,ay2-1),max(px1,ax2-3),hp_bar_str,cp(C_RED if not flash else C_AMBER,bold=True))
            # charging indicator
            if a.get("angel_charge",0)>0 and a["angel_charge"]%4==0:
                sa(win,min(py2,ay2+1),max(px1,ax2-2),"FIRE!",cp(C_MAGENTA,bold=True))
        # EVA cursor / reticle
        cx3,cy3=int(a["cx"]),int(a["cy"])
        if px1<=cx3<=px2 and py1<=cy3<=py2:
            shield_on=a.get("shield_on",False)
            reticle_col=C_CYAN if shield_on else C_GREEN
            sa(win,cy3,cx3,"╋",cp(reticle_col,bold=True))
            if cy3>py1:sa(win,cy3-1,cx3,"┃",cp(reticle_col))
            if cy3<py2:sa(win,cy3+1,cx3,"┃",cp(reticle_col))
            if cx3>px1:sa(win,cy3,cx3-1,"━",cp(reticle_col))
            if cx3<px2:sa(win,cy3,cx3+1,"━",cp(reticle_col))
            if shield_on:
                for rch,ry,rx in[("╗",cy3-1,cx3+1),("╝",cy3+1,cx3+1),
                                   ("╔",cy3-1,cx3-1),("╚",cy3+1,cx3-1)]:
                    sa(win,ry,rx,rch,cp(C_CYAN,bold=True))
        # EVA HP bar
        eva_col=val_col(a["eva_hp"])
        ef=a.get("eva_flash",0)>0
        sa(win,H-6,1,"EVA:",cp(C_DIM))
        sa(win,H-6,5,mkbar(a["eva_hp"],24),cp(C_RED if ef else eva_col,bold=ef))
        sa(win,H-6,30,f"{a['eva_hp']:3d}%",cp(eva_col,bold=True))
        # HUD
        sa(win,H-5,1,
           f" SCORE:{a['score']:05d}  HITS:{a['hits']}  AMMO:{a['ammo']:02d}"
           f"  PWR:{a['power_shots']}  ANGEL:{'█'*a['hp']}{'░'*(5-a['hp'])}"
           f"  TIME:{a['time_left']:02d}s ",
           cp(C_ORANGE,bold=True))
        if a.get("shield_on"):
            sa(win,H-4,1,"[SHIELD ON]",cp(C_CYAN,bold=True))
        sa(win,H-4,W-3-30,a["msg"][:28],cp(C_DIM))
        sa(win,H-3,1,"WASD:move  SPACE:fire  F:power-shot  Z:shield  ESC:exit",
           cp(C_DIM,dim=True))
    elif a["phase"]=="win":
        sa(win,H//2-1,W//2-9,"ANGEL NEUTRALIZED!",cp(C_GREEN,bold=True))
        sa(win,H//2,W//2-10,f"SCORE:{a['score']}  HITS:{a['hits']}",cp(C_AMBER))
        sa(win,H//2+2,W//2-6,"ESC to return",cp(C_DIM))
    elif a["phase"]=="lose":
        sa(win,H//2-1,W//2-7,"EVA DESTROYED",cp(C_RED,bold=True))
        sa(win,H//2,W//2-10,f"SCORE:{a['score']}  HITS:{a['hits']}",cp(C_AMBER))
        sa(win,H//2+2,W//2-6,"ESC to return",cp(C_DIM))

# ══ SYNC GAME ═══════════════════════════════════════════════════════════════
def draw_game_sync(win,H,W):
    s=syn;win.erase()
    box(win,0,0,H,W,"SYNC RATE CALIBRATION",style=BS_GAME,bcol=C_CYAN,tcol=C_CYAN)
    wave_y=H//2
    tgt=s["target"];tol=s["tolerance"]
    tgt_x=max(2,min(W-5,int(2+(W-4)*tgt/100.0)))
    band_l=max(2,int(2+(W-4)*(tgt-tol)/100.0))
    band_r=min(W-3,int(2+(W-4)*(tgt+tol)/100.0))
    sh(win,wave_y,band_l,"▓",max(0,band_r-band_l+1),cp(C_AMBER,dim=True))
    sa(win,max(1,wave_y-2),max(1,tgt_x-3),"TARGET",cp(C_AMBER,bold=True))
    sa(win,wave_y-1,tgt_x,"▼",cp(C_AMBER,bold=True))
    cur=s["current"]
    cur_x=max(2,min(W-3,int(2+(W-4)*cur/100.0)))
    sh(win,wave_y,2,"░",W-4,cp(C_DIM))
    sh(win,wave_y,2,"█",max(0,cur_x-2),cp(val_col(cur)))
    in_zone=band_l<=cur_x<=band_r
    sa(win,wave_y,cur_x,"▲",cp(C_GREEN if in_zone else C_RED,bold=True))
    sa(win,wave_y+1,cur_x,"│",cp(C_GREEN if in_zone else C_RED))
    sa(win,wave_y-1,2,"0%",cp(C_DIM));sa(win,wave_y-1,W-5,"100%",cp(C_DIM))
    sa(win,wave_y+2,2,f"CURRENT:{cur:.1f}%",cp(val_col(cur),bold=True))
    sa(win,wave_y+2,W//2-4,f"TARGET:{tgt:.1f}%",cp(C_AMBER,bold=True))
    zt="◈ IN ZONE! +pts ◈" if in_zone else "  OUT OF ZONE  "
    sa(win,wave_y+3,W//2-len(zt)//2,zt,cp(C_GREEN if in_zone else C_RED,bold=True))
    if s["history"]:
        sec(win,wave_y+5,1,W-2,"HISTORY")
        spark="▁▂▃▄▅▆▇█"
        for hi2,hv in enumerate(s["history"][-(W-4):]):
            ii=min(7,int(hv/100.0*7))
            vc=C_GREEN if band_l<=int(2+(W-4)*hv/100.0)<=band_r else C_DIM
            sa(win,wave_y+6,2+hi2,spark[ii],cp(vc))
    sa(win,H-2,1,s["msg"][:W-3],cp(C_DIM))
    sa(win,H-1,1,"HOLD SPACE=raise sync  ESC=exit",cp(C_DIM,dim=True))
    if s["phase"]=="win":
        m=f"CALIBRATION COMPLETE!  SCORE:{s['score']}"
        sa(win,H//2,max(1,W//2-len(m)//2),m,cp(C_GREEN,bold=True))

# ══ TRIVIA ══════════════════════════════════════════════════════════════════
def draw_game_nerv(win,H,W):
    t=trv;win.erase()
    box(win,0,0,H,W,"NERV TRIVIA",style=BS_GAME,bcol=C_MAGENTA,tcol=C_MAGENTA)
    if t["phase"]=="play":
        qs=t["shuffled_qs"]
        if t["q_idx"]<len(qs):
            q,ans,opts=qs[t["q_idx"]]
            # Question
            sa(win,2,2,f"Q{t['q_idx']+1}/{len(qs)}",cp(C_AMBER,bold=True))
            qlines=textwrap.wrap(q,W-6) or[q[:W-6]]
            for li,ql in enumerate(qlines):sa(win,2+li,8,ql,cp(C_ORANGE,bold=True))
            sh(win,3+len(qlines),2,"─",W-4,cp(C_DIM))
            # Options
            for i,opt in enumerate(opts):
                sel=i==t["selected"]
                sy=5+len(qlines)+i*2
                if sy>=H-5:break
                if sel:sh(win,sy,3," ",W-5,cp(C_ORANGE_BG))
                sa(win,sy,4,("▶ " if sel else "  ")+f"[{i+1}] {opt}",
                   cp(C_GREEN if sel else C_DIM,bold=sel))
            if t["answered"]:
                ok="CORRECT" in t["result"]
                sa(win,H-5,2,t["result"][:W-4],cp(C_GREEN if ok else C_RED,bold=True))
                sa(win,H-4,2,"Press ENTER for next question",cp(C_DIM))
            else:
                sa(win,H-4,2,"↑↓:select  ENTER:confirm",cp(C_DIM))
            # Progress bar
            pct=t["q_idx"]/len(qs)*100
            sa(win,H-3,2,f"SCORE:{t['score']}/{len(qs)}  ",cp(C_AMBER,bold=True))
            sa(win,H-3,18,mkbar(pct,min(20,W-22)),cp(C_AMBER))
        else:t["phase"]="done"
    elif t["phase"]=="done":
        total=len(trv["shuffled_qs"]);pct2=int(trv["score"]/total*100)
        grade="S" if pct2>=90 else "A" if pct2>=70 else "B" if pct2>=50 else "C"
        m=f"FINAL: {trv['score']}/{total} ({pct2}%) — GRADE {grade}"
        sa(win,H//2,max(1,W//2-len(m)//2),m,cp(C_GREEN if pct2>=70 else C_RED,bold=True))
        cmt={"S":"MAGI recognizes your worth.","A":"NERV welcomes you, pilot.",
             "B":"More training required.","C":"You are not ready."}
        c=cmt[grade]
        sa(win,H//2+2,max(1,W//2-len(c)//2),c,cp(C_DIM))
        sa(win,H//2+4,W//2-6,"ESC to return",cp(C_DIM))

# ══ SEELE OVERLAY ═══════════════════════════════════════════════════════════
def draw_seele_overlay(win,H,W):
    win.erase()
    for r in range(H):sh(win,r,0," ",W,cp(C_MAGENTA))
    title="SEELE — HUMAN INSTRUMENTALITY COMMITTEE"
    sa(win,1,max(0,W//2-len(title)//2),title,cp(C_WHITE,bold=True))
    # SEELE number indicator
    sa(win,1,2,"GEHIRN / SEELE",cp(C_MAGENTA,dim=True))
    sa(win,1,W-16,"SOUND ONLY",cp(C_MAGENTA,dim=True))
    sh(win,2,2,"━",W-4,cp(C_MAGENTA))
    per_row=4;mon_w=max(18,(W-4)//per_row);mon_h=4;sy=4
    for i in range(12):
        row=i//per_row;col=i%per_row
        mx=2+col*mon_w;my=sy+row*(mon_h+1)
        if my+mon_h>=H-4 or mx+mon_w>=W:break
        box(win,my,mx,mon_h,mon_w-1,style=BS_SEELE,bcol=C_MAGENTA,tcol=C_WHITE)
        sa(win,my+1,mx+2,f"SEELE {i+1:02d}",cp(C_WHITE,bold=True))
        sa(win,my+2,mx+2,"SOUND ONLY" if i==0 else "CONNECTED",cp(C_MAGENTA,dim=True))
    sa(win,H-4,max(0,W//2-17),"The scenario proceeds as planned.",cp(C_WHITE))
    sa(win,H-3,max(0,W//2-19),"Third Impact is the will of mankind.",cp(C_WHITE,dim=True))
    sh(win,H-2,2,"━",W-4,cp(C_MAGENTA))
    sa(win,H-1,max(0,W//2-10),"  PRESS S TO CLOSE  ",cp(C_WHITE,bold=True))

def render(stdscr,H,W):
    global tick;tick+=1
    # Advance hospital typewriter animation every frame
    if hospital["active"]:tick_hospital()
    if hospital["active"]:draw_hospital(stdscr,H,W);return
    if seele_mode:draw_seele_overlay(stdscr,H,W);return
    top_h=1;bot_h=1;mid_h=H-2
    left_w=min(32,max(20,W//4))
    right_w=min(30,max(18,W//5))
    cen_w=W-left_w-right_w
    alert_h=max(4,mid_h*2//5)
    comm_h=mid_h-alert_h
    try:
        w_top  =stdscr.derwin(top_h,  W,       0,             0)
        w_alert=stdscr.derwin(alert_h,right_w, top_h,         left_w+cen_w)
        w_comm =stdscr.derwin(comm_h, right_w, top_h+alert_h, left_w+cen_w)
        w_bot  =stdscr.derwin(bot_h,  W,       H-1,           0)
    except curses.error:
        sa(stdscr,H//2,2,"RESIZE TERMINAL (min 80x24)",cp(C_RED,bold=True))
        stdscr.refresh();return
    try:
        draw_topbar(w_top,W)
        draw_alert_panel(w_alert,alert_h,right_w)
        draw_comm_panel(w_comm,comm_h,right_w)
        draw_statusbar(w_bot,W)
        caw=left_w+cen_w
        if game_mode=="attack":
            wg=stdscr.derwin(mid_h,caw,top_h,0)
            draw_game_attack(wg,mid_h,caw);wg.noutrefresh()
        elif game_mode=="sync":
            wg=stdscr.derwin(mid_h,caw,top_h,0)
            draw_game_sync(wg,mid_h,caw);wg.noutrefresh()
        elif game_mode=="nerv":
            wg=stdscr.derwin(mid_h,caw,top_h,0)
            draw_game_nerv(wg,mid_h,caw);wg.noutrefresh()
        elif game_mode=="battle":
            wg=stdscr.derwin(mid_h,caw,top_h,0)
            draw_battle_panel(wg,mid_h,caw);wg.noutrefresh()
        elif view_mode=="deploy":
            ww=stdscr.derwin(mid_h,caw,top_h,0)
            draw_deploy_panel(ww,mid_h,caw);ww.noutrefresh()
        elif view_mode=="loadout":
            ww=stdscr.derwin(mid_h,caw,top_h,0)
            draw_loadout_panel(ww,mid_h,caw);ww.noutrefresh()
        elif view_mode=="field":
            wl=stdscr.derwin(mid_h,left_w,top_h,0)
            wc=stdscr.derwin(mid_h,cen_w,top_h,left_w)
            draw_eva_panel(wl,mid_h,left_w)
            draw_field_panel(wc,mid_h,cen_w)
            wl.noutrefresh();wc.noutrefresh()
        elif view_mode=="angel":
            wl=stdscr.derwin(mid_h,left_w,top_h,0)
            wc=stdscr.derwin(mid_h,cen_w,top_h,left_w)
            draw_eva_panel(wl,mid_h,left_w)
            draw_angel_panel(wc,mid_h,cen_w)
            wl.noutrefresh();wc.noutrefresh()
        else:  # main
            wl=stdscr.derwin(mid_h,left_w,top_h,0)
            wc=stdscr.derwin(mid_h,cen_w,top_h,left_w)
            draw_eva_panel(wl,mid_h,left_w)
            draw_magi_panel(wc,mid_h,cen_w)
            wl.noutrefresh();wc.noutrefresh()
        stdscr.noutrefresh()
        w_top.noutrefresh();w_alert.noutrefresh()
        w_comm.noutrefresh();w_bot.noutrefresh()
        curses.doupdate()
    except curses.error:pass

# ══ BATTLE LOGIC ════════════════════════════════════════════════════════════
def start_battle(eva_list):
    global game_mode
    battle.update({"active":True,"eva_party":list(eva_list),"active_eva":0,
                   "phase":"PLAYER_TURN","cursor":0,"log":[],"turn":1,
                   "anim_frames":0,"shield_turns":0,"sub_menu":None,"item_sel":0,
                   "items":{"N2 MINE":1,"REPAIR KIT":2,"LCL BOOST":2}})
    for ek in eva_list:
        d=eva_units[ek]
        d["battle_hp"]=d["battle_max_hp"]
    ang_data=ANGELS[angel_idx % len(ANGELS)]
    angel.update({**ang_data,"alive":True,"status_effect":None,"charge":0,"angel_stun":0})
    game_mode="battle"
    wlog(f"BATTLE: {angel['class']} — HP:{angel['hp']} ATF:{angel['atf']}%")
    for ab in angel["abilities"][:2]:wlog(f"  Can use: {ab}")
    alerts.appendleft(("CRIT",f"COMBAT: {angel['class']} INITIATED"))

def battle_player_action(action):
    b=battle
    if b["phase"]!="PLAYER_TURN":return
    ek=b["eva_party"][b["active_eva"]]
    d=eva_units[ek]
    pdata=PILOTS.get(d["pilot"],{})
    atk_m=pdata.get("stat_atk",1.0)
    def_m=pdata.get("stat_def",1.0)
    b["last_action"]=action

    if action=="ATTACK":
        aw=d.get("active_weapon",0)
        # Filter out None slots
        valid_load=[w for w in d.get("loadout",[]) if w]
        if not valid_load:wlog("No weapon equipped! Use loadout editor."); return
        aw=min(aw,len(valid_load)-1)
        wname=valid_load[aw]
        wd=WEAPON_CATALOGUE.get(wname,{})
        if wd.get("type") in("DEFENSE","UTILITY"):
            wlog(f"{wname} can't attack!");return
        ammo=d["ammo"].get(wname,0)
        if ammo==0 and wd.get("ammo",99)<99:
            wlog(f"{wname} out of ammo!");return
        acc=wd.get("acc",75)
        atf_pen=int(angel.get("atf",60)/100*20)
        eff_acc=max(10,acc-atf_pen)
        hit=random.randint(1,100)<=eff_acc
        if hit:
            dmin,dmax=wd.get("dmg",(5,15))
            dmg=int(random.randint(dmin,dmax)*atk_m)
            if d["sync"]>90:dmg=int(dmg*1.2)
            if wd.get("type")=="BOMB":dmg=int(dmg*1.5)
            if wname=="DUMMY PLUG":dmg=int(dmg*1.2)
            angel["hp"]=max(0,angel["hp"]-dmg)
            if ammo<99:d["ammo"][wname]=max(0,ammo-1)
            b["anim_frames"]=5
            pilot_q=PILOT_QUOTES.get(d["pilot"],{})
            attack_q=random.choice(pilot_q.get("attack",["Attacking!"]))
            wlog(f"{ek}: {attack_q}")
            wlog(f"▸{wname}: HIT -{dmg}HP [acc:{eff_acc}%]")
            if wname=="PROG KNIFE" and random.random()<0.18:
                angel["angel_stun"]=1
                wlog("Critical! Angel stunned!")
            if angel["hp"]<=0:
                angel["alive"]=False;b["phase"]="WIN"
                wlog(f"ANGEL {angel['class']} NEUTRALIZED!")
                pq=PILOT_QUOTES.get(d["pilot"],{})
                wq=random.choice(pq.get("win",["Victory!"]))
                wlog(f"{d['pilot']}: {wq}")
                alerts.appendleft(("OK","BATTLE WON — ANGEL DOWN"))
                return
        else:
            wlog(f"{ek}▸{wname}: MISS [acc:{eff_acc}%  atf:{angel['atf']}%]")
        b["phase"]="ANGEL_TURN";b["turn"]+=1

    elif action=="AT FIELD":
        b["shield_turns"]=3
        d["atf"]=min(100.0,d["atf"]+12)
        wlog(f"{ek}: AT field! Shield x3 turns. ATF:{d['atf']:.0f}%")
        b["anim_frames"]=3;b["phase"]="ANGEL_TURN";b["turn"]+=1

    elif action=="FLEE":
        wlog("Retreating from battle!");b["phase"]="LOSE"

def battle_angel_turn():
    b=battle
    ang=angel
    if ang.get("angel_stun",0)>0:
        ang["angel_stun"]-=1
        wlog(f"{ang['class']}: stunned! Skips turn.")
        b["phase"]="PLAYER_TURN";return
    ek=b["eva_party"][b["active_eva"]]
    d=eva_units[ek]
    pdata=PILOTS.get(d["pilot"],{})
    def_m=pdata.get("stat_def",1.0)
    ability=random.choice(ang.get("abilities",["ENERGY_BLAST"]))
    b["last_action"]=ability;b["anim_frames"]=4

    if ability in("ENERGY_BLAST","WHIP_LASH","BITE_ATTACK","WATER_SLAM"):
        dmg=int(random.randint(ang["atk_min"],ang["atk_max"])/def_m)
        if b["shield_turns"]>0:
            dmg=max(1,int(dmg*0.4));b["shield_turns"]-=1
            wlog(f"{ang['class']}▸{ability}: Shield! -{dmg}HP")
        else:
            wlog(f"{ang['class']}▸{ability}: -{dmg}HP!")
        d["battle_hp"]=max(0,d["battle_hp"]-dmg)
    elif ability=="AT_FIELD":
        ang["atf"]=min(100,ang.get("atf",60)+8)
        wlog(f"{ang['class']}: AT field up! ATF:{ang['atf']}%")
    elif ability=="CORE_REGEN":
        r=random.randint(8,18);ang["hp"]=min(ang["max_hp"],ang["hp"]+r)
        wlog(f"{ang['class']}: Regen +{r}HP")
    elif ability=="PARTICLE_CANNON":
        dmg=int(random.randint(ang["atk_min"]*2,ang["atk_max"]*2)/def_m)
        if b["shield_turns"]>0:dmg=int(dmg*0.6);b["shield_turns"]=max(0,b["shield_turns"]-1)
        d["battle_hp"]=max(0,d["battle_hp"]-dmg)
        wlog(f"{ang['class']}▸PARTICLE CANNON: -{dmg}HP!!")
    elif ability=="DOUBLE_STRIKE":
        for _ in range(2):
            dmg=int(random.randint(ang["atk_min"]//2,ang["atk_max"]//2)/def_m)
            if b["shield_turns"]>0:dmg=int(dmg*0.5);b["shield_turns"]=max(0,b["shield_turns"]-1)
            d["battle_hp"]=max(0,d["battle_hp"]-dmg)
        wlog(f"{ang['class']}▸DOUBLE STRIKE: hit twice!")
    elif ability=="DRILL":
        dmg=int(random.randint(ang["atk_min"],ang["atk_max"]))
        d["battle_hp"]=max(0,d["battle_hp"]-dmg)
        wlog(f"{ang['class']}▸DRILL: pierces shield! -{dmg}HP")

    # Check EVA down
    # Pilot reacts to taking damage
    if d["battle_hp"]>0:
        pq=PILOT_QUOTES.get(d["pilot"],{})
        hq=random.choice(pq.get("hit",["Taking damage!"]))
        if random.random()<0.4:wlog(f"{d['pilot']}: {hq}")
    if d["battle_hp"]<=0:
        wlog(f"{ek} is DOWN!")
        nxt=next((i for i,e in enumerate(b["eva_party"])
                  if i!=b["active_eva"] and eva_units[e]["battle_hp"]>0),None)
        if nxt is not None:
            b["active_eva"]=nxt
            wlog(f"Auto-switch to {b['eva_party'][nxt]}!")
            b["phase"]="PLAYER_TURN"
        else:
            b["phase"]="LOSE"
            wlog("All EVAs defeated.");alerts.appendleft(("CRIT","ALL EVAS DOWN"))
        return
    b["phase"]="PLAYER_TURN"

# ══ THREADS ═════════════════════════════════════════════════════════════════
def thread_fluctuate():
    while run:
        time.sleep(0.55)
        with lock:
            for uname,d in eva_units.items():
                for key in["sync","pwr","atf","armor","lcl"]:
                    d[key]=max(1.0,min(100.0,d[key]+random.gauss(0,0.5)))
                if uname=="EVA-01" and d["sync"]>97 and random.random()<0.015:
                    if d["status"] not in("BERSERK","STANDBY"):
                        d["status"]="BERSERK";d["unit_col"]=C_RED
                        alerts.appendleft(("CRIT","EVA-01 BERSERK!"))
                        comm_log.append(("RITSUKO","EVA-01 BERSERK MODE!"))
                        comm_log.append(("MISATO","Shinji! Stay conscious!"))
                elif uname=="EVA-01" and d["sync"]<88 and d["status"]=="BERSERK":
                    d["status"]="ACTIVE";d["unit_col"]=C_GREEN
                    alerts.appendleft(("OK","EVA-01 BERSERK SUBSIDING"))
                if d["lcl"]<28 and d["status"] not in("STANDBY","BERSERK") and random.random()<0.04:
                    alerts.appendleft(("CRIT",f"{uname} LCL CRITICAL"))
            if angel["alive"] and game_mode not in("battle",):
                angel["range_km"]=max(0.2,angel["range_km"]-random.uniform(0,0.025))
                angel["bearing"]=(angel["bearing"]+random.randint(-2,2))%360
                ax,ay=angel["pos"]
                targets=[d["pos"] for d in eva_units.values() if d["deployed"]]
                if targets and random.random()<0.22:
                    tx,ty=min(targets,key=lambda t:dist(ax,ay,t[0],t[1]))
                    nx=ax+(-1 if ax>tx else 1 if ax<tx else 0)
                    ny=ay+(-1 if ay>ty else 1 if ay<ty else 0)
                    angel["pos"]=(max(0,min(FIELD_W-1,nx)),max(0,min(FIELD_H-1,ny)))
            # Attack arcade physics
            if game_mode=="attack" and atk["phase"]=="play":
                a=atk
                a["angel_x"]+=a["angel_vx"]*0.9
                a["angel_y"]+=a["angel_vy"]*0.6
                xmax=a.get("xmax",55);ymax=a.get("ymax",16)
                if a["angel_x"]<2 or a["angel_x"]>xmax:a["angel_vx"]*=-1
                if a["angel_y"]<2 or a["angel_y"]>ymax:a["angel_vy"]*=-1
                a["angel_x"]=max(2.0,min(float(xmax),a["angel_x"]))
                a["angel_y"]=max(2.0,min(float(ymax),a["angel_y"]))
                a["shots"]=[(x,y,ag+1,pt) for x,y,ag,pt in a["shots"] if ag<7]
                if a["flash"]>0:a["flash"]-=1
                if a.get("eva_flash",0)>0:a["eva_flash"]-=1
                # Angel fires back
                a["angel_charge"]=a.get("angel_charge",0)+1
                fire_rate=max(6,20-a.get("level",1)*2)
                if a["angel_charge"]>=fire_rate:
                    a["angel_charge"]=0
                    dmg=random.randint(5,15)
                    if a.get("shield_on",False):
                        dmg=max(1,dmg//3);a["msg"]=f"Shield blocked! -{dmg}%"
                    else:
                        a["msg"]=f"Angel fires back! -{dmg}%"
                    a["eva_hp"]=max(0,a["eva_hp"]-dmg)
                    a["eva_flash"]=4
                    if a["eva_hp"]<=0:
                        a["phase"]="lose"
                        alerts.appendleft(("CRIT","COMBAT SIM: EVA DESTROYED"))
                if a.get("shield_on") and a.get("shield_turns",0)>0:
                    a["shield_turns"]-=1
                    if a["shield_turns"]<=0:a["shield_on"]=False;a["msg"]="Shield expired."
                if tick%17==0 and a["time_left"]>0:
                    a["time_left"]-=1
                    if a["time_left"]<=0 and a["phase"]=="play":
                        a["phase"]="lose"
                        alerts.appendleft(("CRIT","COMBAT SIM: TIME EXPIRED"))
            # Sync game target
            if game_mode=="sync" and syn["phase"]=="play":
                syn["wave_phase"]=(syn["wave_phase"]+0.05)%360
                syn["target"]=50+30*math.sin(math.radians(syn["wave_phase"]))
            # Battle anim countdown
            if game_mode=="battle" and battle["anim_frames"]>0:
                battle["anim_frames"]-=1

def thread_alerts():
    while run:
        time.sleep(random.uniform(5,10))
        with lock:alerts.appendleft(random.choice(alert_pool))

def thread_reticle():
    global reticle_ang
    while run:
        time.sleep(0.06)
        with lock:reticle_ang=(reticle_ang+2)%360

# ══ COMMAND HANDLER ═════════════════════════════════════════════════════════
def handle_command(raw):
    global game_mode,view_mode
    cmd=raw.strip().lower()
    if not cmd:return
    comm_log.append(("YOU",f"> {cmd}"))
    p=cmd.split()

    def get_uk(token):
        t=token.upper()
        return f"EVA-{t}" if not t.startswith("EVA") else t

    if p[0]=="pilot" and len(p)>=3:
        uk=get_uk(p[1])
        search=" ".join(x.upper() for x in p[2:])
        matched=next((k for k in PILOTS if any(w in k for w in search.split())),None)
        if uk in eva_units and matched:
            old=eva_units[uk]["pilot"]
            eva_units[uk]["pilot"]=matched
            eva_units[uk]["sync"]=min(100.0,PILOTS[matched]["sync_base"]+random.uniform(-3,3))
            comm_log.append(("RITSUKO",f"{uk}: {old} → {matched}"))
            comm_log.append(("MAGI",f"SYNC: {eva_units[uk]['sync']:.1f}%"))
            alerts.appendleft(("INFO",f"PILOT: {uk}"))
        else:
            comm_log.append(("MAGI","PILOTS: SHINJI REI ASUKA KAWORU YUI"))
        return
    if p[0]=="swap" and len(p)==3:
        u1=get_uk(p[1]);u2=get_uk(p[2])
        if u1 in eva_units and u2 in eva_units:
            pl1=eva_units[u1]["pilot"];pl2=eva_units[u2]["pilot"]
            eva_units[u1]["pilot"]=pl2;eva_units[u2]["pilot"]=pl1
            eva_units[u1]["sync"]=PILOTS.get(pl2,{}).get("sync_base",50)+random.uniform(-3,3)
            eva_units[u2]["sync"]=PILOTS.get(pl1,{}).get("sync_base",50)+random.uniform(-3,3)
            comm_log.append(("RITSUKO",f"SWAP: {u1}↔{u2}"))
        else:comm_log.append(("MAGI","USAGE: swap 01 02"))
        return
    if p[0]=="deploy" and len(p)>=2:
        uk=get_uk(p[1])
        if uk in eva_units:
            d=eva_units[uk]
            if d["deployed"]:comm_log.append(("MAGI",f"{uk} already deployed."))
            else:
                d["deployed"]=True;d["status"]="ACTIVE";deploy_choices[uk]=True
                comm_log.append(("MISATO",f"{uk} launch!"))
                alerts.appendleft(("OK",f"{uk} DEPLOYED"))
        else:comm_log.append(("MAGI","USAGE: deploy 00/01/02"))
        return
    if p[0]=="recall" and len(p)>=2:
        uk=get_uk(p[1])
        if uk in eva_units:
            eva_units[uk]["deployed"]=False;eva_units[uk]["status"]="STANDBY"
            deploy_choices[uk]=False
            comm_log.append(("MISATO",f"{uk} recalled."))
        else:comm_log.append(("MAGI","USAGE: recall 01"))
        return
    if p[0]=="eject" and len(p)>=2:
        uk=get_uk(p[1])
        if uk in eva_units:
            eva_units[uk]["status"]="STANDBY";eva_units[uk]["deployed"]=False
            deploy_choices[uk]=False
            comm_log.append(("MAGI",f"{uk} EJECT AUTHORIZED"))
        else:comm_log.append(("MAGI","USAGE: eject 02"))
        return
    if p[0]=="move" and len(p)==4:
        uk=get_uk(p[1])
        try:
            nx=max(0,min(FIELD_W-1,int(p[2])));ny=max(0,min(FIELD_H-1,int(p[3])))
            if uk in eva_units:
                eva_units[uk]["pos"]=(nx,ny)
                if not eva_units[uk]["deployed"]:eva_units[uk]["deployed"]=True;eva_units[uk]["status"]="ACTIVE"
                comm_log.append(("MAGI",f"{uk} → ({nx},{ny})"))
            else:comm_log.append(("MAGI","USAGE: move 01 15 8"))
        except ValueError:comm_log.append(("MAGI","USAGE: move <unit> <x> <y>"))
        return
    if p[0]=="advance" and len(p)>=2:
        uk=get_uk(p[1])
        if uk in eva_units and angel["alive"]:
            d=eva_units[uk];ex,ey=d["pos"];ax2,ay2=angel["pos"]
            nx=ex+(-1 if ex>ax2 else 1 if ex<ax2 else 0)
            ny=ey+(-1 if ey>ay2 else 1 if ey<ay2 else 0)
            d["pos"]=(max(0,min(FIELD_W-1,nx)),max(0,min(FIELD_H-1,ny)))
            if not d["deployed"]:d["deployed"]=True;d["status"]="ACTIVE"
            comm_log.append(("MISATO",f"{uk} advancing. Range:{dist(nx,ny,ax2,ay2):.1f}"))
        else:comm_log.append(("MAGI","USAGE: advance 01"))
        return
    if p[0]=="fire" and len(p)>=2:
        uk=get_uk(p[1])
        if uk in eva_units and angel["alive"]:
            d=eva_units[uk];ex,ey=d["pos"];ax2,ay2=angel["pos"]
            d_to=dist(ex,ey,ax2,ay2)
            aw=d.get("active_weapon",0);aw=min(aw,len(d["loadout"])-1)
            wname=d["loadout"][aw] if d["loadout"] else None
            if not wname:comm_log.append(("MAGI","No weapon!"));return
            wd=WEAPON_CATALOGUE.get(wname,{})
            rng=wd.get("rng",1)+1;ammo=d["ammo"].get(wname,0)
            if d_to>rng:comm_log.append(("RITSUKO",f"Range:{d_to:.1f}>{rng}. Advance first."))
            elif ammo==0 and wd.get("ammo",99)<99:comm_log.append(("RITSUKO",f"{wname} out of ammo!"))
            else:
                dmg=random.randint(*wd.get("dmg",(5,15)))
                if ammo<99:d["ammo"][wname]=max(0,ammo-1)
                angel["hp"]=max(0,angel["hp"]-dmg)
                comm_log.append(("MISATO",f"{uk} fires {wname}! -{dmg}HP"))
                comm_log.append(("RITSUKO",f"Angel HP:{angel['hp']}/{angel['max_hp']}"))
                alerts.appendleft(("WARN",f"ANGEL HIT HP:{angel['hp']}"))
                if angel["hp"]<=0:
                    angel["alive"]=False
                    comm_log.append(("MISATO","ANGEL NEUTRALIZED!"))
                    alerts.appendleft(("OK","ANGEL NEUTRALIZED"))
        else:comm_log.append(("MAGI","USAGE: fire 01"))
        return
    if p[0]=="repair" and len(p)>=2:
        uk=get_uk(p[1])
        if uk in eva_units:
            d=eva_units[uk]
            d["armor"]=min(100,d["armor"]+random.uniform(15,28))
            d["pwr"]=min(100,d["pwr"]+random.uniform(10,20))
            d["battle_hp"]=min(d["battle_max_hp"],d["battle_hp"]+30)
            if d["status"]=="CRITICAL":d["status"]="STANDBY"
            comm_log.append(("RITSUKO",f"{uk} repaired. HP:{d['battle_hp']}/{d['battle_max_hp']}"))
        else:comm_log.append(("MAGI","USAGE: repair 02"))
        return
    if p[0]=="boost" and len(p)>=2:
        uk=get_uk(p[1])
        if uk in eva_units:
            d=eva_units[uk]
            d["atf"]=min(100,d["atf"]+random.uniform(18,32))
            d["sync"]=min(100,d["sync"]+random.uniform(5,10))
            comm_log.append(("RITSUKO",f"{uk} ATF boosted: {d['atf']:.0f}%"))
        else:comm_log.append(("MAGI","USAGE: boost 01"))
        return
    if cmd=="kill angel":
        angel["alive"]=False;angel["hp"]=0
        comm_log.append(("MAGI","ANGEL NEUTRALIZED"))
        alerts.appendleft(("OK","ANGEL CLEARED"));return
    if cmd=="revive angel":
        global angel_idx
        angel_idx=(angel_idx+1)%len(ANGELS)  # cycle to next angel
        ang_data=ANGELS[angel_idx%len(ANGELS)]
        angel.update({**ang_data,"alive":True,"pos":(24,3),"range_km":3.0,
                      "bearing":247,"status_effect":None,"charge":0,"angel_stun":0})
        comm_log.append(("RITSUKO",f"Angel class: {angel['class']}"))
        comm_log.append(("MAGI","ANGEL SIGNAL REACQUIRED"))
        alerts.appendleft(("CRIT","ANGEL REVIVED"));return
    if cmd.startswith("bearing "):
        try:angel["bearing"]=int(cmd.split()[1])%360;comm_log.append(("MAGI",f"BEARING:{angel['bearing']}°"))
        except:comm_log.append(("MAGI","USAGE: bearing <deg>"))
        return
    if cmd.startswith("range "):
        try:angel["range_km"]=float(cmd.split()[1]);comm_log.append(("MAGI",f"RANGE:{angel['range_km']:.2f}km"))
        except:comm_log.append(("MAGI","USAGE: range <km>"))
        return
    if cmd=="clear":
        comm_log.clear();comm_log.append(("MAGI","LOG CLEARED."));return
    if cmd.startswith("alert "):
        global ALERT_LEVEL
        try:
            lvl=int(cmd.split()[1])
            if 1<=lvl<=3:
                ALERT_LEVEL=lvl
                name=ALERT_NAMES[lvl]
                comm_log.append(("HYUGA",f"ALERT LEVEL {lvl}: {name}"))
                comm_log.append(("MISATO",{1:"All clear.",2:"Battle stations on standby.",3:"LAUNCH ALL EVAS NOW!"}[lvl]))
                alerts.appendleft(({1:"OK",2:"WARN",3:"CRIT"}[lvl],f"ALERT LVL {lvl}: {name}"))
            else:comm_log.append(("MAGI","ALERT LEVEL: 1, 2, or 3 only"))
        except:comm_log.append(("MAGI","USAGE: alert <1/2/3>"))
        return
    if cmd=="sync up":
        for uk,d in eva_units.items():
            boost=random.uniform(3,10)
            d["sync"]=min(100,d["sync"]+boost)
        for sp,tx in CMD_DB["sync up"]:comm_log.append((sp,tx))
        return
    if cmd=="hospital":
        # ░░ EASTER EGG — ASCII video player ░░
        # To watch the real video, exit NERV and run in your terminal:
        #   mpv --vo=tct "https://www.youtube.com/watch?v=56GlnLQTK6M"
        # or install: pkg install mpv yt-dlp
        hospital.update({"active":True,"scene":0,"tick":0,"phase":0,"done":False})
        comm_log.append(("MAGI","ACCESSING PSYCHOLOGICAL FILE..."))
        comm_log.append(("MAGI","SUBJECT: IKARI SHINJI // LEVEL 5"))
        comm_log.append(("MAGI","Tip: For real video run outside NERV:"))
        comm_log.append(("MAGI","  mpv --vo=tct https://www.youtube.com/watch?v=56GlnLQTK6M"))
        alerts.appendleft(("INFO","NERV PSYCH FILE — PLAYING"))
        return
    if cmd=="game attack":
        for sp,tx in CMD_DB["game attack"]:comm_log.append((sp,tx))
        game_mode="attack";reset_attack();return
    if cmd=="game sync":
        for sp,tx in CMD_DB["game sync"]:comm_log.append((sp,tx))
        game_mode="sync";reset_sync();return
    if cmd=="game nerv":
        for sp,tx in CMD_DB["game nerv"]:comm_log.append((sp,tx))
        game_mode="nerv";reset_trivia();return
    if cmd in CMD_DB:
        lines=CMD_DB[cmd]
        if cmd=="quote":sp,tx=random.choice(lines);comm_log.append((sp,tx))
        else:
            for sp,tx in lines:comm_log.append((sp,tx))
        return
    # Fuzzy match partial commands
    partial_matches=[k for k in CMD_DB if cmd in k or k.startswith(cmd.split()[0] if cmd.split() else "")]
    if partial_matches:
        comm_log.append(("MAGI",f"Did you mean: {', '.join(partial_matches[:4])}?"))
    else:
        comm_log.append(("MAGI",f"UNKNOWN: {cmd.upper()}"))
        comm_log.append(("MAGI","TYPE 'help' FOR COMMANDS."))

# ══ GAME RESETS ═════════════════════════════════════════════════════════════
def reset_attack():
    atk.update({"cx":20,"cy":8,"angel_x":30.0,"angel_y":6.0,
                 "angel_vx":1.2,"angel_vy":0.8,"shots":[],
                 "score":0,"hits":0,"misses":0,"ammo":20,"hp":5,"eva_hp":100,
                 "flash":0,"eva_flash":0,
                 "msg":"WASD=move SPACE=fire F=power Z=shield",
                 "phase":"play","time_left":90,"xmax":55,"ymax":16,
                 "power_shots":3,"shield_on":False,"shield_turns":0,
                 "angel_charge":0,"level":1})

def reset_sync():
    syn.update({"target":50.0,"current":50.0,"velocity":0.0,"wave_phase":0.0,
                 "score":0,"streak":0,"best_streak":0,"rounds":0,"max_rounds":12,
                 "msg":"Hold SPACE to raise sync. Match the target!",
                 "phase":"play","history":[],"tolerance":8.0,"zone_ticks":0})

def reset_trivia():
    trv.update({"q_idx":0,"score":0,"answered":False,"selected":0,"result":"","phase":"play",
                 "shuffled_qs":random.sample(TRIVIA_QS,len(TRIVIA_QS))})

# ══ MAIN ════════════════════════════════════════════════════════════════════
def main(stdscr):
    global selected_magi,cmd_buffer,run,focus,view_mode,seele_mode,game_mode
    global cmd_history,hist_idx,field_sel,deploy_sel
    global loadout_unit_idx,loadout_slot_sel,loadout_wep_sel
    global angel_idx

    curses.curs_set(0);curses.start_color();curses.use_default_colors()
    if curses.COLORS>=256:
        curses.init_pair(C_ORANGE,208,-1);curses.init_pair(C_DIM,94,-1)
        curses.init_pair(C_AMBER,214,-1); curses.init_pair(C_RED,196,-1)
        curses.init_pair(C_GREEN,46,-1);  curses.init_pair(C_CYAN,51,-1)
        curses.init_pair(C_WHITE,15,-1);  curses.init_pair(C_MAGENTA,129,-1)
        curses.init_pair(C_ORANGE_BG,0,208);curses.init_pair(C_RED_BG,15,196)
    else:
        for ci,cc in[(C_ORANGE,curses.COLOR_RED),(C_DIM,curses.COLOR_RED),
                     (C_AMBER,curses.COLOR_YELLOW),(C_RED,curses.COLOR_RED),
                     (C_GREEN,curses.COLOR_GREEN),(C_CYAN,curses.COLOR_CYAN),
                     (C_WHITE,curses.COLOR_WHITE),(C_MAGENTA,curses.COLOR_MAGENTA)]:
            curses.init_pair(ci,cc,-1)
        curses.init_pair(C_ORANGE_BG,curses.COLOR_BLACK,curses.COLOR_RED)
        curses.init_pair(C_RED_BG,curses.COLOR_WHITE,curses.COLOR_RED)

    stdscr.timeout(50)
    for fn in[thread_fluctuate,thread_alerts,thread_reticle]:
        threading.Thread(target=fn,daemon=True).start()

    # vi stays synced to view_mode — always re-derive before use
    def get_vi():
        try:return views.index(view_mode)
        except ValueError:return 0
    vi=0  # just a starting value; always re-derived in V handler

    while run:
        H,W=stdscr.getmaxyx()
        if H<24 or W<80:
            stdscr.erase()
            sa(stdscr,H//2,2,f"NERV: TOO SMALL ({W}x{H}) — NEED 80x24+",cp(C_RED,bold=True))
            stdscr.refresh()
            if stdscr.getch() in(ord('q'),ord('Q')):run=False
            continue

        with lock:render(stdscr,H,W)
        key=stdscr.getch()

        # ── SYNC GAME physics (runs regardless of focus) ──────────────────────
        if game_mode=="sync" and syn["phase"]=="play":
            with lock:
                s=syn; pressing=(key==ord(' '))
                if pressing: s["velocity"]=min(s["velocity"]+1.5,8.0)
                else:        s["velocity"]=max(s["velocity"]-1.2,-5.0)
                s["current"]=max(0.0,min(100.0,s["current"]+s["velocity"]*0.18))
                s["history"].append(s["current"])
                in_z=abs(s["current"]-s["target"])<=s["tolerance"]
                if in_z:
                    s["zone_ticks"]+=1
                    if s["zone_ticks"]%10==0:
                        s["score"]+=10;s["streak"]+=1
                        s["best_streak"]=max(s["best_streak"],s["streak"])
                        s["rounds"]+=1
                        s["msg"]=f"LOCKED! +10 streak x{s['streak']}"
                        if s["rounds"]>=s["max_rounds"]:
                            s["phase"]="win"
                            alerts.appendleft(("OK","SYNC DONE"))
                else:
                    s["zone_ticks"]=0
                    if s["streak"]>0:s["msg"]=f"Streak broken at {s['streak']}!";s["streak"]=0
                    else:s["msg"]="Hold SPACE. Match the target."
            if key==27:game_mode=None
            elif key in(ord('q'),ord('Q')):run=False;break
            continue

        if key==-1:continue

        # ── HOSPITAL VIDEO ────────────────────────────────────────────────────
        if hospital["active"]:
            h=hospital
            if key==27:
                h["active"]=False;h["scene"]=0;h["tick"]=0
                comm_log.append(("MAGI","PSYCHOLOGICAL FILE CLOSED."))
            elif key!=-1:
                if h["done"] or h["scene"]>=len(HOSP_SCENES):
                    h["active"]=False;h["scene"]=0;h["tick"]=0
                    comm_log.append(("MAGI","RETURNING TO NORMAL OPERATIONS."))
                else:
                    _dur,_fn,_sfx=HOSP_SCENES[h["scene"]]
                    if _sfx=="done" or _dur==0:
                        h["active"]=False;h["scene"]=0;h["tick"]=0
                        comm_log.append(("MAGI","RETURNING TO NORMAL OPERATIONS."))
                    else:
                        h["scene"]+=1;h["tick"]=0
                        if h["scene"]>=len(HOSP_SCENES):h["done"]=True
            continue

        # ── ESC ───────────────────────────────────────────────────────────────
        if key==27:
            if game_mode:  game_mode=None
            elif seele_mode: seele_mode=False
            elif view_mode in("loadout","deploy"): view_mode="main"
            elif focus=="comm" and cmd_buffer: cmd_buffer=""
            continue

        # ══ GLOBAL HOTKEYS — work from ANY focus/view ════════════════════════
        # These are checked BEFORE focus-specific handling so they always work.

        if key in(ord('q'),ord('Q')) and focus!="comm":
            run=False;break

        # V — cycle view_mode only. NEVER changes focus.
        if key in(ord('v'),ord('V')):
            try:vi=views.index(view_mode)
            except ValueError:vi=0
            vi=(vi+1)%len(views)
            view_mode=views[vi]
            continue

        # S — seele overlay (only from magi/field focus, not comm)
        if key in(ord('s'),ord('S')) and focus in("magi","field"):
            seele_mode=not seele_mode;continue

        # K — kill angel (from magi/field)
        if key in(ord('k'),ord('K')) and focus!="comm":
            with lock:
                if angel["alive"]:
                    angel["alive"]=False
                    alerts.appendleft(("OK","ANGEL NEUTRALIZED"))
                    comm_log.append(("MAGI","PATTERN BLUE GONE."))
            continue

        # G — cycle minigames (from magi/field)
        if key in(ord('g'),ord('G')) and focus!="comm":
            gmc=[None,"attack","sync","nerv"]
            gi=gmc.index(game_mode) if game_mode in gmc else 0
            game_mode=gmc[(gi+1)%len(gmc)]
            if game_mode=="attack":reset_attack()
            elif game_mode=="sync":reset_sync()
            elif game_mode=="nerv":reset_trivia()
            continue

        # TAB — cycles focus ONLY. Never touches view_mode.
        if key==ord('\t'):
            idx2=FOCUS_ORDER.index(focus)
            focus=FOCUS_ORDER[(idx2+1)%len(FOCUS_ORDER)]
            continue

        # ══ GAME MODE INPUT ══════════════════════════════════════════════════

        if game_mode=="attack":
            a=atk
            if a["phase"]=="play":
                if   key in(curses.KEY_UP,   ord('w'),ord('W')): a["cy"]=max(2,a["cy"]-1)
                elif key in(curses.KEY_DOWN,  ord('s'),ord('S')): a["cy"]=min(H-9,a["cy"]+1)
                elif key in(curses.KEY_LEFT,  ord('a'),ord('A')): a["cx"]=max(2,a["cx"]-2)
                elif key in(curses.KEY_RIGHT, ord('d'),ord('D')): a["cx"]=min(W-35,a["cx"]+2)
                elif key in(ord(' '),curses.KEY_ENTER,ord('\n'),ord('\r')):
                    if a["ammo"]>0:
                        a["shots"].append((a["cx"],a["cy"],0,"normal"));a["ammo"]-=1
                        ax2,ay2=int(a["angel_x"]),int(a["angel_y"])
                        if abs(a["cx"]-ax2)<=3 and abs(a["cy"]-ay2)<=2:
                            a["hits"]+=1;a["score"]+=100;a["hp"]-=1;a["flash"]=5
                            a["msg"]=f"HIT! Score:{a['score']}"
                            if a["hp"]<=0:
                                a["phase"]="win";angel["alive"]=False
                                a["score"]+=a["time_left"]*5
                                alerts.appendleft(("OK","COMBAT SIM: ANGEL DOWN"))
                        else:
                            a["misses"]+=1;a["score"]=max(0,a["score"]-5)
                            a["msg"]=f"Miss! Ammo:{a['ammo']}"
                        if a["ammo"]<=0 and a["phase"]=="play":
                            a["phase"]="lose"
                elif key in(ord('f'),ord('F')):
                    if a["power_shots"]>0 and a["ammo"]>0:
                        a["shots"].append((a["cx"],a["cy"],0,"power"))
                        a["ammo"]-=1;a["power_shots"]-=1
                        ax2,ay2=int(a["angel_x"]),int(a["angel_y"])
                        if abs(a["cx"]-ax2)<=4 and abs(a["cy"]-ay2)<=3:
                            a["hits"]+=1;a["score"]+=250;a["hp"]=max(0,a["hp"]-2)
                            a["flash"]=7;a["msg"]=f"POWER HIT x2! Score:{a['score']}"
                            if a["hp"]<=0:a["phase"]="win";angel["alive"]=False
                        else:a["msg"]=f"Power miss. Pwrshots:{a['power_shots']}"
                elif key in(ord('z'),ord('Z')):
                    a["shield_on"]=True;a["shield_turns"]=5
                    a["msg"]="SHIELD ON (5 angel hits)"
            if key in(ord('q'),ord('Q')):run=False;break
            continue

        if game_mode=="nerv":
            t=trv;qs=t["shuffled_qs"]
            if t["phase"]=="play" and t["q_idx"]<len(qs):
                _,ans,opts=qs[t["q_idx"]]
                if not t["answered"]:
                    if   key in(curses.KEY_UP,  ord('w'),ord('W')): t["selected"]=(t["selected"]-1)%len(opts)
                    elif key in(curses.KEY_DOWN, ord('s'),ord('S')): t["selected"]=(t["selected"]+1)%len(opts)
                    elif key in(ord('\n'),ord('\r'),curses.KEY_ENTER):
                        t["answered"]=True;chosen=opts[t["selected"]]
                        if chosen==ans:t["score"]+=1;t["result"]="✓ CORRECT!  "+ans
                        else:t["result"]=f"✗ WRONG.  Answer: {ans}"
                elif key in(ord('\n'),ord('\r'),curses.KEY_ENTER):
                    t["q_idx"]+=1;t["answered"]=False;t["selected"]=0;t["result"]=""
                    if t["q_idx"]>=len(qs):t["phase"]="done"
            if key in(ord('q'),ord('Q')):run=False;break
            continue

        if game_mode=="battle":
            b=battle
            if b["phase"] in("PLAYER_TURN","SELECT"):
                if b["sub_menu"]=="item":
                    items=list(b["items"].items())
                    if key in(curses.KEY_LEFT, ord('a'),ord('A')): b["item_sel"]=(b["item_sel"]-1)%max(1,len(items))
                    elif key in(curses.KEY_RIGHT,ord('d'),ord('D')): b["item_sel"]=(b["item_sel"]+1)%max(1,len(items))
                    elif key in(ord('\n'),ord('\r'),curses.KEY_ENTER):
                        iname,cnt=items[b["item_sel"]%len(items)]
                        if cnt>0:
                            b["items"][iname]-=1
                            ek=b["eva_party"][b["active_eva"]];d=eva_units[ek]
                            if iname=="N2 MINE":
                                dmg=random.randint(50,80);angel["hp"]=max(0,angel["hp"]-dmg)
                                wlog(f"N2 MINE! -{dmg}HP → {angel['hp']}/{angel['max_hp']}")
                                if angel["hp"]<=0:angel["alive"]=False;b["phase"]="WIN"
                            elif iname=="REPAIR KIT":
                                heal=random.randint(25,40)
                                d["battle_hp"]=min(d["battle_max_hp"],d["battle_hp"]+heal)
                                wlog(f"Repair Kit! +{heal}HP → {d['battle_hp']}/{d['battle_max_hp']}")
                            elif iname=="LCL BOOST":
                                d["sync"]=min(100,d["sync"]+15)
                                wlog(f"LCL Boost! SYNC +15 → {d['sync']:.0f}%")
                            b["sub_menu"]=None
                            if b["phase"]!="WIN":b["phase"]="ANGEL_TURN";b["turn"]+=1
                        else:wlog(f"No {iname} left!")
                    elif key==27:b["sub_menu"]=None
                elif b["sub_menu"]=="switch":
                    others=[i for i,e in enumerate(b["eva_party"])
                            if i!=b["active_eva"] and eva_units[e]["battle_hp"]>0]
                    if key in(curses.KEY_LEFT, ord('a'),ord('A')): b["item_sel"]=(b["item_sel"]-1)%max(1,len(others))
                    elif key in(curses.KEY_RIGHT,ord('d'),ord('D')): b["item_sel"]=(b["item_sel"]+1)%max(1,len(others))
                    elif key in(ord('\n'),ord('\r'),curses.KEY_ENTER):
                        if others:
                            b["active_eva"]=others[b["item_sel"]%len(others)]
                            wlog(f"Switched to {b['eva_party'][b['active_eva']]}!")
                        b["sub_menu"]=None;b["phase"]="ANGEL_TURN";b["turn"]+=1
                    elif key==27:b["sub_menu"]=None
                else:
                    if   key in(curses.KEY_UP,  ord('w'),ord('W')): b["cursor"]=(b["cursor"]-1)%len(b["actions"])
                    elif key in(curses.KEY_DOWN, ord('s'),ord('S')): b["cursor"]=(b["cursor"]+1)%len(b["actions"])
                    elif key in(ord('1'),ord('2'),ord('3')):
                        wi=key-ord('1');ek=b["eva_party"][b["active_eva"]];d=eva_units[ek]
                        if wi<len(d["loadout"]):d["active_weapon"]=wi
                    elif key in(ord('f'),ord('F')): battle_player_action("FLEE")
                    elif key in(ord('\n'),ord('\r'),curses.KEY_ENTER):
                        act=b["actions"][b["cursor"]]
                        if act=="ITEM":b["sub_menu"]="item";b["item_sel"]=0
                        elif act=="SWITCH":
                            if len(b["eva_party"])>1:b["sub_menu"]="switch";b["item_sel"]=0
                            else:wlog("Only one EVA in party!")
                        elif act=="FLEE":battle_player_action("FLEE")
                        else:battle_player_action(act)
            if b["phase"]=="ANGEL_TURN":
                with lock:battle_angel_turn()
            if key in(ord('q'),ord('Q')):run=False;break
            continue

        # ══ LOADOUT VIEW ═════════════════════════════════════════════════════
        if view_mode=="loadout":
            if   key in(curses.KEY_UP,   ord('w'),ord('W')): loadout_wep_sel=(loadout_wep_sel-1)%len(WEP_KEYS)
            elif key in(curses.KEY_DOWN,  ord('s'),ord('S')): loadout_wep_sel=(loadout_wep_sel+1)%len(WEP_KEYS)
            elif key in(curses.KEY_LEFT,  ord('a'),ord('A')): loadout_slot_sel=(loadout_slot_sel-1)%3
            elif key in(curses.KEY_RIGHT, ord('d'),ord('D')): loadout_slot_sel=(loadout_slot_sel+1)%3
            elif key==ord('['):  loadout_unit_idx=(loadout_unit_idx-1)%len(EVA_KEYS);loadout_slot_sel=0
            elif key==ord(']'):  loadout_unit_idx=(loadout_unit_idx+1)%len(EVA_KEYS);loadout_slot_sel=0
            elif key in(ord('\n'),ord('\r'),curses.KEY_ENTER):
                uk=EVA_KEYS[loadout_unit_idx%len(EVA_KEYS)];d=eva_units[uk]
                wname=WEP_KEYS[loadout_wep_sel];wd=WEAPON_CATALOGUE[wname]
                while len(d["loadout"])<3:d["loadout"].append(None)
                slot=loadout_slot_sel%3
                old_wep=d["loadout"][slot] or "EMPTY"
                d["loadout"][slot]=wname;d["ammo"][wname]=wd["ammo"]
                if d["active_weapon"]>=len(d["loadout"]):d["active_weapon"]=0
                comm_log.append(("RITSUKO",f"{uk} slot {slot+1}: {wname} (was {old_wep})"))
                alerts.appendleft(("INFO",f"{uk} LOADOUT UPDATED"))
            elif key in(ord('v'),ord('V'),ord('\t'),27): view_mode="main"
            elif key in(ord('q'),ord('Q')): run=False;break
            continue

        # ══ DEPLOY VIEW ══════════════════════════════════════════════════════
        if view_mode=="deploy":
            if   key in(curses.KEY_UP,   ord('w'),ord('W')): deploy_sel=(deploy_sel-1)%len(EVA_KEYS)
            elif key in(curses.KEY_DOWN,  ord('s'),ord('S')): deploy_sel=(deploy_sel+1)%len(EVA_KEYS)
            elif key==ord(' '):
                uk=EVA_KEYS[deploy_sel];deploy_choices[uk]=not deploy_choices.get(uk,False)
            elif key in(ord('\n'),ord('\r'),curses.KEY_ENTER):
                chosen=[uk for uk in EVA_KEYS if deploy_choices.get(uk)]
                if chosen:
                    with lock:start_battle(chosen)
                else:comm_log.append(("MAGI","Select at least 1 EVA!"))
            elif key in(ord('v'),ord('V'),ord('\t'),27): view_mode="main"
            elif key in(ord('q'),ord('Q')): run=False;break
            continue

        # ══ COMM FOCUS ═══════════════════════════════════════════════════════
        if focus=="comm":
            if   key in(curses.KEY_BACKSPACE,127,8): cmd_buffer=cmd_buffer[:-1]
            elif key in(ord('\n'),ord('\r'),curses.KEY_ENTER):
                if cmd_buffer.strip():cmd_history.append(cmd_buffer);hist_idx=-1
                with lock:handle_command(cmd_buffer)
                cmd_buffer=""
            elif key==curses.KEY_UP:
                if cmd_history:
                    hist_idx=max(0,len(cmd_history)-1 if hist_idx==-1 else hist_idx-1)
                    cmd_buffer=cmd_history[hist_idx]
            elif key==curses.KEY_DOWN:
                if hist_idx!=-1:
                    hist_idx+=1
                    cmd_buffer=cmd_history[hist_idx] if hist_idx<len(cmd_history) else ""
                    if hist_idx>=len(cmd_history):hist_idx=-1
            elif 32<=key<=126:
                if len(cmd_buffer)<80:cmd_buffer+=chr(key)
            continue

        # ══ MAGI FOCUS ═══════════════════════════════════════════════════════
        if focus=="magi":
            if   key in(curses.KEY_LEFT,curses.KEY_UP,   ord('a'),ord('A'),ord('w'),ord('W')):
                with lock:selected_magi=(selected_magi-1)%3
            elif key in(curses.KEY_RIGHT,curses.KEY_DOWN, ord('d'),ord('D'),ord('s'),ord('S')):
                with lock:selected_magi=(selected_magi+1)%3
            elif key in(ord('\n'),ord('\r'),curses.KEY_ENTER,ord(' ')):
                with lock:
                    name=magi_names[selected_magi];v=magi_votes[name]["vote"]
                    new_v=magi_cycle[(magi_cycle.index(v)+1)%3]
                    magi_votes[name]["vote"]=new_v
                    alerts.appendleft(("INFO",f"MAGI {name}: {new_v}"))
                    ct,_=magi_consensus()
                    comm_log.append(("MAGI",f"{name} VOTES {new_v} — {ct}"))
            continue

        # ══ FIELD FOCUS ══════════════════════════════════════════════════════
        if focus=="field":
            uk=EVA_KEYS[field_sel];d=eva_units[uk];ex,ey=d["pos"]
            moved=False
            if   key in(curses.KEY_LEFT, ord('a'),ord('A')): d["pos"]=(max(0,ex-1),ey);moved=True
            elif key in(curses.KEY_RIGHT,ord('d'),ord('D')): d["pos"]=(min(FIELD_W-1,ex+1),ey);moved=True
            elif key in(curses.KEY_UP,   ord('w'),ord('W')): d["pos"]=(ex,max(0,ey-1));moved=True
            elif key in(curses.KEY_DOWN, ord('s'),ord('S')): d["pos"]=(ex,min(FIELD_H-1,ey+1));moved=True
            elif key==ord('['): field_sel=(field_sel-1)%len(EVA_KEYS)
            elif key==ord(']'): field_sel=(field_sel+1)%len(EVA_KEYS)
            elif key in(ord('1'),ord('2'),ord('3')):
                fi=key-ord('1')
                if fi<len(EVA_KEYS):field_sel=fi
            elif key==ord(','):
                d["active_weapon"]=(d["active_weapon"]-1)%max(1,len(d["loadout"]))
                comm_log.append(("RITSUKO",f"{uk}→{d['loadout'][d['active_weapon']]}"))
            elif key==ord('.'):
                d["active_weapon"]=(d["active_weapon"]+1)%max(1,len(d["loadout"]))
                comm_log.append(("RITSUKO",f"{uk}→{d['loadout'][d['active_weapon']]}"))
            elif key in(ord('b'),ord('B')):
                view_mode="deploy"
                comm_log.append(("MISATO","Choose your squad. SPACE=toggle ENTER=fight!"))
            elif key in(ord('l'),ord('L')):
                view_mode="loadout"
                comm_log.append(("RITSUKO","Loadout editor. ↑↓:weapon ←→:slot []:EVA ENTER:equip"))
            elif key in(ord(' '),ord('\n'),ord('\r'),curses.KEY_ENTER):
                ex2,ey2=d["pos"];ax2,ay2=angel["pos"]
                d_ang=dist(ex2,ey2,ax2,ay2)
                if angel["alive"] and d_ang<=2:
                    view_mode="deploy"
                    comm_log.append(("MISATO","ANGEL IN RANGE — choose squad!"))
                    alerts.appendleft(("CRIT","ANGEL CONTACT — CHOOSE SQUAD"))
                elif angel["alive"] and d["loadout"]:
                    aw=d.get("active_weapon",0);aw=min(aw,len(d["loadout"])-1)
                    wname=d["loadout"][aw]
                    if wname:
                        wd=WEAPON_CATALOGUE.get(wname,{})
                        rng=wd.get("rng",1)+1;ammo=d["ammo"].get(wname,0)
                        if d_ang<=rng and (ammo>0 or wd.get("ammo",99)>=99):
                            dmg=random.randint(*wd.get("dmg",(5,15)))
                            if ammo<99:d["ammo"][wname]=max(0,ammo-1)
                            angel["hp"]=max(0,angel["hp"]-dmg)
                            comm_log.append(("MISATO",f"{uk} fires {wname}! -{dmg}HP"))
                            alerts.appendleft(("WARN",f"ANGEL HIT HP:{angel['hp']}"))
                            if angel["hp"]<=0:
                                angel["alive"]=False
                                comm_log.append(("MISATO","ANGEL NEUTRALIZED!"))
                                alerts.appendleft(("OK","ANGEL NEUTRALIZED"))
                        else:
                            comm_log.append(("RITSUKO",f"Range:{d_ang:.1f} need≤{rng}. Move closer."))
                else:comm_log.append(("MAGI","NO TARGET."))
            if moved:
                if not d["deployed"]:d["deployed"]=True;d["status"]="ACTIVE"
                ex2,ey2=d["pos"]
                if angel["alive"] and dist(ex2,ey2,angel["pos"][0],angel["pos"][1])<=2:
                    comm_log.append(("MISATO",f"{uk} IN RANGE! SPACE=engage B=deploy L=loadout"))
                    alerts.appendleft(("WARN",f"{uk} ANGEL RANGE"))
            continue


if __name__=="__main__":
    try:curses.wrapper(main)
    except KeyboardInterrupt:pass
    finally:
        run=False
        print()
        print("\033[1;33m╔════════════════════════════════════════╗\033[0m")
        print("\033[1;33m║   NERV MAGI SYSTEM v8.0 — OFFLINE      ║\033[0m")
        print("\033[1;33m╚════════════════════════════════════════╝\033[0m")
        print("\033[2;31m  GOD'S IN HIS HEAVEN.")
        print("  ALL'S RIGHT WITH THE WORLD.\033[0m\n")
