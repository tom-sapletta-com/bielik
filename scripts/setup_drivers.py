#!/usr/bin/env python3
"""
Driver setup and verification script for Bielik.

This script helps users set up and verify the correct drivers
for optimal performance with Bielik's AI models.
"""

import os
import sys
import platform
import subprocess
import shutil
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

# Configure logging
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('driver_setup.log')
    ]
)
logger = logging.getLogger(__name__)

# Constants
IS_LINUX = platform.system() == 'Linux'
IS_MAC = platform.system() == 'Darwin'
IS_WINDOWS = platform.system() == 'Windows'

class DriverManager:
    """Manages driver setup and verification."""
    
    def __init__(self):
        """Initialize the driver manager."""
        self.system_info = self._get_system_info()
        self.driver_status = {
            'cuda': self._check_cuda(),
            'rocm': self._check_rocm(),
            'metal': self._check_metal(),
            'opencl': self._check_opencl(),
            'cpu': self._check_cpu()
        }
    
    def _get_system_info(self) -> Dict[str, str]:
        """Get system information."""
        return {
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'python_version': platform.python_version(),
        }
    
    def _run_command(self, cmd: Union[str, List[str]]) -> Tuple[int, str, str]:
        """Run a shell command and return the result."""
        if isinstance(cmd, str):
            cmd = cmd.split()
            
        try:
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            return (
                result.returncode,
                result.stdout.strip(),
                result.stderr.strip()
            )
        except Exception as e:
            logger.error(f"Error running command '{' '.join(cmd)}': {str(e)}")
            return (-1, "", str(e))
    
    def _check_cuda(self) -> Dict[str, Union[bool, str]]:
        """Check if CUDA is available and properly configured."""
        status = {
            'available': False,
            'version': None,
            'devices': [],
            'message': 'CUDA not detected'
        }
        
        if IS_WINDOWS:
            nvcc_path = shutil.which('nvcc')
            if nvcc_path:
                status['available'] = True
                # Get CUDA version from nvcc
                rc, out, _ = self._run_command('nvcc --version')
                if rc == 0 and 'release' in out:
                    version = out.split('release ')[1].split(',')[0]
                    status['version'] = version
                    status['message'] = f'CUDA {version} detected'
        
        elif IS_LINUX or IS_MAC:
            # Check for nvidia-smi
            nvidia_smi = shutil.which('nvidia-smi')
            if nvidia_smi:
                status['available'] = True
                rc, out, _ = self._run_command('nvidia-smi')
                if rc == 0:
                    # Parse nvidia-smi output
                    lines = out.split('\n')
                    for line in lines:
                        if 'Driver Version:' in line:
                            parts = line.split()
                            if len(parts) >= 6:
                                status['version'] = parts[5]
                                status['message'] = f'NVIDIA driver {parts[5]} detected'
        
        return status
    
    def _check_rocm(self) -> Dict[str, Union[bool, str]]:
        """Check if ROCm is available and properly configured."""
        status = {
            'available': False,
            'version': None,
            'devices': [],
            'message': 'ROCm not detected'
        }
        
        if IS_LINUX:
            # Check for ROCm installation
            rocminfo = shutil.which('rocminfo')
            if rocminfo:
                status['available'] = True
                rc, out, _ = self._run_command('rocminfo')
                if rc == 0:
                    status['message'] = 'ROCm is installed'
                    
                    # Try to get version from rocminfo
                    rc, version_out, _ = self._run_command('dpkg -l | grep rocm')
                    if rc == 0 and version_out:
                        # Extract version from package info
                        for line in version_out.split('\n'):
                            if 'rocm' in line and 'ii' in line:
                                parts = line.split()
                                if len(parts) > 2:
                                    status['version'] = parts[2]
                                    status['message'] = f'ROCm {parts[2]} detected'
                                    break
        
        return status
    
    def _check_metal(self) -> Dict[str, Union[bool, str]]:
        """Check if Metal is available (macOS only)."""
        status = {
            'available': False,
            'message': 'Metal not available'
        }
        
        if IS_MAC:
            # On macOS, Metal is the default GPU API
            status['available'] = True
            status['message'] = 'Metal is available on this Mac'
            
            # Try to get GPU info
            try:
                import metal
                device = metal.MTLCreateSystemDefaultDevice()
                if device:
                    status['device'] = str(device.name())
            except ImportError:
                pass
        
        return status
    
    def _check_opencl(self) -> Dict[str, Union[bool, str]]:
        """Check if OpenCL is available."""
        status = {
            'available': False,
            'platforms': [],
            'message': 'OpenCL not detected'
        }
        
        try:
            import pyopencl as cl
            platforms = cl.get_platforms()
            if platforms:
                status['available'] = True
                status['message'] = f'Found {len(platforms)} OpenCL platform(s)'
                for i, platform in enumerate(platforms):
                    platform_info = {
                        'name': platform.name.strip(),
                        'vendor': platform.vendor.strip(),
                        'version': platform.version.strip(),
                        'devices': []
                    }
                    
                    try:
                        devices = platform.get_devices()
                        for device in devices:
                            platform_info['devices'].append({
                                'name': device.name.strip(),
                                'type': str(device.type).split('.')[-1],
                                'version': device.version.strip(),
                                'max_work_group_size': device.max_work_group_size,
                                'max_compute_units': device.max_compute_units
                            })
                    except Exception as e:
                        logger.warning(f"Error getting OpenCL devices: {str(e)}")
                    
                    status['platforms'].append(platform_info)
        except ImportError:
            status['message'] = 'pyopencl not installed. Install with: pip install pyopencl'
        except Exception as e:
            status['message'] = f'Error checking OpenCL: {str(e)}'
        
        return status
    
    def _check_cpu(self) -> Dict[str, Union[bool, str]]:
        """Get CPU information."""
        cpu_info = {
            'name': platform.processor(),
            'cores': os.cpu_count() or 1,
            'architecture': platform.machine(),
            'message': 'CPU information'
        }
        
        # Try to get more detailed CPU info
        try:
            if IS_LINUX:
                with open('/proc/cpuinfo') as f:
                    for line in f:
                        if 'model name' in line:
                            cpu_info['name'] = line.split(':', 1)[1].strip()
                            break
            elif IS_MAC:
                rc, out, _ = self._run_command('sysctl -n machdep.cpu.brand_string')
                if rc == 0 and out:
                    cpu_info['name'] = out.strip()
            elif IS_WINDOWS:
                rc, out, _ = self._run_command('wmic cpu get name')
                if rc == 0 and out:
                    # Skip the header line and get the first CPU name
                    lines = [line.strip() for line in out.split('\n') if line.strip()]
                    if len(lines) > 1:
                        cpu_info['name'] = lines[1]
        except Exception as e:
            logger.warning(f"Could not get detailed CPU info: {str(e)}")
        
        return cpu_info
    
    def check_drivers(self) -> Dict[str, Dict[str, Union[bool, str]]]:
        """Check all available drivers and accelerators."""
        return self.driver_status
    
    def get_recommendations(self) -> List[str]:
        """Get recommendations for driver setup."""
        recommendations = []
        
        # Check for CUDA/ROCm on Linux
        if IS_LINUX:
            if not self.driver_status['cuda']['available'] and not self.driver_status['rocm']['available']:
                if 'nvidia' in str(self.driver_status['cpu']['name']).lower():
                    recommendations.append(
                        "NVIDIA GPU detected but CUDA is not installed. "
                        "Consider installing NVIDIA drivers and CUDA toolkit for better performance."
                    )
                elif 'amd' in str(self.driver_status['cpu']['name']).lower():
                    recommendations.append(
                        "AMD GPU detected but ROCm is not installed. "
                        "Consider installing ROCm for better performance with AMD GPUs."
                    )
        
        # Check for Metal on macOS
        if IS_MAC and not self.driver_status['metal']['available']:
            recommendations.append(
                "Metal is not available. Make sure you're running on a Mac with a Metal-compatible GPU."
            )
        
        # Check for OpenCL
        if not self.driver_status['opencl']['available']:
            recommendations.append(
                "OpenCL is not available. Install OpenCL drivers for your GPU for better compatibility."
            )
        
        # General recommendations
        if not any([
            self.driver_status['cuda']['available'],
            self.driver_status['rocm']['available'],
            self.driver_status['metal']['available']
        ]):
            recommendations.append(
                "No GPU acceleration detected. Bielik will run on CPU only, which may be slow. "
                "Consider installing appropriate GPU drivers for better performance."
            )
        
        return recommendations if recommendations else ["Your system is properly configured for optimal performance."]
    
    def print_summary(self):
        """Print a summary of the system configuration."""
        print("\n" + "="*50)
        print("Bielik Driver Setup and Verification")
        print("="*50)
        
        print("\nSystem Information:")
        print(f"  OS: {self.system_info['system']} {self.system_info['release']}")
        print(f"  CPU: {self.driver_status['cpu']['name']} ({self.driver_status['cpu']['cores']} cores)")
        
        print("\nAccelerator Status:")
        # CUDA
        cuda_status = self.driver_status['cuda']
        print(f"  CUDA: {'✅ Available' if cuda_status['available'] else '❌ Not available'}")
        if cuda_status['available']:
            print(f"    Version: {cuda_status.get('version', 'Unknown')}")
            print(f"    Message: {cuda_status['message']}")
        
        # ROCm
        rocm_status = self.driver_status['rocm']
        print(f"  ROCm: {'✅ Available' if rocm_status['available'] else '❌ Not available'}")
        if rocm_status['available']:
            print(f"    Version: {rocm_status.get('version', 'Unknown')}")
            print(f"    Message: {rocm_status['message']}")
        
        # Metal
        metal_status = self.driver_status['metal']
        print(f"  Metal: {'✅ Available' if metal_status['available'] else '❌ Not available'}")
        if metal_status['available']:
            print(f"    Device: {metal_status.get('device', 'Unknown')}")
        
        # OpenCL
        opencl_status = self.driver_status['opencl']
        print(f"  OpenCL: {'✅ Available' if opencl_status['available'] else '❌ Not available'}")
        if opencl_status['available']:
            print(f"    {opencl_status['message']}")
            for i, platform in enumerate(opencl_status['platforms']):
                print(f"    Platform {i+1}: {platform['name']} ({platform['vendor']})")
                for j, device in enumerate(platform['devices']):
                    print(f"      Device {j+1}: {device['name']} ({device['type']})")
        
        # Recommendations
        print("\nRecommendations:")
        for i, rec in enumerate(self.get_recommendations(), 1):
            print(f"  {i}. {rec}")
        
        print("\n" + "="*50 + "\n")


def main():
    """Main function for the driver setup script."""
    print("Bielik Driver Setup and Verification Tool")
    print("This tool will check your system for GPU drivers and provide setup recommendations.\n")
    
    try:
        manager = DriverManager()
        manager.print_summary()
        
        # Save results to a JSON file
        results = {
            'system_info': manager.system_info,
            'driver_status': manager.driver_status,
            'recommendations': manager.get_recommendations()
        }
        
        with open('bielik_driver_check.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        print("\nDetailed results have been saved to 'bielik_driver_check.json'")
        
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}", exc_info=True)
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
