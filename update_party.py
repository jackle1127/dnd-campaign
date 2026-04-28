import json, re
from pathlib import Path
from datetime import datetime

REPO_ROOT = Path(__file__).parent
PARTY_DIR = REPO_ROOT / 'this-is-bullcrit' / 'party'
DATA_FILE = REPO_ROOT / 'all_characters.json'

SLUG_MAP = {
    '153282190': 'kaelen-thornecrest',
    '153546441': 'rayne-willowshade',
    '153077893': 'szeth-stormblessed',
    '152806918': 'vacir',
    '164100589': 'darian-thornecrest',
    '164913938': 'fib-noodlecork',
}

NO_FETCH = {'152117866'}
DECEASED = {'153282190'}

SKIP_TRAITS = {
    'Creature Type', 'Size', 'Speed', 'Languages',
    'Ability Score Increases', 'Ability Score Increase',
    'Age',
}

LANG_DISPLAY = {
    'common': 'Common',
    'common-sign-language': 'Common Sign Language',
    'thieves-cant': "Thieves' Cant",
    'druidic': 'Druidic',
    'elvish': 'Elvish',
    'dwarvish': 'Dwarvish',
    'gnomish': 'Gnomish',
    'draconic': 'Draconic',
    'goblin': 'Goblin',
    'orc': 'Orc',
    'halfling': 'Halfling',
    'giant': 'Giant',
    'gnoll': 'Gnoll',
    'sylvan': 'Sylvan',
    'undercommon': 'Undercommon',
    'abyssal': 'Abyssal',
    'celestial': 'Celestial',
    'infernal': 'Infernal',
    'primordial': 'Primordial',
    'deep-speech': 'Deep Speech',
}

def mod(val):
    m = (val - 10) // 2
    return f'+{m}' if m >= 0 else str(m)

def mod_int(val):
    return (val - 10) // 2

def get_stats(char):
    stats = {s['id']: s['value'] for s in char.get('stats', [])}
    bonuses = {s['id']: s['value'] or 0 for s in char.get('bonusStats', [])}
    overrides = {s['id']: s['value'] for s in char.get('overrideStats', [])}
    result = {}
    for sid in [1, 2, 3, 4, 5, 6]:
        base = stats.get(sid, 10)
        val = overrides.get(sid) or (base + bonuses.get(sid, 0))
        result[sid] = val
    return result

def get_all_mods(char):
    result = {}
    for cat, mods in char.get('modifiers', {}).items():
        for m in mods:
            sub = m.get('subType', '')
            t = m.get('type', '')
            if t in ('proficiency', 'expertise', 'half-proficiency'):
                if sub not in result or t == 'expertise':
                    result[sub] = t
    return result

def get_prof_bonus(level):
    return 2 + (level - 1) // 4

def get_ac(char, stats):
    dex = mod_int(stats[2])
    inv = char.get('inventory', [])
    armor = [i for i in inv if i.get('equipped') and i.get('definition', {}).get('filterType') == 'Armor']
    if armor:
        best = max(armor, key=lambda i: i['definition'].get('armorClass', 0))
        d = best['definition']
        base = d.get('armorClass', 10)
        atype = d.get('type', '') or ''
        name = d.get('name', 'Armor')
        if 'Heavy' in atype:
            return base, name
        elif 'Medium' in atype:
            return base + min(dex, 2), name
        else:
            return base + dex, name
    return 10 + dex, 'Unarmored'

def get_speed(char):
    race = char.get('race', {}) or {}
    ws = race.get('weightSpeeds', {}) or {}
    return (ws.get('normal', {}) or {}).get('walk', 30)

def strip_html(html_str):
    text = re.sub(r'<[^>]+>', ' ', html_str or '')
    text = (text
        .replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
        .replace('&nbsp;', ' ').replace('&#39;', "'").replace('&rsquo;', "'")
        .replace('&ldquo;', '"').replace('&rdquo;', '"').replace('&ndash;', '-')
        .replace('&mdash;', '-').replace('’', "'").replace('“', '"')
        .replace('”', '"').replace('–', '-').replace('—', '-'))
    return re.sub(r'\s+', ' ', text).strip()

def truncate(text, length=300):
    if len(text) <= length:
        return text
    return text[:length].rsplit(' ', 1)[0] + '...'

def get_spells(char):
    spells = []
    for cs in char.get('classSpells', []):
        for s in cs.get('spells', []):
            spells.append(s['definition']['name'])
    return spells

def get_inventory(char):
    return [i['definition']['name'] for i in char.get('inventory', []) if i.get('definition')]

