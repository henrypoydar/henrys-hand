# Henry's hand TTF font

![](/henrys-hand-ttf-preview.png?raw=true "Henry's Hand TTF Preview")

## Files

- `Henry's Hand.ttf`: the original, a single SemiBold (600) weight. Install this on your computer.
- `henrys-hand-variable.ttf`: a variable font with a weight axis from 300 to 700. Install this to get Light, Regular, SemiBold, and Bold.
- `henrys-hand.woff2`: the variable font for the web.

## Weights

![](/henrys-hand-weights-preview.png?raw=true "Henry's Hand weights")

The original is SemiBold (600). Light (300) and Bold (700) are generated from its outlines, and Regular (400) falls between Light and SemiBold.

## Changelog

- 3.000: variable weight axis (300–700) and WOFF2.

## Use on the web

```css
@font-face {
  font-family: "Henry's Hand";
  src: url("henrys-hand.woff2") format("woff2");
  font-weight: 300 700;
  font-display: swap;
}

body {
  font-family: "Henry's Hand", cursive;
  font-weight: 400;
}
```

Licensed under a Creative Commons Attribution 3.0 United States License
http://creativecommons.org/licenses/by/3.0/us/
