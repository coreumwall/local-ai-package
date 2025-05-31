#!/usr/bin/env python3
"""
start_services.py

This script starts the Supabase stack first, waits for it to initialize, and then starts
the local AI stack. Both stacks use the same Docker Compose project name ("localai")
so they appear together in Docker Desktop.
"""

import os
import subprocess
import shutil
import time
import argparse
import platform
import sys

def run_command(cmd, cwd=None):
    """Run a shell command and print it."""
    print("Running:", " ".join(cmd))
    subprocess.run(cmd, cwd=cwd, check=True)

def clone_supabase_repo():
    """Clone the Supabase repository using sparse checkout if not already present."""
    if not os.path.exists("supabase"):
        print("Cloning the Supabase repository...")
        run_command([
            "git", "clone", "--filter=blob:none", "--no-checkout",
            "https://github.com/supabase/supabase.git"
        ])
        os.chdir("supabase")
        run_command(["git", "sparse-checkout", "init", "--cone"])
        run_command(["git", "sparse-checkout", "set", "docker"])
        run_command(["git", "checkout", "master"])
        os.chdir("..")
    else:
        print("Supabase repository already exists, updating...")
        os.chdir("supabase")
        run_command(["git", "pull"])
        os.chdir("..")

def prepare_supabase_env():
    """Copy .env to .env in supabase/docker."""
    env_path = os.path.join("supabase", "docker", ".env")
    env_example_path = os.path.join(".env")
    print("Copying .env in root to .env in supabase/docker...")
    shutil.copyfile(env_example_path, env_path)

def stop_existing_containers(profile=None):
    print("Stopping and removing existing containers for the unified project 'localai'...")
    cmd = ["docker", "compose", "-p", "localai"]
    if profile and profile != "none":
        cmd.extend(["--profile", profile])
    cmd.extend(["-f", "docker-compose.yml", "down"])
    run_command(cmd)

def start_supabase():
    """Start the Supabase services (using its compose file)."""
    print("Starting Supabase services...")
    run_command([
        "docker", "compose", "-p", "localai", "-f", "supabase/docker/docker-compose.yml", "up", "-d"
    ])

def start_local_ai(profile=None, services_to_start=None):
    """Start the local AI services (using its compose file)."""
    cmd = ["docker", "compose", "-p", "localai"]
    if profile and profile != "none":
        cmd.extend(["--profile", profile])
    cmd.extend(["-f", "docker-compose.yml", "up", "-d"])

    if services_to_start:
        print(f"Starting selected local AI services: {', '.join(services_to_start)}")
        cmd.extend(services_to_start)
    else:
        print("Starting all local AI services based on profile (or no specific services requested)...")

    run_command(cmd)

def generate_searxng_secret_key():
    """Generate a secret key for SearXNG based on the current platform."""
    print("Checking SearXNG settings...")
    
    # Define paths for SearXNG settings files
    settings_path = os.path.join("searxng", "settings.yml")
    settings_base_path = os.path.join("searxng", "settings-base.yml")
    
    # Check if settings-base.yml exists
    if not os.path.exists(settings_base_path):
        print(f"Warning: SearXNG base settings file not found at {settings_base_path}")
        return
    
    # Check if settings.yml exists, if not create it from settings-base.yml
    if not os.path.exists(settings_path):
        print(f"SearXNG settings.yml not found. Creating from {settings_base_path}...")
        try:
            shutil.copyfile(settings_base_path, settings_path)
            print(f"Created {settings_path} from {settings_base_path}")
        except Exception as e:
            print(f"Error creating settings.yml: {e}")
            return
    else:
        print(f"SearXNG settings.yml already exists at {settings_path}")
    
    print("Generating SearXNG secret key...")
    
    # Detect the platform and run the appropriate command
    system = platform.system()
    
    try:
        if system == "Windows":
            print("Detected Windows platform, using PowerShell to generate secret key...")
            # PowerShell command to generate a random key and replace in the settings file
            ps_command = [
                "powershell", "-Command",
                "$randomBytes = New-Object byte[] 32; " +
                "(New-Object Security.Cryptography.RNGCryptoServiceProvider).GetBytes($randomBytes); " +
                "$secretKey = -join ($randomBytes | ForEach-Object { \"{0:x2}\" -f $_ }); " +
                "(Get-Content searxng/settings.yml) -replace 'ultrasecretkey', $secretKey | Set-Content searxng/settings.yml"
            ]
            subprocess.run(ps_command, check=True)
            
        elif system == "Darwin":  # macOS
            print("Detected macOS platform, using sed command with empty string parameter...")
            # macOS sed command requires an empty string for the -i parameter
            openssl_cmd = ["openssl", "rand", "-hex", "32"]
            random_key = subprocess.check_output(openssl_cmd).decode('utf-8').strip()
            sed_cmd = ["sed", "-i", "", f"s|ultrasecretkey|{random_key}|g", settings_path]
            subprocess.run(sed_cmd, check=True)
            
        else:  # Linux and other Unix-like systems
            print("Detected Linux/Unix platform, using standard sed command...")
            # Standard sed command for Linux
            openssl_cmd = ["openssl", "rand", "-hex", "32"]
            random_key = subprocess.check_output(openssl_cmd).decode('utf-8').strip()
            sed_cmd = ["sed", "-i", f"s|ultrasecretkey|{random_key}|g", settings_path]
            subprocess.run(sed_cmd, check=True)
            
        print("SearXNG secret key generated successfully.")
        
    except Exception as e:
        print(f"Error generating SearXNG secret key: {e}")
        print("You may need to manually generate the secret key using the commands:")
        print("  - Linux: sed -i \"s|ultrasecretkey|$(openssl rand -hex 32)|g\" searxng/settings.yml")
        print("  - macOS: sed -i '' \"s|ultrasecretkey|$(openssl rand -hex 32)|g\" searxng/settings.yml")
        print("  - Windows (PowerShell):")
        print("    $randomBytes = New-Object byte[] 32")
        print("    (New-Object Security.Cryptography.RNGCryptoServiceProvider).GetBytes($randomBytes)")
        print("    $secretKey = -join ($randomBytes | ForEach-Object { \"{0:x2}\" -f $_ })")
        print("    (Get-Content searxng/settings.yml) -replace 'ultrasecretkey', $secretKey | Set-Content searxng/settings.yml")

