# Google Docs Formatting Guide

Conventions for backstory and campaign docs in this project.

## Heading Hierarchy

| Level | Style | Used For |
|---|---|---|
| H2 | `HEADING_2` | Major sections (e.g. "Family of House Thornecrest") |
| H3 | `HEADING_3` | Individual entries within sections (e.g. "Lord Garran Thornecrest - The Patriarch") |

## Applying Heading Styles via API

When setting a heading, always apply **both** the paragraph style and the text style together - otherwise the heading may appear gray and non-bold.

```python
requests = [
    {
        'updateParagraphStyle': {
            'range': {'startIndex': start, 'endIndex': end},
            'paragraphStyle': {'namedStyleType': 'HEADING_2'},  # or HEADING_3
            'fields': 'namedStyleType'
        }
    },
    {
        'updateTextStyle': {
            'range': {'startIndex': start, 'endIndex': end - 1},
            'textStyle': {
                'bold': True,
                'foregroundColor': {'color': {'rgbColor': {}}}  # empty rgbColor = default (black)
            },
            'fields': 'bold,foregroundColor'
        }
    }
]
```

> Note: `end - 1` in the text style range avoids including the trailing newline character.

## Section Dividers

Use an empty paragraph with a bottom border between major sections (e.g. between Family and Timeline).

```python
# Step 1: insert an empty paragraph at the divider index
{'insertText': {'location': {'index': idx}, 'text': '\n'}}

# Step 2: apply bottom border to that paragraph
{
    'updateParagraphStyle': {
        'range': {'startIndex': idx, 'endIndex': idx + 1},
        'paragraphStyle': {
            'borderBottom': {
                'color': {'color': {'rgbColor': {'red': 0.6, 'green': 0.6, 'blue': 0.6}}},
                'dashStyle': 'SOLID',
                'padding': {'magnitude': 1, 'unit': 'PT'},
                'width': {'magnitude': 1, 'unit': 'PT'}
            },
            'spaceAbove': {'magnitude': 6, 'unit': 'PT'},
            'spaceBelow': {'magnitude': 0, 'unit': 'PT'}  # let the heading's spaceAbove handle the gap
        },
        'fields': 'borderBottom,spaceAbove,spaceBelow'
    }
}
```

> Note: the two requests must be sent in separate batchUpdate calls - insert first, then style.

### Spacing rules

- Set `spaceBelow` to **0** on the divider paragraph - the H2 heading's default `spaceAbove` (18pt) provides the gap naturally.
- Do NOT set explicit `spaceAbove`/`spaceBelow` on the heading that follows the divider - it will override the named style default and make the heading look cramped.
- If a heading after a divider looks too close, check whether it has an explicit `spaceAbove` override and clear it by resetting to 18pt (the H2 default).

### Where dividers go in character docs

- Between **Family of House Thornecrest** and **Timeline**

## Bolding Important Names and Locations

Use `updateTextStyle` with `bold: True` on specific text ranges. Find ranges by walking paragraph elements and matching substrings against the run's `startIndex`.

Important terms to bold in character docs:
- Character names (full and short forms)
- Locations: Bramblewood, Sea Mist, Vaultspire, Ironwood Fortress, Skullport
- Organizations: House Thornecrest, Argent Circle, Wet Bandits, Waterfront Triad, Xanathar Syndicate, Arcanum Lyceum
- Key NPCs: Helga, Elyra Vance

## Doc IDs

| Doc | ID |
|---|---|
| Kaelen "Slick" Thornecrest (DECEASED) | `1JBScKRsV1w8rNyq11avbs9f06QpSvP0mL_TJ7bCaSXo` |
| Darian Thornecrest | `14ckTLcv68XYrZOQd3RBd6y_AxjwQE-B0Dk4beELEp2Y` |
