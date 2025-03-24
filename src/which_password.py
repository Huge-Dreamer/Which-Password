#!/usr/bin/env python3
import os
import sys
import time
import logging
import argparse
from pathlib import Path
from typing import Optional, List
import subprocess
from tqdm import tqdm
import json
import signal
import threading
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
import multiprocessing
import psutil

class PasswordCracker:
    def __init__(self, config_path: str = "config/config.json"):
        self.config = self._load_config(config_path)
        self.setup_logging()
        self.sevenzip_path = self._find_sevenzip()
        self.running = True
        self.successful_password = None
        self.config_path = config_path

    def _load_config(self, config_path: str) -> dict:
        """Load configuration from JSON file or create default."""
        # Get system information
        cpu_count = multiprocessing.cpu_count()
        total_memory = psutil.virtual_memory().total
        available_memory = psutil.virtual_memory().available
        
        # Calculate optimal worker count based on CPU cores
        optimal_workers = min(cpu_count * 2, 16)  # Use 2x CPU cores, but cap at 16
        
        # Calculate memory-based limits
        max_memory_per_worker = 512 * 1024 * 1024  # 512MB per worker
        memory_based_workers = min(available_memory // max_memory_per_worker, 16)
        
        # Use the lower of CPU-based and memory-based worker counts
        max_workers = min(optimal_workers, memory_based_workers)
        
        default_config = {
            "max_workers": max_workers,
            "timeout": 0,  # 0 means no timeout
            "output_dir": "extracted",
            "save_successful": True,
            "successful_passwords_file": "successful_passwords.txt",
            "supported_formats": [".rar", ".zip", ".7z", ".tar", ".gz"],
            "retry_limit": 1000,
            "log_level": "INFO",
            "sevenzip_path": "",  # Allow custom 7-Zip path in config
            "batch_size": 1000,  # Number of passwords to process in each batch
            "memory_limit": int(available_memory * 0.8),  # Use 80% of available memory
            "cpu_priority": "high"  # Process priority
        }
        
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    return {**default_config, **json.load(f)}
        except Exception as e:
            print(f"Error loading config: {e}")
        
        return default_config

    def setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=getattr(logging, self.config["log_level"]),
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('password_cracker.log'),
                logging.StreamHandler()
            ]
        )
        
        # Set process priority
        try:
            if sys.platform == 'win32':
                import win32api, win32process, win32con
                priority = win32process.HIGH_PRIORITY_CLASS if self.config["cpu_priority"] == "high" else win32process.NORMAL_PRIORITY_CLASS
                win32process.SetPriorityClass(win32api.GetCurrentProcess(), priority)
            else:
                import os
                os.nice(-10)  # Increase priority on Unix-like systems
        except Exception as e:
            logging.warning(f"Could not set process priority: {e}")

    def _find_sevenzip(self) -> str:
        """Find 7-Zip installation path."""
        # First check if path is specified in config
        if self.config.get("sevenzip_path") and os.path.exists(self.config["sevenzip_path"]):
            return self.config["sevenzip_path"]

        # Then check common installation paths
        possible_paths = [
            r"C:\Program Files\7-Zip\7z.exe",
            r"C:\Program Files (x86)\7-Zip\7z.exe",
            os.path.expandvars(r"%ProgramFiles%\7-Zip\7z.exe"),
            os.path.expandvars(r"%ProgramFiles(x86)%\7-Zip\7z.exe"),
            os.environ.get("SEVENZIP_PATH", "")
        ]
        
        for path in possible_paths:
            if path and os.path.exists(path):
                return path
        
        # If not found, try to find it in PATH
        try:
            result = subprocess.run(['where', '7z'], capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip().split('\n')[0]
        except:
            pass

        print("\nError: 7-Zip not found!")
        print("\nPlease do one of the following:")
        print("1. Install 7-Zip from https://www.7-zip.org/")
        print("2. Add 7-Zip to your system PATH")
        print("3. Specify the path to 7-Zip in config.json:")
        print('   {"sevenzip_path": "C:\\Path\\To\\7z.exe"}')
        print("\nAfter doing one of the above, run the script again.")
        sys.exit(1)

    def try_password(self, archive_path: str, password: str) -> bool:
        """Try to extract the archive with a given password."""
        if not self.running:
            return False

        try:
            # Get the directory containing the archive
            archive_dir = os.path.dirname(os.path.abspath(archive_path))
            # Create output directory in the same directory as the archive
            output_dir = os.path.join(archive_dir, self.config["output_dir"])
            os.makedirs(output_dir, exist_ok=True)

            cmd = [
                self.sevenzip_path,
                "x",
                archive_path,
                f"-p{password}",
                f"-o{output_dir}",
                "-y"
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                self.successful_password = password
                if self.config["save_successful"]:
                    self._save_successful_password(password)
                return True

        except subprocess.TimeoutExpired:
            logging.warning(f"Timeout while trying password: {password}")
        except Exception as e:
            logging.error(f"Error trying password {password}: {e}")

        return False

    def _save_successful_password(self, password: str):
        """Save successful password to file."""
        try:
            # Get the directory containing the config file
            config_dir = os.path.dirname(self.config_path)
            # Save the successful passwords file in the same directory
            successful_file = os.path.join(config_dir, self.config["successful_passwords_file"])
            
            with open(successful_file, 'a') as f:
                f.write(f"{password}\n")
        except Exception as e:
            logging.error(f"Error saving successful password: {e}")

    def crack_password(self, archive_path: str, password_file: str):
        """Main password cracking function with progress tracking and timeout."""
        if not os.path.exists(archive_path):
            raise FileNotFoundError(f"Archive not found: {archive_path}")
        if not os.path.exists(password_file):
            raise FileNotFoundError(f"Password file not found: {password_file}")

        # Read passwords in batches
        batch_size = self.config["batch_size"]
        total_passwords = 0
        processed_passwords = 0
        
        # Count total passwords first
        with open(password_file, 'r', encoding='utf-8', errors='ignore') as f:
            total_passwords = sum(1 for _ in f)
        
        logging.info(f"Starting password cracking with {total_passwords} passwords")
        logging.info(f"Using {self.config['max_workers']} workers with batch size {batch_size}")

        # Setup timeout if specified
        timeout_event = threading.Event()
        if self.config["timeout"] > 0:
            timer = threading.Timer(self.config["timeout"], self._handle_timeout, args=[timeout_event])
            timer.start()

        try:
            with ThreadPoolExecutor(max_workers=self.config["max_workers"]) as executor:
                with open(password_file, 'r', encoding='utf-8', errors='ignore') as f:
                    batch = []
                    futures = []
                    
                    for line in f:
                        if not self.running or timeout_event.is_set():
                            break
                            
                        password = line.strip()
                        if password:
                            batch.append(password)
                            
                            if len(batch) >= batch_size:
                                # Submit batch of passwords
                                for pwd in batch:
                                    if not self.running or timeout_event.is_set():
                                        break
                                    futures.append(
                                        executor.submit(self.try_password, archive_path, pwd)
                                    )
                                batch = []
                                
                                # Process completed futures
                                for future in tqdm(futures, total=len(futures), 
                                                 desc=f"Trying passwords ({processed_passwords}/{total_passwords})",
                                                 leave=False):
                                    try:
                                        if future.result(timeout=0.1):  # 100ms timeout per password
                                            self.running = False
                                            break
                                    except TimeoutError:
                                        continue
                                    
                                    if not self.running or timeout_event.is_set():
                                        break
                                
                                processed_passwords += len(futures)
                                futures = []
                                
                                # Check memory usage
                                if psutil.Process().memory_info().rss > self.config["memory_limit"]:
                                    logging.warning("Memory limit reached, waiting for cleanup...")
                                    time.sleep(1)  # Give system time to free memory
                    
                    # Process remaining passwords
                    if batch and self.running and not timeout_event.is_set():
                        for pwd in batch:
                            futures.append(
                                executor.submit(self.try_password, archive_path, pwd)
                            )
                        
                        for future in tqdm(futures, total=len(futures),
                                         desc=f"Trying passwords ({processed_passwords}/{total_passwords})",
                                         leave=False):
                            try:
                                if future.result(timeout=0.1):
                                    self.running = False
                                    break
                            except TimeoutError:
                                continue
                            
                            if not self.running or timeout_event.is_set():
                                break
                        
                        processed_passwords += len(futures)

        finally:
            if self.config["timeout"] > 0:
                timer.cancel()
            self.running = False

        if self.successful_password:
            logging.info(f"Success! Password found: {self.successful_password}")
        else:
            logging.info("No valid password found.")

    def _handle_timeout(self, timeout_event: threading.Event):
        """Handle timeout event."""
        timeout_event.set()
        self.running = False
        logging.info("Stopping password cracking process...")

    def stop_cracking(self):
        """Stop the password cracking process."""
        self.running = False
        logging.info("Stopping password cracking process...")

def main():
    parser = argparse.ArgumentParser(description="Password-protected archive cracker")
    parser.add_argument("archive", help="Path to the archive file")
    parser.add_argument("--passwords", default="PWD.txt", help="Path to password file")
    parser.add_argument("--config", default="config.json", help="Path to config file")
    args = parser.parse_args()

    try:
        cracker = PasswordCracker(args.config)
        cracker.crack_password(args.archive, args.passwords)
    except KeyboardInterrupt:
        print("\nProcess interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 