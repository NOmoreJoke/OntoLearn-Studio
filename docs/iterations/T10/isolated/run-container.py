"""Start only this task's private Docker display; never start a host Electron."""

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--attempt", type=int, required=True)
attempt = parser.parse_args().attempt
assert 1 <= attempt <= 99
NAME = f"ontolearn-t10-01a15bce-native-v{attempt}"
IMAGE = "ontolearn-t10-native:a8a497a-v1"
OUTPUT = Path(__file__).resolve().parents[3] / f"reviews/T10/evidence/out/isolated-v{attempt}"
OUTPUT.mkdir(parents=True, exist_ok=False)
(OUTPUT / "host-driver-sha256.txt").write_text(
    hashlib.sha256(Path(__file__).read_bytes()).hexdigest() + "\n"
)


def docker(*args, timeout=20):
    return subprocess.run(
        ["docker", *args], check=True, capture_output=True, text=True, timeout=timeout
    ).stdout


created = False
try:
    container_id = docker(
        "create",
        "--name",
        NAME,
        "--label",
        "org.ontolearn.task=T10",
        "--user",
        "1110:1110",
        "--network",
        "none",
        "--cap-add",
        "SYS_ADMIN",
        "--cpus",
        "2",
        "--memory",
        "4g",
        "--shm-size",
        "1g",
        "--pids-limit",
        "512",
        IMAGE,
    ).strip()
    created = True
    info = json.loads(docker("inspect", container_id))[0]
    host = info["HostConfig"]
    config = {
        "id": info["Id"],
        "image": info["Image"],
        "user": info["Config"]["User"],
        "networkMode": host["NetworkMode"],
        "privileged": host["Privileged"],
        "capAdd": host["CapAdd"],
        "securityOpt": host["SecurityOpt"],
        "mounts": info["Mounts"],
        "portBindings": host["PortBindings"],
        "nanoCpus": host["NanoCpus"],
        "memory": host["Memory"],
        "shmSize": host["ShmSize"],
        "pidsLimit": host["PidsLimit"],
        "pidMode": host["PidMode"],
        "ipcMode": host["IpcMode"],
    }
    (OUTPUT / "container-config.json").write_text(json.dumps(config, indent=2) + "\n")
    assert container_id == config["id"]
    assert config["user"] == "1110:1110" and config["networkMode"] == "none"
    assert config["privileged"] is False and config["capAdd"] in (["SYS_ADMIN"], ["CAP_SYS_ADMIN"])
    assert not config["securityOpt"] and not config["mounts"] and not config["portBindings"]
    assert config["pidMode"] == "" and config["ipcMode"] == "private"
    assert config["nanoCpus"] == 2_000_000_000 and config["memory"] == 4 * 1024**3
    assert config["shmSize"] == 1024**3 and config["pidsLimit"] == 512
    # A build may have started before the review fixes. Verify its exact scripts before launch.
    controls = OUTPUT / "image-controls"
    controls.mkdir()
    docker("cp", f"{container_id}:/opt/t10-controls/.", str(controls), timeout=30)
    manifest = json.loads((controls / "manifest.json").read_text())
    checked_controls = {}
    for filename in ["run.sh", "prepare-native.mjs", "native-hook.cjs", "native-driver.mjs"]:
        actual = hashlib.sha256((controls / filename).read_bytes()).hexdigest()
        expected = hashlib.sha256(Path(__file__).with_name(filename).read_bytes()).hexdigest()
        assert actual == expected == manifest["controls"][filename], filename
        checked_controls[filename] = actual
    (OUTPUT / "verified-controls.json").write_text(json.dumps(checked_controls, indent=2) + "\n")
    result = subprocess.run(
        ["docker", "start", "--attach", container_id], capture_output=True, text=True, timeout=100
    )
    (OUTPUT / "container-stdout.txt").write_text(result.stdout)
    (OUTPUT / "container-stderr.txt").write_text(result.stderr)
    state = json.loads(docker("inspect", container_id))[0]["State"]
    (OUTPUT / "container-state.json").write_text(json.dumps(state, indent=2) + "\n")
    docker("cp", f"{container_id}:/opt/t10-evidence/.", str(OUTPUT), timeout=30)
    assert result.returncode == 0 and state["Status"] == "exited" and state["ExitCode"] == 0
finally:
    if created:
        # Stop this exact created container only. Keep the stopped container for audit.
        state = json.loads(docker("inspect", container_id))[0]["State"]
        if state["Running"]:
            docker("kill", container_id)
        state = json.loads(docker("inspect", container_id))[0]["State"]
        (OUTPUT / "final-state.json").write_text(json.dumps(state, indent=2) + "\n")
        docker("cp", f"{container_id}:/opt/t10-evidence/.", str(OUTPUT), timeout=30)
