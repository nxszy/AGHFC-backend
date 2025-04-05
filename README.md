# AGHFC-backend
Backend repository for uni project "AGH Fried Chicken"

# How to run it?
First, copy the env variables.
```
cp .env.example .env
```
Build and run the container.
```
docker compose build
docker compose up
```
Aaand you are ready to go!

# How to keep the project clean?

## Dependecies
If you want to install a dependency that will be used only in development:
```
(inside the container)
poetry add --group dev package
```
If you want to install a dependency that will be used everywhere:
```
(inside the container)
poetry add package
```

## Code
Inside the container you can use:
```
make all
```
It runs `black`, `isort`, `ruff` and `mypy` to ensure that the code is the highest quality.

You can also try to run:
```
make fix
```
It runs `ruff` with `-fix` option to autofix detected problems (at least some of them).