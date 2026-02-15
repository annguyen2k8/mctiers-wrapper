from mctiers import MCTiersAPI

api = MCTiersAPI()

print(api.list_all_gamemodes())

print(api.get_gamemodes_rankings("vanilla", retired=True))
