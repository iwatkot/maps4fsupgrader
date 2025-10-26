"""Maps4FS Container Upgrader."""

import sys
import time

import docker
from tqdm import tqdm

from maps4fsupgrader.config import ContainerParams
from maps4fsupgrader.logger import Logger

logger = Logger(level="INFO")


class Maps4FSUpgrader:
    """Handles upgrading Maps4FS containers."""

    def __init__(self):
        try:
            self.client = docker.from_env()
        except (docker.errors.DockerException, OSError) as e:
            error_msg = (
                "Error: Cannot connect to Docker daemon. "
                "This container needs access to the Docker socket.\n\n"
                "To run this container properly, use the command:\n\n"
                "docker run -v /var/run/docker.sock:/var/run/docker.sock "
                '-e USERPROFILE="$env:USERPROFILE" iwatkot/maps4fsupgrader\n\n'
                f"Original error: {e}"
            )
            logger.error(error_msg)
            sys.exit(1)

        self.containers = [
            ("maps4fsapi", ContainerParams.maps4fsapi),
            ("maps4fsui", ContainerParams.maps4fsui),
        ]

    def stop_container(self, container_name: str) -> bool:
        """Stop a container if it exists and is running."""
        try:
            container = self.client.containers.get(container_name)
            if container.status == "running":
                logger.info("Stopping container: %s", container_name)
                container.stop()
                logger.info("Container %s stopped", container_name)
                return True
            logger.info("Container %s is not running", container_name)
            return True
        except docker.errors.NotFound:
            logger.info("Container %s not found", container_name)
            return True
        except (docker.errors.APIError, docker.errors.DockerException) as e:
            logger.error("Error stopping container %s: %s", container_name, e)
            return False

    def remove_container(self, container_name: str) -> bool:
        """Remove a container if it exists."""
        try:
            container = self.client.containers.get(container_name)
            logger.info("Removing container: %s", container_name)
            container.remove()
            logger.info("Container %s removed", container_name)
            return True
        except docker.errors.NotFound:
            logger.info("Container %s not found", container_name)
            return True
        except (docker.errors.APIError, docker.errors.DockerException) as e:
            logger.error("Error removing container %s: %s", container_name, e)
            return False

    def remove_image(self, image_name: str) -> bool:
        """Remove an image if it exists."""
        try:
            logger.info("Removing image: %s", image_name)
            self.client.images.remove(image_name, force=True)
            logger.info("Image %s removed", image_name)
            return True
        except docker.errors.ImageNotFound:
            logger.info("Image %s not found", image_name)
            return True
        except (docker.errors.APIError, docker.errors.DockerException) as e:
            logger.error("Error removing image %s: %s", image_name, e)
            return False

    # pylint: disable=too-many-nested-blocks, too-many-branches
    def pull_image_with_progress(self, image_name: str) -> bool:
        """Pull a Docker image with tqdm progress bar."""
        try:
            logger.info("Pulling image: %s", image_name)

            try:
                # Pull with progress tracking
                pull_logs = self.client.api.pull(image_name, stream=True, decode=True)

                # Track layers and create progress bar
                layers = {}
                pbar = None
                total_layers = 0
                completed_layers = 0

                for line in pull_logs:
                    try:
                        if "status" in line:
                            status = line["status"]
                            layer_id = line.get("id", "")

                            # Track new layers
                            if layer_id and layer_id not in layers:
                                layers[layer_id] = {"status": "started"}
                                total_layers += 1

                                # Create progress bar on first layer
                                if not pbar:
                                    pbar = tqdm(
                                        total=0,  # We'll update total as we discover layers
                                        desc="Pulling layers",
                                        unit="layer",
                                        bar_format=(
                                            "{l_bar}{bar}| {n_fmt}/{total_fmt} layers "
                                            "[{elapsed}<{remaining}]",
                                        ),
                                    )

                                # Update total
                                pbar.total = total_layers
                                pbar.refresh()

                            # Update progress on layer completion
                            if layer_id and status == "Pull complete":
                                if (
                                    layers.get(layer_id, {}).get("status")
                                    != "completed"
                                ):
                                    layers[layer_id]["status"] = "completed"
                                    completed_layers += 1
                                    if pbar:
                                        pbar.update(1)

                            # Show final result
                            elif (
                                "Downloaded newer image" in status
                                or "Image is up to date" in status
                            ):
                                if pbar:
                                    pbar.close()
                                logger.info("Result: %s", status)
                                break

                    # pylint: disable=broad-except
                    except Exception:
                        continue

                # Close progress bar if still open
                if pbar:
                    pbar.close()

            # pylint: disable=broad-except
            except Exception as stream_error:
                # If streaming fails, fall back to simple pull
                logger.warning("Streaming failed, using simple pull: %s", stream_error)
                self.client.images.pull(image_name)

            logger.info("Successfully pulled: %s", image_name)
            return True

        except (docker.errors.APIError, docker.errors.DockerException) as e:
            logger.error("Failed to pull image %s: %s", image_name, e)
            return False

    def deploy_container(self, container_name: str, config: dict) -> bool:
        """Deploy a container with the given configuration."""
        try:
            # Pull image with progress
            if not self.pull_image_with_progress(config["image"]):
                return False

            # Prepare volumes
            volumes = {}
            if "volumes" in config:
                for host_path, container_path in config["volumes"].items():
                    # Convert Windows backslashes to forward slashes for Docker
                    docker_path = host_path.replace("\\", "/")
                    logger.info("Using volume: %s -> %s", docker_path, container_path)
                    volumes[docker_path] = {"bind": container_path, "mode": "rw"}
            logger.info("Volumes prepared for container: %s", container_name)

            # Prepare ports
            ports = {}
            if "ports" in config:
                for host_port, container_port in config["ports"].items():
                    ports[container_port] = host_port
            logger.info("Ports prepared for container: %s", container_name)

            logger.info("Creating and starting container: %s", container_name)
            default_restart = {"Name": "unless-stopped"}
            restart_policy = config.get("restart_policy", default_restart)
            self.client.containers.run(
                image=config["image"],
                name=config["name"],
                ports=ports,
                volumes=volumes,
                restart_policy=restart_policy,
                detach=True,
            )

            logger.info("Container %s deployed", container_name)
            return True

        except (docker.errors.APIError, docker.errors.DockerException) as e:
            logger.error("Error deploying container %s: %s", container_name, e)
            return False

    def upgrade_container(self, container_name: str, config: dict) -> bool:
        """Upgrade a single container: stop, remove, and redeploy."""
        logger.info("Upgrading container: %s", container_name)

        # Step 1: Stop container
        if not self.stop_container(container_name):
            return False

        # Step 2: Remove container
        if not self.remove_container(container_name):
            return False

        # Step 3: Remove image
        if not self.remove_image(config["image"]):
            return False

        # Step 4: Deploy container
        if not self.deploy_container(container_name, config):
            return False

        logger.info("Container %s upgraded successfully!", container_name)
        return True

    def upgrade_all(self) -> bool:
        """Upgrade all containers sequentially."""
        logger.info("Starting Maps4FS container upgrade process...")
        container_count = len(self.containers)
        logger.info("Processing %s containers sequentially", container_count)

        success_count = 0
        for container_name, config in self.containers:
            if self.upgrade_container(container_name, config):
                success_count += 1
                # Wait a bit between containers to ensure proper startup
                if container_name == "maps4fsapi":
                    msg = "Waiting 10 seconds for API container to start..."
                    logger.info(msg)
                    time.sleep(10)
            else:
                logger.error("Failed to upgrade %s", container_name)
                return False

        logger.info("Upgrade completed successfully!")
        containers_msg = f"{success_count}/{container_count} containers"
        logger.info("Upgraded %s", containers_msg)
        return True


def main():
    """Main entry point."""
    upgrader = Maps4FSUpgrader()

    try:
        success = upgrader.upgrade_all()
        if success:
            logger.info("All containers upgraded successfully!")
            sys.exit(0)
        logger.error("Upgrade failed!")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.warning("Upgrade interrupted by user")
        sys.exit(1)
    except (docker.errors.DockerException, OSError) as e:
        logger.error("Unexpected error: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
