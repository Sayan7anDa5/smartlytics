"""Single source for segment bins and chart color maps."""

# Price segments in INR. Contiguous bins, documented once (no off-by-one gaps).
SEGMENT_ORDER = ["Budget", "Mid-Range", "Premium", "Flagship"]

# Right-closed bin edges used by pandas.cut: (0,15000], (15000,30000],
# (30000,50000], (50000, inf].
SEGMENT_BIN_EDGES = [0, 15_000, 30_000, 50_000, float("inf")]

SEGMENT_COLORS = {
    "Budget": "#10b981",
    "Mid-Range": "#3b82f6",
    "Premium": "#8b5cf6",
    "Flagship": "#f59e0b",
}

BRAND_COLORS = {
    "Samsung": "#1428A0", "Xiaomi": "#FF6900", "Realme": "#F5C900",
    "Vivo": "#415FFF", "OPPO": "#1BA784", "OnePlus": "#F5010C",
    "Apple": "#A2AAAD", "Motorola": "#5C2D91", "Nothing": "#94a3b8",
    "Google": "#4285F4", "iQOO": "#00A3E0", "POCO": "#FFD700",
}