def check_and_fix_docker_compose_for_searxng():
    """Check and modify docker-compose.yml for SearXNG first run."""
    docker_compose_path = "docker-compose.yml"
    if not os.path.exists(docker_compose_path):
        print(f"Warning: Docker Compose file not found at {docker_compose_path}")
        return
    
    try:
        # Read the docker-compose.yml file
        with open(docker_compose_path, 'r') as file:
            content = file.read()
        
        # Default to first run
        is_first_run = True
        
        # Check if Docker is running and if the SearXNG container exists
        try:
            # Check if the SearXNG container is running
            container_check = subprocess.run(
                ["docker", "ps", "--filter", "name=searxng", "--format", "{{.Names}}"],
                capture_output=True, text=True, check=True
            )
            searxng_containers = container_check.stdout.strip().split('\n')
            
            # If SearXNG container is running, check inside for uwsgi.ini
            if any(container for container in searxng_containers if container):
                container_name = next(container for container in searxng_containers if container)
                print(f"Found running SearXNG container: {container_name}")
                
                # Check if uwsgi.ini exists inside the container
                container_check = subprocess.run(
                    ["docker", "exec", container_name, "sh", "-c", "[ -f /etc/searxng/uwsgi.ini ] && echo 'found' || echo 'not_found'"],
                    capture_output=True, text=True, check=False
                )
                
                if "found" in container_check.stdout:
                    print("Found uwsgi.ini inside the SearXNG container - not first run")
                    is_first_run = False
                else:
                    print("uwsgi.ini not found inside the SearXNG container - first run")
                    is_first_run = True
            else:
                print("No running SearXNG container found - assuming first run")
        except Exception as e:
            print(f"Error checking Docker container: {e} - assuming first run")
        
        if is_first_run and "cap_drop: - ALL" in content:
            print("First run detected for SearXNG. Temporarily removing 'cap_drop: - ALL' directive...")
            # Temporarily comment out the cap_drop line
            modified_content = content.replace("cap_drop: - ALL", "# cap_drop: - ALL  # Temporarily commented out for first run")
            
            # Write the modified content back
            with open(docker_compose_path, 'w') as file:
                file.write(modified_content)
                
            print("Note: After the first run completes successfully, you should re-add 'cap_drop: - ALL' to docker-compose.yml for security reasons.")
        elif not is_first_run and "# cap_drop: - ALL  # Temporarily commented out for first run" in content:
            print("SearXNG has been initialized. Re-enabling 'cap_drop: - ALL' directive for security...")
            # Uncomment the cap_drop line
            modified_content = content.replace("# cap_drop: - ALL  # Temporarily commented out for first run", "cap_drop: - ALL")
            
            # Write the modified content back
            with open(docker_compose_path, 'w') as file:
                file.write(modified_content)
    
    except Exception as e:
        print(f"Error checking/modifying docker-compose.yml for SearXNG: {e}")

