
#profile description can be assigned here too
def OverviewSerializer(profile):
    return {
       "name": profile.name,
       "description": profile.description,
    }