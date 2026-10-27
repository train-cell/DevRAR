# Asset provenance

| Shipped material | Origin | Distribution |
|---|---|---|
| HTML, CSS, JavaScript and component layout | Created for DevRAR in this repository | Project MIT license |
| Typographic D mark and inline SVG/charts/share cards | Original text and geometry created for DevRAR | Project MIT license |
| Narrator wording and optional roast | Original project copy | Project MIT license |
| `preview.png` | Screenshot of this UI using the explicitly synthetic demo | Project MIT license |
| Inter variable, Space Grotesk variable, JetBrains Mono regular | Unmodified upstream WOFF2 files pinned below | SIL Open Font License 1.1; original notices are packaged and embedded in every generated HTML report |

## Pinned font sources

The files are stored in `src/devrar/assets/fonts/`. No font request leaves the
generated HTML: its renderer embeds WOFF2 data URIs and permits only `data:`
font sources in the Content Security Policy. System fallbacks cover glyphs not
available in an embedded family. Font notices remain in the HTML even when it
is copied away from the installation.

| File | Upstream commit and source | SHA256 |
|---|---|---|
| InterVariable.woff2 | [rsms/inter, 353b61b](https://github.com/rsms/inter/blob/353b61b9f4430d5f420d56605a6e7993e0941470/docs/font-files/InterVariable.woff2) | `693b77d4f32ee9b8bfc995589b5fad5e99adf2832738661f5402f9978429a8e3` |
| SpaceGrotesk.woff2 | [floriankarsten/space-grotesk, 03507d0](https://github.com/floriankarsten/space-grotesk/blob/03507d024a01282884232081fc6011c09ff4e849/fonts/woff2/SpaceGrotesk%5Bwght%5D.woff2) | `8e085aa438094f11487a836652edd5c054fa6a96f63fc7c282105ee3a4b08c07` |
| JetBrainsMono-Regular.woff2 | [JetBrains/JetBrainsMono, 1937130](https://github.com/JetBrains/JetBrainsMono/blob/19371302b95d218af43299bce79ddbddd0bc364d/fonts/webfonts/JetBrainsMono-Regular.woff2) | `f1a7a03672cdd494ce0d5543fac6e4360fe22403c6de297fdc2e55a815f7baff` |

The corresponding `Inter-OFL.txt`, `SpaceGrotesk-OFL.txt` and
`JetBrainsMono-OFL.txt` preserve the complete upstream copyright and license
texts. The MIT code license does not replace those font licenses.

No vendor artwork, downloaded photographs, television frames, clips, script
extracts, actor likenesses or third-party character artwork are shipped. Debra
is a narrator reference selected by the owner; the code license does not grant
rights to third-party characters or brands. The visual reference does not imply
affiliation with Spotify or another product.

Generated personal reports are outside the repository. Browser evidence in CI
uses synthetic data only. New third-party assets require their source and license
to be recorded here before distribution.
