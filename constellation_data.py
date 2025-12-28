# Constellation lines defined by pairs of star names (Bayer designation or common name)
# We will try to match these against the names returned by Astrometry.net

CONSTELLATION_COLORS = {
    'Ori': 'lime',      # Orion - Green
    'Lep': 'cyan',      # Lepus - Cyan
    'Eri': 'magenta',   # Eridanus - Magenta
    'Ursa Major': 'yellow' # Big Dipper - Yellow
}

# Approximate distances from Earth in Light Years (ly)
# Source: General astronomical catalogs (Hipparcos/Gaia approximations)
STAR_DISTANCES_LY = {
    # Orion
    'Alpha Ori': 642.5,   # Betelgeuse
    'Beta Ori': 863.0,    # Rigel
    'Gamma Ori': 250.0,   # Bellatrix
    'Delta Ori': 1200.0,  # Mintaka
    'Epsilon Ori': 2000.0,# Alnilam
    'Zeta Ori': 1260.0,   # Alnitak
    'Kappa Ori': 724.0,   # Saiph
    'Lambda Ori': 1100.0, # Meissa
    'Iota Ori': 1300.0,   # Hatysa
    'Eta Ori': 900.0,     # Saif al Jabbar
    'Mu Ori': 150.0,
    'Xi Ori': 1200.0,
    'Nu Ori': 500.0,
    'Pi3 Ori': 26.0,      # Tabit
    'Pi2 Ori': 220.0,
    'Pi1 Ori': 120.0,
    'Pi4 Ori': 1000.0,
    'Pi5 Ori': 1300.0,
    'Pi6 Ori': 900.0,
    
    # Lepus
    'Alpha Lep': 2200.0,  # Arneb
    'Beta Lep': 160.0,    # Nihal
    'Epsilon Lep': 213.0,
    'Mu Lep': 186.0,
    'Zeta Lep': 70.0,
    'Gamma Lep': 29.0,
    'Delta Lep': 114.0,

    # Eridanus
    'Beta Eri': 89.0,     # Cursa
    'Lambda Eri': 58.0,
    
    # Ursa Major
    'Alpha UMa': 123.0,   # Dubhe
    'Beta UMa': 79.0,     # Merak
    'Gamma UMa': 83.0,    # Phecda
    'Delta UMa': 80.0,    # Megrez
    'Epsilon UMa': 82.0,  # Alioth
    'Zeta UMa': 78.0,     # Mizar
    'Eta UMa': 103.0,     # Alkaid
}

CONSTELLATION_LINES = {
    'Ori': [
        # Body
        ('Alpha Ori', 'Lambda Ori'), # Betelgeuse - Meissa
        ('Lambda Ori', 'Gamma Ori'), # Meissa - Bellatrix
        ('Gamma Ori', 'Delta Ori'),  # Bellatrix - Mintaka
        ('Delta Ori', 'Epsilon Ori'), # Mintaka - Alnilam
        ('Epsilon Ori', 'Zeta Ori'),  # Alnilam - Alnitak
        ('Zeta Ori', 'Kappa Ori'),    # Alnitak - Saiph
        ('Kappa Ori', 'Beta Ori'),    # Saiph - Rigel
        ('Beta Ori', 'Eta Ori'),      # Rigel - Eta
        ('Eta Ori', 'Delta Ori'),     # Eta - Mintaka
        
        # Club / Arm
        ('Alpha Ori', 'Mu Ori'),
        ('Mu Ori', 'Xi Ori'),
        ('Xi Ori', 'Nu Ori'),
        # ('Nu Ori', 'Chi2 Ori'), # Removed Chi2 as it's less common/harder to match
        
        # Shield / Bow
        ('Gamma Ori', 'Pi3 Ori'),
        ('Pi3 Ori', 'Pi2 Ori'),
        ('Pi2 Ori', 'Pi1 Ori'),
        ('Pi3 Ori', 'Pi4 Ori'),
        ('Pi4 Ori', 'Pi5 Ori'),
        ('Pi5 Ori', 'Pi6 Ori'),
    ],
    'Lep': [
        ('Alpha Lep', 'Beta Lep'),
        ('Beta Lep', 'Epsilon Lep'),
        ('Epsilon Lep', 'Mu Lep'),
        ('Mu Lep', 'Zeta Lep'),
        ('Zeta Lep', 'Gamma Lep'),
        ('Gamma Lep', 'Delta Lep'),
        ('Delta Lep', 'Alpha Lep'),
    ],
    'Eri': [
        ('Beta Eri', 'Lambda Eri'),
        # Eridanus is huge and complex, adding a few main lines if possible
        # It connects to Rigel (Beta Ori) visually but usually starts at Cursa (Beta Eri)
    ],
    'Ursa Major': [
        ('Alpha UMa', 'Beta UMa'),
        ('Beta UMa', 'Gamma UMa'),
        ('Gamma UMa', 'Delta UMa'),
        ('Delta UMa', 'Epsilon UMa'),
        ('Epsilon UMa', 'Zeta UMa'),
        ('Zeta UMa', 'Eta UMa'),
    ]
}

# Mapping from Greek letters (and some common abbreviations) to English names
GREEK_MAP = {
    '\u03b1': 'Alpha',
    '\u03b2': 'Beta',
    '\u03b3': 'Gamma',
    '\u03b4': 'Delta',
    '\u03b5': 'Epsilon',
    '\u03b6': 'Zeta',
    '\u03b7': 'Eta',
    '\u03b8': 'Theta',
    '\u03b9': 'Iota',
    '\u03ba': 'Kappa',
    '\u03bb': 'Lambda',
    '\u03bc': 'Mu',
    '\u03bd': 'Nu',
    '\u03be': 'Xi',
    '\u03bf': 'Omicron',
    '\u03c0': 'Pi',
    '\u03c1': 'Rho',
    '\u03c3': 'Sigma',
    '\u03c4': 'Tau',
    '\u03c5': 'Upsilon',
    '\u03c6': 'Phi',
    '\u03c7': 'Chi',
    '\u03c8': 'Psi',
    '\u03c9': 'Omega',
}

def normalize_name(name):
    """
    Normalize a star name from Astrometry.net to a standard format (e.g., 'Alpha Ori').
    Input examples: '\u03b1 Ori', 'Betelgeuse', '58 Ori'
    """
    # Replace Greek letters
    for greek, english in GREEK_MAP.items():
        name = name.replace(greek, english)
    
    # Remove extra spaces
    name = ' '.join(name.split())
    
    return name

def find_star_in_annotations(star_name_pattern, annotations):
    """
    Find a star in the annotations list that matches the pattern.
    star_name_pattern: e.g., 'Alpha Ori'
    annotations: list of dicts from Astrometry.net
    """
    # We want to match if 'Alpha Ori' is in the list of names for the star
    # The annotation names might be ["Alpha Ori / 58 Ori", "Betelgeuse"]
    
    target_parts = star_name_pattern.split()
    
    for star in annotations:
        names = star.get('names', [])
        for name in names:
            norm_name = normalize_name(name)
            
            # Check for exact match of the pattern (e.g. "Alpha Ori")
            # or if the pattern is a substring (e.g. "Alpha Ori" in "Alpha Ori / ...")
            
            # Simple check: if the target pattern appears in the normalized name
            if star_name_pattern in norm_name:
                return star
            
            # Also check for Flamsteed numbers if provided (e.g. "58 Ori")
            # But our patterns are mostly Bayer.
            
    return None
