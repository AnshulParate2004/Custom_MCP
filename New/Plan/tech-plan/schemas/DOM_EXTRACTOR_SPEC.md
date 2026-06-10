# DOM Extractor Specification

**Parent:** `browser/state.py` | **Iteration:** 5

In-page JavaScript run via `page.evaluate()` to build indexed element list.

## Selectors (in order)

```javascript
const SELECTORS = [
  'a[href]',
  'button:not([disabled])',
  'input:not([type=hidden]):not([disabled])',
  'textarea:not([disabled])',
  'select:not([disabled])',
  '[role=button]',
  '[role=link]',
  '[role=textbox]',
  '[contenteditable=true]'
];
```

## Visibility filter

- `getBoundingClientRect()` width/height > 0
- `getComputedStyle(el).visibility !== 'hidden'`
- `getComputedStyle(el).display !== 'none'`

## Output per element

```javascript
{
  index: 0,           // assigned after filter
  tag: 'input',
  type: 'text',       // if input
  text: '',           // innerText slice 0..50
  placeholder: 'Search',
  ariaLabel: ''
}
```

## Limits

- Max 200 elements (`browser_config.example.json`)
- Truncate text to 50 chars per element

## Snapshot storage

Python side stores `{ elements: [...], url, title, timestamp }` for `click(index)` resolution.
