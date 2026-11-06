# Vendored files

The files under `_dsa-tokens/` and `_dsa-surface/` are copied unmodified from [design-system-ASK](https://github.com/apexSolarKiss/design-system-ASK). They are the design system's tokens, fonts, page shell, compact actions, document register with its comparison tables and their rails, and review marks. The page loads them as they are.

**Do not edit them.** A local difference belongs in `styles/voltaire.css`, which the page loads after them. Keeping the vendored bytes unchanged is what lets each file be checked against the design system.

- **Donor:** `apexSolarKiss/design-system-ASK` at commit `14e1bb0c69dee70ed0ea17052ddf74e385c71f6d`, where design-system-ASK#204 merged. All 20 files are at that commit.
- **Files:** 20, each byte-identical to its donor's file

| Here | In design-system-ASK | Bytes | SHA-256 |
|---|---|---:|---|
| `_dsa-surface/criterion-assessment.css` | `criterion-assessment.css` | 5,881 | `006e0a9fd09759115645303b94a0449acefbd3b251175fa4302553f783008d77` |
| `_dsa-surface/evidence-state.css` | `evidence-state.css` | 4,362 | `1256fb8c9178a29aa4ee9d4b586da40087e1ea30a1264689bd9a0b4e0aab209e` |
| `_dsa-surface/review-semantics.css` | `review-semantics.css` | 33,109 | `74345c46c9260d6cfb0eefb47f4ff4d289e4b7cd51279afaeecacf1e75b1f31a` |
| `_dsa-surface/spectral-state.css` | `spectral-state.css` | 5,235 | `dd30fdc0b7b9174801129f0d01f45e22da5bbd92ff47e58d7aabaeea64f0d05b` |
| `_dsa-surface/surface-action.css` | `surface-action.css` | 21,898 | `f00ccde1b4db17687fd6ecd62644700932107352b37476184718f2036209fb2e` |
| `_dsa-surface/surface-document-overflow.js` | `surface-document-overflow.js` | 3,623 | `d66d31b36f697e20739ba009dcfa7ba05328be33fd6f401fa41443d3e268bca1` |
| `_dsa-surface/surface-document.css` | `surface-document.css` | 78,786 | `fc912a50a95ae93040fd7ff98ab4611ba28b70ee5e844058f9138334e08aee46` |
| `_dsa-surface/surface-panel.css` | `surface-panel.css` | 11,230 | `883e24ac5407a4fe24f9149b0d8964a06995cc88b6b6150b1a1bdfd9aee2976e` |
| `_dsa-surface/surface-shell.css` | `patterns/surface-shell/surface-shell.css` | 70,163 | `a960e0c0bae43c7e9b8f051579c3912b2b67d300bf94fdcd3d2bbe10ba8fa84e` |
| `_dsa-surface/surface-shell.js` | `patterns/surface-shell/surface-shell.js` | 53,439 | `a69b9de1d5b316ab8ee37f2670f61284dac5f84be2ba43c522bdc2e2d6f8d5e9` |
| `_dsa-surface/surface-shell.template.html` | `patterns/surface-shell/surface-shell.template.html` | 15,855 | `3d2afab1ecf846b132eab6e9c1e1982817a187ba04dd7fa63a4ceebc7e1700c6` |
| `_dsa-surface/surface-text-link.css` | `surface-text-link.css` | 7,921 | `9a6acf457ffbe2a0bb31ae28507855b6446195ff9dcd3cc7112f04ec5bf0fce3` |
| `_dsa-surface/surface-treatments.css` | `surface-treatments.css` | 47,403 | `ee6f1dc655d9fe84efaa6c5190320b5cabc823334b1e79cde999d4275e28d25b` |
| `_dsa-tokens/colors_and_type.css` | `colors_and_type.css` | 15,496 | `4fed9d796a0d51072802f430b9528459a5cbb9c709fa1964bf5b13f18464122a` |
| `_dsa-tokens/fonts/Inter-OFL.txt` | `fonts/Inter-OFL.txt` | 4,380 | `262481e844521b326f5ecd053e59b98c8b2da78c8ee1bdbb6e8174305e54935a` |
| `_dsa-tokens/fonts/InterVariable-Italic.woff2` | `fonts/InterVariable-Italic.woff2` | 387,976 | `e564f652916db6c139570fefb9524a77c4d48f30c92928de9db19b6b5c7a262a` |
| `_dsa-tokens/fonts/InterVariable.woff2` | `fonts/InterVariable.woff2` | 352,240 | `693b77d4f32ee9b8bfc995589b5fad5e99adf2832738661f5402f9978429a8e3` |
| `_dsa-tokens/fonts/JetBrainsMono-Italic.woff2` | `fonts/JetBrainsMono-Italic.woff2` | 123,160 | `76a805b6ea613ce2e3973f1bac6fa29db23116b2881390b59247d22890844ecc` |
| `_dsa-tokens/fonts/JetBrainsMono-OFL.txt` | `fonts/JetBrainsMono-OFL.txt` | 4,399 | `a76abf002c49097d146e86740a3105a5d00450b1592e820a1109a8c5680cd697` |
| `_dsa-tokens/fonts/JetBrainsMono.woff2` | `fonts/JetBrainsMono.woff2` | 113,672 | `31ec365b93e4bad6f202ce23352a56d01ca4462b2afc782ed2cf6fa42ca9ac0e` |

## Load order

The page loads, in this order:

```text
_dsa-tokens/colors_and_type.css
_dsa-surface/surface-action.css
_dsa-surface/surface-panel.css
_dsa-surface/surface-text-link.css
_dsa-surface/surface-document.css
_dsa-surface/surface-treatments.css
_dsa-surface/spectral-state.css
_dsa-surface/evidence-state.css
_dsa-surface/review-semantics.css
_dsa-surface/criterion-assessment.css
_dsa-surface/surface-shell.css
styles/voltaire.css
```

The order is part of the design system's contract. `spectral-state.css` and `criterion-assessment.css` color the comparison tables' rails, which take their paint from `surface-treatments.css`; `evidence-state.css` and `review-semantics.css` serve the check in "About this prototype".

`_dsa-surface/surface-shell.template.html` is loaded by no page. It is the shell's canonical markup specimen, which the shell contract asks every consumer to carry with `surface-shell.css`, so a page can be checked against it.

Scripts load at the end of the body: `_dsa-surface/surface-document-overflow.js`, for the comparison tables' scroll cue, then `_dsa-surface/surface-shell.js`, for the navigation.

## Re-syncing

The copies stay at their commit until someone updates them on purpose. Forking or cloning this repository does not update them.

1. Choose the new design-system-ASK commit and read what changed in these files since the donor above.
2. Copy each file listed above from that commit, unmodified, to the same place here. Add a file only if the page now needs it, and add it to this list and to the load order.
3. Update the donor, the byte counts and the SHA-256 values above. Check every file against the donor (`git show <commit>:<path> | shasum -a 256`).
4. Open the page in light and dark, at desktop and phone widths, and use its navigation, including a section link. design-system-ASK's `tools/check-custom-properties.mjs --root <this repository> --page index.html` checks that every custom property the page uses is defined.
