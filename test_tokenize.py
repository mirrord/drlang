from src.drlang.language import tokenize

tokens = tokenize("$score >= 90", None)
print(f"Total tokens: {len(tokens)}")
for i, t in enumerate(tokens):
    print(f"{i}: {t.type} = [{t.value}]")
print("\nTesting just '$score':")
tokens2 = tokenize("$score", None)
for i, t in enumerate(tokens2):
    print(f"{i}: {t.type} = [{t.value}]")