def main():
    parser = argparse.ArgumentParser(description='Start the local AI and Supabase services.')
    parser.add_argument('--profile', choices=['cpu', 'gpu-nvidia', 'gpu-amd', 'none'], default='cpu',
                      help='Profile to use for Docker Compose (default: cpu)')
    parser.add_argument('--services', type=str, default=None,
                      help='Comma-separated list of services to start (e.g., flowise,ollama,open-webui). If not provided, all services are started.')
    args = parser.parse_args()

    # --- Service Definitions and Dependencies ---
    # This map defines user-friendly names to actual service names in docker-compose
    # and their direct dependencies.
    SERVICE_MAP = {
        "flowise": {"services": ["flowise"], "depends_on": []},
        "open-webui": {"services": ["open-webui"], "depends_on": ["ollama"]},
        "n8n": {"services": ["n8n", "n8n-import"], "depends_on": ["postgres"]},
        "qdrant": {"services": ["qdrant"], "depends_on": []},
        "neo4j": {"services": ["neo4j"], "depends_on": []},
        "caddy": {"services": ["caddy"], "depends_on": []},
        "langfuse": {
            "services": ["langfuse-worker", "langfuse-web", "clickhouse", "minio", "postgres", "redis"],
            "depends_on": [] # Internal dependencies are in docker-compose.yml
        },
        "minio": {"services": ["minio"], "depends_on": []},
        "postgres": {"services": ["postgres"], "depends_on": []},
        "redis": {"services": ["redis"], "depends_on": []},
        "searxng": {"services": ["searxng"], "depends_on": []},
        "litellm": {"services": ["litellm"], "depends_on": ["ollama", "redis"]},
        "ollama": { # Ollama is profile-dependent
            "cpu": {"services": ["ollama-cpu", "ollama-pull-llama-cpu"], "depends_on": []},
            "gpu-nvidia": {"services": ["ollama-gpu", "ollama-pull-llama-gpu"], "depends_on": []},
            "gpu-amd": {"services": ["ollama-gpu-amd", "ollama-pull-llama-gpu-amd"], "depends_on": []},
            "none": {"services": [], "depends_on": []}
        },
    }

    clone_supabase_repo()
    prepare_supabase_env()
    
    # Generate SearXNG secret key and check docker-compose.yml
    generate_searxng_secret_key()
    check_and_fix_docker_compose_for_searxng()
    
    stop_existing_containers(args.profile) # Stops all services in the 'localai' project
    
    # Start Supabase first
    start_supabase()
    
    # Give Supabase some time to initialize
    print("Waiting for Supabase to initialize...")
    time.sleep(10)
    
    # Determine which local AI services to start
    services_to_actually_run = []
    if args.services:
        requested_services_input = [s.strip().lower() for s in args.services.split(',')]

        services_to_process_queue = list(requested_services_input) # Queue to manage services and their dependencies
        final_service_set = set() # Using a set to avoid duplicates

        processed_for_dependencies = set() # Keep track of services whose dependencies have been added

        while services_to_process_queue:
            service_name = services_to_process_queue.pop(0)

            if service_name in processed_for_dependencies:
                continue

            actual_service_names_to_add = []
            dependencies_to_add_to_queue = []

            if service_name == "ollama":
                # Determine correct Ollama services based on profile
                ollama_profile_key = args.profile if args.profile in SERVICE_MAP["ollama"] else "cpu"
                if ollama_profile_key == "none": # if profile is none, ollama effectively means no services
                    print("Ollama selected but profile is 'none'. No Ollama services will be started.")
                    actual_service_names_to_add = []
                else:
                    actual_service_names_to_add = SERVICE_MAP["ollama"][ollama_profile_key]["services"]
                # Ollama's internal services (e.g., puller) are part of its definition, no further deps here.
            elif service_name in SERVICE_MAP:
                service_info = SERVICE_MAP[service_name]
                actual_service_names_to_add = service_info["services"]
                dependencies_to_add_to_queue = service_info["depends_on"]
            else:
                print(f"Warning: Service '{service_name}' not recognized and will be ignored.")
                processed_for_dependencies.add(service_name) # Mark as processed to avoid re-warning
                continue

            for s_name in actual_service_names_to_add:
                final_service_set.add(s_name)

            processed_for_dependencies.add(service_name)

            for dep in dependencies_to_add_to_queue:
                if dep not in processed_for_dependencies:
                    services_to_process_queue.append(dep) # Add dependency to the queue

        services_to_actually_run = list(final_service_set)

        # Caddy is a special case: if any service is targeted for startup, Caddy should also run.
        if services_to_actually_run and "caddy" not in services_to_actually_run and "caddy" in SERVICE_MAP:
            caddy_services = SERVICE_MAP["caddy"]["services"]
            if not any(cs in services_to_actually_run for cs in caddy_services): # Avoid adding if already present
                 print("Adding 'caddy' service as other services are being started.")
                 services_to_actually_run.extend(caddy_services)


        if not services_to_actually_run and requested_services_input:
            # This means user specified services, but none were valid or resolved to actual service names
            print("No valid services were selected to start. Supabase is running. No other Local AI services will be started.")
            sys.exit(0) # Exit gracefully, Supabase is up, but no local AI services.

    if args.services is None:
        # No specific services requested, start all services for the given profile
        print("No specific services selected via --services, starting all Local AI services for the profile.")
        start_local_ai(args.profile)
    elif services_to_actually_run:
        # Start the selected and dependency-resolved services
        start_local_ai(args.profile, services_to_actually_run)
    else:
        # This case implies args.services was given, but resulted in an empty list (e.g. only "ollama" with profile "none")
        # and no other services that would pull in Caddy.
        print("No Local AI services will be started based on selection and profile. Supabase is running.")

if __name__ == "__main__":
    main()
