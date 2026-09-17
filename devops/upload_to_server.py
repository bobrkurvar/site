import shlex
import subprocess
from core import conf

def remote_directory_exists(server: str, path: str) -> bool:
    result = subprocess.run(
        [
            "ssh",
            server,
            f"test -d {shlex.quote(path)}",
        ]
    )
    return result.returncode == 0

def upload_release():
    remote_path = "newsite"
    if not remote_directory_exists(
        conf.server,
        remote_path,
    ):
        print(f"Remote path not found: {remote_path}")
        return

    subprocess.run(
        [
            "scp",
            "-r",
            "docker-compose.base.yml",
            "docker-compose.prod.yml",
            "dist/linux/devops",
            "db_archive/migrations",
            "nginx",
            ".env",
            f"{conf.server}:{remote_path}/",
        ],
        check=True,
    )