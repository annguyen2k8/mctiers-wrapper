from mctiers import MCTiersAPI

api = MCTiersAPI()

print(api.get_tester_history("d219c8eed32e4da2b22e0aa69d36c88a"))
print(api.get_recent_high_test())
