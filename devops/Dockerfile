FROM python:3.14 AS build
WORKDIR /src
RUN pip install --no-cache-dir pyinstaller questionary
COPY . .
RUN pyinstaller --clean --onefile --name devops ./__main__.py

FROM scratch
COPY --from=build /src/dist/devops /devops