"""Configuration dict for the package.

 - `non_countries`: Tuple[str] specifying the country codes that should be
 removed from data. The default list contains codes for all non-country
 data points present in GDP and Population .csv files (mostly aggregated
 regions like the EU, North Africa etc.).

 - `standardized_country_names`: Dict[str, str] mapping country names to their
 standardized form; used in data preprocessing. Assumes all country names are
 already in uppercase.

 - `stats_top_k`: int - how many top results per group to return in statistical
 tables produced by the `analysis` module. Default: 5 (per task specification).

 - `stats_required_columns`: Tuple[str] containing column names that must be
 present in "clean" dataframe provided in the constructor of `Stats` object.
"""

CONFIG = {
    "non_countries": (
        "AFE", "AFW", "ARB", "CEB", "CSS", "EAP", "EAR", "EAS", "ECA", "ECS",
        "EMU", "EUU", "FCS", "HIC", "HPC", "IBD", "IBT", "IDA", "IDB", "IDX",
        "LAC", "LCN", "LDC", "LIC", "LMC", "LMY", "LTE", "MEA", "MIC", "MNA",
        "NAC", "OED", "OSS", "PRE", "PSS", "PST", "SAS", "SSA", "SSF", "SST",
        "TEA", "TEC", "TLA", "TMN", "TSA", "TSS", "UMC", "WLD",
    ),
    "standardized_country_names": {
        "ANTIGUA & BARBUDA": "ANTIGUA AND BARBUDA",
        "BAHAMAS, THE": "BAHAMAS",
        "BOSNIA & HERZEGOVINA": "BOSNIA AND HERZEGOVINA",
        "BRUNEI DARUSSALAM": "BRUNEI (DARUSSALAM)",
        "CAPE VERDE": "CABO VERDE",
        "CHINA (MAINLAND)": "CHINA",
        "CONGO, DEM. REP.": "DEMOCRATIC REPUBLIC OF THE CONGO "
        "(FORMERLY ZAIRE)",
        "CONGO, REP.": "CONGO",
        "CZECH REPUBLIC": "CZECHIA",
        "COTE D IVOIRE": "COTE D'IVOIRE",
        "DEMOCRATIC PEOPLE S REPUBLIC OF KOREA": "NORTH KOREA",
        "EGYPT, ARAB REP.": "EGYPT",
        "FAEROE ISLANDS": "FAROE ISLANDS",
        "FRANCE (INCLUDING MONACO)": "FRANCE",
        "GAMBIA, THE": "GAMBIA",
        "GUINEA-BISSAU": "GUINEA BISSAU",
        "HONG KONG SAR, CHINA": "HONG KONG",
        "HONG KONG SPECIAL ADMINSTRATIVE REGION OF CHINA": "HONG KONG",
        "IRAN, ISLAMIC REP.": "IRAN",
        "ISLAMIC REPUBLIC OF IRAN": "IRAN",
        "ITALY (INCLUDING SAN MARINO)": "ITALY",
        "KOREA, DEM. PEOPLE'S REP.": "NORTH KOREA",
        "KOREA, REP.": "SOUTH KOREA",
        "KYRGYZ REPUBLIC": "KYRGYZSTAN",
        "LAO PDR": "LAO",
        "LAO PEOPLE S DEMOCRATIC REPUBLIC": "LAO",
        "LIBYAN ARAB JAMAHIRIYAH": "LIBYA",
        "MACAO SAR, CHINA": "MACAU",
        "MACAU SPECIAL ADMINSTRATIVE REGION OF CHINA": "MACAU",
        "MICRONESIA, FED. STS.": "FEDERATED STATES OF MICRONESIA",
        "MYANMAR (FORMERLY BURMA)": "MYANMAR",
        "NORTH MACEDONIA": "MACEDONIA",
        "PLURINATIONAL STATE OF BOLIVIA": "BOLIVIA",
        "REPUBLIC OF CAMEROON": "CAMEROON",
        "REPUBLIC OF KOREA": "SOUTH KOREA",
        "REPUBLIC OF MOLDOVA": "MOLDOVA",
        "REPUBLIC OF SOUTH SUDAN": "SOUTH SUDAN",
        "SAINT LUCIA": "ST. LUCIA",
        "SAINT MARTIN (DUTCH PORTION)": "SINT MAARTEN (DUTCH PART)",
        "SAO TOME & PRINCIPE": "SAO TOME AND PRINCIPE",
        "SLOVAK REPUBLIC": "SLOVAKIA",
        "ST. KITTS-NEVIS": "ST. KITTS AND NEVIS",
        "ST. VINCENT & THE GRENADINES": "ST. VINCENT AND THE GRENADINES",
        "TIMOR-LESTE (FORMERLY EAST TIMOR)": "TIMOR-LESTE",
        "TURKIYE": "TURKEY",
        "UNITED REPUBLIC OF TANZANIA": "TANZANIA",
        "UNITED STATES": "UNITED STATES OF AMERICA",
        "WEST BANK AND GAZA": "OCCUPIED PALESTINIAN TERRITORY",
        "VIET NAM": "VIETNAM",
        "VENEZUELA, RB": "VENEZUELA",
        "YEMEN, REP.": "YEMEN",
    },
    "stats_top_k": 5,
    "stats_required_columns": (
        "Country",
        "Year",
        "Population",
        "Emissions [total metric tons]",
        "GDP [current US$]",
    ),
}
