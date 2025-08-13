import requests
import subprocess
from zipfile import ZipFile
from io import BytesIO
import sys


def pull_artifact(gh_repo, gh_token, artifact_name, output_path):
    # try: # if want to add hash to the artifact name
    #     git_hash = (
    #         subprocess.check_output(["git", "rev-parse", "HEAD"])
    #         .strip()
    #         .decode("ascii")
    #     )
    # except subprocess.CalledProcessError:
    #     print("rtds_action: can't get git hash")
    #     return

    r = requests.get(
        f"https://api.github.com/repos/{gh_repo}/actions/artifacts",
        params=dict(per_page=100),
        headers={"Authorization": f"token {gh_token}"},
    )
    if r.status_code != 200:
        print(f"Can't list files ({r.status_code})")
        return

    expected_name = f"{artifact_name}"
    result = r.json()
    for artifact in result.get("artifacts", []):
        if artifact["name"] == expected_name:
            print(artifact)
            r = requests.get(
                artifact["archive_download_url"],
                headers={"Authorization": f"token {gh_token}"},
            )

            if r.status_code != 200:
                print(f"Can't download artifact ({r.status_code})")
                return

            with ZipFile(BytesIO(r.content)) as f:
                f.extractall(path=output_path)

    return

if __name__ == '__main__':

    gh_repo = sys.argv[1]
    gh_token = sys.argv[2]
    artifact_name = sys.argv[3]
    output_path = sys.argv[4]

    pull_artifact(gh_repo, gh_token, artifact_name, output_path)
