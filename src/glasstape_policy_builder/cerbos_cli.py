"""Cerbos CLI Interface - Wrapper for executing Cerbos CLI commands."""

import subprocess
import tempfile
import re
from pathlib import Path
from typing import Optional

from .types import ValidationResult, TestResult


class CerbosCLI:
    """Interface to Cerbos CLI for validation and testing"""
    
    def __init__(self, work_dir: Optional[str] = None):
        # Sanitize work directory to prevent path traversal
        if work_dir:
            work_dir = Path(work_dir).resolve()  # Resolve to absolute path
            # Ensure it's within safe boundaries
            if not str(work_dir).startswith(('/tmp', tempfile.gettempdir())):
                raise ValueError("Work directory must be within /tmp or system temp directory")
        
        self.work_dir = Path(work_dir or tempfile.gettempdir()) / "glasstape-policies"
        self.work_dir.mkdir(parents=True, exist_ok=True)
    
    def check_installation(self) -> bool:
        """Check if Cerbos CLI is installed"""
        try:
            result = subprocess.run(
                ['cerbos', '--version'],
                capture_output=True,
                text=True,
                timeout=5,
                shell=False  # Prevent shell injection
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            return False
    
    def compile(self, policy_yaml: str) -> ValidationResult:
        """
        Validate policy with cerbos compile
        
        Args:
            policy_yaml: Cerbos policy YAML string
            
        Returns:
            ValidationResult with success status and any errors/warnings
        """
        try:
            # Create temporary policy file
            policy_file = self.work_dir / "policy.yaml"
            policy_file.write_text(policy_yaml)
            
            # Run cerbos compile
            result = subprocess.run(
                ['cerbos', 'compile', str(self.work_dir)],
                capture_output=True,
                text=True,
                timeout=30,
                shell=False  # Prevent shell injection
            )
            
            output = result.stdout + result.stderr
            
            # Check for errors
            if 'error' in output.lower() or result.returncode != 0:
                return ValidationResult(
                    success=False,
                    errors=self._extract_errors(output),
                    warnings=self._extract_warnings(output)
                )
            
            return ValidationResult(
                success=True,
                errors=[],
                warnings=self._extract_warnings(output)
            )
            
        except subprocess.TimeoutExpired:
            return ValidationResult(
                success=False,
                errors=["Validation timeout - policy compilation took too long"],
                warnings=[]
            )
        except Exception as e:
            return ValidationResult(
                success=False,
                errors=[f"Validation error: {str(e)}"],
                warnings=[]
            )
        finally:
            # Clean up
            policy_file.unlink(missing_ok=True)
    
    def test(self, policy_yaml: str, test_yaml: str) -> TestResult:
        """
        Run tests with cerbos test
        
        Args:
            policy_yaml: Cerbos policy YAML string
            test_yaml: Cerbos test suite YAML string
            
        Returns:
            TestResult with pass/fail counts and details
        """
        try:
            # Setup files
            policy_file = self.work_dir / "policy.yaml"
            test_file = self.work_dir / "test.yaml"
            
            policy_file.write_text(policy_yaml)
            test_file.write_text(test_yaml)
            
            # Run cerbos test
            result = subprocess.run(
                ['cerbos', 'test', str(self.work_dir)],
                capture_output=True,
                text=True,
                timeout=60,
                shell=False  # Prevent shell injection
            )
            
            return self._parse_test_output(result.stdout)
            
        except subprocess.TimeoutExpired:
            raise RuntimeError("Test execution timeout")
        except Exception as e:
            raise RuntimeError(f"Test execution failed: {str(e)}")
        finally:
            # Clean up
            policy_file.unlink(missing_ok=True)
            test_file.unlink(missing_ok=True)
    
    def _extract_errors(self, output: str) -> list[str]:
        """Extract error messages from Cerbos output"""
        errors = []
        for line in output.split('\n'):
            if 'error' in line.lower() and line.strip():
                errors.append(line.strip())
        return errors
    
    def _extract_warnings(self, output: str) -> list[str]:
        """Extract warning messages from Cerbos output"""
        warnings = []
        for line in output.split('\n'):
            if 'warn' in line.lower() and line.strip():
                warnings.append(line.strip())
        return warnings
    
    def _parse_test_output(self, output: str) -> TestResult:
        """Parse Cerbos test output"""
        # Parse "X passed, Y failed" format
        passed_match = re.search(r'(\d+)\s+passed', output)
        failed_match = re.search(r'(\d+)\s+failed', output)
        
        passed = int(passed_match.group(1)) if passed_match else 0
        failed = int(failed_match.group(1)) if failed_match else 0
        
        return TestResult(
            passed=passed,
            failed=failed,
            total=passed + failed,
            details=output
        )

