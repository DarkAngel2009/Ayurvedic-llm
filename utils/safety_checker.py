class SafetyChecker:
    def __init__(self):
        self.rules = {
            'pregnancy': {
                'yoga_avoid': ['hot yoga', 'deep twists'],
                'herbs_avoid': ['senna', 'aloe', 'neem'],
                'acupuncture_avoid': ['LI4', 'SP6']
            }
        }
    
    def check_safety(self, user_profile, recs):
        warnings, safe = [], []
        conditions = user_profile.get('conditions', [])
        for r in recs:
            flag = True
            for c in conditions:
                if c in self.rules:
                    for items in self.rules[c].values():
                        if any(i in r for i in items):
                            warnings.append(f"Caution: {r} for {c}")
                            flag = False
            if flag:
                safe.append(r)
        return {'safe_recommendations': safe, 'warnings': warnings}
