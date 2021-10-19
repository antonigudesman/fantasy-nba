DATA_SOURCE = (
    ('FanDuel', 'FanDuel'),
    ('DraftKings', 'DraftKings'),
    ('Yahoo', 'Yahoo'),
    ('Fanball', 'Fanball')
)

POSITION = ['PG', 'SG', 'SF', 'PF', 'C']
SEASON_START_MONTH = 10
SEASON_START_DAY = 15
SEASON_END_MONTH = 10
SEASON_END_DAY = 14


POSITION_ORDER = {
    "PG": 0,
    "SG": 1,
    "SF": 2,
    "PF": 3,
    "C": 4
}


POSITION_LIMITS = {
    'FanDuel': [
                   ["PG", 2, 2],
                   ["SG", 2, 2],
                   ["SF", 2, 2],
                   ["PF", 2, 2],
                   ["C", 1, 1]
               ],
    'DraftKings': [
                      ["PG", 1, 3],
                      ["SG", 1, 3],
                      ["SF", 1, 3],
                      ["PF", 1, 3],
                      ["C", 1, 2],
                      ["PG,SG", 3, 4],
                      ["SF,PF", 3, 4]
                  ],
    'Yahoo': [
                ["PG", 1, 3],
                ["SG", 1, 3],
                ["SF", 1, 3],
                ["PF", 1, 3],
                ["C", 1, 2],
                ["PG,SG", 3, 4],
                ["SF,PF", 3, 4]
            ],
    'Fanball': [
                ["PG", 1, 3],
                ["SG", 1, 3],
                ["SF", 1, 3],
                ["PF", 1, 3],
                ["C", 1, 3],
                ["PG,SG", 3, 4],
                ["SF,PF", 3, 4]
            ]
}


SALARY_CAP = {
    'FanDuel': 60000,
    'DraftKings': 50000,
    'Yahoo': 200,
    'Fanball': 55000
}


ROSTER_SIZE = {
    'FanDuel': 9,
    'DraftKings': 8,
    'Yahoo': 8,
    'Fanball': 8
}


TEAM_LIMIT = {
    'FanDuel': 3,
    'Yahoo': 3,
    'DraftKings': 2,
    'Fanball': 2
}


TEAM_MEMEBER_LIMIT = {
    'FanDuel': 4,
    'Yahoo': 6,
    'DraftKings': 8,
    'Fanball': 8
}


CSV_MAP_FIELDS = {
    'DraftKings': ['PG', 'SG', 'SF', 'PF', 'C', 'PG,SG', 'SF,PF'],
    'Yahoo': ['PG', 'SG', 'PG,SG', 'SF', 'PF', 'SF,PF', 'C'],
    'Fanball': ['PG', 'SG', 'SF', 'PF', 'C', 'PG,SG', 'SF,PF,C']
}


CSV_FIELDS = {
    'FanDuel': ['PG', 'PG', 'SG', 'SG', 'SF', 'SF', 'PF', 'PF', 'C'],
    'DraftKings': ['PG', 'SG', 'SF', 'PF', 'C', 'G', 'F', 'UTIL'],
    'Yahoo': ['PG', 'SG', 'G', 'SF', 'PF', 'F', 'C', 'UTIL'],
    'Fanball': ['PG', 'SG', 'SF', 'PF', 'C', 'G', 'F/C', 'UTIL']
}
