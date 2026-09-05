pyinstaller `
    --clean `
    --onefile `
    --name devops `
    --distpath dist/windows `
    devops/__main__.py

Remove-Item -Recurse -Force build
Remove-Item -Force devops.spec

docker build `
    -f devops/Dockerfile `
    -o dist/linux `
    devops