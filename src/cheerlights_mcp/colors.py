"""The CheerLights palette: the eleven color names the network uses and their HEX values."""

from .models import RGB, PaletteColor

PALETTE: dict[str, str] = {
    "red": "#ff0000",
    "green": "#008000",
    "blue": "#0000ff",
    "cyan": "#00ffff",
    "white": "#ffffff",
    "oldlace": "#fdf5e6",
    "purple": "#800080",
    "magenta": "#ff00ff",
    "yellow": "#ffff00",
    "orange": "#ffa500",
    "pink": "#ffc0cb",
}


def normalize(name: str) -> str:
    """Lowercase a color name and drop spaces, so "Old Lace" matches "oldlace"."""
    return "".join(name.lower().split())


def palette_color(name: str) -> PaletteColor | None:
    """Return the palette entry for a color name, or None if it is not a CheerLights color."""
    key = normalize(name)
    hex_code = PALETTE.get(key)
    if hex_code is None:
        return None
    return PaletteColor(
        name=key,
        hex=hex_code,
        rgb=RGB(red=int(hex_code[1:3], 16), green=int(hex_code[3:5], 16), blue=int(hex_code[5:7], 16)),
    )


def palette() -> list[PaletteColor]:
    """All eleven CheerLights colors, in palette order."""
    return [entry for name in PALETTE if (entry := palette_color(name)) is not None]