def get_feats(char):
    return [f['definition']['name'] for f in char.get('feats', []) if f.get('definition')]

def build_spells_section(char):
    """Build ## Spells section content. Returns None if no spells found."""
    by_level = {}
    # Class spells
    for cs in char.get('classSpells', []):
        for s in cs.get('spells', []):
            d = s['definition']
            by_level.setdefault(d.get('level', 0), []).append(d['name'])
    # Race/feat/background spells
    sp_dict = char.get('spells') or {}
    for cat in ['race', 'feat', 'background']:
        for s in (sp_dict.get(cat) or []):
            d = s.get('definition', {})
            by_level.setdefault(d.get('level', 0), []).append(d['name'])
    if not by_level:
        return None
    lines = []
    level_names = {0: 'Cantrips', 1: '1st Level', 2: '2nd Level', 3: '3rd Level',
                   4: '4th Level', 5: '5th Level', 6: '6th Level', 7: '7th Level',
                   8: '8th Level', 9: '9th Level'}
    for lvl in sorted(by_level):
        label = level_names.get(lvl, f'Level {lvl}')
        names = ', '.join(sorted(set(by_level[lvl])))
        lines.append(f'**{label}:** {names}')
    return '  \n'.join(lines)

def build_languages_section(char):
    """Build ## Languages section content."""
    seen = set()
    langs = []
    for cat, mods in (char.get('modifiers') or {}).items():
        for m in mods:
            if m.get('type') == 'language':
                sub = m.get('subType', '')
                if sub and sub not in seen:
                    seen.add(sub)
                    langs.append(LANG_DISPLAY.get(sub, sub.replace('-', ' ').title()))
    if not langs:
        return None
    return ', '.join(langs)

def build_equipment_section(char):
    """Build ## Equipment section content."""
    counts = {}
    for item in char.get('inventory', []):
        d = item.get('definition', {})
        if not d:
            continue
        name = d.get('name', '')
        qty = item.get('quantity', 1)
        counts[name] = counts.get(name, 0) + qty
    if not counts:
        return None
    parts = []
    for name, qty in counts.items():
        parts.append(f'{name} x{qty}' if qty > 1 else name)
    return ', '.join(parts)

def compute_saves(s, profs, prof_bonus):
    save_map = [
        ('strength-saving-throws', 1, 'STR'),
        ('dexterity-saving-throws', 2, 'DEX'),
        ('constitution-saving-throws', 3, 'CON'),
        ('intelligence-saving-throws', 4, 'INT'),
        ('wisdom-saving-throws', 5, 'WIS'),
        ('charisma-saving-throws', 6, 'CHA'),
    ]
    parts = []
    for sub, sid, label in save_map:
        m = mod_int(s[sid])
        is_prof = sub in profs
        val = m + (prof_bonus if is_prof else 0)
        sign = '+' if val >= 0 else ''
        marker = '*' if is_prof else ''
        parts.append(f'{label}{marker} {sign}{val}')
    return f'**Saving Throws:** {" | ".join(parts)}  \n*proficient'

def compute_passive_perception(s, profs, prof_bonus):
    wis_mod = mod_int(s[5])
    if profs.get('perception') == 'expertise':
        return 10 + wis_mod + prof_bonus * 2
    elif 'perception' in profs:
        return 10 + wis_mod + prof_bonus
    return 10 + wis_mod

def build_features(char, s, prof_bonus):
    lines = []

    for c in char.get('classes', []):
        class_name = c['definition']['name']
        class_level = c['level']
        lines.append(f'### {class_name} Features')
        for cf in c['definition'].get('classFeatures', []):
            if cf.get('requiredLevel', 99) > class_level:
                continue
            name = cf.get('name', '')
            if re.match(r'^Core .+ Traits$', name):
                continue
            desc = strip_html(cf.get('description', ''))
            if desc:
                lines.append(f'**{name}:** {truncate(desc)}')

        subclass = c.get('subclassDefinition')
        if subclass:
            for scf in subclass.get('classFeatures', []):
                if scf.get('requiredLevel', 99) <= class_level:
                    name = scf.get('name', '')
                    desc = strip_html(scf.get('description', ''))
                    if desc:
                        lines.append(f'**{name}:** {truncate(desc)}')
        lines.append('')

    race = char.get('race', {}) or {}
    race_name = race.get('fullName') or race.get('baseRaceName', 'Race')
    racial_traits = race.get('racialTraits', [])
    if racial_traits:
        lines.append(f'### {race_name} Traits')
        for t in racial_traits:
            d = t.get('definition', {})
            name = d.get('name', '')
            if name in SKIP_TRAITS:
                continue
            desc = strip_html(d.get('description', ''))
            if desc:
                lines.append(f'**{name}:** {truncate(desc)}')
        lines.append('')

    bg = char.get('background', {}) or {}
    bg_def = bg.get('definition', {}) or {}
    bg_name = bg_def.get('name', '')
    feat_name = bg_def.get('featureName', '')
    feat_desc = bg_def.get('featureDescription', '') or ''
    if bg_name and feat_name:
        lines.append(f'### {bg_name} Background')
        if feat_desc:
            lines.append(f'**{feat_name}:** {truncate(strip_html(feat_desc))}')
        else:
            lines.append(f'**{feat_name}**')
        lines.append('')

    feats = char.get('feats', [])
    if feats:
        lines.append('### Feats')
        for f in feats:
            d = f.get('definition', {}) or {}
            name = d.get('name', '')
            desc = strip_html(d.get('description', ''))
            if name:
                lines.append(f'**{name}:** {truncate(desc)}' if desc else f'**{name}**')
        lines.append('')

    while lines and lines[-1] == '':
        lines.pop()
    return '\n'.join(lines)

