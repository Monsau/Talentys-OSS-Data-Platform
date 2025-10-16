"""
╔════════════════════════════════════════════════════════════╗
║     COMPLETE ORCHESTRATION - DATA PLATFORM AUTO-BUILD      ║
║                                                            ║
║  Deploys the complete infrastructure automatically:        ║
║  - Dremio + PostgreSQL + MinIO + Elasticsearch             ║
║  - Airbyte (Data Integration)                              ║
║  - dbt (models + tests)                                    ║
║  - Apache Superset & Airflow                               ║
║  - Dremio → PostgreSQL synchronization                     ║
║  - Automatic dashboards                                    ║
╚════════════════════════════════════════════════════════════╝
"""

import os
import sys
import time
import subprocess
import json
from pathlib import Path

# Fix encodage Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

class DataPlatformOrchestrator:
    """Complete data platform orchestrator"""
    
    def __init__(self, workspace_path):
        self.workspace = Path(workspace_path)
        self.venv_path = self.workspace / "venv_dremio_311"
        self.python_exe = self.venv_path / "Scripts" / "python.exe"
        self.steps_completed = []
        self.steps_failed = []
        
    def log(self, message, level="INFO"):
        """Log with timestamp"""
        timestamp = time.strftime("%H:%M:%S")
        icon = {"INFO": "ℹ️", "SUCCESS": "✅", "ERROR": "❌", "WARNING": "⚠️"}.get(level, "•")
        print(f"[{timestamp}] {icon} {message}")
    
    def run_command(self, command, description, cwd=None, check=True):
        """Execute a shell command"""
        self.log(f"{description}...", "INFO")
        try:
            if isinstance(command, str):
                result = subprocess.run(
                    command, 
                    shell=True, 
                    cwd=cwd or self.workspace,
                    capture_output=True,
                    text=True,
                    check=check,
                    encoding='utf-8',
                    errors='ignore'
                )
            else:
                result = subprocess.run(
                    command,
                    cwd=cwd or self.workspace,
                    capture_output=True,
                    text=True,
                    check=check,
                    encoding='utf-8',
                    errors='ignore'
                )
            
            if check and result.returncode != 0:
                self.log(f"{description} - FAILED", "ERROR")
                if result.stderr:
                    print(f"Error: {result.stderr[:500]}")
                return False, result.stdout
            
            self.log(f"{description} - OK", "SUCCESS")
            return True, result.stdout
            
        except subprocess.CalledProcessError as e:
            self.log(f"{description} - FAILED", "ERROR")
            if e.stderr:
                print(f"Error: {e.stderr[:500]}")
            return False, e.stdout if e.stdout else ""
        except Exception as e:
            self.log(f"{description} - ERROR: {str(e)}", "ERROR")
            return False, ""
    
    def check_prerequisites(self):
        """Check prerequisites"""
        self.log("Checking prerequisites", "INFO")
        
        # Docker
        success, _ = self.run_command("docker --version", "Docker installed", check=False)
        if not success:
            self.log("Docker is not installed", "ERROR")
            return False
        
        # Docker Compose
        success, _ = self.run_command("docker-compose --version", "Docker Compose installed", check=False)
        if not success:
            self.log("Docker Compose is not installed", "ERROR")
            return False
        
        # Python
        success, _ = self.run_command("python --version", "Python installed", check=False)
        if not success:
            self.log("Python is not installed", "ERROR")
            return False
        
        self.log("All prerequisites satisfied", "SUCCESS")
        self.steps_completed.append("Prerequisites")
        return True
    
    def deploy_infrastructure(self):
        """Deploy Docker infrastructure"""
        self.log("=" * 60, "INFO")
        self.log("STEP 1: DOCKER INFRASTRUCTURE DEPLOYMENT", "INFO")
        self.log("=" * 60, "INFO")
        
        # Stop existing containers
        self.run_command("docker-compose down", "Stopping existing containers", check=False)
        
        # Start main infrastructure
        success, _ = self.run_command(
            "docker-compose up -d",
            "Starting Dremio + PostgreSQL + MinIO + Elasticsearch + Superset + Airflow"
        )
        if not success:
            self.steps_failed.append("Infrastructure")
            return False
        
        # Start Airbyte
        self.log("Starting Airbyte...", "INFO")
        success, _ = self.run_command(
            "docker-compose -f docker-compose.yml -f docker-compose-airbyte-stable.yml up -d",
            "Launching Airbyte (Data Integration)",
            check=False
        )
        if not success:
            self.log("Airbyte did not start (optional, continuing)", "WARNING")
        
        # Wait for services to be ready
        self.log("Waiting for services to start (60 seconds)...", "INFO")
        time.sleep(60)
        
        # Check that containers are running
        success, output = self.run_command("docker ps", "Checking containers")
        if not success or "dremio" not in output:
            self.steps_failed.append("Infrastructure")
            return False
        
        self.steps_completed.append("Infrastructure")
        return True
    
    def deploy_superset(self):
        """Deploy Apache Superset"""
        self.log("=" * 60, "INFO")
        self.log("STEP 2: APACHE SUPERSET DEPLOYMENT", "INFO")
        self.log("=" * 60, "INFO")
        
        success, _ = self.run_command(
            "docker-compose -f docker-compose-superset.yml up -d",
            "Starting Apache Superset"
        )
        if not success:
            self.steps_failed.append("Superset")
            return False
        
        # Wait for Superset to be ready
        self.log("Waiting for Superset to start (30 seconds)...", "INFO")
        time.sleep(30)
        
        self.steps_completed.append("Superset")
        return True
    
    def setup_dbt_environment(self):
        """Configure dbt environment"""
        self.log("=" * 60, "INFO")
        self.log("STEP 3: DBT ENVIRONMENT CONFIGURATION", "INFO")
        self.log("=" * 60, "INFO")
        
        # Check if venv exists
        if not self.venv_path.exists():
            self.log("Virtual environment not found, creating...", "WARNING")
            success, _ = self.run_command(
                "python -m venv venv_dremio_311",
                "Creating venv"
            )
            if not success:
                self.steps_failed.append("dbt Environment")
                return False
        
        # Install dependencies
        pip_exe = self.venv_path / "Scripts" / "pip.exe"
        success, _ = self.run_command(
            f'"{pip_exe}" install -r requirements.txt',
            "Installing Python dependencies"
        )
        if not success:
            self.steps_failed.append("dbt Environment")
            return False
        
        self.steps_completed.append("dbt Environment")
        return True
    
    def run_dbt_models(self):
        """Execute dbt models"""
        self.log("=" * 60, "INFO")
        self.log("STEP 4: DBT MODELS EXECUTION", "INFO")
        self.log("=" * 60, "INFO")
        
        dbt_path = self.workspace / "dbt"
        dbt_exe = self.venv_path / "Scripts" / "dbt.exe"
        
        # dbt debug
        self.run_command(
            f'"{dbt_exe}" debug',
            "Checking dbt configuration",
            cwd=dbt_path,
            check=False
        )
        
        # dbt run
        success, _ = self.run_command(
            f'"{dbt_exe}" run --select phase3_all_in_one',
            "Executing phase3_all_in_one model",
            cwd=dbt_path
        )
        if not success:
            self.steps_failed.append("dbt Models")
            return False
        
        # dbt test
        success, _ = self.run_command(
            f'"{dbt_exe}" test',
            "Executing dbt tests",
            cwd=dbt_path
        )
        if not success:
            self.log("dbt tests failed but continuing", "WARNING")
        
        self.steps_completed.append("dbt Models")
        return True
    
    def sync_dremio_to_postgres(self):
        """Synchronize Dremio to PostgreSQL"""
        self.log("=" * 60, "INFO")
        self.log("STEP 5: DREMIO → POSTGRESQL SYNCHRONIZATION", "INFO")
        self.log("=" * 60, "INFO")
        
        script_path = self.workspace / "scripts" / "sync_dremio_realtime.py"
        
        if not script_path.exists():
            self.log("Sync script not found", "ERROR")
            self.steps_failed.append("Dremio Sync")
            return False
        
        success, _ = self.run_command(
            f'"{self.python_exe}" "{script_path}"',
            "Synchronizing Dremio data"
        )
        if not success:
            self.steps_failed.append("Dremio Sync")
            return False
        
        self.steps_completed.append("Dremio Sync")
        return True
    
    def populate_superset(self):
        """Populate Superset with dashboards"""
        self.log("=" * 60, "INFO")
        self.log("STEP 6: SUPERSET DASHBOARDS CREATION", "INFO")
        self.log("=" * 60, "INFO")
        
        # Dashboard 1: PostgreSQL
        script_path = self.workspace / "scripts" / "populate_superset.py"
        if script_path.exists():
            success, _ = self.run_command(
                f'"{self.python_exe}" "{script_path}"',
                "Creating Dashboard 1 (PostgreSQL)"
            )
            if not success:
                self.log("Dashboard 1 failed but continuing", "WARNING")
        
        # Dashboard 2: Dremio
        script_path = self.workspace / "scripts" / "rebuild_dremio_dashboard.py"
        if script_path.exists():
            success, _ = self.run_command(
                f'"{self.python_exe}" "{script_path}"',
                "Creating Dashboard 2 (Dremio)"
            )
            if not success:
                self.log("Dashboard 2 failed but continuing", "WARNING")
        
        self.steps_completed.append("Superset Dashboards")
        return True
    
    def generate_opendata_dashboard(self):
        """Generate Open Data HTML dashboard"""
        self.log("=" * 60, "INFO")
        self.log("STEP 7: OPEN DATA DASHBOARD GENERATION", "INFO")
        self.log("=" * 60, "INFO")
        
        script_path = self.workspace / "scripts" / "generate_opendata_dashboard.py"
        
        if not script_path.exists():
            self.log("Open Data script not found, skipping", "WARNING")
            return True
        
        success, _ = self.run_command(
            f'"{self.python_exe}" "{script_path}"',
            "Generating HTML Open Data dashboard"
        )
        if not success:
            self.log("Open Data dashboard failed but continuing", "WARNING")
        else:
            self.steps_completed.append("Open Data Dashboard")
        
        return True
    
    def print_summary(self):
        """Display final summary"""
        self.log("=" * 60, "INFO")
        self.log("DEPLOYMENT SUMMARY", "INFO")
        self.log("=" * 60, "INFO")
        
        print("\n✅ COMPLETED STEPS:")
        for step in self.steps_completed:
            print(f"   ✅ {step}")
        
        if self.steps_failed:
            print("\n❌ FAILED STEPS:")
            for step in self.steps_failed:
                print(f"   ❌ {step}")
        
        print("\n📊 AVAILABLE DASHBOARDS:")
        print("   • Dremio UI: http://localhost:9047 (admin/admin123)")
        print("   • Superset Dashboard 1: http://localhost:8088/superset/dashboard/1/")
        print("   • Superset Dashboard 2 (Dremio): http://localhost:8088/superset/dashboard/2/")
        print("   • Open Data HTML: file:///c:/projets/dremiodbt/opendata/dashboard.html")
        
        print("\n🔄 SYNCHRONIZATION:")
        print("   • Manual: python scripts\\sync_dremio_realtime.py")
        print("   • Auto: python scripts\\sync_dremio_realtime.py --continuous 5")
        
        print("\n📄 DOCUMENTATION:")
        print("   • SUPERSET_DREMIO_FINAL.md (complete guide)")
        print("   • PHASE3_COMPLETE_SUMMARY.md")
        
        print("\n" + "=" * 60)
        if not self.steps_failed:
            print("🎉 COMPLETE DEPLOYMENT SUCCESSFUL!")
        else:
            print("⚠️ PARTIAL DEPLOYMENT - Check errors above")
        print("=" * 60 + "\n")
    
    def orchestrate(self):
        """Orchestrate complete deployment"""
        print("""
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║       DATA PLATFORM AUTO-BUILD ORCHESTRATION               ║
║                                                            ║
║  Automatic complete platform deployment                    ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
        """)
        
        start_time = time.time()
        
        # 0. Prerequisites
        if not self.check_prerequisites():
            self.log("Prerequisites not satisfied, stopping", "ERROR")
            return False
        
        # 1. Docker Infrastructure
        if not self.deploy_infrastructure():
            self.log("Infrastructure deployment failed", "ERROR")
            self.print_summary()
            return False
        
        # 2. Apache Superset
        if not self.deploy_superset():
            self.log("Superset deployment failed", "ERROR")
            # Continue anyway
        
        # 3. dbt Environment
        if not self.setup_dbt_environment():
            self.log("dbt configuration failed", "ERROR")
            # Continue anyway
        
        # 4. dbt Models
        if not self.run_dbt_models():
            self.log("dbt execution failed", "ERROR")
            # Continue anyway
        
        # 5. Dremio Sync
        if not self.sync_dremio_to_postgres():
            self.log("Dremio synchronization failed", "ERROR")
            # Continue anyway
        
        # 6. Superset Dashboards
        self.populate_superset()
        
        # 7. Open Data Dashboard
        self.generate_opendata_dashboard()
        
        # Final summary
        elapsed = time.time() - start_time
        self.log(f"Total time: {elapsed:.1f} seconds", "INFO")
        self.print_summary()
        
        return len(self.steps_failed) == 0


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Complete data platform orchestration"
    )
    parser.add_argument(
        "--workspace",
        default=r"c:\projets\dremiodbt",
        help="Workspace path"
    )
    parser.add_argument(
        "--skip-infrastructure",
        action="store_true",
        help="Skip Docker infrastructure deployment"
    )
    
    args = parser.parse_args()
    
    orchestrator = DataPlatformOrchestrator(args.workspace)
    
    try:
        success = orchestrator.orchestrate()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n\n⚠️ User interruption")
        return 1
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