def update_inline_field(text, field, new_value):
    pattern = rf'(\*\*{re.escape(field)}:\*\*\s*).*'
    new_text, n = re.subn(pattern, rf'\g<1>{new_value}', text)
    return new_text, n > 0

def update_ability_scores_table(text, s):
    row = f'| {s[1]} ({mod(s[1])}) | {s[2]} ({mod(s[2])}) | {s[3]} ({mod(s[3])}) | {s[4]} ({mod(s[4])}) | {s[5]} ({mod(s[5])}) | {s[6]} ({mod(s[6])}) |'
    pattern = r'(## Ability Scores\n+\|[^\n]+\|\n\|[-| ]+\|\n)\|[^\n]+\|'
    new_text, n = re.subn(pattern, rf'\g<1>{row}', text)
    return new_text, n > 0

def update_combat_row(text, ac_str, init_mod, speed, prof_bonus):
    row = f'| {ac_str} | {init_mod} | {speed} ft. | +{prof_bonus} |'
    pattern = r'(## Combat\n+\|[^\n]+\|\n\|[-| ]+\|\n)\|[^\n]+\|'
    new_text, n = re.subn(pattern, rf'\g<1>{row}', text)
    return new_text, n > 0

def update_saving_throws(text, saves_line):
    pattern = r'\*\*Saving Throws:\*\*[^\n]*\n\*proficient'
    new_text, n = re.subn(pattern, saves_line, text)
    return new_text, n > 0

def update_passive_perception(text, value):
    pattern = r'(\*\*Passive Perception:\*\*\s*)\d+'
    new_text, n = re.subn(pattern, rf'\g<1>{value}', text)
    return new_text, n > 0

def update_features_section(text, features_content):
    if '## Features and Traits' not in text:
        return text, False
    start_marker = '## Features and Traits'
    start_idx = text.index(start_marker) + len(start_marker)
    while start_idx < len(text) and text[start_idx] == '\n':
        start_idx += 1
    end_idx = len(text)
    for marker in ['\n## ', '\n*Last updated', '\n---']:
        pos = text.find(marker, start_idx)
        if pos != -1 and pos < end_idx:
            end_idx = pos
    new_text = text[:start_idx] + features_content + '\n' + text[end_idx:]
    return new_text, True

def strip_dndbeyond_stats(text):
    """Remove the old ## D&D Beyond Stats appendix section."""
    marker = '## D&D Beyond Stats'
    if marker not in text:
        return text
    # Find the --- separator that precedes it
    idx = text.index(marker)
    # Walk back past whitespace/newlines to find the preceding ---
    pre = text[:idx].rstrip()
    if pre.endswith('---'):
        pre = pre[:-3].rstrip()
    return pre + '\n'

def update_or_insert_section(text, section_name, content):
    """Update existing ## Section if present; otherwise insert before *Last updated*."""
    header = f'## {section_name}'
    if header in text:
        # Update in place - replace content between header and next ## or *Last updated or ---
        start_idx = text.index(header) + len(header)
        while start_idx < len(text) and text[start_idx] == '\n':
            start_idx += 1
        end_idx = len(text)
        for marker in ['\n## ', '\n*Last updated', '\n---']:
            pos = text.find(marker, start_idx)
            if pos != -1 and pos < end_idx:
                end_idx = pos
        return text[:start_idx] + content + '\n' + text[end_idx:]
    else:
        # Insert before *Last updated* or before --- or at end
        for marker in ['\n*Last updated', '\n---']:
            pos = text.find(marker)
            if pos != -1:
                return text[:pos] + f'\n\n{header}\n\n{content}\n' + text[pos:]
        return text.rstrip() + f'\n\n{header}\n\n{content}\n'

def update_list_section(text, section_name, items):
    if not items:
        return text, False
    new_list = '\n'.join(f'- {item}' for item in items)
    pattern = rf'(## {re.escape(section_name)}\n+)((?:- .+\n?)+)'
    new_text, n = re.subn(pattern, rf'\g<1>{new_list}\n', text)
    return new_text, n > 0

def update_last_updated(text, today):
    new_text, n = re.subn(r'\*Last updated: \d{4}-\d{2}-\d{2}\*', f'*Last updated: {today}*', text)
    if n == 0:
        new_text = text.rstrip() + f'\n\n*Last updated: {today}*\n'
    return new_text


raw = DATA_FILE.read_text(encoding='utf-8').strip()
if raw.startswith('"'):
    raw = json.loads(raw)
all_chars = json.loads(raw)

today = datetime.now().strftime('%Y-%m-%d')
summary = []

for char_id_int, resp in all_chars.items():
    char_id = str(char_id_int)
    if char_id in NO_FETCH:
        print(f'  SKIP {char_id} (NO-FETCH)')
        continue

    char = resp.get('data', {})
    if not char or not char.get('name'):
        print(f'  SKIP {char_id}: no data ({resp.get("message", "?")})')
        continue

    name = char['name']
    slug = SLUG_MAP.get(char_id, name.lower().replace(' ', '-'))
    md_path = PARTY_DIR / f'{slug}.md'

    if not md_path.exists():
        print(f'  SKIP {name}: no markdown file at {md_path.name}')
        continue

    text = md_path.read_text(encoding='utf-8')
    classes = char.get('classes', [])
    class_str = ', '.join(f"{c['definition']['name']} {c['level']}" for c in classes)
    total_level = sum(c['level'] for c in classes)
    hp = char.get('baseHitPoints', '?')
    status = 'DECEASED' if char_id in DECEASED else 'Active'
    s = get_stats(char)
    prof_bonus = get_prof_bonus(total_level)
    profs = get_all_mods(char)
    ac, armor_name = get_ac(char, s)
    ac_label = f'{ac} ({armor_name})'
    speed = get_speed(char)
    init_mod = mod(s[2])
    saves_line = compute_saves(s, profs, prof_bonus)
    passive_perc = compute_passive_perception(s, profs, prof_bonus)
    features_content = build_features(char, s, prof_bonus)
    spells = get_spells(char)
    inventory = get_inventory(char)
    feats = get_feats(char)

    text = strip_dndbeyond_stats(text)
    text, _ = update_inline_field(text, 'Class', class_str)
    text, _ = update_inline_field(text, 'Level', total_level)
    text, _ = update_inline_field(text, 'HP', hp)
    text, _ = update_inline_field(text, 'Status', status)
    text, _ = update_ability_scores_table(text, s)
    text, _ = update_combat_row(text, ac_label, init_mod, speed, prof_bonus)
    text, _ = update_saving_throws(text, saves_line)
    text, _ = update_passive_perception(text, passive_perc)
    text, _ = update_features_section(text, features_content)
    # Only update Spells if D&D Beyond has actual class spells; otherwise preserve manual content
    has_class_spells = any(
        len(cs.get('spells', [])) > 0 for cs in char.get('classSpells', [])
    )
    spells_content = build_spells_section(char)
    if spells_content and has_class_spells:
        text = update_or_insert_section(text, 'Spells', spells_content)
    elif spells_content and '## Spells' not in text:
        # No class spells but has race/feat spells - insert fresh section only
        text = update_or_insert_section(text, 'Spells', spells_content)
    langs_content = build_languages_section(char)
    if langs_content:
        text = update_or_insert_section(text, 'Languages', langs_content)
    equip_content = build_equipment_section(char)
    if equip_content:
        text = update_or_insert_section(text, 'Equipment', equip_content)
    text = update_last_updated(text, today)

    md_path.write_text(text, encoding='utf-8')
    print(f'  UPDATED: {name}')
    summary.append((name, class_str, hp, s))

print(f'\nDone. Updated {len(summary)} characters.')
print(f'\n{"Character":<30} {"Class":<25} {"HP":<5} STR DEX CON INT WIS CHA')
print('-' * 90)
for name, cls, hp, s in summary:
    print(f'{name:<30} {cls:<25} {str(hp):<5} {s[1]:<4}{s[2]:<4}{s[3]:<4}{s[4]:<4}{s[5]:<4}{s[6]}')
